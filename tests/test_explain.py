import json
import math
import pytest
from engine import maxwell as mx
from engine.constants import EPS0
from engine.explain import X, S, W, V, P, Sweep, Series, render, invert, plain

BASE = dict(kind="E", eps1=1, eps2=4, F1=132, theta1_deg=52)
run = lambda q: mx.boundary(**q)


def _go(x, params=BASE):
    return render(x, run, params, run(params))


def test_placeholders_filled_from_engine():
    x = X(asked="θ₂?", idea="Tangential E is continuous.", steps=[S("E₁t is «t» V/m.", r"E_{1t}=«t»")],
          answer="θ₂ = «th» °", vals={"t": V("F1", 0), "th": V("theta2_deg")})
    out = _go(x)
    assert "104.0" in out["steps"][0]["say"] and "104.0" in out["steps"][0]["tex"]
    assert "78.95" in out["answer"]
    assert "«" not in json.dumps(out, ensure_ascii=False)
    assert out["verified"]


def test_params_placeholder():
    out = _go(X(asked="«e2»", idea="", steps=[], vals={"e2": P("eps2")}))
    assert out["asked"] == "4"


def test_whatif_reruns_engine():
    x = X(asked="", idea="", steps=[], vals={"th": V("theta2_deg")},
          whatif=[W("εr₂ = 9?", lambda p: {**p, "eps2": 9}, "θ₂ = «th» °")])
    w = _go(x)["whatif"][0]
    assert plain(math.degrees(math.atan(9 * math.tan(math.radians(52))))) in w["say"]
    assert w["verified"] is True


def test_missing_placeholder_raises():
    with pytest.raises(KeyError):
        _go(X(asked="", idea="", steps=[S("«nope»")]))


def test_render_rejects_non_scalar():
    with pytest.raises(TypeError):
        _go(X(asked="«f»", idea="", steps=[], vals={"f": lambda r, p: r["values"]["F1"]}))


def test_sweep_plot_uses_engine():
    x = X(asked="", idea="", steps=[], plot=Sweep("eps2", [1, 2, 4], V("F2", 0), "εr₂", "E₂t (V/m)"))
    out = _go(x)
    t1 = 132 * math.sin(math.radians(52))
    assert out["plot"]["x"] == [1, 2, 4]
    assert all(abs(y - t1) < 1e-9 * t1 for y in out["plot"]["ys"][0]["y"])


def test_series_plot_reads_base_run():
    q = dict(mode="motional", N=1, B0=0.1, f=50, w=0.1, l=0.1)
    r = mx.faraday(**q)
    x = X(asked="", idea="", steps=[], plot=Series(lambda r, p: r["t"], [("Φ", lambda r, p: r["Phi"])], "t (s)", "Φ (Wb)"))
    out = render(x, lambda p: mx.faraday(**p), q, r)
    assert out["plot"]["x"] == r["t"] and out["plot"]["ys"][0]["name"] == "Φ"


def test_invert_finds_root_and_adds_check():
    r, f = invert(mx.currents, {"eps_r": 81, "sigma": 4}, "f", "ratio", 10.0, 1e3, 1e9, log=True)
    assert f == pytest.approx(4 / (2 * math.pi * 81 * EPS0 * 10), rel=1e-9)
    assert r["checks"][-1]["label"] == "forward model reproduces the target" and r["checks"][-1]["passed"]
    assert r["all_passed"]


def test_invert_rejects_target_outside_bracket():
    with pytest.raises(ValueError):
        invert(mx.currents, {"eps_r": 81, "sigma": 4}, "f", "ratio", 10.0, 1e8, 1e9, log=True)


def test_plain_format():
    assert plain(0.001234) == "1.234 × 10⁻³"
    assert plain(78.948) == "78.95"
    assert plain(0) == "0"
    assert plain(-2.5e6) == "−2.500 × 10⁶"
