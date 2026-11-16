import numpy as np
import pytest
from engine import magnetostatics as ms
from engine.constants import MU0


def test_single_wire():
    r = ms.wires([{"I": 10, "x": 0, "y": 0}], probe=(0.2, 0))
    assert r["values"]["B_mag"] == pytest.approx(MU0 * 10 / (2 * np.pi * 0.2), rel=1e-12)
    assert r["values"]["B"][1] > 0  # +z current → B along +φ = +y at (x>0, 0)
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]


@pytest.mark.parametrize("I2", [5, -5])
def test_two_wires_force(I2):
    r = ms.wires([{"I": 5, "x": -0.1, "y": 0}, {"I": I2, "x": 0.1, "y": 0}], probe=(0, 0.3))
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]
    fx = r["forces"][0][0]
    assert (fx > 0) == (I2 > 0)  # parallel attract (wire 1 pulled toward +x)


@pytest.mark.parametrize("kind", ["loop", "helmholtz", "solenoid"])
def test_loops(kind):
    r = ms.loops(kind, I=2, a=0.1, N=12, length=0.4, probe=(0.06, 0.03))
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]


def test_loop_centre():
    assert ms.loops("loop", I=1, a=0.1)["values"]["B_center"] == pytest.approx(MU0 / 0.2, rel=1e-9)


@pytest.mark.parametrize("kind,r", [("wire", 0.005), ("wire", 0.02), ("tube", 0.015), ("coax", 0.005),
                                    ("coax", 0.015), ("coax", 0.022), ("toroid", 0.015), ("solenoid", 0.005)])
def test_ampere(kind, r):
    res = ms.ampere(kind, I=3, a=0.01, b=0.02, c=0.025, r=r)
    assert res["all_passed"], [c for c in res["checks"] if not c["passed"]]


@pytest.mark.parametrize("kind", ["solenoid", "coax", "toroid", "twowire"])
def test_inductance(kind):
    r = ms.inductance(kind, a=1e-3, b=3e-3, d=0.05, length=1.0)
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]


def test_coax_inductance_value():
    # RG-58-like: μ0/2π ln(1.47/0.45) ≈ 0.237 µH/m
    L = ms.inductance("coax", a=0.45e-3, b=1.47e-3, length=1)["values"]["L"]
    assert L == pytest.approx(2e-7 * np.log(1.47 / 0.45), rel=1e-6)
