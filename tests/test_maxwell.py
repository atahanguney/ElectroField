import numpy as np
import pytest
from engine import maxwell as mx
from engine.constants import EPS0


def test_dielectric_refraction():
    r = mx.boundary("E", eps1=1, eps2=4, F1=10, theta1_deg=40)
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]
    t2, n2 = r["values"]["F2"]
    assert t2 == pytest.approx(10 * np.sin(np.radians(40)))
    assert n2 == pytest.approx(10 * np.cos(np.radians(40)) / 4)


def test_surface_charge_jump():
    r = mx.boundary("E", eps1=2, eps2=5, F1=1e3, theta1_deg=30, source=5e-9)
    assert r["all_passed"]
    assert r["values"]["flux"][0] - r["values"]["flux"][1] == pytest.approx(5e-9, rel=1e-9)


def test_pec_E():
    r = mx.boundary("E", eps1=1, F1=100, theta1_deg=0, pec=True)
    assert r["values"]["source"] == pytest.approx(EPS0 * 100)
    assert r["all_passed"]


@pytest.mark.parametrize("Js", [0.0, 2.0, -3.0])
def test_magnetic(Js):
    r = mx.boundary("H", mu1=1, mu2=100, F1=5, theta1_deg=60, source=Js)
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]
    assert r["values"]["F2"][1] == pytest.approx(5 * np.cos(np.radians(60)) / 100)


@pytest.mark.parametrize("mode", ["transformer", "motional"])
def test_faraday(mode):
    r = mx.faraday(mode, B0=0.2, f=60, w=0.1, l=0.3, N=10, R=2)
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]
    assert r["values"]["V_peak"] == pytest.approx(10 * 0.2 * 0.03 * 2 * np.pi * 60, rel=2e-4)


def test_currents_seawater():
    r = mx.currents(81, 4, 1e6)
    assert r["all_passed"]
    assert r["values"]["fc"] == pytest.approx(4 / (2 * np.pi * 81 * EPS0))
    assert r["values"]["tau"] == pytest.approx(81 * EPS0 / 4)
