import numpy as np
import pytest
from engine import reflection as rf


def test_air_glass_normal():
    r = rf.normal(1e9, 1, 1, 0, 2.25, 1, 0)
    v = r["values"]
    assert v["Gamma_mag"] == pytest.approx(0.2, rel=1e-9)   # (1/1.5 − 1)/(1/1.5 + 1) = −0.2
    assert v["Gamma_deg"] == pytest.approx(180, abs=1e-9) or v["Gamma_deg"] == pytest.approx(-180, abs=1e-9)
    assert v["S"] == pytest.approx(1.5, rel=1e-9)
    assert v["R"] + v["T"] == pytest.approx(1, rel=1e-12)
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]


@pytest.mark.parametrize("m2", [(81, 1, 4), (1, 1, 5.8e7), (4, 1, 0.01)])
def test_lossy_normal(m2):
    r = rf.normal(1e6, 1, 1, 0, *m2)
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]


def test_copper_is_nearly_short():
    assert rf.normal(1e9, 1, 1, 0, 1, 1, 5.8e7)["values"]["Gamma_mag"] > 0.9999


@pytest.mark.parametrize("th", [0, 20, 56.3, 70, 85])
def test_oblique_air_glass(th):
    r = rf.oblique(1, 1, 2.25, 1, th)
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]


def test_brewster_value():
    r = rf.oblique(1, 1, 2.25, 1, 30)
    assert r["values"]["theta_B"] == pytest.approx(np.degrees(np.arctan(1.5)), rel=1e-9)


@pytest.mark.parametrize("th", [30, 45, 60])
def test_glass_air_tir(th):
    r = rf.oblique(2.25, 1, 1, 1, th)
    assert r["values"]["theta_c"] == pytest.approx(np.degrees(np.arcsin(1 / 1.5)))
    assert r["values"]["tir"] == (th > 41.81)
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]
