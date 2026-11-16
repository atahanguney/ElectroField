"""Derivation log: formula steps + independent checks, JSON-safe."""
import math
import numpy as np


def num(x):
    """Convert numpy/complex/inf values to JSON-safe structures."""
    if isinstance(x, (list, tuple)):
        return [num(v) for v in x]
    if isinstance(x, np.ndarray):
        if np.iscomplexobj(x):
            return {"re": num(x.real), "im": num(x.imag)}
        return [num(v) for v in x.tolist()]
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    if isinstance(x, (complex, np.complexfloating)):
        return {"re": num(x.real), "im": num(x.imag)}
    if isinstance(x, (float, np.floating, int, np.integer)):
        x = float(x)
        return x if math.isfinite(x) else None
    return x


def fmt(x, sig=4):
    """Engineering-friendly TeX number, e.g. 1.234\\times10^{-3}."""
    if x is None or not math.isfinite(x):
        return r"\infty"
    if x == 0:
        return "0"
    e = int(math.floor(math.log10(abs(x))))
    if -2 <= e <= 3:
        return f"{x:.{max(sig - 1 - e, 0)}f}" if e >= 0 else f"{x:.{sig - 1 - e}f}"
    m = x / 10 ** e
    return rf"{m:.{sig - 1}f}\times10^{{{e}}}"


class Derivation:
    def __init__(self):
        self.steps, self.checks = [], []

    def step(self, label, tex, value=None, unit="", note=""):
        self.steps.append({"label": label, "tex": tex, "value": num(value),
                           "unit": unit, "note": note})
        return value

    def check(self, label, reference, computed, tol=1e-9, method="", scale=None):
        """Compare two independently obtained values.

        Relative error |ref − computed| / scale, scale defaults to |ref|
        (absolute error when ref = 0). Pass `scale` for identities whose terms
        cancel, e.g. α² − β² in a good conductor.
        """
        ref, cmp_ = complex(reference), complex(computed)
        if scale is None:
            scale = abs(ref) if abs(ref) > 0 else 1.0
        err = abs(ref - cmp_) / scale
        self.checks.append({"label": label, "method": method,
                            "reference": num(ref if ref.imag else ref.real),
                            "computed": num(cmp_ if cmp_.imag else cmp_.real),
                            "rel_error": num(err), "tol": tol,
                            "passed": bool(err <= tol)})
        return err <= tol

    def out(self, **values):
        return {"values": {k: num(v) for k, v in values.items()},
                "steps": self.steps, "checks": self.checks,
                "all_passed": all(c["passed"] for c in self.checks)}
