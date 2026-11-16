import numpy as np
import pytest
from engine import tlines as tl
from engine.constants import C0


@pytest.mark.parametrize("RL,XL", [(100, 50), (25, -30), (50, 0), (50, 80), (0, 30), (200, 0)])
def test_checks(RL, XL):
    r = tl.line(50, RL, XL, 1e9, 0.37)
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]


def test_matched_load():
    v = tl.line(50, 50, 0)["values"]
    assert v["Gamma_mag"] == 0 and v["S"] == 1


def test_quarter_wave_inverts():
    lam = C0 / 1e9
    Zin = tl.line(50, 100, 0, 1e9, lam / 4)["values"]["Zin"]
    assert Zin["re"] == pytest.approx(25, rel=1e-9) and abs(Zin["im"]) < 1e-6


def test_half_wave_repeats():
    lam = C0 / 1e9
    Zin = tl.line(75, 30, 40, 1e9, lam / 2)["values"]["Zin"]
    assert Zin["re"] == pytest.approx(30, rel=1e-8) and Zin["im"] == pytest.approx(40, rel=1e-8)


def test_ulaby_style_load():
    # Z_L = 100 + j50 on 50 Ω: |Γ| = 0.447, angle 26.57°, S = 2.618
    v = tl.line(50, 100, 50)["values"]
    assert v["Gamma_mag"] == pytest.approx(np.sqrt(0.2), rel=1e-9)
    assert v["Gamma_deg"] == pytest.approx(26.565, abs=1e-3)
    assert v["S"] == pytest.approx(2.618, rel=1e-3)
