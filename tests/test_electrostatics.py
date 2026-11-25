import numpy as np
import pytest
from engine import electrostatics as es
from engine.constants import EPS0, K_E

nC = 1e-9


def test_single_charge_field():
    r = es.point_charges([{"q": 1 * nC, "x": 0, "y": 0}], probe=(0.5, 0))
    assert r["values"]["E_mag"] == pytest.approx(K_E * nC / 0.25, rel=1e-12)
    assert r["values"]["V"] == pytest.approx(K_E * nC / 0.5, rel=1e-12)
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]


def test_dipole_checks_and_lines():
    r = es.point_charges([{"q": nC, "x": -0.2, "y": 0}, {"q": -nC, "x": 0.2, "y": 0}], probe=(0.1, 0.3))
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]
    assert len(r["field_lines"]) >= 18 and r["equipotentials"]
    # on the perpendicular bisector V = 0
    assert es.point_charges([{"q": nC, "x": -0.2, "y": 0}, {"q": -nC, "x": 0.2, "y": 0}], probe=(0, 0.4))["values"]["V"] == pytest.approx(0, abs=1e-9)


def test_image_method():
    r = es.point_charges([{"q": 2 * nC, "x": 0, "y": 0.3}], ground=True, probe=(0.2, 0.1))
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]
    assert any(c["image"] for c in r["charges"])


def test_invalid_charges():
    with pytest.raises(ValueError):
        es.point_charges([{"q": nC, "x": 0, "y": -0.1}], ground=True)
    with pytest.raises(ValueError):
        es.point_charges([{"q": nC, "x": 0, "y": 0}, {"q": nC, "x": 0, "y": 0}])


@pytest.mark.parametrize("kind,r", [("sphere", 0.05), ("sphere", 0.2), ("shell", 0.05), ("shell", 0.2), ("line", 0.05),
                                    ("cylinder", 0.05), ("cylinder", 0.2), ("coax", 0.2), ("sheet", 0.05),
                                    ("slab", 0.05), ("slab", 0.2)])
def test_gauss_all_checks(kind, r):
    res = es.gauss(kind, 1e-6, a=0.1, b=0.3, r=r)
    assert res["all_passed"], [c for c in res["checks"] if not c["passed"]]


def test_gauss_sphere_closed_form():
    rho, a = 1e-6, 0.1
    out = es.gauss("sphere", rho, a=a, r=0.3)["values"]["E"]
    Q = rho * 4 / 3 * np.pi * a ** 3
    assert out == pytest.approx(Q / (4 * np.pi * EPS0 * 0.09), rel=1e-12)


@pytest.mark.parametrize("kind", ["parallel", "coax", "spherical"])
def test_capacitors(kind):
    r = es.capacitor(kind, V0=10, eps_r=2.2)
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]


def test_rg58_like_coax():
    # a = 0.45 mm, b = 1.47 mm, PE εr = 2.25 → ≈ 106 pF/m (datasheet ~100 pF/m)
    C = es.capacitor("coax", a=0.45e-3, b=1.47e-3, eps_r=2.25)["values"]["C"]
    assert 100e-12 < C < 110e-12


def test_gradient_check_holds_at_a_field_null():
    from engine import electrostatics as es
    d = 0.3
    x0 = d / (1 + 2)          # q2 = 4 q1: E = 0 at d/3
    r = es.point_charges([{"q": 1e-9, "x": 0, "y": 0}, {"q": 4e-9, "x": d, "y": 0}], False, (x0, 0.0), n=21)
    assert r["all_passed"], [c["label"] for c in r["checks"] if not c["passed"]]


@pytest.mark.parametrize("b", [1.0, 10.0])
def test_spherical_capacitor_checks_hold_for_far_outer_sphere(b):
    from engine import electrostatics as es
    assert es.capacitor("spherical", a=0.05, b=b)["all_passed"]


def test_grounded_plane_check_is_fast_and_holds():
    import time
    from engine import electrostatics as es
    t = time.perf_counter()
    r = es.point_charges([{"q": 2e-9, "x": 0.0, "y": 0.3}, {"q": -1e-9, "x": 0.2, "y": 0.1}], True, (0.05, 0.2))
    assert r["all_passed"] and time.perf_counter() - t < 0.4
    c = next(c for c in r["checks"] if "induced charge" in c["label"])
    assert c["reference"] == pytest.approx(-1e-9) and c["passed"]
