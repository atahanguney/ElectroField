"""The landing-page snapshot (web/data/home.json) must match what the engine computes now."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _builder():
    spec = importlib.util.spec_from_file_location("build_home_example", ROOT / "scripts" / "build_home_example.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_snapshot_is_current():
    stored = json.loads((ROOT / "web" / "data" / "home.json").read_text(encoding="utf-8"))
    assert stored == _builder().build(), "run: python scripts/build_home_example.py"


def test_snapshot_checks_pass():
    stored = json.loads((ROOT / "web" / "data" / "home.json").read_text(encoding="utf-8"))
    assert stored["all_passed"] and all(c["passed"] for c in stored["checks"])
    assert len(stored["field"]["z"]) == len(stored["field"]["E"]["re"]) > 100
