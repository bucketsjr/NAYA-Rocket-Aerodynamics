# Verification and validation evidence matrix

| Topic | Evidence | State |
|---|---|---|
| Assumptions and traceability | `scripts/model.py`, `geometry/naya_concept.json` | Explicit; only length stems from prior project summary |
| CAD surface closure | Trimesh watertightness + tests | Checked PASS for included new STL |
| Discrete potential equation linear solve | `potential_flow_metadata.json` | PASS at 400×200; relative residual ≈9.7e−10 |
| Far-field velocity consistency | Unit test near remote inlet corner | Basic numerical smoke test PASS |
| 2-D surrogate grid convergence | `grid_sensitivity_surrogate.csv` | **NOT SHOWN**; Cp probe changes |
| 3-D OpenFOAM mesh generation | `openfoam/naya_external` | **NOT RUN** |
| 3-D wall y+, convergence, load balance | Future RANS logs, forces, y+ plots | **NOT AVAILABLE** |
| Grid convergence of aerodynamic loads | Need at least three proven 3-D cases | **NOT AVAILABLE** |
| Physical benchmark validation | Need independent trusted measurements | **NOT AVAILABLE** |

## Four different meanings of “verified”

- **Algebraic convergence:** the discrete equations were solved to a numerical residual tolerance.
- **Discretisation convergence:** a quantity of interest is stable under systematic grid refinement.
- **Model suitability:** assumptions represent important physics, including viscous/turbulent effects.
- **Validation:** predictions agree with experimental reality or a relevant trusted benchmark within uncertainty.

The existing results only establish limited algebraic convergence and basic coding smoke tests. They are useful for a portfolio on method and scientific transparency, **not physical certification or CFD-derived aerodynamics**.
