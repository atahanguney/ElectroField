"""Server-free dispatcher: the same `/api/*` routes as server/main.py, as plain Python.

Used by the browser build (Pyodide on GitHub Pages) so the static site runs the
identical engine. `tests/test_routes.py` checks every route against the FastAPI server.
"""
import json
import math

import numpy as np

from . import constants as K, coordinates as co, dimensions as dm, electrostatics as es, magnetostatics as ms
from . import maxwell as mx, questions as qb, radiation as ra, reflection as rf, tlines as tl, waves as wv

REQ = object()   # marks a required parameter


def _rad(v, is_angle, deg):
    return math.radians(v) if (is_angle and deg) else v


def _coords_element(system, u1, u2, u3, d1, d2, d3, deg=True):
    ang = co.SYSTEMS.get(system, {}).get("angle")
    if ang is None:
        raise ValueError(f"unknown system {system!r}")
    return co.element(system, [_rad(x, a, deg) for x, a in zip((u1, u2, u3), ang)], [_rad(x, a, deg) for x, a in zip((d1, d2, d3), ang)])


def _coords_convert(src, dst, u1, u2, u3, A1=None, A2=None, A3=None, deg=True):
    if src not in co.SYSTEMS or dst not in co.SYSTEMS:
        raise ValueError("unknown coordinate system")
    u = [_rad(x, a, deg) for x, a in zip((u1, u2, u3), co.SYSTEMS[src]["angle"])]
    r = co.convert(src, dst, u, None if A1 is None else [A1, A2 or 0.0, A3 or 0.0])
    if deg:
        r["values"]["point"] = [math.degrees(x) if a else x for x, a in zip(r["values"]["point"], co.SYSTEMS[dst]["angle"])]
    return r


F, I, S, B = float, int, str, bool
ROUTES = {
    "constants": (lambda: [{"key": k, "tex": t, "value": v, "unit": u, "name": n} for k, t, v, u, n in K.TABLE], {}),
    "coords/element": (_coords_element, {"system": (S, REQ), "u1": (F, REQ), "u2": (F, REQ), "u3": (F, REQ), "d1": (F, REQ), "d2": (F, REQ), "d3": (F, REQ), "deg": (B, True)}),
    "coords/convert": (_coords_convert, {"src": (S, REQ), "dst": (S, REQ), "u1": (F, REQ), "u2": (F, REQ), "u3": (F, REQ), "A1": (F, None), "A2": (F, None), "A3": (F, None), "deg": (B, True)}),
    "waves/solve": (wv.solve, {"f": (F, REQ), "eps_r": (F, 1), "mu_r": (F, 1), "sigma": (F, 0), "E0": (F, 1)}),
    "waves/sweep": (lambda param, lo, hi, f, eps_r, mu_r, sigma, n: wv.sweep(param, lo, hi, f, eps_r, mu_r, sigma, min(max(n, 10), 2000)),
                    {"param": (S, REQ), "lo": (F, REQ), "hi": (F, REQ), "f": (F, 1e9), "eps_r": (F, 1), "mu_r": (F, 1), "sigma": (F, 0), "n": (I, 300)}),
    "es/charges": (lambda charges, ground=False, probe=(0.0, 0.0), span=1.0: es.point_charges(
        [{"q": float(c["q"]), "x": float(c["x"]), "y": float(c["y"])} for c in charges], bool(ground), tuple(map(float, probe)), min(max(float(span), 1e-3), 1e3)), "json"),
    "es/gauss": (es.gauss, {"kind": (S, REQ), "rho": (F, REQ), "a": (F, 0.1), "b": (F, 0.3), "eps_r": (F, 1), "r": (F, 0.05)}),
    "es/capacitor": (es.capacitor, {"kind": (S, REQ), "V0": (F, 1), "eps_r": (F, 1), "A": (F, 1e-2), "d": (F, 1e-3), "a": (F, 1e-3), "b": (F, 3.5e-3), "length": (F, 1), "E_bd": (F, 3e6)}),
    "ms/wires": (lambda currents, probe=(0.0, 0.5): ms.wires([{"I": float(w["I"]), "x": float(w["x"]), "y": float(w["y"])} for w in currents], tuple(map(float, probe))), "json"),
    "ms/loops": (lambda kind, I, a, N, length, sep, pr, pz: ms.loops(kind, I, a, N, length, sep, (pr, pz)),
                 {"kind": (S, "loop"), "I": (F, 1), "a": (F, 0.1), "N": (I, 10), "length": (F, 0.3), "sep": (F, None), "pr": (F, 0.05), "pz": (F, 0.05)}),
    "ms/ampere": (ms.ampere, {"kind": (S, REQ), "I": (F, 1), "a": (F, 0.01), "b": (F, 0.02), "c": (F, 0.025), "N": (I, 100), "n_per_m": (F, 1000), "mu_r": (F, 1), "r": (F, 0.005)}),
    "ms/inductance": (ms.inductance, {"kind": (S, REQ), "I": (F, 1), "N": (I, 100), "a": (F, 0.01), "b": (F, 0.02), "length": (F, 0.1), "h": (F, 0.01), "d": (F, 0.1), "mu_r": (F, 1)}),
    "rf/normal": (rf.normal, {"f": (F, 1e9), "eps1": (F, 1), "mu1": (F, 1), "s1": (F, 0), "eps2": (F, 4), "mu2": (F, 1), "s2": (F, 0), "E0": (F, 1)}),
    "rf/oblique": (rf.oblique, {"eps1": (F, 1), "mu1": (F, 1), "eps2": (F, 2.25), "mu2": (F, 1), "theta_deg": (F, 30)}),
    "tl/line": (tl.line, {"Z0": (F, 50), "RL": (F, 100), "XL": (F, 50), "f": (F, 1e9), "length": (F, 0.3), "vf": (F, 1), "Vg": (F, 10), "Zg": (F, 50)}),
    "ra/waveguide": (ra.waveguide, {"a": (F, 22.86e-3), "b": (F, 10.16e-3), "eps_r": (F, 1), "mu_r": (F, 1), "f": (F, 10e9), "mode": (S, "TE"), "m": (I, 1), "n": (I, 0)}),
    "ra/dipole": (ra.dipole, {"length_lambda": (F, 0.5), "I0": (F, 1), "f": (F, 100e6)}),
    "ra/array": (ra.array, {"N": (I, 8), "d_lambda": (F, 0.5), "delta_deg": (F, 0)}),
    "dim/compare": (dm.compare, {"f": (F, 1e9), "eps_r": (F, 1), "mu_r": (F, 1), "sigma": (F, 0), "r_max_lambda": (F, 6)}),
    "qb/catalog": (qb.catalog, {}),
    "qb/new": (lambda chapter, level, id, seed: qb.generate(id, chapter, level, seed), {"chapter": (S, None), "level": (I, None), "id": (S, None), "seed": (I, None)}),
    "qb/check": (lambda id, seed, answer: qb.check(id, seed, answer), {"id": (S, REQ), "seed": (I, REQ), "answer": (F, None)}),
    "mx/boundary": (mx.boundary, {"kind": (S, "E"), "eps1": (F, 1), "eps2": (F, 4), "mu1": (F, 1), "mu2": (F, 1), "F1": (F, 1), "theta1_deg": (F, 40), "source": (F, 0), "pec": (B, False)}),
    "mx/faraday": (mx.faraday, {"mode": (S, "motional"), "B0": (F, 0.1), "f": (F, 50), "w": (F, 0.1), "l": (F, 0.2), "N": (I, 1), "R": (F, 1), "alpha_deg": (F, 0)}),
    "mx/currents": (mx.currents, {"eps_r": (F, 81), "sigma": (F, 4), "f": (F, 1e6), "E0": (F, 1)}),
}


