"""In-app assistant: Claude chooses and parameterises engine calls; the engine computes.

Claude never produces physics numbers on its own — every quantity it reports comes
from a tool result below. Each tool call is also returned to the browser as an
"action" so the matching chapter opens with exactly those parameters (the graph).

Credentials: ANTHROPIC_API_KEY (or an `ant auth login` profile).
"""
import json
import math

import anthropic

from engine import dimensions as dm
from engine import coordinates as co, electrostatics as es, magnetostatics as ms, maxwell as mx, radiation as ra, reflection as rf, tlines as tl, waves as wv

MODEL = "claude-opus-5-5"
MAX_ROUNDS = 6

SYSTEM = """You are the assistant inside ElectroField, an applied-electromagnetics workbench for electrical engineering students and engineers (notation of Ulaby & Ravaioli and Cheng).

Rules:
- Every number you state must come from a tool result in this conversation. Never compute or estimate physics values yourself; if no tool covers the question, say so and explain qualitatively.
- When the user asks for a graph, a field picture, a sweep or "show me", call the matching tool: the app opens that chapter with your parameters and draws the plots. Mention which chapter/tab opened.
- Convert the user's units to the tool's SI inputs (e.g. 2.45 GHz → 2.45e9 Hz, 5 nC stays q_nC = 5, 3 mm → 0.003 m). Angles in degrees.
- After a tool call, explain the result physically and briefly: which regime, which formula governs it, what would change if a parameter changed. Report whether the engine's independent checks passed.
- Reply in the language the user writes in. Be concise; use plain text with simple inline math (no LaTeX blocks).
"""

