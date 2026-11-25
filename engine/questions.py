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
from .explain import X, S, W, V as EV, P, render, invert


def _nice(x, sig=2):
    if x == 0:
        return 0.0
    return float(f"{x:.{sig}g}")


def _u(rng, lo, hi, sig=2, log=False):
    v = math.exp(rng.uniform(math.log(lo), math.log(hi))) if log else rng.uniform(lo, hi)
    return _nice(v, sig)


def _i(rng, lo, hi):
    return int(rng.integers(lo, hi + 1))


def _minus(x):
    """Given data as written, with a typographic minus."""
    return f"{x:g}".replace("-", "−")


def _pick(rng, xs):
    return xs[int(rng.integers(0, len(xs)))]


# Each template: id, chapter, level (1 basic … 3 harder), ref, unit, scale (SI → shown unit),
# gen(rng) → params, text(p) → str, solve(p) → (engine result, answer in SI, chapter action), tol
T = []


def q(**kw):
    kw.setdefault("tol", 0.01)
    kw.setdefault("abs_tol", None)
    kw.setdefault("scale", 1.0)
    kw.setdefault("x", None)      # written explanation (engine/explain.py)
    kw.setdefault("fig", None)    # p → figure spec showing the givens only
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

# ---------------- Chapter 4 (explained: engine/explain.py; vals take (engine result, template params))
_ifig = lambda e1, e2, th, H=False: {"type": "interface", "e1": e1, "e2": e2, "theta": th, "H": H}
q(id="c4-refraction", chapter="maxwell", level=2, ref="Ulaby §4-8", unit="°", abs_tol=0.2,
  gen=lambda r: {"e1": _pick(r, [1, 2, 3]), "e2": _pick(r, [4, 6, 9, 12]), "th": _i(r, 15, 75), "E": _i(r, 10, 200)},
  text=lambda p: f"A static field E₁ = {p['E']} V/m in medium 1 (εr = {p['e1']}) meets a charge-free planar boundary with medium 2 (εr = {p['e2']}) "
                 f"at θ₁ = {p['th']}° from the normal. Find the angle θ₂ of E₂ from the normal.",
  fig=lambda p: _ifig(p["e1"], p["e2"], p["th"]),
  solve=lambda p: _bc(p),
  x=X(asked="The angle θ₂ between E₂ and the normal to the boundary.",
      idea="Tangential E is continuous and, with no surface charge, normal D is continuous. "
           "Dividing one condition by the other removes the magnitudes and leaves a rule for the angles.",
      steps=[S("Tangential E is continuous.", r"E_2\sin\theta_2=E_1\sin\theta_1=«t»\ \text{V/m}"),
             S("Normal D is continuous, so the normal E scales by ε₁/ε₂.", r"\varepsilon_2E_2\cos\theta_2=\varepsilon_1E_1\cos\theta_1\ \Rightarrow\ E_2\cos\theta_2=«n»\ \text{V/m}"),
             S("Divide the first equation by the second; E₂ cancels.", r"\tan\theta_2=\frac{\varepsilon_{r2}}{\varepsilon_{r1}}\tan\theta_1\ \Rightarrow\ \theta_2=«th»^\circ")],
      answer="θ₂ = «th»°",
      whatif=[W("…|E₂| were asked?", lambda p: p, "Recombine the two components: |E₂| = «F» V/m.", r"|E_2|=\sqrt{E_{2t}^2+E_{2n}^2}=«F»\ \text{V/m}"),
              W("…the two media were swapped?", lambda p: {**p, "e1": p["e2"], "e2": p["e1"]},
                "Going into the lower permittivity, the field bends toward the normal: θ₂ = «th»°.", r"\tan\theta_2=\frac{\varepsilon_{r1}}{\varepsilon_{r2}}\tan\theta_1\ \Rightarrow\ \theta_2=«th»^\circ")],
      mistake="Using the optical Snell's law with √ε. That law is for waves; static fields refract by the tangent rule.",
      vals={"t": EV("F2", 0), "n": EV("F2", 1), "th": EV("theta2_deg"), "F": EV("F2_mag")}))
