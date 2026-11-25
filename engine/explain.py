"""Explained solutions: original prose + numbers taken from engine runs.

A problem's explanation is written by hand (X/S/W below). Every number in it is a
placeholder «name» resolved from an engine result, so no result is ever typed by hand.
What-if variants and evidence sweeps re-run the engine; their checks must pass too.
"""
import math
import re

import numpy as np
from scipy.optimize import brentq

from .derivation import fmt, num

_PH = re.compile(r"«(\w+)»")
_SUP = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def S(say, tex=None):
    """One solution step: a sentence and (optionally) its formula with the number."""
    return {"say": say, "tex": tex}


def W(q, change, say, tex=None):
    """'If the question had asked…': change(params) → new params; the engine is re-run."""
    return {"q": q, "change": change, "say": say, "tex": tex}


def Sweep(param, values, y, xlabel, ylabel, logx=False, logy=False):
    """Evidence plot: one engine run per value of `param`."""
    return {"sweep": param, "values": list(values), "y": y, "xlabel": xlabel, "ylabel": ylabel, "logx": logx, "logy": logy}


def Series(x, ys, xlabel, ylabel, logx=False, logy=False):
    """Evidence plot from arrays of the base run; ys = [(name, extractor), …]."""
    return {"x": x, "ys": ys, "xlabel": xlabel, "ylabel": ylabel, "logx": logx, "logy": logy}


def X(asked, idea, steps, answer="", answer_text="", whatif=(), evidence_say="", plot=None, mistake="", fig=None, vals=None):
    return {"asked": asked, "idea": idea, "steps": list(steps), "answer": answer, "answer_text": answer_text,
            "whatif": list(whatif), "evidence_say": evidence_say, "plot": plot, "mistake": mistake, "fig": fig, "vals": dict(vals or {})}


def V(key, i=None):
    """Extractor for r['values'][key] (or its i-th element)."""
    return (lambda r, p: r["values"][key]) if i is None else (lambda r, p: r["values"][key][i])


def P(key):
    """Extractor for an input parameter."""
    return lambda r, p: p[key]


def plain(x, sig=4):
    """Prose number: 78.95, 104.0, 1.234 × 10⁻³ (Unicode minus)."""
    x = float(x)
    if not math.isfinite(x):
        return "∞"
    if x == 0:
        return "0"
    sgn, a = ("−" if x < 0 else ""), abs(x)
    e = int(math.floor(math.log10(a)))
    short = _exact(a, sig)
    if short is not None and -2 <= e <= 5:      # given data such as 4, 0.05, 2500 stay as written
        return sgn + short
    if -2 <= e <= 3:
        s = f"{a:.{max(sig - 1 - e, 0)}f}"
        if float(s) >= 10 ** (e + 1) and e < 3:   # rounding carried over (e.g. 99.996 → 100.0)
            s = f"{a:.{max(sig - 2 - e, 0)}f}"
        return sgn + s
    m = a / 10 ** e
    if round(m, sig - 1) >= 10:
        m, e = m / 10, e + 1
    return f"{sgn}{m:.{sig - 1}f} × 10{str(e).translate(_SUP)}"


def _exact(a, sig):
    """Shortest fixed-point text of a ≥ 0 when it needs at most `sig` significant digits, else None."""
    s = f"{a:.{sig}g}"
    if "e" in s or float(s) != a:
        return None
    return s


def _tex(v):
    short = _exact(abs(v), 4)
    if short is not None and 1e-2 <= abs(v) < 1e6:
        return ("-" if v < 0 else "") + short
    return fmt(v)


def _scalar(v, name):
    if isinstance(v, (bool, np.bool_)) or not isinstance(v, (int, float, np.integer, np.floating)):
        raise TypeError(f"placeholder «{name}» must be a real number, got {type(v).__name__}")
    return float(v)


def _fill(text, vals, r, p, tex=False):
    if not text:
        return text

    def sub(m):
        name = m.group(1)
        if name not in vals:
            raise KeyError(f"no value for placeholder «{name}»")
        v = _scalar(vals[name](r, p), name)
        return _tex(v) if tex else plain(v)
    return _PH.sub(sub, text)


def render(x, run, params, result):
    """Fill an X spec from `result` (= run(params)); what-ifs and sweeps call run(new params)."""
    vals, ok = x["vals"], bool(result.get("all_passed", True))
    f = lambda s, r=result, p=params, tex=False: _fill(s, vals, r, p, tex)
    out = {"asked": f(x["asked"]), "idea": f(x["idea"]),
           "steps": [{"say": f(s["say"]), "tex": f(s["tex"], tex=True)} for s in x["steps"]],
           "answer": f(x["answer"]), "answer_text": f(x["answer_text"]), "evidence_say": f(x["evidence_say"]),
           "mistake": f(x["mistake"]), "whatif": [], "plot": None, "fig": None}
    for w in x["whatif"]:
        p2 = w["change"](dict(params))
        r2 = run(p2)
        good = bool(r2.get("all_passed", True))
        ok = ok and good
        out["whatif"].append({"q": f(w["q"]), "say": f(w["say"], r2, p2), "tex": f(w["tex"], r2, p2, True), "verified": good})
    pl = x["plot"]
    if pl and "sweep" in pl:
        ys = []
        for v in pl["values"]:
            p2 = {**params, pl["sweep"]: v}
            r2 = run(p2)
            ok = ok and bool(r2.get("all_passed", True))
            ys.append(_scalar(pl["y"](r2, p2), pl["sweep"]))
        out["plot"] = {"x": num(pl["values"]), "ys": [{"name": pl["ylabel"], "y": ys}], **{k: pl[k] for k in ("xlabel", "ylabel", "logx", "logy")}}
    elif pl:
        out["plot"] = {"x": num(pl["x"](result, params)), "ys": [{"name": n, "y": num(g(result, params))} for n, g in pl["ys"]],
                       **{k: pl[k] for k in ("xlabel", "ylabel", "logx", "logy")}}
    if x["fig"]:
        out["fig"] = {k: num(v) for k, v in x["fig"](result, params).items()}
    out["verified"] = ok
    return out


def invert(fn, kw, name, key, target, lo, hi, log=False):
    """Find the value of input `name` for which fn(**kw)'s output `key` equals `target`.

    Root finding on the engine forward model (brentq); the forward residual at the root is
    appended as an independent check. Raises ValueError when the bracket holds no root.
    """
    get = (lambda r: r["values"][key]) if isinstance(key, str) else key
    g = lambda u: float(get(fn(**kw, **{name: math.exp(u) if log else u}))) - target
    a, b = (math.log(lo), math.log(hi)) if log else (lo, hi)
    u = brentq(g, a, b, xtol=1e-14, rtol=1e-13, maxiter=200)
    x = math.exp(u) if log else u
    r = fn(**kw, **{name: x})
    got = float(get(r))
    err = abs(got - target) / (abs(target) or 1.0)
    r = dict(r)
    r["checks"] = list(r["checks"]) + [{"label": "forward model reproduces the target", "method": "engine re-run at the root (Brent's method)",
                                        "reference": float(target), "computed": got, "rel_error": err, "tol": 1e-9, "passed": bool(err <= 1e-9)}]
    r["all_passed"] = all(c["passed"] for c in r["checks"])
    return r, x
