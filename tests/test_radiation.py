import numpy as np
import pytest
from engine import radiation as ra


def test_wr90_te10():
    r = ra.waveguide(f=10e9)
    v = r["values"]
    assert v["fc"] == pytest.approx(6.557e9, rel=1e-3)        # WR-90 TE10 cut-off
    assert r["modes"][0]["mode"] == "TE10" and r["modes"][1]["mode"] == "TE20"
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]


@pytest.mark.parametrize("mode,m,n,f", [("TE", 0, 1, 20e9), ("TE", 1, 1, 20e9), ("TM", 1, 1, 20e9), ("TM", 2, 1, 10e9), ("TE", 1, 0, 5e9)])
def test_modes(mode, m, n, f):
    r = ra.waveguide(mode=mode, m=m, n=n, f=f)
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]


def test_half_wave_dipole():
    r = ra.dipole(0.5)
    assert r["values"]["R_rad"] == pytest.approx(73.08, rel=1e-3)
    assert r["values"]["D"] == pytest.approx(1.64, rel=2e-3)
    assert r["values"]["hpbw_deg"] == pytest.approx(78, abs=1)
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]


@pytest.mark.parametrize("L", [0.05, 1.0, 1.25])
def test_dipoles(L):
    assert ra.dipole(L)["all_passed"]


@pytest.mark.parametrize("N,d,delta", [(8, 0.5, 0), (8, 0.25, -90), (16, 0.5, 60), (4, 1.2, 0)])
def test_arrays(N, d, delta):
    r = ra.array(N, d, delta)
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]


def test_endfire_direction():
    assert ra.array(8, 0.25, -90)["values"]["theta0"] == pytest.approx(0, abs=1e-6)


@pytest.mark.parametrize("d, delta", [(1.0, 0.0), (0.7, -178.0)])
def test_array_checks_hold_with_grating_lobes(d, delta):
    from engine import radiation as ra
    r = ra.array(N=8, d_lambda=d, delta_deg=delta)
    assert r["values"]["grating"] and r["all_passed"], [c["label"] for c in r["checks"] if not c["passed"]]