q(id="c4-h-refraction", chapter="maxwell", level=2, ref="Ulaby §5-6", unit="°", abs_tol=0.2,
  gen=lambda r: {"m2": _pick(r, [4, 10, 25, 80]), "th": _i(r, 10, 60), "H": _i(r, 1, 50)},
  text=lambda p: f"A magnetic field H₁ = {p['H']} A/m in air meets the flat surface of a magnetic material (μr = {p['m2']}) at θ₁ = {p['th']}° from the normal. "
                 f"No surface current flows. Find the angle θ₂ of H₂ from the normal inside the material.",
  fig=lambda p: _ifig(1, p["m2"], p["th"], True),
  solve=lambda p: _bch(p),
  x=X(asked="The angle θ₂ between H₂ and the normal, inside the magnetic material.",
      idea="With no surface current, tangential H and normal B = μH are continuous. Their ratio gives a tangent rule with μ in place of ε.",
      steps=[S("Tangential H is continuous.", r"H_2\sin\theta_2=H_1\sin\theta_1=«t»\ \text{A/m}"),
             S("Normal B is continuous, so the normal H drops by μr.", r"\mu_2H_2\cos\theta_2=\mu_1H_1\cos\theta_1\ \Rightarrow\ H_2\cos\theta_2=«n»\ \text{A/m}"),
             S("Divide; H₂ cancels.", r"\tan\theta_2=\frac{\mu_{r2}}{\mu_{r1}}\tan\theta_1\ \Rightarrow\ \theta_2=«th»^\circ")],
      answer="θ₂ = «th»°",
      whatif=[W("…|H₂| were asked?", lambda p: p, "|H₂| = «F» A/m.", r"|H_2|=\sqrt{H_{2t}^2+H_{2n}^2}=«F»\ \text{A/m}"),
              W("…the material had μr = 1000?", lambda p: {**p, "m2": 1000}, "H inside lies almost along the surface: θ₂ = «th»°.",
                r"\theta_2=\tan^{-1}(1000\tan\theta_1)=«th»^\circ")],
      mistake="Putting μ₁/μ₂ instead of μ₂/μ₁ in the tangent rule. The field bends away from the normal on entering higher μ.",
      vals={"t": EV("F2", 0), "n": EV("F2", 1), "th": EV("theta2_deg"), "F": EV("F2_mag")}))
q(id="c4-generator", chapter="maxwell", level=1, ref="Ulaby §6-5", unit="V",
  gen=lambda r: {"N": _pick(r, [10, 50, 100, 200]), "B": _u(r, 0.05, 1), "w": _u(r, 0.05, 0.3), "l": _u(r, 0.05, 0.3), "f": _pick(r, [50, 60, 120])},
  text=lambda p: f"A {p['w']} m × {p['l']} m coil of {p['N']} turns rotates at {p['f']} rev/s in a uniform B = {p['B']} T perpendicular to the rotation axis. "
                 f"Find the peak induced EMF.",
  fig=lambda p: {"type": "generator", "N": p["N"]},
  solve=lambda p: _far(p),
  x=X(asked="The amplitude V̂ of the EMF of a coil spinning in a static field.",
      idea="Turning the coil changes the flux through it, Φ = BA cos Ωt, and Faraday's law converts that change into an EMF.",
      steps=[S("Coil area and angular speed.", r"A=wl=«A»\ \text{m}^2,\qquad\Omega=2\pi f=«W»\ \text{rad/s}"),
             S("The EMF is the rate of change of the flux linkage.", r"V_{emf}=-\frac{d}{dt}\big(NBA\cos\Omega t\big)=NBA\Omega\sin\Omega t"),
             S("Its amplitude is the factor in front of the sine.", r"\hat V=NBA\Omega=«V»\ \text{V}")],
      answer="V̂ = «V» V",
      whatif=[W("…the coil spun twice as fast?", lambda p: {**p, "f": 2 * p["f"]}, "V̂ ∝ Ω, so it doubles to «V» V.", r"\hat V=NBA\Omega=«V»\ \text{V}"),
              W("…the field were halved?", lambda p: {**p, "B": p["B"] / 2}, "V̂ ∝ B, so it halves to «V» V.", r"\hat V=«V»\ \text{V}")],
      mistake="Forgetting the factor 2π between rev/s and rad/s.",
      vals={"A": EV("A"), "W": EV("omega"), "V": EV("V_peak")}))
