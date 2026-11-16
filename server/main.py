"""HTTP API over the physics engine + static frontend.

Run:  python run.py   (or: uvicorn server.main:app --reload)
"""
import math
import os
from pathlib import Path

import plotly
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

from engine import dimensions as dm, questions as qb
from engine import constants as K, coordinates as co, electrostatics as es, magnetostatics as ms, maxwell as mx, radiation as ra, reflection as rf, tlines as tl, waves as wv

ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="ElectroField API", version="2.0")


@app.middleware("http")
async def _no_cache(request: Request, call_next):
    # local tool: always serve the current frontend files (avoids stale ES modules)
    resp = await call_next(request)
    if not request.url.path.startswith("/api/"):
        resp.headers["Cache-Control"] = "no-cache"
    return resp


@app.exception_handler(ValueError)
async def _bad_input(_: Request, exc: ValueError):
    return JSONResponse({"error": str(exc)}, status_code=400)


def _rad(v, is_angle, deg):
    return math.radians(v) if (is_angle and deg) else v


@app.get("/api/constants")
def constants():
    return [{"key": k, "tex": t, "value": v, "unit": u, "name": n} for k, t, v, u, n in K.TABLE]


@app.get("/api/coords/element")
def coords_element(system: str, u1: float, u2: float, u3: float,
                   d1: float, d2: float, d3: float, deg: bool = True):
    ang = co.SYSTEMS.get(system, {}).get("angle")
    if ang is None:
        raise HTTPException(400, f"unknown system {system!r}")
    u = [_rad(x, a, deg) for x, a in zip((u1, u2, u3), ang)]
    d = [_rad(x, a, deg) for x, a in zip((d1, d2, d3), ang)]
    return co.element(system, u, d)


@app.get("/api/coords/convert")
def coords_convert(src: str, dst: str, u1: float, u2: float, u3: float,
                   A1: float | None = None, A2: float | None = None, A3: float | None = None,
                   deg: bool = True):
    if src not in co.SYSTEMS or dst not in co.SYSTEMS:
        raise HTTPException(400, "unknown coordinate system")
    u = [_rad(x, a, deg) for x, a in zip((u1, u2, u3), co.SYSTEMS[src]["angle"])]
    A = None if A1 is None else [A1, A2 or 0.0, A3 or 0.0]
    r = co.convert(src, dst, u, A)
    if deg:
        p = r["values"]["point"]
        r["values"]["point"] = [math.degrees(x) if a else x for x, a in zip(p, co.SYSTEMS[dst]["angle"])]
    return r


@app.get("/api/waves/solve")
def waves_solve(f: float, eps_r: float = 1, mu_r: float = 1, sigma: float = 0, E0: float = 1):
    return wv.solve(f, eps_r, mu_r, sigma, E0)


@app.get("/api/waves/sweep")
def waves_sweep(param: str, lo: float, hi: float, f: float = 1e9, eps_r: float = 1,
                mu_r: float = 1, sigma: float = 0, n: int = 300):
    return wv.sweep(param, lo, hi, f, eps_r, mu_r, sigma, min(max(n, 10), 2000))


# ---------------------------------------------------------------- electrostatics
class Charge(BaseModel):
    q: float  # C
    x: float
    y: float


class ChargesIn(BaseModel):
    charges: list[Charge]
    ground: bool = False
    probe: tuple[float, float] = (0.0, 0.0)
    span: float = 1.0


@app.post("/api/es/charges")
def es_charges(body: ChargesIn):
    return es.point_charges([c.model_dump() for c in body.charges], body.ground, body.probe,
                            min(max(body.span, 1e-3), 1e3))


@app.get("/api/es/gauss")
def es_gauss(kind: str, rho: float, a: float = 0.1, b: float = 0.3, eps_r: float = 1, r: float = 0.05):
    return es.gauss(kind, rho, a, b, eps_r, r)


@app.get("/api/es/capacitor")
def es_capacitor(kind: str, V0: float = 1, eps_r: float = 1, A: float = 1e-2, d: float = 1e-3,
                 a: float = 1e-3, b: float = 3.5e-3, length: float = 1, E_bd: float = 3e6):
    return es.capacitor(kind, V0, eps_r, A, d, a, b, length, E_bd)


# ---------------------------------------------------------------- magnetostatics
class Wire(BaseModel):
    I: float
    x: float
    y: float


class WiresIn(BaseModel):
    currents: list[Wire]
    probe: tuple[float, float] = (0.0, 0.5)


@app.post("/api/ms/wires")
def ms_wires(body: WiresIn):
    return ms.wires([w.model_dump() for w in body.currents], body.probe)


@app.get("/api/ms/loops")
def ms_loops(kind: str = "loop", I: float = 1, a: float = 0.1, N: int = 10, length: float = 0.3,
             sep: float | None = None, pr: float = 0.05, pz: float = 0.05):
    return ms.loops(kind, I, a, N, length, sep, (pr, pz))


@app.get("/api/ms/ampere")
def ms_ampere(kind: str, I: float = 1, a: float = 0.01, b: float = 0.02, c: float = 0.025, N: int = 100,
              n_per_m: float = 1000, mu_r: float = 1, r: float = 0.005):
    return ms.ampere(kind, I, a, b, c, N, n_per_m, mu_r, r)


@app.get("/api/ms/inductance")
def ms_inductance(kind: str, I: float = 1, N: int = 100, a: float = 0.01, b: float = 0.02, length: float = 0.1,
                  h: float = 0.01, d: float = 0.1, mu_r: float = 1):
    return ms.inductance(kind, I, N, a, b, length, h, d, mu_r)


