"""The assistant's tools must run the engine correctly (no API call needed)."""
import json
import pytest
from server import assistant as A

CASES = [
    ("plane_wave", {"f": 2.45e9, "eps_r": 52.7, "sigma": 1.74}),
    ("coordinate_element", {"system": "cylindrical", "u": [1, 30, 0], "d": [0.1, 10, 0.1]}),
    ("point_charges", {"charges": [{"q_nC": 2, "x": 0, "y": 0.3}], "ground": True, "probe": [0.2, 0.1]}),
    ("gauss_law", {"kind": "coax", "rho": 1e-9, "a": 0.01, "b": 0.03, "r": 0.02}),
    ("capacitor", {"kind": "parallel", "V0": 5, "A": 1e-4, "d": 1e-4, "eps_r": 4.4}),
    ("parallel_wires", {"wires": [{"I": 10, "x": -0.1, "y": 0}, {"I": -10, "x": 0.1, "y": 0}], "probe": [0, 0.2]}),
    ("current_loops", {"kind": "helmholtz", "I": 2, "a": 0.15}),
    ("ampere_law", {"kind": "coax", "I": 5, "a": 0.002, "b": 0.006, "c": 0.007, "r": 0.004}),
    ("inductance", {"kind": "toroid", "N": 200, "a": 0.02, "b": 0.03, "h": 0.01, "mu_r": 2000}),
    ("reflection_normal", {"f": 1e9, "eps2": 2.25}),
    ("reflection_oblique", {"eps1": 2.25, "eps2": 1, "theta_deg": 50}),
    ("transmission_line", {"Z0": 50, "RL": 73, "XL": 42.5, "f": 1e8, "length": 1.2, "vf": 0.66}),
    ("waveguide", {"f": 12e9, "mode": "TE", "m": 1, "n": 0}),
    ("dipole_antenna", {"length_lambda": 0.5, "f": 433e6}),
    ("linear_array", {"N": 10, "d_lambda": 0.5, "delta_deg": -45}),
    ("wave_dimensions", {"f": 2.4e9, "eps_r": 1, "sigma": 0}),
    ("boundary_condition", {"kind": "H", "mu1": 1, "mu2": 1000, "F1": 10, "theta1_deg": 45}),
    ("faraday_emf", {"mode": "motional", "B0": 0.5, "f": 50, "w": 0.2, "l": 0.2, "N": 100, "R": 10}),
    ("conduction_vs_displacement", {"eps_r": 81, "sigma": 4, "f": 1e6}),
]


@pytest.mark.parametrize("name,args", CASES)
def test_tool(name, args):
    r, action = A._run(name, args)
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]
    assert action["chapter"] in ("waves", "coordinates", "electrostatics", "magnetostatics", "maxwell", "reflection", "tlines", "radiation", "dimensions")
    json.loads(A._summary(r))


def test_tool_names_match_schemas():
    assert {t["name"] for t in A.TOOLS} == {c[0] for c in CASES}