q(id="c4-crossover", chapter="maxwell", level=1, ref="Ulaby §6-7", unit="MHz", scale=1e-6,
  gen=lambda r: {"er": _pick(r, [5, 10, 25, 81]), "s": _u(r, 1e-3, 5, log=True)},
  text=lambda p: f"For a medium with εr = {p['er']} and σ = {p['s']} S/m, at what frequency do conduction and displacement current densities have equal magnitude?",
  fig=lambda p: {"type": "medium", "label": f"εr = {p['er']}, σ = {p['s']} S/m"},
  solve=lambda p: _cur(p),
  x=X(asked="The frequency f_c at which |J_c| = |J_d|.",
      idea="In ∇×H = σE + jωεE the conduction term is fixed and the displacement term grows with frequency; they are equal where σ = ωε.",
      steps=[S("Ratio of the two current densities.", r"\frac{|J_c|}{|J_d|}=\frac{\sigma}{\omega\varepsilon}"),
             S("Set it to 1 and solve for f.", r"f_c=\frac{\sigma}{2\pi\varepsilon_0\varepsilon_r}=«fc»\ \text{MHz}")],
      answer="f_c = «fc» MHz",
      whatif=[W("…σ were ten times larger?", lambda p: {**p, "s": 10 * p["s"]}, "f_c ∝ σ, so it rises to «fc» MHz.", r"f_c=«fc»\ \text{MHz}"),
              W("…the ratio |J_c|/|J_d| at 1 MHz were asked?", lambda p: p, "|J_c|/|J_d| = «ratio».", r"\frac{\sigma}{2\pi(10^6)\varepsilon}=«ratio»")],
      mistake="Using f instead of ω = 2πf in σ = ωε.",
      vals={"fc": lambda r, p: r["values"]["fc"] / 1e6, "ratio": EV("ratio")}))
q(id="c4-ratio-freq", chapter="maxwell", level=2, ref="Ulaby §6-7", unit="MHz", scale=1e-6,
  gen=lambda r: {"er": _pick(r, [5, 10, 25, 81]), "s": _u(r, 1e-3, 5, log=True), "k": _pick(r, [0.1, 10, 100])},
  text=lambda p: f"A medium has εr = {p['er']} and σ = {p['s']} S/m. At what frequency is the conduction current density exactly {p['k']:g} times "
                 f"the displacement current density?",
  fig=lambda p: {"type": "medium", "label": f"εr = {p['er']}, σ = {p['s']} S/m"},
  solve=lambda p: _ratio_f(p),
  x=X(asked="The frequency at which |J_c|/|J_d| equals «k».",
      idea="The ratio σ/ωε falls as 1/f, so each value of the ratio belongs to exactly one frequency.",
      steps=[S("Write the ratio as a function of f.", r"\frac{|J_c|}{|J_d|}=\frac{\sigma}{2\pi f\varepsilon}"),
             S("Set it equal to the target and solve for f.", r"f=\frac{\sigma}{2\pi\varepsilon_0\varepsilon_r\,k}=«f»\ \text{MHz}"),
             S("Check: at that frequency the engine's own model gives a ratio of «ratio».")],
      answer="f = «f» MHz",
      whatif=[W("…the two currents were to be equal (k = 1)?", lambda p: {**p, "k": 1}, "That is the crossover frequency, f_c = «f» MHz.", r"f_c=\frac{\sigma}{2\pi\varepsilon}=«f»\ \text{MHz}"),
              W("…the ratio were to be ten times larger?", lambda p: {**p, "k": 10 * p["k"]}, "f ∝ 1/k, so f drops by ten to «f» MHz.", r"f=«f»\ \text{MHz}")],
      mistake="Inverting the ratio: a larger conduction-to-displacement ratio means a lower frequency, not a higher one.",
      vals={"k": P("k"), "f": lambda r, p: r["values"]["f"] / 1e6, "ratio": EV("ratio")}))
