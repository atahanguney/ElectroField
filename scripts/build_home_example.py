"""Write web/data/home.json: the landing-page example, computed by the engine ahead of time.

The landing page shows this snapshot immediately, so a visitor sees real engine output
before the in-browser engine (Pyodide, ~30 MB) has downloaded. tests/test_home_example.py
fails if the file differs from what the engine returns now; rerun this script after
changing engine/waves.py:

    python scripts/build_home_example.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine import questions, report, routes, worked  # noqa: E402

OUT = ROOT / "web" / "data" / "home.json"
PARAMS = {"f": 1e6, "eps_r": 81, "mu_r": 1, "sigma": 4, "E0": 1}   # 1 MHz in sea water
EVERY = 3   # keep every 3rd field sample: 134 points is plenty for a 600 px wide plot


def _round(x):
    """6 significant digits: keeps the file small and the comparison stable across platforms."""
    if isinstance(x, float):
        return float(f"{x:.6g}")
    if isinstance(x, list):
        return [_round(v) for v in x]
    if isinstance(x, dict):
        return {k: _round(v) for k, v in x.items()}
    return x


def build():
    r = json.loads(routes.call_json("waves/solve", json.dumps(PARAMS)))["ok"]
    f = r["field"]
    pick = lambda a: a[::EVERY]
    return _round({
        "params": PARAMS,
        "values": r["values"],
        "steps": r["steps"],
        "checks": r["checks"],
        "all_passed": r["all_passed"],
        "field": {"z": pick(f["z"]), "E": {"re": pick(f["E"]["re"]), "im": pick(f["E"]["im"])}},
        "counts": {"worked": len(worked.P), "templates": len(questions.T), "report_cases": len(report.CASES)},
    })


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(build(), ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size // 1024} kB)")
