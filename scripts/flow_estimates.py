#!/usr/bin/env python3
"""Dimensional checks only. NOT CFD predictions, drag estimates, or flight data."""
import csv, math, argparse
from pathlib import Path
from model import Rocket

def rows(speeds=(5,15,30), rho=1.225,nu=1.5e-5,speed_of_sound=343):
    r=Rocket();d=2*r.body_radius_m
    for U in speeds:
        yield {'U_m_s':U,'q_Pa':.5*rho*U**2,'Re_based_on_length':U*r.length_m/nu,
               'Re_based_on_assumed_diameter':U*d/nu,'Mach_assumed_343_m_s':U/speed_of_sound,
               'reference_frontal_area_m2':math.pi*(d/2)**2}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default='results/dimensional_estimates.csv')
    o=p.parse_args();dest=Path(o.output);dest.parent.mkdir(parents=True,exist_ok=True)
    rr=list(rows());
    with open(dest,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
    print('Wrote assumptions-only dimensionless/dimensional estimates:',dest)