# ---------------------------------------------------------------- reflection
@app.get("/api/rf/normal")
def rf_normal(f: float = 1e9, eps1: float = 1, mu1: float = 1, s1: float = 0, eps2: float = 4, mu2: float = 1,
              s2: float = 0, E0: float = 1):
    return rf.normal(f, eps1, mu1, s1, eps2, mu2, s2, E0)


@app.get("/api/rf/oblique")
def rf_oblique(eps1: float = 1, mu1: float = 1, eps2: float = 2.25, mu2: float = 1, theta_deg: float = 30):
    return rf.oblique(eps1, mu1, eps2, mu2, theta_deg)


# ---------------------------------------------------------------- transmission lines
@app.get("/api/tl/line")
def tl_line(Z0: float = 50, RL: float = 100, XL: float = 50, f: float = 1e9, length: float = 0.3, vf: float = 1,
            Vg: float = 10, Zg: float = 50):
    return tl.line(Z0, RL, XL, f, length, vf, Vg, Zg)


# ---------------------------------------------------------------- waveguides & antennas
@app.get("/api/ra/waveguide")
def ra_waveguide(a: float = 22.86e-3, b: float = 10.16e-3, eps_r: float = 1, mu_r: float = 1, f: float = 10e9,
                 mode: str = "TE", m: int = 1, n: int = 0):
    return ra.waveguide(a, b, eps_r, mu_r, f, mode, m, n)


@app.get("/api/ra/dipole")
def ra_dipole(length_lambda: float = 0.5, I0: float = 1, f: float = 100e6):
    return ra.dipole(length_lambda, I0, f)


@app.get("/api/ra/array")
def ra_array(N: int = 8, d_lambda: float = 0.5, delta_deg: float = 0):
    return ra.array(N, d_lambda, delta_deg)


# ---------------------------------------------------------------- 1-D / 2-D / 3-D waves
@app.get("/api/dim/compare")
def dim_compare(f: float = 1e9, eps_r: float = 1, mu_r: float = 1, sigma: float = 0, r_max_lambda: float = 6):
    return dm.compare(f, eps_r, mu_r, sigma, r_max_lambda)


# ---------------------------------------------------------------- verification report
@app.get("/api/report/run")
def report_run():
    from engine import report
    return report.run()


# ---------------------------------------------------------------- question bank
@app.get("/api/qb/catalog")
def qb_catalog():
    return qb.catalog()


@app.get("/api/qb/new")
def qb_new(chapter: str | None = None, level: int | None = None, id: str | None = None, seed: int | None = None):
    return qb.generate(id, chapter, level, seed)


@app.get("/api/qb/check")
def qb_check(id: str, seed: int, answer: float | None = None):
    return qb.check(id, seed, answer)


# ---------------------------------------------------------------- Maxwell / boundaries
@app.get("/api/mx/boundary")
def mx_boundary(kind: str = "E", eps1: float = 1, eps2: float = 4, mu1: float = 1, mu2: float = 1,
                F1: float = 1, theta1_deg: float = 40, source: float = 0, pec: bool = False):
    return mx.boundary(kind, eps1, eps2, mu1, mu2, F1, theta1_deg, source, pec)


@app.get("/api/mx/faraday")
def mx_faraday(mode: str = "motional", B0: float = 0.1, f: float = 50, w: float = 0.1, l: float = 0.2,
               N: int = 1, R: float = 1, alpha_deg: float = 0):
    return mx.faraday(mode, B0, f, w, l, N, R, alpha_deg)


@app.get("/api/mx/currents")
def mx_currents(eps_r: float = 81, sigma: float = 4, f: float = 1e6, E0: float = 1):
    return mx.currents(eps_r, sigma, f, E0)


# ---------------------------------------------------------------- assistant
class ChatIn(BaseModel):
    messages: list[dict]


@app.post("/api/assistant")
def assistant_chat(body: ChatIn):
    import anthropic
    from server import assistant
    try:
        return assistant.chat(body.messages)
    except anthropic.AuthenticationError:
        return JSONResponse({"error": "No valid Anthropic credentials. Set ANTHROPIC_API_KEY (or run `ant auth login`) and restart the server."}, 401)
    except anthropic.RateLimitError:
        return JSONResponse({"error": "Rate limited by the Anthropic API — try again shortly."}, 429)
    except anthropic.APIConnectionError:
        return JSONResponse({"error": "Cannot reach the Anthropic API (network)."}, 502)
    except anthropic.APIStatusError as e:
        return JSONResponse({"error": f"Anthropic API error {e.status_code}: {e.message}"}, 502)
    except TypeError as e:  # raised by the SDK when no credential source exists
        if "api_key" in str(e) or "auth" in str(e).lower():
            return JSONResponse({"error": "No Anthropic credentials. Set ANTHROPIC_API_KEY (or run `ant auth login`) and restart the server."}, 401)
        raise


_PLOTLY = Path(plotly.__file__).parent / "package_data" / "plotly.min.js"


@app.get("/vendor/plotly.min.js")
def plotly_js():
    return FileResponse(_PLOTLY, media_type="application/javascript")


# engine sources are also served so the in-browser (Pyodide) build can be tested locally: /?backend=pyodide
app.mount("/engine", StaticFiles(directory=ROOT / "engine"), name="engine")
app.mount("/legacy", StaticFiles(directory=ROOT / "legacy"), name="legacy")
app.mount("/", StaticFiles(directory=ROOT / "web", html=True), name="web")
