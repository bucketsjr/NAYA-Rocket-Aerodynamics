PYTHON ?= python3
.PHONY: checks geometry surrogate graphics estimates openfoam-case
checks:
	$(PYTHON) -m pytest -q
	$(PYTHON) scripts/check_release.py
geometry:
	$(PYTHON) scripts/generate_geometry.py --output geometry/naya_concept.stl --check
openfoam-case:
	$(PYTHON) scripts/create_openfoam_case.py
surrogate:
	$(PYTHON) scripts/potential_flow_2d.py --nx 400 --ny 200 --u 15
estimates:
	$(PYTHON) scripts/flow_estimates.py
graphics:
	$(PYTHON) scripts/make_portfolio_figures.py
