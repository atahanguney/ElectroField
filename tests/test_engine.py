"""Verification against textbook closed-form results and limiting cases."""
import numpy as np
import pytest
from engine import coordinates as co, waves as wv
from engine.constants import C0, ETA0


# ---------- coordinates ----------------------------------------------------
@pytest.mark.parametrize("system,u", [("cartesian", (1, 2, 3)), ("cylindrical", (2, 0.7, -1)),
                                      ("spherical", (3, 1.1, 4.0))])
def test_element_checks_pass(system, u):
    r = co.element(system, u, (0.1, 0.1, 0.1))
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]


def test_spherical_volume_element_formula():
    R, th = 2.0, np.pi / 3
    r = co.element("spherical", (R, th, 0.5), (1e-3, 1e-3, 1e-3))
    assert r["values"]["dv"] == pytest.approx(R ** 2 * np.sin(th) * 1e-9, rel=1e-12)


def test_differential_converges_to_exact():
    r = co.element("spherical", (1.0, 0.8, 0.2), (0.2, 0.2, 0.2))
    errs = [c["rel_error"] for c in r["convergence"]]
    # first-order convergence: halving d roughly halves the error
    for a, b in zip(errs, errs[1:]):
        assert 0.4 < b / a < 0.6


def test_convert_known_point():
    # Ulaby-style: (x,y,z)=(2,3,-1) → R=√14, θ=cos⁻¹(−1/√14), φ=tan⁻¹(3/2)
    r = co.convert("cartesian", "spherical", (2, 3, -1))
    R, th, ph = r["values"]["point"]
    assert R == pytest.approx(np.sqrt(14))
    assert th == pytest.approx(np.arccos(-1 / np.sqrt(14)))
    assert ph == pytest.approx(np.arctan2(3, 2))


def test_vector_transform_preserves_norm():
    r = co.convert("cylindrical", "spherical", (2, 1.0, 1.5), A=(1, -2, 3))
    assert r["all_passed"]
    assert np.linalg.norm(r["values"]["vector"]) == pytest.approx(np.sqrt(14))


def test_bad_domain():
    with pytest.raises(ValueError):
        co.element("spherical", (1, 4.0, 0), (0.1, 0.1, 0.1))


# ---------- plane waves ----------------------------------------------------
def test_free_space():
    r = wv.solve(1e9)
    v = r["values"]
    assert v["alpha"] == 0
    assert v["vp"] == pytest.approx(C0, rel=1e-9)
    assert v["eta_mag"] == pytest.approx(ETA0, rel=1e-12)
    assert v["wavelength"] == pytest.approx(0.299792458, rel=1e-9)
    assert r["all_passed"]


@pytest.mark.parametrize("f,er,mr,s", [(1e6, 81, 1, 4), (1e9, 2.5, 1, 1e-4), (60, 1, 1, 5.8e7),
                                       (2.45e9, 50, 1, 2.0), (1e5, 1, 500, 1e7)])
def test_all_checks_pass(f, er, mr, s):
    r = wv.solve(f, er, mr, s)
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]


def test_copper_skin_depth():
    # textbook: copper at 1 MHz, δs ≈ 66 µm (σ = 5.8e7 S/m)
    v = wv.solve(1e6, 1, 1, 5.8e7)["values"]
    assert v["skin_depth"] == pytest.approx(1 / np.sqrt(np.pi * 1e6 * 4e-7 * np.pi * 5.8e7), rel=1e-6)
    assert 65e-6 < v["skin_depth"] < 67e-6
    assert v["eta_phase_deg"] == pytest.approx(45, abs=1e-4)


def test_seawater_regime():
    # sea water εr=81, σ=4 S/m: good conductor at 1 kHz, low-loss-ish only at very high f
    assert wv.solve(1e3, 81, 1, 4)["values"]["regime"] == "good conductor"


def test_sweep_boundaries():
    s = wv.sweep("f", 1e3, 1e12, eps_r=81, sigma=4)
    assert s["boundaries"]["good_conductor"] == pytest.approx(4 / (2 * np.pi * 8.8541878188e-12 * 81 * 100), rel=1e-6)
    assert len(s["alpha"]) == 300 and all(a >= 0 for a in s["alpha"])


def test_invalid_inputs():
    with pytest.raises(ValueError):
        wv.solve(-1)
    with pytest.raises(ValueError):
        wv.sweep("bogus", 1, 2)
