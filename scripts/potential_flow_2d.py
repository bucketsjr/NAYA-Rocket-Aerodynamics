#!/usr/bin/env python3
"""Solve Laplace's equation for idealised 2-D potential flow around a rocket profile.

Governing assumptions: incompressible, irrotational, inviscid, steady 2-D.
This is a genuine *numerical potential-flow* calculation, NOT viscous CFD,
NOT 3-D rocket RANS, and NOT flight/test-performance evidence.

Discretisation: cell-centered FV five-point Laplacian, zero normal flow on
stair-stepped immersed solid, prescribed freestream potential on outer faces.
"""
import argparse, csv, json
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import cg, LinearOperator
from scipy.ndimage import distance_transform_edt
from model import Rocket

def solve(nx=320,ny=160, freestream=15.0, rocket=None, limit=4000):
    r=(rocket or Rocket()).validate()
    xb=(-1.8,2.2);yb=(-0.72,0.72)
    dx=(xb[1]-xb[0])/nx;dy=(yb[1]-yb[0])/ny
    x=xb[0]+(np.arange(nx)+0.5)*dx
    y=yb[0]+(np.arange(ny)+0.5)*dy
    X,Y=np.meshgrid(x,y)
    solid=(np.abs(Y)<=r.fin_radius(X))&(X>=r.nose_tip)&(X<=r.tail_end)
    fluid=~solid
    ids=np.full(fluid.shape,-1,dtype=np.int32)
    ids[fluid]=np.arange(fluid.sum(),dtype=np.int32)
    n=fluid.sum()
    diag=np.zeros(n);b=np.zeros(n)
    rows=[];cols=[];data=[]
    # For an internal face, attach standard -laplace coefficients.
    # For a solid adjacent cell face, face flux is zero (no penetration).
    # On an external boundary, φ = U∞ x at the face, with half-cell distance.
    for direction,offset,spacing in [('E',(0,1),dx),('W',(0,-1),dx),('N',(1,0),dy),('S',(-1,0),dy)]:
        dj,di=offset
        j0,j1=max(0,-dj),min(ny,ny-dj)
        i0,i1=max(0,-di),min(nx,nx-di)
        current=fluid[j0:j1,i0:i1]
        adjacent=fluid[j0+dj:j1+dj,i0+di:i1+di]
        both=current & adjacent
        src=ids[j0:j1,i0:i1][both]
        dst=ids[j0+dj:j1+dj,i0+di:i1+di][both]
        w=1.0/(spacing**2)
        diag[src]+=w
        rows.append(src);cols.append(dst);data.append(np.full(len(src),-w))
        # External Dirichlet faces, all of which are outside the fluid body.
        if direction=='E': edge=fluid[:,-1];src=ids[:,-1][edge];phi=freestream*xb[1]
        elif direction=='W': edge=fluid[:,0];src=ids[:,0][edge];phi=freestream*xb[0]
        elif direction=='N': edge=fluid[-1,:];src=ids[-1,:][edge];phi=freestream*x[edge]
        else: edge=fluid[0,:];src=ids[0,:][edge];phi=freestream*x[edge]
        diag[src]+=2*w
        b[src]+=2*w*phi
    rows.append(np.arange(n,dtype=np.int32));cols.append(np.arange(n,dtype=np.int32));data.append(diag)
    A=sparse.coo_matrix((np.concatenate(data),(np.concatenate(rows),np.concatenate(cols))),shape=(n,n)).tocsr()
    precond=LinearOperator((n,n),matvec=lambda v:v/diag)
    initial=(freestream*X)[fluid]
    counter=[0]
    def tick(_):counter[0]+=1
    phi_inner,status=cg(A,b,x0=initial,rtol=1e-9,atol=1e-10,maxiter=limit,M=precond,callback=tick)
    if status!=0: raise RuntimeError(f'Linear solver did not converge. cg status={status}, iterations={counter[0]}')
    resid=float(np.linalg.norm(A@phi_inner-b)/np.linalg.norm(b))
    phi=np.full((ny,nx),np.nan)
    phi[fluid]=phi_inner
    # Nearest-fluid extension is exclusively for visualisation. Velocities
    # directly adjacent to stepped boundaries are masked and not quantitative.
    nearest=distance_transform_edt(solid,return_distances=False,return_indices=True)
    extended=phi[tuple(nearest)]
    vx=np.gradient(extended,dx,axis=1)
    vy=np.gradient(extended,dy,axis=0)
    from scipy.ndimage import binary_dilation
    edge=binary_dilation(solid,iterations=2)
    vx=np.where(edge,np.nan,vx);vy=np.where(edge,np.nan,vy)
    speed=np.sqrt(vx*vx+vy*vy)
    cp=1-(speed/freestream)**2
    # Sample an *off-body fixed location*, away from wall numerical artefacts.
    probe=(-0.055,0.190)
    pi=np.argmin(abs(x-probe[0]));pj=np.argmin(abs(y-probe[1]))
    if not np.isfinite(cp[pj,pi]): raise ValueError('Probe overlaps the masked body region')
    return dict(x=x,y=y,X=X,Y=Y,solid=solid,phi=phi,vx=vx,vy=vy,speed=speed,cp=cp,
                nx=nx,ny=ny,dx=dx,dy=dy,freestream=freestream,iterations=counter[0],residual=resid,
                probe_x=float(x[pi]),probe_y=float(y[pj]),probe_cp=float(cp[pj,pi]),
                probe_speed=float(speed[pj,pi]))

