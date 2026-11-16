"""Question bank: original problems in the style of Ulaby / Cheng end-of-chapter exercises.

Each template draws its numbers from a seeded RNG, so (template id, seed) reproduces the
same problem. The answer is never stored: it is computed by the engine solver on demand,
and the solver's own independent checks must pass before an answer is accepted.
"""
import math
import numpy as np

from . import dimensions as dm
from . import coordinates as co, electrostatics as es, magnetostatics as ms, maxwell as mx
from . import radiation as ra, reflection as rf, tlines as tl, waves as wv
from .constants import C0


def _nice(x, sig=2):
    if x == 0:
        return 0.0
    return float(f"{x:.{sig}g}")


def _u(rng, lo, hi, sig=2, log=False):
    v = math.exp(rng.uniform(math.log(lo), math.log(hi))) if log else rng.uniform(lo, hi)
    return _nice(v, sig)


def _i(rng, lo, hi):
    return int(rng.integers(lo, hi + 1))


def _pick(rng, xs):
    return xs[int(rng.integers(0, len(xs)))]


# Each template: id, chapter, level (1 basic … 3 harder), ref, unit, scale (SI → shown unit),
# gen(rng) → params, text(p) → str, solve(p) → (engine result, answer in SI, chapter action), tol
T = []


def q(**kw):
    kw.setdefault("tol", 0.01)
    kw.setdefault("abs_tol", None)
    kw.setdefault("scale", 1.0)
    T.append(kw)


# ---------------- Chapter 0 (1-D / 2-D / 3-D)
q(id="c0-spread", chapter="dimensions", level=1, ref="Ulaby §9-1", unit="dB", abs_tol=0.1,
  gen=lambda r: {"dim": _pick(r, ["2D", "3D"]), "k": _pick(r, [2, 3, 4, 5, 10])},
  text=lambda p: f"In a lossless medium, a {'line source radiates a cylindrical' if p['dim'] == '2D' else 'point source radiates a spherical'} wave. "
                 f"By how many dB does the field level change when the distance (in the far zone) is multiplied by {p['k']}?",
  solve=lambda p: _spread(p))

# ---------------- Chapter 1
q(id="c1-sph-dv", chapter="coordinates", level=1, ref="Ulaby §3-2.3", unit="cm³", scale=1e6,
  gen=lambda r: {"R": _u(r, 0.5, 3), "th": _i(r, 20, 160), "ph": _i(r, 0, 300), "dR": _u(r, 0.01, 0.05), "dth": _i(r, 1, 5), "dph": _i(r, 1, 5)},
  text=lambda p: f"At the point R = {p['R']} m, θ = {p['th']}°, φ = {p['ph']}°, a small spherical volume element has edges dR = {p['dR']} m, "
                 f"dθ = {p['dth']}° and dφ = {p['dph']}°. Using the differential volume element, find dv.",
  solve=lambda p: _coords("spherical", [p["R"], p["th"], p["ph"]], [p["dR"], p["dth"], p["dph"]], lambda r: r["values"]["dv"]))
q(id="c1-cyl-ds", chapter="coordinates", level=1, ref="Ulaby §3-2.2", unit="cm²", scale=1e4,
  gen=lambda r: {"r": _u(r, 0.2, 2), "ph": _i(r, 0, 300), "z": _u(r, -1, 1), "dph": _i(r, 2, 10), "dz": _u(r, 0.01, 0.1)},
  text=lambda p: f"On the cylindrical surface r = {p['r']} m, a patch spans dφ = {p['dph']}° and dz = {p['dz']} m around φ = {p['ph']}°, z = {p['z']} m. "
                 f"Find the area ds_r of the patch.",
  solve=lambda p: _coords("cylindrical", [p["r"], p["ph"], p["z"]], [0.01, p["dph"], p["dz"]], lambda r: r["values"]["ds"][0]))