q(id="c4-rhos", chapter="maxwell", level=3, ref="Ulaby §4-8", unit="nC/m²", scale=1e9,
  gen=lambda r: _rhos_gen(r),
  text=lambda p: f"Medium 1 (εr = {p['e1']}) lies above medium 2 (εr = {p['e2']}). Just above the flat interface E₁ = {p['E']} V/m, pointing away from it at "
                 f"{p['th']}° from the normal. A probe just below the interface measures the normal component E₂n = {_minus(p['E2n'])} V/m "
                 f"(positive = pointing from medium 2 toward medium 1). What free surface charge density ρs is on the interface?",
  fig=lambda p: _ifig(p["e1"], p["e2"], p["th"]),
  solve=lambda p: _rhos(p),
  x=X(asked="The free surface charge ρs implied by the field measured on both sides of the interface.",
      idea="Gauss's law on a thin pill-box: the normal component of D jumps by exactly the free surface charge, D₁n − D₂n = ρs, "
           "with the normal pointing from medium 2 into medium 1.",
      steps=[S("Normal D just above the interface.", r"D_{1n}=\varepsilon_0\varepsilon_{r1}E_1\cos\theta_1=«D1»\ \text{nC/m}^2"),
             S("Normal D just below, from the measured E₂n.", r"D_{2n}=\varepsilon_0\varepsilon_{r2}E_{2n}=«D2»\ \text{nC/m}^2"),
             S("The difference is the surface charge.", r"\rho_s=D_{1n}-D_{2n}=«rs»\ \text{nC/m}^2"),
             S("The engine also solves the forward problem for ρs by root finding and confirms it reproduces the measured E₂n.")],
      answer="ρs = «rs» nC/m²",
      whatif=[W("…the tangential field below the interface were asked?", lambda p: p, "ρs does not affect it: E₂t = E₁t = «t» V/m.", r"E_{2t}=E_1\sin\theta_1=«t»\ \text{V/m}"),
              W("…|E₂| and its angle were asked?", lambda p: p, "|E₂| = «F» V/m at θ₂ = «th2»° from the normal.", r"|E_2|=\sqrt{E_{2t}^2+E_{2n}^2}=«F»\ \text{V/m}")],
      mistake="Using ε₀ on both sides, or dropping the sign of E₂n. D, not E, carries the jump.",
      vals={"D1": lambda r, p: r["values"]["flux"][0] * 1e9, "D2": lambda r, p: r["values"]["flux"][1] * 1e9, "rs": lambda r, p: r["values"]["source"] * 1e9, "t": EV("F2", 0), "F": EV("F2_mag"), "th2": EV("theta2_deg")}))
