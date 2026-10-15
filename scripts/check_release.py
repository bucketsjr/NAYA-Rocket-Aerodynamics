#!/usr/bin/env python3
"""Automatic non-exhaustive packaging sanity checks. NOT a confidentiality review."""
from pathlib import Path
import sys,json
import trimesh
ROOT=Path(__file__).resolve().parents[1]
assert (ROOT/'LICENSE').exists() and (ROOT/'LICENSE-DOCS.md').exists()
assert 'not' in (ROOT/'README.md').read_text().lower()
model=ROOT/'geometry'/'naya_concept.stl'
assert model.exists()
assert trimesh.load_mesh(model,force='mesh').is_watertight
assert json.loads((ROOT/'results'/'potential_flow_metadata.json').read_text())['residual']<1e-6
assert all((ROOT/'figures'/p).exists() for p in ('speed_surrogate.png','cp_surrogate.png','streamlines_surrogate.png','grid_sensitivity_surrogate.png','concept_cad_surface.png','domain_schematic.png'))
print('PASS: files present, surface watertight, numerical residual reported. Manual IP and scientific checks still required.')
