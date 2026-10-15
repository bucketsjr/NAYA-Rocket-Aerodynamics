# Transfer from SEM400 wing CFD to NAYA-inspired rocket analysis

**Provenance:** The earlier SEM400 AIAA DPW2 wing project and its methodology are known from previous project discussions, but the original ANSYS Fluent `.cas`/`.dat` files and numerical output were **not available** when this new repository was generated. This is **new research-extension work**, not a recovered or rebranded CFD assessment.

| Workflow | SEM400 project work | NAYA-inspired new study | Evidence here |
|---|---|---|---|
| Geometry | Wing half-body and DesignModeler boolean operations | Parametric rocket with assumed diameter and fins | New CadQuery generator, watertight STL |
| Computational domain | Far-field box | Uniform external flow box | Schematic and blockMesh dictionary |
| Meshing | Refinement + inflation layers | snappyHexMesh, planned inflation | **Unrun** starter case; inflation currently off |
| Boundary conditions | Pressure far-field | Incompressible velocity inlet, pressure outlet, imposed lateral freestream | **Unrun** starter; boundary formulations not identical |
| Turbulence | k–ω SST | k–ω SST selected | Configuration only; no RANS solution |
| Verification | Mesh independence investigations | 2-D surrogate grid sensitivity, future formal 3-D study | Real four-grid 2-D results; **not grid-independent** |
| Validation | Reference workshop comparison | Future independent experiment / benchmark | **Not available** |

## What changes in a rocket analysis?

A rocket requires a clear axial direction, a reference centre for force/moment extraction, and appropriate frontal reference area. The four fins preclude a generic half-wing symmetry setup for asymmetric angle of attack. A hypothetical *unpowered* freestream study is **not** representative of the original NAYA suspended powered test rig. The current potential-flow solver does not capture boundary-layer shear, separation or turbulent wake structure.

## Suitable interview description

> I transferred the CFD workflow from my wing simulation coursework to a new rocket-concept geometry: controlled assumptions, CAD/pre-processing, numerical visualisation, sensitivity analysis and a higher-fidelity OpenFOAM configuration. The repository distinguishes successful educational calculations from future RANS computations and measurements not yet conducted.
