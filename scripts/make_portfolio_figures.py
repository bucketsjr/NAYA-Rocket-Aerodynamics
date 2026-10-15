#!/usr/bin/env python3
"""Rebuild illustration and grid-sensitivity assets, without inventing RANS data."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh
from model import Rocket
from potential_flow_2d import solve

ROOT=Path(__file__).resolve().parents[1]
FIG=ROOT/'figures';RES=ROOT/'results'
FIG.mkdir(exist_ok=True);RES.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':10,'savefig.dpi':180,'axes.spines.top':False,'axes.spines.right':False})
r=Rocket()

# Figure 1 — 3-D surface geometry created from *this* repository's own STL.
mesh=trimesh.load_mesh(ROOT/'geometry'/'naya_concept.stl',process=True)
fig=plt.figure(figsize=(10,5.8))
ax=fig.add_subplot(111,projection='3d',computed_zorder=False)
tri=mesh.vertices[mesh.faces]
collection=Poly3DCollection(tri,facecolor='#b7c4d0',edgecolors='#63798b',linewidths=.05,alpha=1)
ax.add_collection3d(collection)
ax.set_xlim(-0.55,.55);ax.set_ylim(-.25,.25);ax.set_zlim(-.25,.25)
ax.set_box_aspect((2.3,1,1),zoom=1.5)
ax.view_init(elev=23,azim=-55)
ax.set_axis_off()
ax.set_title('NAYA-inspired parametric geometry | Assumed dimensions',pad=20,fontsize=14)
fig.text(.5,.05,'CAD-derived surface triangulation — not an as-built NAYA model or volume mesh',ha='center',color='#5a6471',fontsize=9)
fig.tight_layout();fig.savefig(FIG/'concept_cad_surface.png');plt.close(fig)

# Figure 2 — domain schematic, not a CFD mesh display.
fig,ax=plt.subplots(figsize=(11,4.2))
ax.add_patch(Rectangle((-1.8,-.72),4,1.44,fill=False,lw=1.7,color='#333333'))
xx=np.linspace(r.nose_tip,r.tail_end,800);rr=r.fin_radius(xx)
ax.fill_between(xx,-rr,rr,color='#424c5a',lw=0)
ax.plot(xx,rr,color='#20262b',lw=.8);ax.plot(xx,-rr,color='#20262b',lw=.8)
for y in [-.54,-.38,0,.38,.54]:
    ax.annotate('',xy=(-1.20,y),xytext=(-1.62,y),arrowprops={'arrowstyle':'->','lw':1.7,'color':'#197c96'})
ax.text(-1.77,.79,'Inlet: uniform freestream',color='#197c96')
ax.text(1.12,.79,'Outlet: reference pressure',color='#197c96')
ax.text(.68,-.84,'Far-field transverse boundaries',color='#444')
ax.text(0,-.29,'No-slip body (RANS template)',ha='center',color='#4a5568')
ax.set_xlim(-1.95,2.34);ax.set_ylim(-.96,.96);ax.set_aspect('equal')
ax.set_xlabel('x [m]');ax.set_ylabel('y [m]')
ax.set_title('3-D external-flow domain (planar schematic, not computational mesh)')
fig.tight_layout();fig.savefig(FIG/'domain_schematic.png');plt.close(fig)

# Figure 3 — multi-grid sensitivity of actual new 2D numerical solution.
rows=[]
for nx,ny in [(160,80),(240,120),(320,160),(400,200)]:
    s=solve(nx,ny,freestream=15)
    rows.append((nx,ny,nx*ny,s['dx'],s['dy'],s['iterations'],s['residual'],s['probe_cp']))
import csv
with open(RES/'grid_sensitivity_surrogate.csv','w',newline='') as f:
    w=csv.writer(f);w.writerow(['nx','ny','rectangular_cells_total','dx_m','dy_m','cg_iterations','linear_residual_l2','cp_fixed_off_body_probe']);w.writerows(rows)
fig,ax=plt.subplots(figsize=(8.3,4.6))
ax.plot([q[2] for q in rows],[q[7] for q in rows],marker='o',lw=2,color='#187a99')
for q in rows:
    ax.annotate(f'{q[0]}×{q[1]}',xy=(q[2],q[7]),xytext=(6,7),textcoords='offset points',fontsize=8)
ax.axhline(0,color='#999',lw=.6)
ax.set_xlabel('Total structured cells in 2-D domain [–]')
ax.set_ylabel('Cp at fixed off-body probe, approx x = −0.055 m, y = 0.190 m [–]')
ax.set_title('Grid sensitivity | 2-D potential-flow surrogate')
ax.grid(alpha=.2)
fig.text(.5,.015,'Non-monotonic response possible with stair-stepped geometry; NOT a 3-D CFD convergence claim.',ha='center',fontsize=8,color='#68707b')
fig.tight_layout(rect=(0,.04,1,1));fig.savefig(FIG/'grid_sensitivity_surrogate.png');plt.close(fig)
print('Saved:',*[str(x) for x in FIG.glob('*.png')],sep='\n')