q(id="c1-conv-theta", chapter="coordinates", level=2, ref="Ulaby §3-3", unit="°", abs_tol=0.2,
  gen=lambda r: {"x": _i(r, -5, 5) or 1, "y": _i(r, -5, 5), "z": _i(r, -5, 5) or -2},
  text=lambda p: f"Express the point P = ({p['x']}, {p['y']}, {p['z']}) m in spherical coordinates. What is the polar angle θ?",
  solve=lambda p: _conv(p))

# ---------------- Chapter 2
q(id="c2-two-charges", chapter="electrostatics", level=2, ref="Ulaby §4-3", unit="V/m",
  gen=lambda r: {"q1": _pick(r, [1, 2, 3, 4, 5]), "q2": _pick(r, [-4, -3, -2, -1, 1, 2]), "d": _u(r, 0.2, 0.6), "py": _u(r, 0.1, 0.5)},
  text=lambda p: f"Point charges q₁ = {p['q1']} nC at (−{p['d'] / 2:g}, 0) m and q₂ = {p['q2']} nC at ({p['d'] / 2:g}, 0) m lie in free space. "
                 f"Find the magnitude of E at (0, {p['py']}) m.",
  solve=lambda p: _charges(p))
q(id="c2-gauss-sphere", chapter="electrostatics", level=2, ref="Ulaby §4-4", unit="V/m",
  gen=lambda r: {"rho": _u(r, 1, 9), "a": _u(r, 0.05, 0.2), "f": _pick(r, [0.5, 0.8, 1.5, 2.5])},
  text=lambda p: f"A sphere of radius a = {p['a']} m holds a uniform charge density ρv = {p['rho']} µC/m³ in free space. "
                 f"Use Gauss's law to find |E| at R = {_nice(p['f'] * p['a'], 3)} m.",
  solve=lambda p: _gauss("sphere", p["rho"] * 1e-6, p["a"], _nice(p["f"] * p["a"], 3)))
q(id="c2-coax-C", chapter="electrostatics", level=1, ref="Ulaby §4-10", unit="pF/m", scale=1e12,
  gen=lambda r: {"a": _u(r, 0.3, 1.5), "ratio": _u(r, 2, 5), "er": _pick(r, [1, 2.1, 2.25, 3.5, 4])},
  text=lambda p: f"A coaxial line has inner radius a = {p['a']} mm and outer radius b = {_nice(p['a'] * p['ratio'], 3)} mm, filled with a dielectric of εr = {p['er']}. "
                 f"Find the capacitance per metre.",
  solve=lambda p: _cap("coax", a=p["a"] * 1e-3, b=_nice(p["a"] * p["ratio"], 3) * 1e-3, eps_r=p["er"], length=1.0, key="C"))
q(id="c2-plate-bd", chapter="electrostatics", level=2, ref="Ulaby §4-10", unit="kV", scale=1e-3,
  gen=lambda r: {"d": _u(r, 0.1, 2), "er": _pick(r, [1, 2.2, 4.4]), "Ebd": _pick(r, [3, 12, 20, 60])},
  text=lambda p: f"A parallel-plate capacitor has a gap of {p['d']} mm filled with a dielectric (εr = {p['er']}) whose dielectric strength is {p['Ebd']} MV/m. "
                 f"Neglecting fringing, what is the largest voltage it can hold?",
  solve=lambda p: _cap("parallel", d=p["d"] * 1e-3, eps_r=p["er"], E_bd=p["Ebd"] * 1e6, key="V_bd"))

# ---------------- Chapter 3
q(id="c3-wire-force", chapter="magnetostatics", level=1, ref="Ulaby §5-2.3", unit="µN/m", scale=1e6,
  gen=lambda r: {"I1": _i(r, 2, 50), "I2": _pick(r, [-40, -20, -10, 5, 15, 30]), "d": _u(r, 0.02, 0.5)},
  text=lambda p: f"Two long parallel wires {p['d']} m apart carry {p['I1']} A and {p['I2']} A (sign = direction). "
                 f"Find the magnitude of the force per unit length between them.",
  solve=lambda p: _wires(p))