N = {"type": "number"}
TOOLS = [
    {"name": "plane_wave", "description": "Uniform plane wave in a homogeneous medium: α, β, ηc, skin depth, phase velocity, wavelength, power density; opens Chapter 5 with E/H plots and α/β sweeps.",
     "input_schema": {"type": "object", "properties": {"f": {**N, "description": "frequency in Hz"}, "eps_r": N, "mu_r": N,
                      "sigma": {**N, "description": "conductivity S/m"}, "E0": {**N, "description": "amplitude V/m"}}, "required": ["f"]}},
    {"name": "coordinate_element", "description": "Differential length/area/volume element in cartesian, cylindrical (r, phi, z) or spherical (R, theta, phi) coordinates; opens Chapter 1 with the 3-D element and dimensioned sections.",
     "input_schema": {"type": "object", "properties": {"system": {"type": "string", "enum": ["cartesian", "cylindrical", "spherical"]},
                      "u": {"type": "array", "items": N, "description": "point (lengths m, angles deg)"},
                      "d": {"type": "array", "items": N, "description": "increments (m / deg)"}}, "required": ["system", "u", "d"]}},
    {"name": "point_charges", "description": "Field and potential of up to 8 point charges in the plane z=0, optional grounded plane y=0 (method of images); field lines, equipotentials and E, V at a probe point. Opens Chapter 2.",
     "input_schema": {"type": "object", "properties": {
         "charges": {"type": "array", "items": {"type": "object", "properties": {"q_nC": N, "x": N, "y": N}, "required": ["q_nC", "x", "y"]}},
         "ground": {"type": "boolean"}, "probe": {"type": "array", "items": N, "description": "[x, y] in m"}}, "required": ["charges"]}},
    {"name": "gauss_law", "description": "Gauss's law for symmetric distributions: sphere (rho=ρv), shell (rho=ρs), line (rho=ρl), cylinder (ρv), coax (ρl), sheet (ρs), slab (ρv). Returns Q_enc, D, E, V at distance r with E(r), V(r) plots. b = outer radius (coax) or zero-potential reference (line, cylinder).",
     "input_schema": {"type": "object", "properties": {"kind": {"type": "string", "enum": list(es.GAUSS)}, "rho": N, "a": N, "b": N, "eps_r": N, "r": N},
                      "required": ["kind", "rho"]}},
    {"name": "capacitor", "description": "Parallel-plate (A, d), coaxial (a, b, length) or spherical (a, b) capacitor: C, Q, stored energy, maximum field and breakdown voltage.",
     "input_schema": {"type": "object", "properties": {"kind": {"type": "string", "enum": ["parallel", "coax", "spherical"]}, "V0": N, "eps_r": N,
                      "A": N, "d": N, "a": N, "b": N, "length": N, "E_bd": {**N, "description": "dielectric strength V/m"}}, "required": ["kind"]}},
    {"name": "parallel_wires", "description": "Infinite straight wires perpendicular to the page (I>0 out of page) at (x, y): B field lines, B at a probe, force per unit length on each wire. Opens Chapter 3.",
     "input_schema": {"type": "object", "properties": {"wires": {"type": "array", "items": {"type": "object", "properties": {"I": N, "x": N, "y": N}, "required": ["I", "x", "y"]}},
                      "probe": {"type": "array", "items": N}}, "required": ["wires"]}},
    {"name": "current_loops", "description": "Coaxial circular loops: 'loop', 'helmholtz' (two loops, spacing a) or 'solenoid' (N loops over length). Exact field (elliptic integrals), field lines, axial B_z; probe at (rho, z).",
     "input_schema": {"type": "object", "properties": {"kind": {"type": "string", "enum": ["loop", "helmholtz", "solenoid"]}, "I": N, "a": N,
                      "N": {"type": "integer"}, "length": N, "probe_rho": N, "probe_z": N}, "required": ["kind"]}},
    {"name": "ampere_law", "description": "Ampère's law for wire (radius a), tube (a<r<b), coax (inner a, outer shell b..c), toroid (N turns, a<r<b) or ideal solenoid (n_per_m): B(r) profile and B, H at r.",
     "input_schema": {"type": "object", "properties": {"kind": {"type": "string", "enum": ["wire", "tube", "coax", "toroid", "solenoid"]}, "I": N, "a": N, "b": N, "c": N,
                      "N": {"type": "integer"}, "n_per_m": N, "mu_r": N, "r": N}, "required": ["kind"]}},
    {"name": "inductance", "description": "Inductance and stored magnetic energy: solenoid (N, a, length), coax (a, b, length), toroid with rectangular core (N, a, b, h), two-wire line (a, d, length).",
     "input_schema": {"type": "object", "properties": {"kind": {"type": "string", "enum": ["solenoid", "coax", "toroid", "twowire"]}, "I": N, "N": {"type": "integer"},
                      "a": N, "b": N, "length": N, "h": N, "d": N, "mu_r": N}, "required": ["kind"]}},
    {"name": "reflection_normal", "description": "Normal incidence of a plane wave from medium 1 (z<0) onto medium 2 (z>0), media may be lossy: Γ, τ, SWR, reflected/transmitted power, standing-wave plot. Opens Chapter 6.",
     "input_schema": {"type": "object", "properties": {"f": N, "eps1": N, "mu1": N, "s1": N, "eps2": N, "mu2": N, "s2": N}, "required": ["f"]}},
    {"name": "reflection_oblique", "description": "Oblique incidence between lossless media: Snell, Fresnel Γ⊥/Γ∥, R and T vs angle, Brewster and critical angles, total internal reflection.",
     "input_schema": {"type": "object", "properties": {"eps1": N, "mu1": N, "eps2": N, "mu2": N, "theta_deg": N}, "required": ["theta_deg"]}},
    {"name": "transmission_line", "description": "Lossless transmission line Z0 terminated in ZL = RL + jXL, length (m), frequency, velocity factor vf: Γ, VSWR, return loss, Zin, voltage max/min positions, Smith chart, quarter-wave and single-stub matching. Opens Chapter 7.",
     "input_schema": {"type": "object", "properties": {"Z0": N, "RL": N, "XL": N, "f": N, "length": N, "vf": N}, "required": ["RL"]}},
    {"name": "waveguide", "description": "Rectangular metal waveguide a×b (m) filled with eps_r: cut-off of mode TE/TM m,n, β, guide wavelength, phase/group velocity, wave impedance, list of lowest modes, cross-section field and dispersion plot. Opens Chapter 8.",
     "input_schema": {"type": "object", "properties": {"a": N, "b": N, "eps_r": N, "f": N, "mode": {"type": "string", "enum": ["TE", "TM"]},
                      "m": {"type": "integer"}, "n": {"type": "integer"}}, "required": ["f"]}},
    {"name": "dipole_antenna", "description": "Centre-fed thin dipole of total length length_lambda (in wavelengths): radiation pattern, radiation resistance, directivity, beamwidth, radiated power for peak current I0.",
     "input_schema": {"type": "object", "properties": {"length_lambda": N, "I0": N, "f": N}, "required": ["length_lambda"]}},
    {"name": "linear_array", "description": "Uniform linear array of N isotropic elements, spacing d_lambda (wavelengths), progressive phase delta_deg: array factor pattern, beam direction, directivity, grating lobes.",
     "input_schema": {"type": "object", "properties": {"N": {"type": "integer"}, "d_lambda": N, "delta_deg": N}, "required": ["N", "d_lambda"]}},
    {"name": "wave_dimensions", "description": "Compare 1-D (plane wave / transmission line), 2-D (cylindrical, line source) and 3-D (spherical, point source) waves in the same medium: spreading laws, field maps, amplitude vs distance, and how doubling f, εr, σ or distance changes the level. Opens Chapter 0.",
     "input_schema": {"type": "object", "properties": {"f": N, "eps_r": N, "mu_r": N, "sigma": N, "r_max_lambda": N}, "required": ["f"]}},
    {"name": "boundary_condition", "description": "Boundary conditions at a planar interface. kind E: |E1| V/m, source = surface charge ρs; kind H: |H1| A/m, source = surface current Js_z. theta1_deg from the normal. pec = medium 2 is a perfect conductor. Opens Chapter 4.",
     "input_schema": {"type": "object", "properties": {"kind": {"type": "string", "enum": ["E", "H"]}, "eps1": N, "eps2": N, "mu1": N, "mu2": N,
                      "F1": N, "theta1_deg": N, "source": N, "pec": {"type": "boolean"}}, "required": ["kind"]}},
    {"name": "faraday_emf", "description": "Induced EMF: 'motional' rotating w×l loop (generator) in static B0 at f rev/s, or 'transformer' fixed loop in B0 cos(2πft) at angle alpha. N turns, resistance R.",
     "input_schema": {"type": "object", "properties": {"mode": {"type": "string", "enum": ["motional", "transformer"]}, "B0": N, "f": N, "w": N, "l": N,
                      "N": {"type": "integer"}, "R": N, "alpha_deg": N}, "required": ["mode"]}},
    {"name": "conduction_vs_displacement", "description": "Ratio of conduction to displacement current σ/ωε, crossover frequency and charge relaxation time for a medium.",
     "input_schema": {"type": "object", "properties": {"eps_r": N, "sigma": N, "f": N}, "required": ["eps_r", "sigma", "f"]}},
]


