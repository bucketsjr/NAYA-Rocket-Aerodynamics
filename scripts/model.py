"""Explicit assumptions for a NAYA-inspired *illustrative* rocket body.

Only body length (0.885 m) is traced to the project summary. Other dimensions
are modelling assumptions until checked against the as-built CAD.
"""
from dataclasses import dataclass, asdict
import json
from pathlib import Path
import numpy as np

@dataclass(frozen=True)
class Rocket:
    length_m: float = 0.885  # project summary (not a CAD measurement)
    body_radius_m: float = 0.045  # assumed, NOT measured
    nose_length_m: float = 0.210  # assumed
    tail_taper_length_m: float = 0.045  # assumed
    tail_radius_m: float = 0.033  # assumed
    fin_start_m: float = 0.170  # assumed; x wrt rocket centre
    fin_sweep_m: float = 0.085  # assumed
    fin_end_m: float = 0.410  # assumed
    fin_outer_radius_m: float = 0.135  # assumed
    fin_thickness_m: float = 0.004  # assumed
    fin_count: int = 4  # assumed for surrogate geometry

    def validate(self):
        assert self.length_m > self.nose_length_m > 0
        assert 0 < self.tail_radius_m < self.body_radius_m
        assert 0 < self.tail_taper_length_m < self.length_m / 2
        assert self.fin_start_m < self.fin_end_m < self.length_m / 2
        assert self.fin_outer_radius_m > self.body_radius_m
        assert self.fin_count == 4, 'This demonstration uses four fins.'
        return self

    @property
    def nose_tip(self): return -self.length_m / 2
    @property
    def tail_end(self): return self.length_m / 2
    @property
    def nose_base(self): return self.nose_tip + self.nose_length_m
    @property
    def tail_taper_start(self): return self.tail_end - self.tail_taper_length_m

    def body_radius(self, x):
        xx = np.asarray(x)
        r = np.full_like(xx, self.body_radius_m, dtype=float)
        s = np.clip((xx-self.nose_tip)/self.nose_length_m, 0, 1)
        r = np.where(xx < self.nose_base, self.body_radius_m*np.sin(0.5*np.pi*s), r)
        t = np.clip((xx-self.tail_taper_start)/self.tail_taper_length_m, 0, 1)
        r = np.where(xx > self.tail_taper_start,
                     self.body_radius_m + (self.tail_radius_m-self.body_radius_m)*t, r)
        return np.where((xx < self.nose_tip) | (xx > self.tail_end), 0.0, r)

    def fin_radius(self, x):
        """Approximate 2D cross-section of a vertical fin pair, NOT actual 3D CFD."""
        xx = np.asarray(x)
        r = self.body_radius(xx)
        leading = self.fin_start_m
        tip_start = self.fin_start_m + self.fin_sweep_m
        ramp = np.clip((xx-leading)/(tip_start-leading),0,1)
        maxr = self.body_radius_m + (self.fin_outer_radius_m-self.body_radius_m)*ramp
        aft = np.clip((self.fin_end_m-xx)/0.055,0,1)
        maxr = np.minimum(maxr, self.body_radius_m+(self.fin_outer_radius_m-self.body_radius_m)*aft)
        return np.where((xx>=leading) & (xx<=self.fin_end_m), np.maximum(r,maxr),r)

    def to_json(self, filepath):
        p=Path(filepath);p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps({'data_status':'assumed geometry except length','units':'SI','parameters':asdict(self)},indent=2)+'\n')