q(id="c3-loop-centre", chapter="magnetostatics", level=1, ref="Ulaby §5-2.2", unit="µT", scale=1e6,
  gen=lambda r: {"I": _u(r, 0.5, 20), "a": _u(r, 0.02, 0.3), "N": _pick(r, [1, 1, 10, 50])},
  text=lambda p: f"A flat circular coil of {p['N']} turn(s), radius {p['a']} m, carries {p['I']} A. Find B at its centre.",
  solve=lambda p: _loop(p))
q(id="c3-toroid", chapter="magnetostatics", level=2, ref="Ulaby §5-4", unit="mT", scale=1e3,
  gen=lambda r: {"N": _pick(r, [100, 200, 500, 1000]), "I": _u(r, 0.1, 3), "a": _u(r, 0.02, 0.05), "w": _u(r, 0.01, 0.03), "mur": _pick(r, [1, 1, 50, 200])},
  text=lambda p: f"A toroid with N = {p['N']} turns, inner radius {p['a']} m and outer radius {_nice(p['a'] + p['w'], 3)} m has a core of μr = {p['mur']} "
                 f"and carries I = {p['I']} A. Find B at the mean radius.",
  solve=lambda p: _toroid(p))
q(id="c3-coax-L", chapter="magnetostatics", level=1, ref="Ulaby §5-7", unit="nH/m", scale=1e9,
  gen=lambda r: {"a": _u(r, 0.3, 2), "ratio": _u(r, 2, 6)},
  text=lambda p: f"Find the external inductance per metre of an air coax with a = {p['a']} mm and b = {_nice(p['a'] * p['ratio'], 3)} mm.",
  solve=lambda p: _ind(p))

# ---------------- Chapter 4
q(id="c4-refraction", chapter="maxwell", level=2, ref="Ulaby §4-8", unit="°", abs_tol=0.2,
  gen=lambda r: {"e1": _pick(r, [1, 2, 3]), "e2": _pick(r, [4, 6, 9, 12]), "th": _i(r, 15, 75), "E": _i(r, 10, 200)},
  text=lambda p: f"A static field E₁ = {p['E']} V/m in medium 1 (εr = {p['e1']}) meets a charge-free planar boundary with medium 2 (εr = {p['e2']}) "
                 f"at θ₁ = {p['th']}° from the normal. Find the angle θ₂ of E₂ from the normal.",
  solve=lambda p: _bc(p))
q(id="c4-generator", chapter="maxwell", level=1, ref="Ulaby §6-3", unit="V",
  gen=lambda r: {"N": _pick(r, [10, 50, 100, 200]), "B": _u(r, 0.05, 1), "w": _u(r, 0.05, 0.3), "l": _u(r, 0.05, 0.3), "f": _pick(r, [50, 60, 120])},
  text=lambda p: f"A {p['w']} m × {p['l']} m coil of {p['N']} turns rotates at {p['f']} rev/s in a uniform B = {p['B']} T perpendicular to the rotation axis. "
                 f"Find the peak induced EMF.",
  solve=lambda p: _far(p))
q(id="c4-crossover", chapter="maxwell", level=1, ref="Ulaby §6-7", unit="MHz", scale=1e-6,
  gen=lambda r: {"er": _pick(r, [5, 10, 25, 81]), "s": _u(r, 1e-3, 5, log=True)},
  text=lambda p: f"For a medium with εr = {p['er']} and σ = {p['s']} S/m, at what frequency do conduction and displacement current densities have equal magnitude?",
  solve=lambda p: _cur(p))

# ---------------- Chapter 5
q(id="c5-skin", chapter="waves", level=1, ref="Ulaby §7-5", unit="µm", scale=1e6,
  gen=lambda r: {"m": _pick(r, [("copper", 5.8e7), ("aluminium", 3.5e7), ("brass", 1.5e7), ("silver", 6.2e7)]), "f": _pick(r, [1e6, 10e6, 100e6, 1e9, 10e9])},
  text=lambda p: f"Find the skin depth of {p['m'][0]} (σ = {p['m'][1]:.2g} S/m, μr = 1) at {p['f'] / 1e6:g} MHz.",
  solve=lambda p: _wave(p["f"], 1, 1, p["m"][1], "skin_depth"))