q(id="c4-slab", chapter="maxwell", level=3, ref="Ulaby §4-8", unit="°", abs_tol=0.2,
  gen=lambda r: {"e2": _pick(r, [2, 4, 10]), "e3": _pick(r, [3, 6, 9]), "th": _i(r, 10, 50), "E": _i(r, 50, 500)},
  text=lambda p: f"A static field E₁ = {p['E']} V/m in air makes θ₁ = {p['th']}° with the normal of a flat dielectric slab (εr = {p['e2']}) with parallel faces. "
                 f"Below the slab lies a third medium with εr = {p['e3']}. No surface charge is present. Find the angle θ₃ between E and the normal in the third medium.",
  fig=lambda p: {"type": "slab3", "e1": 1, "e2": p["e2"], "e3": p["e3"], "theta": p["th"]},
  solve=lambda p: _slab(p),
  x=X(asked="The direction of E after it has crossed two parallel boundaries.",
      idea="Apply the tangent rule tan θ_out = (ε_out/ε_in) tan θ_in at each face. Because the faces are parallel, the angle leaving the first face is the angle arriving at the second.",
      steps=[S("First face (air → slab).", r"\tan\theta_2=\varepsilon_{r2}\tan\theta_1\ \Rightarrow\ \theta_2=«thm»^\circ"),
             S("Second face (slab → third medium).", r"\tan\theta_3=\frac{\varepsilon_{r3}}{\varepsilon_{r2}}\tan\theta_2\ \Rightarrow\ \theta_3=«th3»^\circ"),
             S("Multiply the two rules: εr₂ cancels, so the slab does not change the final direction.", r"\tan\theta_3=\frac{\varepsilon_{r3}}{\varepsilon_{r1}}\tan\theta_1")],
      answer="θ₃ = «th3»°",
      whatif=[W("…the slab had εr = 50?", lambda p: {**p, "e2": 50}, "Inside the slab the field turns to «thm»°, but θ₃ is still «th3»°.", r"\theta_3=«th3»^\circ"),
              W("…|E| in the third medium were asked?", lambda p: p, "E_t is the same in all three media and D_n too, so |E₃| = «F» V/m, also independent of the slab.",
                r"|E_3|=\sqrt{E_{1t}^2+\big(\tfrac{\varepsilon_1}{\varepsilon_3}E_{1n}\big)^2}=«F»\ \text{V/m}")],
      mistake="Expecting the slab to change the field beyond it. E_t and D_n both pass straight through, so only the outer media matter.",
      vals={"thm": EV("theta_mid"), "th3": EV("theta2_deg"), "F": EV("F2_mag")}))
q(id="c4-gen-speed", chapter="maxwell", level=3, ref="Ulaby §6-5", unit="rev/s",
  gen=lambda r: _speed_gen(r),
  text=lambda p: f"A {p['N']}-turn coil of {p['w']} m × {p['l']} m rotates in a uniform field B = {p['B']} T about an axis perpendicular to B. "
                 f"How many revolutions per second are needed for a peak EMF of {p['V']:g} V?",
  fig=lambda p: {"type": "generator", "N": p["N"]},
  solve=lambda p: _speed(p),
  x=X(asked="The rotation rate f (rev/s) that gives the required peak EMF.",
      idea="The peak EMF of a rotating coil is V̂ = NBAΩ with Ω = 2πf, so the required speed follows by solving for f.",
      steps=[S("Peak EMF of a coil rotating in a static field.", r"\hat V=NBA\,2\pi f,\qquad A=wl=«A»\ \text{m}^2"),
             S("Solve for f.", r"f=\frac{\hat V}{2\pi NBA}=«f»\ \text{rev/s}"),
             S("Check: the engine's generator model at this speed gives V̂ = «V» V.")],
      answer="f = «f» rev/s",
      whatif=[W("…the field were twice as strong?", lambda p: {**p, "B": 2 * p["B"]}, "f ∝ 1/B, so half the speed is enough: f = «f» rev/s.", r"f=«f»\ \text{rev/s}"),
              W("…the angular speed Ω were asked?", lambda p: p, "Ω = 2πf = «W» rad/s.", r"\Omega=2\pi f=«W»\ \text{rad/s}")],
      mistake="Giving Ω in rad/s when the question asks for revolutions per second.",
      vals={"A": EV("A"), "f": EV("f"), "V": EV("V_peak"), "W": EV("omega")}))

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


def _bch(p):
    kw = {"kind": "H", "mu1": 1, "mu2": p["m2"], "F1": p["H"], "theta1_deg": p["th"]}
    r = mx.boundary(**kw)
    return r, r["values"]["theta2_deg"], {"chapter": "maxwell", "params": {"tab": "boundary", "boundary": kw}}


def _with(r, **vals):
    return {**r, "values": {**r["values"], **vals}}


def _ratio_f(p):
    r, f = invert(mx.currents, {"eps_r": p["er"], "sigma": p["s"]}, "f", "ratio", p["k"], 1e-3, 1e18, log=True)
    kw = {"eps_r": p["er"], "sigma": p["s"], "f": f}
    return _with(r, f=f), f, {"chapter": "maxwell", "params": {"tab": "currents", "currents": kw}}


