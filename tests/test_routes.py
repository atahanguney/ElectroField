"""The browser build (engine/routes.py via Pyodide) must return exactly what the HTTP server returns."""
import json
import math

import pytest
from fastapi.testclient import TestClient

from engine import routes
from server.main import app

client = TestClient(app)

GET = [
    ("constants", {}),
    ("coords/element", {"system": "cylindrical", "u1": 1.5, "u2": 30, "u3": 0.3, "d1": 0.4, "d2": 25, "d3": 0.5}),
    ("coords/convert", {"src": "cartesian", "dst": "spherical", "u1": 2, "u2": 3, "u3": -1, "A1": 1, "A2": 0, "A3": 0}),
    ("waves/solve", {"f": 1e6, "eps_r": 81, "sigma": 4}),
    ("waves/sweep", {"param": "f", "lo": 1e3, "hi": 1e12, "f": 1e6, "eps_r": 81, "sigma": 4}),
    ("es/gauss", {"kind": "coax", "rho": 1e-9, "a": 0.01, "b": 0.03, "r": 0.02}),
    ("es/capacitor", {"kind": "coax", "V0": 100, "eps_r": 2.25, "a": 0.00045, "b": 0.00147}),
    ("ms/loops", {"kind": "helmholtz", "I": 1, "a": 0.1, "pr": 0.05, "pz": 0.03}),
    ("ms/ampere", {"kind": "coax", "I": 5, "r": 0.015}),
    ("ms/inductance", {"kind": "toroid", "N": 200, "a": 0.02, "b": 0.03}),
    ("rf/normal", {"f": 1e8, "eps2": 2.25}),
    ("rf/oblique", {"eps1": 2.25, "eps2": 1, "theta_deg": 50}),
    ("tl/line", {"Z0": 50, "RL": 100, "XL": 50}),
    ("ra/waveguide", {"f": 1e10}),
    ("ra/dipole", {"length_lambda": 0.5}),
    ("ra/array", {"N": 8, "d_lambda": 0.5, "delta_deg": -45}),
    ("dim/compare", {"f": 1e9}),
    ("qb/catalog", {}),
    ("report/run", {}),
    ("wk/catalog", {}),
    ("wk/solve", {"id": "tli2"}),
    ("bs/segment", {"I": 2, "z1": -0.5, "z2": 0.5, "r": 0.2}),
    ("bs/loop", {"I": 1, "a": 0.1, "z": 0.05}),
    ("bs/square", {"I": 1, "a": 0.2}),
    ("img/plane", {"Q": 1e-9, "d": 0.4}),
    ("img/corner", {"Q": 1e-9, "x0": 0.3, "y0": 0.5}),
    ("qb/new", {"id": "c5-skin", "seed": 3}),
    ("qb/check", {"id": "c5-skin", "seed": 3, "answer": 10}),
    ("mx/boundary", {"kind": "H", "mu2": 100, "F1": 5, "theta1_deg": 60}),
    ("mx/faraday", {"mode": "motional", "N": 10}),
    ("mx/currents", {"eps_r": 81, "sigma": 4, "f": 1e6}),
]
POST = [
    ("es/charges", {"charges": [{"q": 1e-9, "x": -0.25, "y": 0}, {"q": -1e-9, "x": 0.25, "y": 0}], "ground": False, "probe": [0, 0.4]}),
    ("ms/wires", {"currents": [{"I": 10, "x": -0.25, "y": 0}, {"I": 10, "x": 0.25, "y": 0}], "probe": [0, 0.5]}),
]


def same(a, b, path="$"):
    if isinstance(a, dict):
        assert isinstance(b, dict) and a.keys() == b.keys(), path
        for k in a:
            same(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list):
        assert isinstance(b, list) and len(a) == len(b), path
        for i, (x, y) in enumerate(zip(a, b)):
            same(x, y, f"{path}[{i}]")
    elif isinstance(a, float) or isinstance(b, float):
        assert a == pytest.approx(b, rel=1e-12, abs=1e-300), path
    else:
        assert a == b, path


@pytest.mark.parametrize("path,params", GET)
def test_get_parity(path, params):
    http = client.get(f"/api/{path}", params=params)
    assert http.status_code == 200
    same(http.json(), json.loads(routes.call_json(path, json.dumps(params)))["ok"])


@pytest.mark.parametrize("path,body", POST)
def test_post_parity(path, body):
    http = client.post(f"/api/{path}", json=body)
    assert http.status_code == 200
    same(http.json(), json.loads(routes.call_json(path, json.dumps(body)))["ok"])


def test_every_route_covered():
    assert {p for p, _ in GET + POST} == set(routes.ROUTES)


def test_browser_loads_every_engine_module():
    """web/js/api.js must copy every engine/*.py into Pyodide."""
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    js = (root / "web" / "js" / "api.js").read_text(encoding="utf-8")
    for f in (root / "engine").glob("*.py"):
        assert f"'{f.name}'" in js, f.name


def test_pages_shell_matches_web_shell():
    """Root index.html (GitHub Pages) must stay the same page as web/index.html."""
    import re
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    body = lambda s: re.search(r"<body>(.*)</body>", s, re.S).group(1).replace("web/", "").strip()
    pages = (root / "index.html").read_text(encoding="utf-8")
    web = (root / "web" / "index.html").read_text(encoding="utf-8")
    assert body(pages) == body(web)
    assert 'href="web/css/base.css"' in pages


def test_errors_are_json():
    out = json.loads(routes.call_json("waves/solve", json.dumps({"f": -1})))
    assert "error" in out
    assert "error" in json.loads(routes.call_json("nope", "{}"))
