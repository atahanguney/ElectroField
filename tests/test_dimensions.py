import numpy as np
import pytest
from engine import dimensions as dm


@pytest.mark.parametrize("f,er,s", [(1e9, 1, 0), (2.45e9, 4, 0), (1e8, 81, 0.5), (10e9, 2.2, 1e-3)])
def test_checks(f, er, s):
    r = dm.compare(f, er, 1, s)
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]


def test_spreading_ordering():
    v = dm.compare(1e9)["values"]
    assert abs(v["level_1D"]) < 1e-9          # lossless 1-D: no loss at all
    assert v["level_3D"] < v["level_2D"] < 0  # sphere spreads faster than cylinder


def test_double_distance():
    s = {x["change"]: x for x in dm.compare(1e9, r_max_lambda=10)["sensitivity"]}["double the distance"]
    assert s["3D"] == pytest.approx(-20 * np.log10(2), abs=1e-6)        # −6.02 dB
    assert s["2D"] == pytest.approx(-10 * np.log10(2), abs=0.05)        # ≈ −3 dB (asymptotically)
    assert s["1D"] == pytest.approx(0, abs=1e-9)