q(id="c5-seawater", chapter="waves", level=2, ref="Ulaby §7-4", unit="dB/m",
  gen=lambda r: {"f": _pick(r, [1e3, 10e3, 100e3, 1e6, 10e6]), "s": _pick(r, [3, 4, 5])},
  text=lambda p: f"A submarine communicates at {p['f'] / 1e3:g} kHz through sea water (εr = 81, σ = {p['s']} S/m). By how many dB per metre is the signal attenuated?",
  solve=lambda p: _wave(p["f"], 81, 1, p["s"], "alpha_dB"))
q(id="c5-lambda", chapter="waves", level=1, ref="Ulaby §7-3", unit="cm", scale=100,
  gen=lambda r: {"f": _pick(r, [0.9e9, 2.45e9, 5.8e9, 10e9]), "er": _pick(r, [2.1, 2.55, 3.8, 4.4, 9.8])},
  text=lambda p: f"What is the wavelength of a {p['f'] / 1e9:g} GHz plane wave in a lossless dielectric with εr = {p['er']}?",
  solve=lambda p: _wave(p["f"], p["er"], 1, 0, "wavelength"))

# ---------------- Chapter 6
q(id="c6-normal-R", chapter="reflection", level=1, ref="Ulaby §8-1", unit="%", scale=100,
  gen=lambda r: {"er": _pick(r, [2.25, 4, 9, 16, 81])},
  text=lambda p: f"A plane wave in air is normally incident on a lossless dielectric half-space with εr = {p['er']}. What percentage of the incident power is reflected?",
  solve=lambda p: _rfn(p))
q(id="c6-brewster", chapter="reflection", level=1, ref="Ulaby §8-4", unit="°", abs_tol=0.1,
  gen=lambda r: {"er": _pick(r, [2.25, 2.56, 4, 6, 81])},
  text=lambda p: f"At what angle of incidence does a parallel-polarised wave in air pass into a non-magnetic dielectric (εr = {p['er']}) without reflection?",
  solve=lambda p: _rfo(1, p["er"], 10, "theta_B"))
q(id="c6-critical", chapter="reflection", level=1, ref="Ulaby §8-3", unit="°", abs_tol=0.1,
  gen=lambda r: {"er": _pick(r, [1.77, 2.25, 2.56, 3.4, 12])},
  text=lambda p: f"Light travels from a medium of εr = {p['er']} (n = {math.sqrt(p['er']):.3g}) toward air. Find the critical angle for total internal reflection.",
  solve=lambda p: _rfo(p["er"], 1, 10, "theta_c"))

# ---------------- Chapter 7
q(id="c7-vswr", chapter="tlines", level=1, ref="Ulaby §2-6", unit="",
  gen=lambda r: {"Z0": _pick(r, [50, 75]), "R": _i(r, 10, 200), "X": _pick(r, [-60, -25, 0, 30, 75])},
  text=lambda p: f"A {p['Z0']} Ω lossless line is terminated in Z_L = {p['R']} {'+' if p['X'] >= 0 else '−'} j{abs(p['X'])} Ω. Find the VSWR.",
  solve=lambda p: _tl(p, "S"))
q(id="c7-return-loss", chapter="tlines", level=1, ref="Ulaby §2-8", unit="dB",
  gen=lambda r: {"Z0": 50, "R": _pick(r, [25, 35, 70, 100, 150]), "X": _pick(r, [-20, 0, 15, 40])},
  text=lambda p: f"Find the return loss of a load Z_L = {p['R']} {'+' if p['X'] >= 0 else '−'} j{abs(p['X'])} Ω on a 50 Ω line.",
  solve=lambda p: _tl(p, "return_loss_dB"))