def _coerce(typ, v):
    if typ is B:
        return v if isinstance(v, bool) else str(v).lower() in ("true", "1", "yes")
    if typ is I:
        x = float(v)
        if x != int(x):
            raise ValueError(f"expected an integer, got {v!r}")
        return int(x)
    if typ is F:
        x = float(v)
        if not math.isfinite(x):
            raise ValueError("parameters must be finite numbers")
        return x
    return str(v)


def call(path, params=None):
    """Run one route. GET-style routes take query parameters (strings ok); JSON routes take the body dict."""
    if path not in ROUTES:
        raise ValueError(f"unknown route {path!r}")
    fn, spec = ROUTES[path]
    params = dict(params or {})
    if spec == "json":
        return fn(**params)
    kw = {}
    for name, (typ, default) in spec.items():
        v = params.get(name)
        if v is None or v == "":
            if default is REQ:
                raise ValueError(f"missing parameter {name!r}")
            kw[name] = default
        else:
            kw[name] = _coerce(typ, v)
    return fn(**kw)


def _clean(o):
    """JSON-safe: numpy → Python, complex → {re, im}, NaN/±inf → None (as the HTTP server sends)."""
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, np.ndarray):
        return _clean(o.tolist())
    if isinstance(o, (bool, np.bool_)):
        return bool(o)
    if isinstance(o, (complex, np.complexfloating)):
        return {"re": _clean(o.real), "im": _clean(o.imag)}
    if isinstance(o, (int, np.integer)):
        return int(o)
    if isinstance(o, (float, np.floating)):
        o = float(o)
        return o if math.isfinite(o) else None
    return o


def call_json(path, params_json="{}"):
    """Entry point for the browser: JSON in, JSON out — {"ok": result} or {"error": message}."""
    try:
        return json.dumps({"ok": _clean(call(path, json.loads(params_json)))})
    except (ValueError, KeyError, TypeError) as e:
        return json.dumps({"error": str(e) or e.__class__.__name__})
