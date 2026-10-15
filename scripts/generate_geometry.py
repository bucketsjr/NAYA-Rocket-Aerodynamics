#!/usr/bin/env python3
"""Create a watertight CAD-derived STL for an assumed NAYA-like rocket.

Uses CadQuery/OpenCascade to fuse four fins with the fuselage. This is NOT a
release of original NAYA CAD and must not be called an as-built replica.
"""
import argparse
from pathlib import Path
import numpy as np
from model import Rocket

def make_shape(rocket: Rocket):
    import cadquery as cq
    rocket.validate()
    xx=np.linspace(rocket.nose_tip,rocket.nose_base,23)
    profile=[(float(x),float(rocket.body_radius(x))) for x in xx]
    profile += [(rocket.tail_taper_start,rocket.body_radius_m),
                (rocket.tail_end,rocket.tail_radius_m),
                (rocket.tail_end,0),(rocket.nose_tip,0)]
    body=cq.Workplane('XY').polyline(profile).close().revolve(360,(0,0),(1,0))
    # Fin polygon in x-z plane, with its root embedded slightly in the body.
    # This geometry is for demonstrative surface meshing, not manufacturing.
    inner=rocket.body_radius_m - 0.008
    coords=[(rocket.fin_start_m,inner),
            (rocket.fin_start_m+rocket.fin_sweep_m,rocket.fin_outer_radius_m),
            (rocket.fin_end_m-0.055,rocket.fin_outer_radius_m),
            (rocket.fin_end_m,inner)]
    fin=(cq.Workplane('XZ').polyline(coords).close()
           .extrude(rocket.fin_thickness_m/2,both=True))
    for a in range(0,360,90):
        body=body.union(fin.rotate((0,0,0),(1,0,0),a))
    return body.val()

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',default='geometry/naya_concept.stl')
    p.add_argument('--check',action='store_true')
    args=p.parse_args()
    import cadquery as cq
    r=Rocket().validate()
    dst=Path(args.output);dst.parent.mkdir(parents=True,exist_ok=True)
    shp=make_shape(r)
    cq.exporters.export(shp,str(dst),exportType='STL',tolerance=0.0018,angularTolerance=0.18)
    r.to_json(dst.with_suffix('.json'))
    print('Geometry:',dst,'volume_m3:',round(shp.Volume(),6))
    import trimesh
    m=trimesh.load_mesh(dst,force='mesh')
    # Some OpenCascade tessellations generate a detached, zero-area seam face.
    # Retain the primary component, and verify the exported geometry is manifold.
    components=m.split(only_watertight=False)
    m=max(components,key=lambda a:len(a.faces))
    m.export(dst)
    if args.check:
        print('faces:',len(m.faces),'watertight:',m.is_watertight,'bounds:',m.bounds)
        assert m.is_watertight
if __name__ == '__main__': main()
