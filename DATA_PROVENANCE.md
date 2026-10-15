# Data and figure provenance (read before citing)

| Item | Origin / method | Scientific status |
|---|---|---|
| 885 mm overall length | Existing capstone project summary | Reported project nominal dimension, **not independently checked against CAD** |
| Radius, fin position/span, nose profile, geometry | Explicit parameters invented for a NAYA-inspired concept | Assumed; no as-built fidelity claim |
| 15 m/s freestream | Selected illustration parameter | Not a measurement and not an inferred rocket velocity |
| `naya_concept.stl` | CadQuery/OpenCascade solid union exported + manifold-repair filter | Recreated new concept; watertight STL verified using Trimesh |
| `speed_surrogate.png` | Numerical finite-volume potential-flow computation at 400 × 200 | Real calculated *2-D inviscid* flow, not full CFD |
| `cp_surrogate.png` | Bernoulli post-processing of calculated potential-field velocity | Idealised 2-D model Cp, not turbulent viscous Cp |
| `streamlines_surrogate.png` | Streamplot of calculated two-dimensional velocity | Educational streamline illustration only |
| `grid_sensitivity_surrogate.png` / CSV | Four reruns at different grids of same new potential-flow solver | Mesh-independence **not demonstrated** |
| `dimensional_estimates.csv` | Algebra with specified assumed air properties | Analytical dimensional checks only |
| `domain_schematic.png` | Manually drawn scheme from case domain numbers | Schematic, not CFD mesh/contour |
| `concept_cad_surface.png` | Plot of generated triangular surface STL | CAD surface display, not 3-D CFD volume mesh |
| `openfoam/naya_external` | Authored input files for a future `simpleFoam` run | **Never executed here; no RANS fields produced** |
