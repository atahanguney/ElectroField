import numpy as np
import pytest
from engine import biot, images


@pytest.mark.parametrize("z1,z2,r", [(-0.5, 0.5, 0.2), (0, 1, 0.1), (-2, 0.3, 0.5)])
def test_segment(z1, z2, r):
    out = biot.segment(2.0, z1, z2, r, N=400)
    assert out["all_passed"], [c for c in out["checks"] if not c["passed"]]


def test_long_segment_approaches_infinite_wire():
    v = biot.segment(1, -1e3, 1e3, 0.1, N=20000)["values"]
    assert v["ratio_to_infinite"] == pytest.approx(1, abs=1e-5)


def test_loop_and_square():
    assert biot.loop(3, 0.1, 0.07)["all_passed"]
    assert biot.loop(1, 0.1, 0)["values"]["H_closed"] == pytest.approx(5.0)   # I/2a
    sq = biot.square(1, 0.2, N=200)
    assert sq["all_passed"], [c for c in sq["checks"] if not c["passed"]]


@pytest.mark.parametrize("Q,d,er", [(1e-9, 0.4, 1), (-2e-9, 0.2, 2.5)])
def test_image_plane(Q, d, er):
    r = images.plane(Q, d, er)
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]
    assert r["a"]["all_passed"] and r["b"]["all_passed"]


def test_image_corner():
    assert images.corner(1e-9, 0.3, 0.5)["all_passed"]