def plot_fields(sol,out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mp
    plt.rcParams.update({'font.size':10,'figure.dpi':150,'savefig.dpi':180,
                         'axes.spines.top':False,'axes.spines.right':False})
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    xx=sol['x'];yy=sol['y'];solid=sol['solid'];X=sol['X'];Y=sol['Y']
    status='ILLUSTRATIVE 2-D INVISCID POTENTIAL FLOW | NOT RANS OR FLIGHT VALIDATION'
    fields=[('speed',sol['speed'],'Velocity magnitude [m/s]','viridis',0.7*sol['freestream'],1.6*sol['freestream']),
            ('cp',sol['cp'],'Ideal-flow pressure coefficient Cp [–]','coolwarm',-1.3,1.2)]
    for tag,values,cbar,cmap,lo,hi in fields:
        fig,ax=plt.subplots(figsize=(12.0,4.0))
        h=ax.pcolormesh(X,Y,np.ma.masked_invalid(values),cmap=cmap,vmin=lo,vmax=hi,shading='nearest',rasterized=True)
        ax.contour(X,Y,solid.astype(float),levels=[0.5],colors='white',linewidths=1.0)
        ax.set_xlim(-0.72,0.88);ax.set_ylim(-0.28,0.28)
        ax.set_aspect('equal');ax.set_xlabel('Axial position x [m]');ax.set_ylabel('Transverse position y [m]')
        ax.set_title(f'NAYA-inspired rocket · {cbar}')
        cb=fig.colorbar(h,ax=ax,fraction=0.033,pad=0.02);cb.set_label(cbar)
        fig.text(.5,.018,status,ha='center',fontsize=8,color='#777777')
        fig.tight_layout(rect=(0,.05,1,1));fig.savefig(out/f'{tag}_surrogate.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(12,4))
    u=np.ma.masked_invalid(sol['vx']);v=np.ma.masked_invalid(sol['vy'])
    ax.streamplot(xx,yy,u,v,color='#2171b5',density=1.7,linewidth=.75,arrowsize=.65)
    ax.contourf(X,Y,solid.astype(float),levels=[.5,1.5],colors=['#262b32'])
    ax.set_xlim(-0.72,0.88);ax.set_ylim(-0.28,0.28);ax.set_aspect('equal')
    ax.set_xlabel('Axial position x [m]');ax.set_ylabel('Transverse position y [m]')
    ax.set_title('NAYA-inspired rocket · Ideal 2-D streamlines')
    fig.text(.5,.018,status,ha='center',fontsize=8,color='#777777')
    fig.tight_layout(rect=(0,.05,1,1));fig.savefig(out/'streamlines_surrogate.png');plt.close(fig)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--nx',type=int,default=320);ap.add_argument('--ny',type=int,default=160)
    ap.add_argument('--u',type=float,default=15.0)
    ap.add_argument('--output',default='figures');ap.add_argument('--results',default='results')
    opts=ap.parse_args()
    if opts.nx<70 or opts.ny<40 or opts.u<=0:ap.error('Need nx>=70, ny>=40, U>0')
    s=solve(opts.nx,opts.ny,opts.u)
    plot_fields(s,opts.output)
    result=Path(opts.results);result.mkdir(parents=True,exist_ok=True)
    meta={k:s[k] for k in ('nx','ny','dx','dy','freestream','iterations','residual','probe_x','probe_y','probe_cp','probe_speed')}
    meta['model']='2D inviscid irrotational potential flow; finite-volume Laplace equation'
    meta['status']='NEW numerical surrogate computation; not 3D viscous CFD or historic SEM400/NAYA results'
    (result/'potential_flow_metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps(meta,indent=2))
if __name__=='__main__':main()