def _run(name, a):
    """Execute one tool → (engine result, UI action)."""
    if name == "plane_wave":
        p = {k: a[k] for k in ("f", "eps_r", "mu_r", "sigma", "E0") if k in a}
        return wv.solve(**p), {"chapter": "waves", "params": p}
    if name == "coordinate_element":
        sysm, u, d = a["system"], list(map(float, a["u"])), list(map(float, a["d"]))
        ang = co.SYSTEMS[sysm]["angle"]
        r = co.element(sysm, [math.radians(x) if g else x for x, g in zip(u, ang)], [math.radians(x) if g else x for x, g in zip(d, ang)])
        return r, {"chapter": "coordinates", "params": {"system": sysm, "u": u, "d": d}}
    if name == "point_charges":
        ch = [{"q": c["q_nC"] * 1e-9, "x": c["x"], "y": c["y"]} for c in a["charges"]]
        probe = tuple(a.get("probe") or (0.0, 0.0))
        r = es.point_charges(ch, a.get("ground", False), probe)
        return r, {"chapter": "electrostatics", "params": {"tab": "charges", "charges": {"q": [[c["q_nC"], c["x"], c["y"]] for c in a["charges"]],
                                                                                         "ground": a.get("ground", False), "probe": list(probe)}}}
    if name == "gauss_law":
        p = {k: a[k] for k in ("kind", "rho", "a", "b", "eps_r", "r") if k in a}
        return es.gauss(**p), {"chapter": "electrostatics", "params": {"tab": "gauss", "gauss": p}}
    if name == "capacitor":
        p = {k: a[k] for k in ("kind", "V0", "eps_r", "A", "d", "a", "b", "length", "E_bd") if k in a}
        return es.capacitor(**p), {"chapter": "electrostatics", "params": {"tab": "capacitor", "capacitor": p}}
    if name == "parallel_wires":
        probe = tuple(a.get("probe") or (0.0, 0.5))
        r = ms.wires([{"I": w["I"], "x": w["x"], "y": w["y"]} for w in a["wires"]], probe)
        return r, {"chapter": "magnetostatics", "params": {"tab": "wires", "wires": {"W": [[w["I"], w["x"], w["y"]] for w in a["wires"]], "probe": list(probe)}}}
    if name == "current_loops":
        p = {k: a[k] for k in ("kind", "I", "a", "N", "length") if k in a}
        pr, pz = a.get("probe_rho", 0.5 * a.get("a", 0.1)), a.get("probe_z", 0.3 * a.get("a", 0.1))
        return ms.loops(**p, probe=(pr, pz)), {"chapter": "magnetostatics", "params": {"tab": "loops", "loops": {**p, "pr": pr, "pz": pz}}}
    if name == "ampere_law":
        p = {k: a[k] for k in ("kind", "I", "a", "b", "c", "N", "n_per_m", "mu_r", "r") if k in a}
        return ms.ampere(**p), {"chapter": "magnetostatics", "params": {"tab": "ampere", "ampere": p}}
    if name == "inductance":
        p = {k: a[k] for k in ("kind", "I", "N", "a", "b", "length", "h", "d", "mu_r") if k in a}
        return ms.inductance(**p), {"chapter": "magnetostatics", "params": {"tab": "inductance", "inductance": p}}
    if name == "reflection_normal":
        p = {k: a[k] for k in ("f", "eps1", "mu1", "s1", "eps2", "mu2", "s2") if k in a}
        return rf.normal(**p), {"chapter": "reflection", "params": {"tab": "normal", "normal": p}}
    if name == "reflection_oblique":
        p = {k: a[k] for k in ("eps1", "mu1", "eps2", "mu2", "theta_deg") if k in a}
        return rf.oblique(**p), {"chapter": "reflection", "params": {"tab": "oblique", "oblique": p}}
    if name == "transmission_line":
        p = {k: a[k] for k in ("Z0", "RL", "XL", "f", "length", "vf") if k in a}
        return tl.line(**p), {"chapter": "tlines", "params": p}
    if name == "waveguide":
        p = {k: a[k] for k in ("a", "b", "eps_r", "f", "mode", "m", "n") if k in a}
        return ra.waveguide(**p), {"chapter": "radiation", "params": {"tab": "waveguide", "waveguide": p}}
    if name == "dipole_antenna":
        p = {k: a[k] for k in ("length_lambda", "I0", "f") if k in a}
        return ra.dipole(**p), {"chapter": "radiation", "params": {"tab": "dipole", "dipole": p}}
    if name == "linear_array":
        p = {k: a[k] for k in ("N", "d_lambda", "delta_deg") if k in a}
        return ra.array(**p), {"chapter": "radiation", "params": {"tab": "array", "array": p}}
    if name == "wave_dimensions":
        p = {k: a[k] for k in ("f", "eps_r", "mu_r", "sigma", "r_max_lambda") if k in a}
        return dm.compare(**p), {"chapter": "dimensions", "params": p}
    if name == "boundary_condition":
        p = {k: a[k] for k in ("kind", "eps1", "eps2", "mu1", "mu2", "F1", "theta1_deg", "source", "pec") if k in a}
        return mx.boundary(**p), {"chapter": "maxwell", "params": {"tab": "boundary", "boundary": p}}
    if name == "faraday_emf":
        p = {k: a[k] for k in ("mode", "B0", "f", "w", "l", "N", "R", "alpha_deg") if k in a}
        return mx.faraday(**p), {"chapter": "maxwell", "params": {"tab": "faraday", "faraday": p}}
    if name == "conduction_vs_displacement":
        p = {k: a[k] for k in ("eps_r", "sigma", "f") if k in a}
        return mx.currents(**p), {"chapter": "maxwell", "params": {"tab": "currents", "currents": p}}
    raise ValueError(f"unknown tool {name}")


