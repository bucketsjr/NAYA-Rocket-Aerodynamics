# Reproduction and extension instructions

## Educational 2-D numerical results (tested here)

From repository root on macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
python scripts/potential_flow_2d.py --nx 400 --ny 200 --u 15
python scripts/flow_estimates.py
```

This reproduces the computed 2-D potential-flow plots and dimensional estimate CSV. CadQuery is **not** needed because the watertight concept STL is provided.

## Optional CAD generation (tested here)

```bash
python -m pip install -r requirements-cad.txt
python scripts/generate_geometry.py --output geometry/naya_concept.stl --check
python scripts/create_openfoam_case.py
python scripts/make_portfolio_figures.py
```

CadQuery's binary OpenCascade dependency may work best from an appropriate conda environment. Modifying dimensions in `scripts/model.py` requires rerunning **all** dependent geometry, OpenFOAM copying, numerical fields and visuals.

## Three-dimensional OpenFOAM case (UNTESTED HERE)

An OpenFOAM.com-style `simpleFoam` starter lives in `openfoam/naya_external`. Install and source a compatible OpenFOAM environment on Linux or in a suitable container. No compatible OpenFOAM utilities were installed in the authoring environment.

```bash
cd openfoam/naya_external
./Allrun
```

The script attempts `blockMesh`, feature extraction, `snappyHexMesh -overwrite`, `checkMesh` and `simpleFoam`, with `log.*` output. **This package does not claim the script completes.** Solver variants may require dictionary changes. The assumed fin thickness is challenging for hex-mesh resolution, and near-wall inflation has not been configured. Even an apparently successful run needs evidence of mass/force convergence, adequate wall y+, mesh/domain independence and physical validation.

## Archive a future validated CFD run

Document OpenFOAM version, hardware, exact dictionaries, per-mesh cell counts, checkMesh logs, residuals, wall y+, forces, post-processing scripts and external validation. Do not hand-enter "CFD" columns into the included surrogate CSV.