q(id="c7-qwt", chapter="tlines", level=2, ref="Ulaby §2-11", unit="Ω",
  gen=lambda r: {"Z0": _pick(r, [50, 75]), "R": _pick(r, [100, 150, 200, 300])},
  text=lambda p: f"A purely resistive load of {p['R']} Ω is to be matched to a {p['Z0']} Ω line with a quarter-wave transformer placed at the first voltage minimum. "
                 f"What characteristic impedance must the transformer have?",
  solve=lambda p: _tlq(p))

# ---------------- Chapter 8
q(id="c8-wg-cutoff", chapter="radiation", level=1, ref="Ulaby §8-10", unit="GHz", scale=1e-9,
  gen=lambda r: {"a": _pick(r, [22.86, 15.8, 34.85, 10.67]), "er": _pick(r, [1, 1, 2.1])},
  text=lambda p: f"A rectangular waveguide has a = {p['a']} mm, b = a/2, and is filled with εr = {p['er']}. Find the cut-off frequency of the dominant TE₁₀ mode.",
  solve=lambda p: _wg(p, 1.5 * C0 / (2 * p["a"] * 1e-3 * math.sqrt(p["er"])), "fc"))
q(id="c8-wg-lambdag", chapter="radiation", level=2, ref="Ulaby §8-10", unit="cm", scale=100,
  gen=lambda r: {"a": 22.86, "er": 1, "f": _pick(r, [8.2e9, 9e9, 10e9, 11e9, 12e9])},
  text=lambda p: f"Find the guide wavelength of the TE₁₀ mode in an air-filled WR-90 guide (a = 22.86 mm, b = 10.16 mm) at {p['f'] / 1e9:g} GHz.",
  solve=lambda p: _wg(p, p["f"], "lambda_g", b=10.16e-3))
q(id="c8-dipole-P", chapter="radiation", level=1, ref="Ulaby §9-3", unit="W",
  gen=lambda r: {"I": _u(r, 0.1, 3)},
  text=lambda p: f"A half-wave dipole is fed with a peak current of {p['I']} A. How much power does it radiate?",
  solve=lambda p: _dip(p))
q(id="c8-array-steer", chapter="radiation", level=2, ref="Ulaby §10-4", unit="°", abs_tol=0.2,
  gen=lambda r: {"N": _pick(r, [4, 8, 16]), "d": _pick(r, [0.25, 0.4, 0.5]), "dl": _pick(r, [-80, -60, -45, -30, 30, 45])},
  text=lambda p: f"A uniform linear array of {p['N']} elements spaced {p['d']}λ apart is fed with a progressive phase δ = {p['dl']}°. "
                 f"At what angle from the array axis does the main beam point?",
  solve=lambda p: _arr(p))


# ---------------- solver adapters → (engine result, SI answer, chapter action)
def _spread(p):
    f = 1e9
    r = dm.compare(f, r_max_lambda=5)
    k = dm._k(f, 1, 1, 0)[0]
    lam = 2 * math.pi / k.real
    r1 = 40 * lam   # far zone: Hankel asymptote error < 1e-3 dB
    lv = 20 * math.log10(abs(dm.psi(p["dim"], k, np.array(p["k"] * r1))) / abs(dm.psi(p["dim"], k, np.array(r1))))
    return r, lv, {"chapter": "dimensions", "params": {"f": f}}



def _coords(sysm, u, d, pick):
    ang = co.SYSTEMS[sysm]["angle"]
    r = co.element(sysm, [math.radians(x) if g else x for x, g in zip(u, ang)], [math.radians(x) if g else x for x, g in zip(d, ang)])
    return r, pick(r), {"chapter": "coordinates", "params": {"system": sysm, "u": u, "d": d}}


def _conv(p):
    r = co.convert("cartesian", "spherical", [p["x"], p["y"], p["z"]])
    return r, math.degrees(r["values"]["point"][1]), {"chapter": "coordinates", "params": {"system": "spherical"}}