def _summary(r):
    """Compact view of an engine result for the model (no arrays)."""
    vals = {k: v for k, v in r["values"].items() if not (isinstance(v, list) and len(v) > 6)}
    steps = [{"step": s["label"], "result": s["value"] if not isinstance(s["value"], list) or len(s["value"]) <= 3 else None,
              "unit": s["unit"], "note": s["note"]} for s in r["steps"]]
    checks = [{"check": c["label"], "passed": c["passed"], "rel_error": c["rel_error"]} for c in r["checks"]]
    return json.dumps({"values": vals, "steps": steps, "checks": checks, "all_checks_passed": r["all_passed"]}, default=str)


def chat(history):
    """history: [{role: 'user'|'assistant', content: str}] → {reply, actions}."""
    if not history or history[-1].get("role") != "user":
        raise ValueError("last message must be from the user")
    msgs = [{"role": m["role"], "content": str(m["content"])[:8000]} for m in history[-20:] if m.get("role") in ("user", "assistant")]
    client = anthropic.Anthropic()
    actions = []
    for _ in range(MAX_ROUNDS):
        resp = client.beta.messages.create(
            model=MODEL, max_tokens=16000, system=SYSTEM, tools=TOOLS, messages=msgs,
            output_config={"effort": "medium"},
            betas=["server-side-fallback-2026-07-01"], fallbacks="default",
        )
        if resp.stop_reason == "refusal":
            return {"reply": "The assistant declined this request.", "actions": actions}
        if resp.stop_reason == "pause_turn":
            msgs.append({"role": "assistant", "content": resp.content})
            continue
        uses = [b for b in resp.content if b.type == "tool_use"]
        if resp.stop_reason != "tool_use" or not uses:
            text = "\n".join(b.text for b in resp.content if b.type == "text").strip()
            return {"reply": text or "(no answer)", "actions": actions}
        msgs.append({"role": "assistant", "content": resp.content})
        results = []
        for u in uses:
            try:
                r, act = _run(u.name, dict(u.input))
                actions.append({**act, "tool": u.name, "all_passed": r["all_passed"]})
                results.append({"type": "tool_result", "tool_use_id": u.id, "content": _summary(r)})
            except (ValueError, KeyError, TypeError) as e:
                results.append({"type": "tool_result", "tool_use_id": u.id, "content": f"input error: {e}", "is_error": True})
        msgs.append({"role": "user", "content": results})
    return {"reply": "Stopped after too many tool rounds.", "actions": actions}
