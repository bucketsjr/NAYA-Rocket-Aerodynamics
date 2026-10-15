from pathlib import Path
import sys,json
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from model import Rocket
from potential_flow_2d import solve

def test_shape_data_invariants():
    r=Rocket().validate()
    assert abs(r.length_m-.885)<1e-8
    assert np.isclose(r.body_radius(r.nose_tip),0)
    assert np.isclose(r.body_radius(0),r.body_radius_m)
    assert r.fin_radius(np.array([.3]))[0]>r.body_radius_m

def test_generated_stl_is_watertight():
    m=trimesh.load_mesh(ROOT/'geometry'/'naya_concept.stl')
    assert m.is_watertight
    assert abs(m.bounds[1,0]-m.bounds[0,0]-.885)<.002

def test_potential_flow_linear_solver_and_farfield():
    s=solve(100,65,10)
    assert s['residual']<1e-7
    # Outer flow away from obstacle should be close to imposed freestream.
    iy=np.argmin(abs(s['y']-0.56));ix=np.argmin(abs(s['x']+1.35))
    assert abs(s['vx'][iy,ix]-10)<1.0
    assert abs(s['vy'][iy,ix])<1.0
    assert np.any(s['solid'])

def test_metadata_has_experimental_status():
    meta=json.loads((ROOT/'results'/'potential_flow_metadata.json').read_text())
    assert 'not 3D viscous CFD' in meta['status']