def _charges(p):
    ch = [{"q": p["q1"] * 1e-9, "x": -p["d"] / 2, "y": 0.0}, {"q": p["q2"] * 1e-9, "x": p["d"] / 2, "y": 0.0}]
    r = es.point_charges(ch, False, (0.0, p["py"]))
    return r, r["values"]["E_mag"], {"chapter": "electrostatics", "params": {"tab": "charges", "charges": {
        "q": [[p["q1"], -p["d"] / 2, 0], [p["q2"], p["d"] / 2, 0]], "ground": False, "probe": [0, p["py"]]}}}


def _gauss(kind, rho, a, rr):
    r = es.gauss(kind, rho, a=a, r=rr)
    return r, r["values"]["E"], {"chapter": "electrostatics", "params": {"tab": "gauss", "gauss": {"kind": kind, "rho": rho, "a": a, "r": rr}}}


def _cap(kind, key, **kw):
    r = es.capacitor(kind, **kw)
    return r, r["values"][key], {"chapter": "electrostatics", "params": {"tab": "capacitor", "capacitor": {"kind": kind, **kw}}}


def _wires(p):
    W = [{"I": p["I1"], "x": -p["d"] / 2, "y": 0.0}, {"I": p["I2"], "x": p["d"] / 2, "y": 0.0}]
    r = ms.wires(W, (0.0, max(p["d"], 0.1)))
    F = math.hypot(*r["forces"][0])
    return r, F, {"chapter": "magnetostatics", "params": {"tab": "wires", "wires": {"W": [[w["I"], w["x"], w["y"]] for w in W], "probe": [0, max(p["d"], 0.1)]}}}


def _loop(p):
    r = ms.loops("loop", I=p["I"] * p["N"], a=p["a"])
    return r, r["values"]["B_center"], {"chapter": "magnetostatics", "params": {"tab": "loops", "loops": {"kind": "loop", "I": p["I"] * p["N"], "a": p["a"]}}}


def _toroid(p):
    b = _nice(p["a"] + p["w"], 3)
    rm = (p["a"] + b) / 2
    kw = {"kind": "toroid", "I": p["I"], "a": p["a"], "b": b, "N": p["N"], "mu_r": p["mur"], "r": rm}
    r = ms.ampere(**kw)
    return r, r["values"]["B"], {"chapter": "magnetostatics", "params": {"tab": "ampere", "ampere": kw}}


def _ind(p):
    kw = {"kind": "coax", "a": p["a"] * 1e-3, "b": _nice(p["a"] * p["ratio"], 3) * 1e-3, "length": 1.0}
    r = ms.inductance(**kw)
    return r, r["values"]["L"], {"chapter": "magnetostatics", "params": {"tab": "inductance", "inductance": kw}}


def _bc(p):
    kw = {"kind": "E", "eps1": p["e1"], "eps2": p["e2"], "F1": p["E"], "theta1_deg": p["th"]}
    r = mx.boundary(**kw)
    return r, r["values"]["theta2_deg"], {"chapter": "maxwell", "params": {"tab": "boundary", "boundary": kw}}


def _far(p):
    kw = {"mode": "motional", "B0": p["B"], "f": p["f"], "w": p["w"], "l": p["l"], "N": p["N"], "R": 1.0}
    r = mx.faraday(**kw)
    return r, r["values"]["V_peak"], {"chapter": "maxwell", "params": {"tab": "faraday", "faraday": kw}}


def _cur(p):
    kw = {"eps_r": p["er"], "sigma": p["s"], "f": 1e6}
    r = mx.currents(**kw)
    return r, r["values"]["fc"], {"chapter": "maxwell", "params": {"tab": "currents", "currents": kw}}


def _wave(f, er, mr, s, key):
    r = wv.solve(f, er, mr, s)
    return r, r["values"][key], {"chapter": "waves", "params": {"f": f, "eps_r": er, "mu_r": mr, "sigma": s}}