def _rhos_gen(rng):
    p = {"e1": _pick(rng, [1, 2]), "e2": _pick(rng, [3, 5, 9]), "E": _i(rng, 200, 2000), "th": _i(rng, 10, 60)}
    rs = _pick(rng, [-3, -1, 1, 2, 4]) * 1e-9
    fwd = mx.boundary(kind="E", eps1=p["e1"], eps2=p["e2"], F1=p["E"], theta1_deg=p["th"], source=rs)
    return {**p, "E2n": _nice(fwd["values"]["F2"][1], 4)}


def _rhos(p):
    kw = {"kind": "E", "eps1": p["e1"], "eps2": p["e2"], "F1": p["E"], "theta1_deg": p["th"]}
    r, rs = invert(mx.boundary, kw, "source", lambda r: r["values"]["F2"][1], p["E2n"], -1e-6, 1e-6)
    return r, rs, {"chapter": "maxwell", "params": {"tab": "boundary", "boundary": {**kw, "source": rs}}}


def _slab(p):
    k1 = {"kind": "E", "eps1": 1, "eps2": p["e2"], "F1": p["E"], "theta1_deg": p["th"]}
    r1 = mx.boundary(**k1)
    r2 = mx.boundary(kind="E", eps1=p["e2"], eps2=p["e3"], F1=r1["values"]["F2_mag"], theta1_deg=r1["values"]["theta2_deg"])
    r = {**r2, "values": {**r2["values"], "theta_mid": r1["values"]["theta2_deg"]},
         "steps": [{**s, "label": f"Face 1: {s['label']}"} for s in r1["steps"]] + [{**s, "label": f"Face 2: {s['label']}"} for s in r2["steps"]],
         "checks": [{**c, "label": f"Face 1: {c['label']}"} for c in r1["checks"]] + [{**c, "label": f"Face 2: {c['label']}"} for c in r2["checks"]],
         "all_passed": r1["all_passed"] and r2["all_passed"]}
    return r, r2["values"]["theta2_deg"], {"chapter": "maxwell", "params": {"tab": "boundary", "boundary": k1}}


def _speed_gen(rng):
    p = {"N": _pick(rng, [10, 50, 100, 200]), "B": _u(rng, 0.05, 1), "w": _u(rng, 0.05, 0.3), "l": _u(rng, 0.05, 0.3)}
    f = _pick(rng, [10, 25, 50, 60, 100])
    fwd = mx.faraday(mode="motional", N=p["N"], B0=p["B"], w=p["w"], l=p["l"], f=f)
    return {**p, "V": _nice(fwd["values"]["V_peak"], 3)}


def _speed(p):
    kw = {"mode": "motional", "N": p["N"], "B0": p["B"], "w": p["w"], "l": p["l"]}
    r, f = invert(mx.faraday, kw, "f", "V_peak", p["V"], 1e-3, 1e6, log=True)
    return _with(r, f=f), f, {"chapter": "maxwell", "params": {"tab": "faraday", "faraday": {**kw, "f": f, "R": 1.0}}}


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
            "text": t["text"](p), "unit": t["unit"], "fig": t["fig"](p) if t["fig"] else None}


def solve(qid, seed):
    t = BY_ID.get(qid)
    if t is None:
        raise ValueError("unknown question id")
    p = t["gen"](np.random.default_rng(int(seed)))
    r, ans, action = t["solve"](p)
    return t, r, ans * t["scale"], action, p


def check(qid, seed, answer=None):
    t, r, ans, action, p = solve(qid, seed)
    out = {"answer": ans, "unit": t["unit"], "verified": r["all_passed"], "steps": r["steps"], "checks": r["checks"], "action": action,
           "tolerance": t["abs_tol"] if t["abs_tol"] is not None else t["tol"],
           "tolerance_kind": "absolute" if t["abs_tol"] is not None else "relative",
           "explain": render(t["x"], lambda q: t["solve"](q)[0], p, r) if t["x"] else None}
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
