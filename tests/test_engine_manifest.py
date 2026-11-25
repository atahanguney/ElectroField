import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_manifest_lists_every_engine_file():
    listed = json.loads((ROOT / "engine" / "manifest.json").read_text(encoding="utf-8"))["files"]
    on_disk = sorted(p.name for p in (ROOT / "engine").glob("*.py"))
    assert sorted(listed) == on_disk


def test_api_fallback_list_matches_manifest():
    src = (ROOT / "web" / "js" / "api.js").read_text(encoding="utf-8")
    m = re.search(r"const ENGINE_FILES = \[(.*?)\];", src, re.S)
    fallback = re.findall(r"'([\w.]+\.py)'", m.group(1))
    listed = json.loads((ROOT / "engine" / "manifest.json").read_text(encoding="utf-8"))["files"]
    assert sorted(fallback) == sorted(listed)
    assert "manifest.json" in src