def _rfn(p):
    kw = {"f": 1e9, "eps2": p["er"]}
    r = rf.normal(**kw)
    return r, r["values"]["R"], {"chapter": "reflection", "params": {"tab": "normal", "normal": kw}}


def _rfo(e1, e2, th, key):
    kw = {"eps1": e1, "eps2": e2, "theta_deg": th}
    r = rf.oblique(**kw)
    return r, r["values"][key], {"chapter": "reflection", "params": {"tab": "oblique", "oblique": kw}}


def _tl(p, key):
    kw = {"Z0": p["Z0"], "RL": p["R"], "XL": p["X"]}
    r = tl.line(**kw)
    return r, r["values"][key], {"chapter": "tlines", "params": kw}


def _tlq(p):
    kw = {"Z0": p["Z0"], "RL": p["R"], "XL": 0}
    r = tl.line(**kw)
    return r, r["match"]["quarter_wave"]["Z_T"], {"chapter": "tlines", "params": kw}


def _wg(p, f, key, b=None):
    kw = {"a": p["a"] * 1e-3, "b": b if b else p["a"] * 1e-3 / 2, "eps_r": p["er"], "f": f, "mode": "TE", "m": 1, "n": 0}
    r = ra.waveguide(**kw)
    return r, r["values"][key], {"chapter": "radiation", "params": {"tab": "waveguide", "waveguide": kw}}


def _dip(p):
    kw = {"length_lambda": 0.5, "I0": p["I"]}
    r = ra.dipole(**kw)
    return r, r["values"]["P_rad"], {"chapter": "radiation", "params": {"tab": "dipole", "dipole": kw}}


def _arr(p):
    kw = {"N": p["N"], "d_lambda": p["d"], "delta_deg": p["dl"]}
    r = ra.array(**kw)
    return r, r["values"]["theta0"], {"chapter": "radiation", "params": {"tab": "array", "array": kw}}


# ---------------- public API
BY_ID = {t["id"]: t for t in T}


def catalog():
    return [{"id": t["id"], "chapter": t["chapter"], "level": t["level"], "ref": t["ref"]} for t in T]


def generate(qid=None, chapter=None, level=None, seed=None):
    rng0 = np.random.default_rng(seed)
    pool = [t for t in T if (chapter in (None, "", "all") or t["chapter"] == chapter) and (not level or t["level"] == int(level))]
    if qid:
        pool = [BY_ID[qid]] if qid in BY_ID else []
    if not pool:
        raise ValueError("no question matches the filter")
    t = pool[int(rng0.integers(0, len(pool)))]
    seed = int(rng0.integers(0, 2 ** 31 - 1)) if seed is None or not qid else int(seed)
    p = t["gen"](np.random.default_rng(seed))
    return {"id": t["id"], "seed": seed, "chapter": t["chapter"], "level": t["level"], "ref": t["ref"],
            "text": t["text"](p), "unit": t["unit"]}


def solve(qid, seed):
    t = BY_ID.get(qid)
    if t is None:
        raise ValueError("unknown question id")
    p = t["gen"](np.random.default_rng(int(seed)))
    r, ans, action = t["solve"](p)
    return t, r, ans * t["scale"], action


def check(qid, seed, answer=None):
    t, r, ans, action = solve(qid, seed)
    out = {"answer": ans, "unit": t["unit"], "verified": r["all_passed"], "steps": r["steps"], "checks": r["checks"], "action": action,
           "tolerance": t["abs_tol"] if t["abs_tol"] is not None else t["tol"],
           "tolerance_kind": "absolute" if t["abs_tol"] is not None else "relative"}
    if answer is not None:
        a = float(answer)
        if t["abs_tol"] is not None:
            ok = abs(a - ans) <= t["abs_tol"]
            out["error"] = abs(a - ans)
        else:
            out["error"] = abs(a - ans) / max(abs(ans), 1e-300)
            ok = out["error"] <= t["tol"]
        out["correct"] = bool(ok)
    return out
