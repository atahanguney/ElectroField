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


# ---------------- written explanations for chapters 0–3 and 5–8 (Maxwell's are inline above)
_c = lambda k: (lambda r, p: r["values"][k]["re"])      # real part of a complex engine value
_EXPL = {
    "c0-spread": X(
        asked="The change of the field level, in dB, when the far-zone distance is multiplied by «k».",
        idea="Energy conservation fixes how a wave thins out. A spherical wave spreads its power over 4πR², so |E| ∝ 1/R; "
             "a cylindrical wave spreads it over 2πρℓ, so |E| ∝ 1/√ρ.",
        steps=[S("Write the ratio of the field amplitudes for the two distances.", r"\frac{|E(k r)|}{|E(r)|}=\begin{cases}1/\sqrt{k} & \text{cylindrical (line source)}\\ 1/k & \text{spherical (point source)}\end{cases}"),
               S("Convert the amplitude ratio to decibels with 20 log₁₀.", r"\Delta L=20\log_{10}\frac{|E(kr)|}{|E(r)|}=«dl»\ \text{dB}"),
               S("The power density ratio is the square of this, and 10 log₁₀ of it gives the same number of decibels.")],
        answer="ΔL = «dl» dB",
        whatif=[W("…the other kind of source were used?", lambda p: {**p, "dim": "3D" if p["dim"] == "2D" else "2D"}, "Switching between cylindrical and spherical spreading gives ΔL = «dl» dB.", r"\Delta L=«dl»\ \text{dB}"),
                W("…the distance were only doubled?", lambda p: {**p, "k": 2}, "ΔL = «dl» dB.", r"\Delta L=«dl»\ \text{dB}")],
        mistake="Using 20 log₁₀ on a power ratio or 10 log₁₀ on a field ratio, which doubles or halves the answer.",
        vals={"k": P("k"), "dl": EV("dlevel")}),
    "c1-sph-dv": X(
        asked="The volume dv of a small spherical element.",
        idea="In spherical coordinates the edges of a small box are dR, R dθ and R sin θ dφ: each angle step must be multiplied by its scale factor to become a length.",
        steps=[S("Convert the angle steps to radians and multiply by the scale factors to get the three edge lengths.",
                 r"dl_R=dR=«l1»,\quad dl_\theta=R\,d\theta=«l2»,\quad dl_\phi=R\sin\theta\,d\phi=«l3}\ \text{m}".replace("«l3}", "«l3»")),
               S("Multiply the three edges.", r"dv=R^2\sin\theta\,dR\,d\theta\,d\phi=«dv»\ \text{cm}^3"),
               S("The exact volume of the finite wedge is «ex» cm³, close to dv because the steps are small.")],
        answer="dv = «dv» cm³",
        whatif=[W("…the point were on the equator (θ = 90°)?", lambda p: {**p, "th": 90}, "There sin θ = 1, so the same steps enclose the most volume: dv = «dv» cm³.", r"dv=R^2\,dR\,d\theta\,d\phi=«dv»\ \text{cm}^3"),
                W("…dφ were doubled?", lambda p: {**p, "dph": 2 * p["dph"]}, "dv is proportional to each step, so it doubles to «dv» cm³.", r"dv=«dv»\ \text{cm}^3")],
        mistake="Leaving dθ and dφ in degrees, or dropping sin θ from the φ edge.",
        vals={"l1": EV("dl", 0), "l2": EV("dl", 1), "l3": EV("dl", 2), "dv": lambda r, p: r["values"]["dv"] * 1e6, "ex": lambda r, p: r["values"]["exact_finite_volume"] * 1e6}),
    "c1-cyl-ds": X(
        asked="The area ds_r of a patch on the surface r = constant.",
        idea="On a cylinder the patch has one curved edge of length r dφ and one straight edge dz.",
        steps=[S("Arc length along φ, with the angle in radians.", r"dl_\phi=r\,d\phi=«l2»\ \text{m}"),
               S("Straight length along z.", r"dl_z=dz=«l3»\ \text{m}"),
               S("Multiply the two edges.", r"ds_r=r\,d\phi\,dz=«ds»\ \text{cm}^2")],
        answer="ds_r = «ds» cm²",
        whatif=[W("…the cylinder had twice the radius?", lambda p: {**p, "r": 2 * p["r"]}, "The arc doubles, so the area doubles: ds_r = «ds» cm².", r"ds_r=«ds»\ \text{cm}^2"),
                W("…the patch lay on a plane z = constant, with a radial step dr = 1 cm?", lambda p: p, "Then the edges are dr and r dφ: ds_z = «dsz» cm².", r"ds_z=r\,dr\,d\phi=«dsz»\ \text{cm}^2")],
        mistake="Using dφ in degrees, or multiplying by r twice.",
        vals={"l2": EV("dl", 1), "l3": EV("dl", 2), "ds": lambda r, p: r["values"]["ds"][0] * 1e4, "dsz": lambda r, p: r["values"]["ds"][2] * 1e4}),
    "c1-conv-theta": X(
        asked="The polar angle θ of P, measured down from the +z axis.",
        idea="R is the distance from the origin and θ is the angle between OP and the +z axis, so cos θ = z/R. θ always lies between 0° and 180°.",
        steps=[S("Distance from the origin.", r"R=\sqrt{x^2+y^2+z^2}=«R»\ \text{m}"),
               S("Polar angle from cos θ = z/R.", r"\theta=\cos^{-1}\frac{z}{R}=«th»^\circ"),
               S("A negative z gives θ above 90°, meaning the point lies below the xy-plane.")],
        answer="θ = «th»°",
        whatif=[W("…the azimuth φ were asked?", lambda p: p, "φ is the angle of the projection on the xy-plane: φ = «ph»°.", r"\phi=\operatorname{atan2}(y,x)=«ph»^\circ"),
                W("…the point were mirrored to −z?", lambda p: {**p, "z": -p["z"]}, "θ becomes its supplement: θ = «th»°.", r"\theta'=180^\circ-\theta=«th»^\circ")],
        mistake="Using tan⁻¹(z/x), or measuring the angle from the xy-plane (that is the elevation, 90° − θ).",
        vals={"R": EV("point", 0), "th": lambda r, p: math.degrees(r["values"]["point"][1]), "ph": lambda r, p: math.degrees(r["values"]["point"][2])}),
    "c2-two-charges": X(
        asked="The magnitude of E at the probe point produced by both charges.",
        idea="Electric fields add as vectors. Find each charge's Coulomb field at the probe, add the x and y components, then take the magnitude.",
        steps=[S("Each field points away from a positive charge and toward a negative one.", r"\mathbf E_i=\frac{q_i}{4\pi\varepsilon_0}\frac{\mathbf R-\mathbf R_i}{|\mathbf R-\mathbf R_i|^3}"),
               S("Add the components of the two fields.", r"E_x=«ex»\ \text{V/m},\qquad E_y=«ey»\ \text{V/m}"),
               S("Take the magnitude.", r"|\mathbf E|=\sqrt{E_x^2+E_y^2}=«E»\ \text{V/m}")],
        answer="|E| = «E» V/m",
        whatif=[W("…the potential at the same point were asked?", lambda p: p, "Potentials add as plain numbers, with sign: V = «V» V.", r"V=\sum_i\frac{q_i}{4\pi\varepsilon_0R_i}=«V»\ \text{V}"),
                W("…q₂ had the opposite sign?", lambda p: {**p, "q2": -p["q2"]}, "The second field reverses, so the components combine differently: |E| = «E» V/m.", r"|\mathbf E|=«E»\ \text{V/m}")],
        mistake="Adding the magnitudes of the two fields instead of their components.",
        vals={"ex": EV("E", 0), "ey": EV("E", 1), "E": EV("E_mag"), "V": EV("V")}),
    "c2-gauss-sphere": X(
        asked="|E| at the given distance from the centre of a uniformly charged sphere.",
        idea="Spherical symmetry lets Gauss's law be applied to a concentric sphere through the point: D is radial and has the same size everywhere on it, and only the charge inside counts.",
        steps=[S("Charge enclosed by the Gaussian sphere (all of it if R > a, only the inner part if R < a).", r"Q_{enc}=«Q»\ \text{C}"),
               S("Gauss's law with D constant on the surface.", r"D\cdot4\pi R^2=Q_{enc}\ \Rightarrow\ D=«D»\ \text{C/m}^2"),
               S("Free space, so divide by ε₀.", r"E=\frac{D}{\varepsilon_0}=«E»\ \text{V/m}")],
        answer="|E| = «E» V/m",
        whatif=[W("…the point were at twice the radius?", lambda p: {**p, "f": 2}, "Outside, the sphere acts like a point charge: E = «E» V/m.", r"E=\frac{\rho_va^3}{3\varepsilon_0R^2}=«E»\ \text{V/m}"),
                W("…the point were on the surface?", lambda p: {**p, "f": 1}, "Inside and outside formulas meet here, where E is largest: E = «E» V/m.", r"E=\frac{\rho_va}{3\varepsilon_0}=«E»\ \text{V/m}")],
        mistake="Using the total charge when R < a. Inside the sphere only the charge within R contributes, so E grows linearly with R.",
        vals={"Q": EV("Q_enc"), "D": EV("D"), "E": EV("E")}),
    "c2-coax-C": X(
        asked="The capacitance per metre of a coaxial line.",
        idea="Put a charge ρℓ per metre on the inner conductor, find E with Gauss's law, integrate E across the gap to get V, and divide.",
        steps=[S("Gauss's law on a cylinder of radius r between the conductors.", r"E=\frac{\rho_\ell}{2\pi\varepsilon r}"),
               S("Integrate from the inner to the outer conductor.", r"V=\int_a^b E\,dr=\frac{\rho_\ell}{2\pi\varepsilon}\ln\frac{b}{a}"),
               S("Capacitance per unit length.", r"C'=\frac{\rho_\ell}{V}=\frac{2\pi\varepsilon}{\ln(b/a)}=«C»\ \text{pF/m}")],
        answer="C′ = «C» pF/m",
        whatif=[W("…the dielectric had twice the permittivity?", lambda p: {**p, "er": 2 * p["er"]}, "C′ is proportional to ε: «C» pF/m.", r"C'=«C»\ \text{pF/m}"),
                W("…b/a were doubled?", lambda p: {**p, "ratio": 2 * p["ratio"]}, "C′ falls only logarithmically with the ratio: «C» pF/m.", r"C'=\frac{2\pi\varepsilon}{\ln(2b/a)}=«C»\ \text{pF/m}")],
        mistake="Using ln(a/b), which is negative, or log₁₀ instead of the natural logarithm.",
        vals={"C": lambda r, p: r["values"]["C"] * 1e12}),
    "c2-plate-bd": X(
        asked="The largest voltage the capacitor can hold before its dielectric breaks down.",
        idea="Neglecting fringing, the field between the plates is uniform, E = V/d. Breakdown starts when E reaches the dielectric strength.",
        steps=[S("Uniform field in the gap.", r"E=\frac{V}{d}"),
               S("Set E equal to the dielectric strength.", r"V_{bd}=E_{bd}\,d=«V»\ \text{kV}"),
               S("εr does not enter: it changes how much charge is stored at a given voltage, not the field.")],
        answer="V_bd = «V» kV",
        whatif=[W("…the gap were halved?", lambda p: {**p, "d": p["d"] / 2}, "V_bd ∝ d, so it halves to «V» kV.", r"V_{bd}=«V»\ \text{kV}"),
                W("…air (3 MV/m) filled the gap instead?", lambda p: {**p, "er": 1, "Ebd": 3}, "Air breaks down at a much lower field: V_bd = «V» kV.", r"V_{bd}=3\times10^6\,d=«V»\ \text{kV}")],
        mistake="Thinking a higher εr raises the breakdown voltage. With a single dielectric only its strength and the gap matter.",
        vals={"V": lambda r, p: r["values"]["V_bd"] / 1e3}),
    "c3-wire-force": X(
        asked="The force per unit length between two long parallel wires.",
        idea="Each wire sits in the field of the other, B = μ₀I/(2πd), and a current in a field feels F′ = I × B per metre. Parallel currents attract; opposite currents repel.",
        steps=[S("Field of wire 1 at the position of wire 2.", r"B_1=\frac{\mu_0I_1}{2\pi d}"),
               S("Force per metre on wire 2.", r"F'=I_2B_1=\frac{\mu_0I_1I_2}{2\pi d}=«F»\ \mu\text{N/m}"),
               S("Same-sign currents attract and opposite signs repel; the magnitude is the same either way.")],
        answer="F′ = «F» µN/m",
        whatif=[W("…the wires were twice as far apart?", lambda p: {**p, "d": 2 * p["d"]}, "F′ ∝ 1/d, so it halves to «F» µN/m.", r"F'=«F»\ \mu\text{N/m}"),
                W("…the second current were reversed?", lambda p: {**p, "I2": -p["I2"]}, "The magnitude is unchanged, «F» µN/m, but attraction becomes repulsion or vice versa.", r"|F'|=«F»\ \mu\text{N/m}")],
        mistake="Using 1/d², as for point charges. Infinite line currents give fields and forces that fall off as 1/d.",
        vals={"F": lambda r, p: math.hypot(*r["forces"][0]) * 1e6}),
    "c3-loop-centre": X(
        asked="The magnetic flux density at the centre of a flat circular coil.",
        idea="Every element of the loop is the same distance a from the centre and perpendicular to the line joining them, so all Biot–Savart contributions point the same way along the axis.",
        steps=[S("Biot–Savart for one element at distance a.", r"dB=\frac{\mu_0I\,dl}{4\pi a^2}"),
               S("Integrate over the circumference 2πa and multiply by the number of turns.", r"B=\frac{\mu_0NI}{2a}=«B»\ \mu\text{T}")],
        answer="B = «B» µT",
        whatif=[W("…the radius were doubled?", lambda p: {**p, "a": 2 * p["a"]}, "B ∝ 1/a, so it halves to «B» µT.", r"B=«B»\ \mu\text{T}"),
                W("…the coil had twice as many turns?", lambda p: {**p, "N": 2 * p["N"]}, "Each turn adds the same field: B = «B» µT.", r"B=«B»\ \mu\text{T}")],
        mistake="Using the straight-wire formula μ₀I/(2πa). At the centre of a loop it is μ₀I/(2a), larger by π.",
        vals={"B": lambda r, p: r["values"]["B_center"] * 1e6}),
    "c3-toroid": X(
        asked="B inside the core of a toroid at its mean radius.",
        idea="By symmetry H runs around the toroid and has the same size on any circle inside the core. Such a circle links the full current NI.",
        steps=[S("Mean radius of the core.", r"r=\frac{a+b}{2}=«r»\ \text{m}"),
               S("Ampère's law on the circle of radius r.", r"H\cdot2\pi r=NI\ \Rightarrow\ H=«H»\ \text{A/m}"),
               S("Multiply by the core permeability.", r"B=\mu_0\mu_rH=«B»\ \text{mT}")],
        answer="B = «B» mT",
        whatif=[W("…the core were air (μr = 1)?", lambda p: {**p, "mur": 1}, "H is unchanged; B drops to «B» mT.", r"B=\mu_0H=«B»\ \text{mT}"),
                W("…H were asked instead?", lambda p: p, "H depends only on N, I and r, not on the core: H = «H» A/m.", r"H=\frac{NI}{2\pi r}=«H»\ \text{A/m}")],
        mistake="Treating B as uniform across the core. It falls as 1/r from the inner to the outer radius.",
        vals={"r": lambda r, p: (p["a"] + _nice(p["a"] + p["w"], 3)) / 2, "H": EV("H"), "B": lambda r, p: r["values"]["B"] * 1e3}),
    "c3-coax-L": X(
        asked="The external inductance per metre of a coaxial line.",
        idea="Between the conductors H = I/(2πr). The flux through a 1 m strip from a to b, divided by the current, is the inductance per metre.",
        steps=[S("Field between the conductors.", r"B=\frac{\mu_0I}{2\pi r}"),
               S("Flux through a strip of unit length.", r"\Phi'=\int_a^b\frac{\mu_0I}{2\pi r}\,dr=\frac{\mu_0I}{2\pi}\ln\frac{b}{a}"),
               S("Divide by I.", r"L'=\frac{\mu_0}{2\pi}\ln\frac{b}{a}=«L»\ \text{nH/m}")],
        answer="L′ = «L» nH/m",
        whatif=[W("…b/a were doubled?", lambda p: {**p, "ratio": 2 * p["ratio"]}, "L′ grows only logarithmically: «L» nH/m.", r"L'=«L»\ \text{nH/m}"),
                W("…the magnetic energy per metre at 1 A were asked?", lambda p: p, "W′ = ½L′I² = «W» nJ/m.", r"W'=\tfrac12L'I^2=«W»\ \text{nJ/m}")],
        mistake="Swapping a and b, or adding the inner conductor's internal inductance when only the external part is asked.",
        vals={"L": lambda r, p: r["values"]["L"] * 1e9, "W": lambda r, p: r["values"]["W"] * 1e9}),
    "c5-skin": X(
        asked="The skin depth δs of the metal at the given frequency.",
        idea="In a good conductor (σ ≫ ωε) the wave decays as e^(−αz) with α = √(πfμσ). The skin depth is the distance over which the amplitude falls to 1/e.",
        steps=[S("Check the regime: the loss tangent is enormous, so the good-conductor formulas apply.", r"\frac{\sigma}{\omega\varepsilon}=«lt»"),
               S("Attenuation constant.", r"\alpha=\sqrt{\pi f\mu\sigma}=«a»\ \text{Np/m}"),
               S("Skin depth.", r"\delta_s=\frac1\alpha=«d»\ \mu\text{m}")],
        answer="δs = «d» µm",
        whatif=[W("…the frequency were 100 times higher?", lambda p: {**p, "f": 100 * p["f"]}, "δs ∝ 1/√f, so it becomes ten times smaller: «d» µm.", r"\delta_s=«d»\ \mu\text{m}"),
                W("…the metal were copper (5.8 × 10⁷ S/m)?", lambda p: {**p, "m": ("copper", 5.8e7)}, "δs = «d» µm.", r"\delta_s=\frac{1}{\sqrt{\pi f\mu_0\sigma}}=«d»\ \mu\text{m}")],
        mistake="Expecting δs to scale as 1/f. It scales as 1/√f.",
        vals={"lt": EV("loss_tangent"), "a": EV("alpha"), "d": lambda r, p: r["values"]["skin_depth"] * 1e6}),
    "c5-seawater": X(
        asked="The attenuation of the field in sea water, in decibels per metre.",
        idea="First decide the regime from the loss tangent σ/ωε. At these frequencies sea water is a good conductor, so α ≈ √(πfμσ); then convert nepers to decibels.",
        steps=[S("Loss tangent.", r"\frac{\sigma}{\omega\varepsilon}=«lt»"),
               S("Attenuation constant (exact formula, which here equals the good-conductor value).", r"\alpha=«a»\ \text{Np/m}"),
               S("The field falls by e^(−α) per metre; in decibels that is 20 log₁₀ e times α.", r"\alpha_{dB}=20\log_{10}(e)\,\alpha=«adb»\ \text{dB/m}")],
        answer="α = «adb» dB/m",
        whatif=[W("…the frequency were ten times higher?", lambda p: {**p, "f": 10 * p["f"]}, "α ∝ √f in a good conductor: «adb» dB/m.", r"\alpha_{dB}=«adb»\ \text{dB/m}"),
                W("…the depth for 100 dB of loss were asked?", lambda p: p, "z = 100/α_dB = «z» m.", r"z=\frac{100\ \text{dB}}{\alpha_{dB}}=«z»\ \text{m}")],
        mistake="Using 10 log₁₀ for a field quantity, which halves the dB figure.",
        vals={"lt": EV("loss_tangent"), "a": EV("alpha"), "adb": EV("alpha_dB"), "z": lambda r, p: 100 / r["values"]["alpha_dB"]}),
    "c5-lambda": X(
        asked="The wavelength inside a lossless dielectric.",
        idea="The frequency is set by the source and does not change; the wave slows to u = c/√εr, so the wavelength shrinks by the same factor.",
        steps=[S("Phase velocity in the dielectric.", r"u_p=\frac{c}{\sqrt{\varepsilon_r}}=«u»\ \text{m/s}"),
               S("Wavelength.", r"\lambda=\frac{u_p}{f}=«lam»\ \text{cm}")],
        answer="λ = «lam» cm",
        whatif=[W("…the wave were in free space?", lambda p: {**p, "er": 1}, "λ₀ = «lam» cm, longer by √εr.", r"\lambda_0=\frac{c}{f}=«lam»\ \text{cm}"),
                W("…the intrinsic impedance were asked?", lambda p: p, "η = η₀/√εr = «eta» Ω.", r"\eta=\frac{\eta_0}{\sqrt{\varepsilon_r}}=«eta»\ \Omega")],
        mistake="Dividing by εr instead of √εr.",
        vals={"u": EV("vp"), "lam": lambda r, p: r["values"]["wavelength"] * 100, "eta": EV("eta_mag")}),
    "c6-normal-R": X(
        asked="The fraction of the incident power reflected at normal incidence.",
        idea="Reflection is set by the impedance mismatch, Γ = (η₂ − η₁)/(η₂ + η₁). Power goes as the square of the field, so the reflected fraction is |Γ|².",
        steps=[S("Intrinsic impedances of the two non-magnetic media.", r"\eta_1=«e1»\ \Omega,\qquad\eta_2=\frac{\eta_0}{\sqrt{\varepsilon_r}}=«e2»\ \Omega"),
               S("Reflection coefficient; the minus sign means the reflected E is inverted.", r"\Gamma=\frac{\eta_2-\eta_1}{\eta_2+\eta_1}=«G»"),
               S("Fraction of power reflected.", r"R=|\Gamma|^2=«R»\ \%")],
        answer="R = «R» %",
        whatif=[W("…the transmitted fraction were asked?", lambda p: p, "Lossless media conserve power: T = 1 − R = «T» %.", r"T=1-|\Gamma|^2=«T»\ \%"),
                W("…the dielectric had εr = 81?", lambda p: {**p, "er": 81}, "A larger mismatch reflects more: R = «R» %.", r"R=«R»\ \%")],
        mistake="Giving |Γ| instead of |Γ|² for the power fraction.",
        vals={"e1": _c("eta1"), "e2": _c("eta2"), "G": _c("Gamma"), "R": lambda r, p: r["values"]["R"] * 100, "T": lambda r, p: r["values"]["T"] * 100}),
    "c6-brewster": X(
        asked="The angle of incidence at which a parallel-polarised wave is not reflected.",
        idea="For parallel (TM) polarisation Γ vanishes when the reflected and transmitted directions are perpendicular. With Snell's law this gives tan θ_B = n₂/n₁.",
        steps=[S("Refractive index of the dielectric.", r"n_2=\sqrt{\varepsilon_r}"),
               S("Brewster condition.", r"\theta_B=\tan^{-1}\frac{n_2}{n_1}=«tb»^\circ"),
               S("Perpendicular polarisation has no such angle between non-magnetic media, so unpolarised light reflected at θ_B comes out perpendicular-polarised.")],
        answer="θ_B = «tb»°",
        whatif=[W("…the dielectric were water at low frequency (εr = 81)?", lambda p: {**p, "er": 81}, "θ_B = «tb»°, closer to grazing.", r"\theta_B=\tan^{-1}9=«tb»^\circ"),
                W("…it were glass (εr = 2.25)?", lambda p: {**p, "er": 2.25}, "θ_B = «tb»°.", r"\theta_B=\tan^{-1}1.5=«tb»^\circ")],
        mistake="Applying the Brewster angle to perpendicular polarisation, which is still reflected there.",
        vals={"tb": EV("theta_B")}),
    "c6-critical": X(
        asked="The critical angle for total internal reflection from the denser medium into air.",
        idea="Snell's law n₁ sin θ_i = n₂ sin θ_t. Total internal reflection starts when the transmitted angle reaches 90°.",
        steps=[S("Set θ_t = 90° in Snell's law.", r"\sin\theta_c=\frac{n_2}{n_1}=\frac{1}{\sqrt{\varepsilon_r}}"),
               S("Solve for the angle.", r"\theta_c=\sin^{-1}\frac{1}{\sqrt{\varepsilon_r}}=«tc»^\circ"),
               S("Beyond θ_c the transmitted field is evanescent and all the power is reflected.")],
        answer="θ_c = «tc»°",
        whatif=[W("…the Brewster angle of the same interface were asked?", lambda p: p, "θ_B = «tb»°, always below θ_c.", r"\theta_B=\tan^{-1}\frac{n_2}{n_1}=«tb»^\circ"),
                W("…the medium had εr = 12?", lambda p: {**p, "er": 12}, "A denser medium traps light at smaller angles: θ_c = «tc»°.", r"\theta_c=«tc»^\circ")],
        mistake="Putting n₁/n₂ (greater than 1) inside sin⁻¹. Total internal reflection only happens going from higher to lower index.",
        vals={"tc": EV("theta_c"), "tb": EV("theta_B")}),
    "c7-vswr": X(
        asked="The voltage standing-wave ratio on the line.",
        idea="The load reflection coefficient sets the standing wave: maxima are 1 + |Γ| and minima 1 − |Γ| times the incident amplitude.",
        steps=[S("Load reflection coefficient and its magnitude.", r"\Gamma_L=\frac{Z_L-Z_0}{Z_L+Z_0},\qquad|\Gamma_L|=«gm»"),
               S("Ratio of maximum to minimum.", r"S=\frac{1+|\Gamma_L|}{1-|\Gamma_L|}=«S»")],
        answer="S = «S»",
        whatif=[W("…the return loss were asked?", lambda p: p, "RL = −20 log₁₀|Γ_L| = «rl» dB.", r"RL=-20\log_{10}|\Gamma_L|=«rl»\ \text{dB}"),
                W("…the load were purely resistive at the same R?", lambda p: {**p, "X": 0}, "S = «S».", r"S=«S»")],
        mistake="Putting the complex Γ instead of |Γ| into the VSWR formula.",
        vals={"gm": EV("Gamma_mag"), "S": EV("S"), "rl": EV("return_loss_dB")}),
    "c7-return-loss": X(
        asked="The return loss of the load on a 50 Ω line.",
        idea="Return loss is how far the reflected wave is below the incident one, in dB: RL = −20 log₁₀|Γ|.",
        steps=[S("Load reflection coefficient.", r"|\Gamma_L|=\left|\frac{Z_L-Z_0}{Z_L+Z_0}\right|=«gm»"),
               S("Convert to decibels.", r"RL=-20\log_{10}|\Gamma_L|=«rl»\ \text{dB}")],
        answer="RL = «rl» dB",
        whatif=[W("…the VSWR were asked?", lambda p: p, "S = «S».", r"S=\frac{1+|\Gamma_L|}{1-|\Gamma_L|}=«S»"),
                W("…the reactance were zero?", lambda p: {**p, "X": 0}, "RL = «rl» dB.", r"RL=«rl»\ \text{dB}")],
        mistake="Using 10 log₁₀|Γ| or reporting a negative return loss; for a passive load RL is positive.",
        vals={"gm": EV("Gamma_mag"), "rl": EV("return_loss_dB"), "S": EV("S")}),
    "c7-qwt": X(
        asked="The characteristic impedance of a λ/4 transformer placed at the first voltage minimum.",
        idea="A λ/4 section turns a real impedance Z into Z_T²/Z. At a voltage minimum the line impedance is real and equals Z₀/S, so the transformer must map Z₀/S onto Z₀.",
        steps=[S("Reflection coefficient and VSWR of the load.", r"|\Gamma_L|=«gm»,\qquad S=«S»"),
               S("With R_L > Z₀ the load sits at a voltage maximum; the first minimum is λ/4 towards the generator, where Z = Z₀/S.", r"Z_{min}=\frac{Z_0}{S}=«zmin»\ \Omega"),
               S("Match Z_min to Z₀ with the transformer.", r"Z_T=\sqrt{Z_0Z_{min}}=\frac{Z_0}{\sqrt S}=«zt»\ \Omega")],
        answer="Z_T = «zt» Ω",
        whatif=[W("…the load were 300 Ω?", lambda p: {**p, "R": 300}, "A larger mismatch needs a lower Z_T: «zt» Ω.", r"Z_T=«zt»\ \Omega"),
                W("…the position of the minimum were asked?", lambda p: p, "d_min = «dmin» λ from the load.", r"d_{min}=«dmin}\,\lambda".replace("«dmin}", "«dmin»"))],
        mistake="Using √(Z₀R_L). That is the transformer for placing it directly at a resistive load, not at the voltage minimum.",
        vals={"gm": EV("Gamma_mag"), "S": EV("S"), "zmin": lambda r, p: p["Z0"] / r["values"]["S"], "zt": lambda r, p: r["match"]["quarter_wave"]["Z_T"],
              "dmin": lambda r, p: r["values"]["d_min"] / r["values"]["lambda_"]}),
    "c8-wg-cutoff": X(
        asked="The cut-off frequency of the dominant TE₁₀ mode.",
        idea="A mode can propagate only when the guide is wide enough for half a wavelength of the filling material across it. For TE₁₀ that means λ_c = 2a.",
        steps=[S("Cut-off wavelength of TE₁₀.", r"\lambda_c=2a"),
               S("Divide the speed in the filling by λ_c.", r"f_c=\frac{c}{2a\sqrt{\varepsilon_r}}=«fc»\ \text{GHz}"),
               S("The height b does not enter TE₁₀; it sets where the next modes start.")],
        answer="f_c = «fc» GHz",
        whatif=[W("…the guide were filled with PTFE (εr = 2.1)?", lambda p: {**p, "er": 2.1}, "f_c drops by √εr: «fc» GHz.", r"f_c=«fc»\ \text{GHz}"),
                W("…the guide wavelength at 1.5 f_c were asked?", lambda p: p, "λ_g = «lg» cm.", r"\lambda_g=\frac{\lambda}{\sqrt{1-(f_c/f)^2}}=«lg»\ \text{cm}")],
        mistake="Using a instead of 2a, or bringing b into the TE₁₀ cut-off.",
        vals={"fc": lambda r, p: r["values"]["fc"] / 1e9, "lg": lambda r, p: r["values"]["lambda_g"] * 100}),
    "c8-wg-lambdag": X(
        asked="The guide wavelength of TE₁₀ at the given frequency.",
        idea="Above cut-off the wave zig-zags between the side walls, so the pattern along the guide repeats over a longer distance than in free space.",
        steps=[S("Cut-off of TE₁₀.", r"f_c=\frac{c}{2a}=«fc»\ \text{GHz}"),
               S("Guide wavelength.", r"\lambda_g=\frac{c/f}{\sqrt{1-(f_c/f)^2}}=«lg»\ \text{cm}"),
               S("Phase and group velocities lie on either side of c, and their product is c².", r"u_p=«up»\ \text{m/s},\qquad u_g=«ug»\ \text{m/s}")],
        answer="λ_g = «lg» cm",
        whatif=[W("…the frequency were 8 GHz?", lambda p: {**p, "f": 8e9}, "Closer to cut-off, λ_g stretches to «lg» cm.", r"\lambda_g=«lg»\ \text{cm}"),
                W("…the wave impedance were asked?", lambda p: p, "Z_TE = η₀/√(1 − (f_c/f)²) = «Z» Ω.", r"Z_{TE}=«Z»\ \Omega")],
        mistake="Expecting λ_g to be shorter than the free-space wavelength. In a hollow guide it is always longer.",
        vals={"fc": lambda r, p: r["values"]["fc"] / 1e9, "lg": lambda r, p: r["values"]["lambda_g"] * 100, "up": EV("up"), "ug": EV("ug"), "Z": EV("Z")}),
    "c8-dipole-P": X(
        asked="The power radiated by a half-wave dipole for the given feed current.",
        idea="The radiated power can be booked as power dissipated in a radiation resistance: P = ½I₀²R_rad for a peak current I₀.",
        steps=[S("Radiation resistance of a λ/2 dipole, from integrating its pattern over a sphere.", r"R_{rad}=«R»\ \Omega"),
               S("Power for the peak current.", r"P_{rad}=\tfrac12I_0^2R_{rad}=«P»\ \text{W}")],
        answer="P_rad = «P» W",
        whatif=[W("…the current were doubled?", lambda p: {**p, "I": 2 * p["I"]}, "P ∝ I₀², so it quadruples to «P» W.", r"P_{rad}=«P»\ \text{W}"),
                W("…the directivity were asked?", lambda p: p, "D = «D», that is «Ddb» dBi.", r"D=«D»")],
        mistake="Dropping the ½: I₀ here is a peak value, not rms.",
        vals={"R": EV("R_rad"), "P": EV("P_rad"), "D": EV("D"), "Ddb": EV("D_dBi")}),
    "c8-array-steer": X(
        asked="The direction θ₀ of the main beam, measured from the array axis.",
        idea="The array factor peaks where the extra path between neighbours, kd cos θ, cancels the feed phase step: kd cos θ₀ + δ = 0.",
        steps=[S("Main-beam condition with kd = 2πd/λ.", r"\cos\theta_0=-\frac{\delta}{kd}"),
               S("Solve for the angle.", r"\theta_0=«t0»^\circ"),
               S("With δ = 0 the beam is broadside (90°); the progressive phase tilts it.")],
        answer="θ₀ = «t0»°",
        whatif=[W("…the elements were fed in phase?", lambda p: {**p, "dl": 0}, "Broadside: θ₀ = «t0»°.", r"\theta_0=«t0»^\circ"),
                W("…the directivity were asked?", lambda p: p, "D = «D» («Ddb» dBi).", r"D=«D»")],
        mistake="Dropping the minus sign, which points the beam to the mirror direction 180° − θ₀.",
        vals={"t0": EV("theta0"), "D": EV("D"), "Ddb": EV("D_dBi")}),
}
_FIGS = {
    "c0-spread": lambda p: {"type": "dims", "dim": p["dim"]},
    "c1-sph-dv": lambda p: {"type": "coord", "system": "spherical"},
    "c1-cyl-ds": lambda p: {"type": "coord", "system": "cylindrical"},
    "c1-conv-theta": lambda p: {"type": "coord", "system": "spherical", "point": [p["x"], p["y"], p["z"]]},
    "c2-two-charges": lambda p: {"type": "charges", "charges": [[p["q1"], -p["d"] / 2, 0], [p["q2"], p["d"] / 2, 0]], "probe": [0, p["py"]]},
    "c2-gauss-sphere": lambda p: {"type": "sphere", "a": p["a"], "r": _nice(p["f"] * p["a"], 3)},
    "c2-coax-C": lambda p: {"type": "coax", "a": p["a"], "b": _nice(p["a"] * p["ratio"], 3)},
    "c2-plate-bd": lambda p: {"type": "plates", "d": p["d"]},
    "c3-wire-force": lambda p: {"type": "wires", "wires": [[p["I1"], -p["d"] / 2, 0], [p["I2"], p["d"] / 2, 0]]},
    "c3-loop-centre": lambda p: {"type": "loop"},
    "c3-toroid": lambda p: {"type": "toroid", "a": p["a"], "b": _nice(p["a"] + p["w"], 3), "label": f"a = {p['a']} m, b = {_nice(p['a'] + p['w'], 3)} m"},
    "c3-coax-L": lambda p: {"type": "coax", "a": p["a"], "b": _nice(p["a"] * p["ratio"], 3)},
    "c5-skin": lambda p: {"type": "slab", "label": p["m"][0]},
    "c5-seawater": lambda p: {"type": "slab", "label": "sea water"},
    "c5-lambda": lambda p: {"type": "slab", "label": f"lossless, εr = {p['er']}"},
    "c6-normal-R": lambda p: {"type": "normal", "e2": p["er"]},
    "c6-brewster": lambda p: {"type": "oblique", "e1": 1, "e2": p["er"], "theta": 55},
    "c6-critical": lambda p: {"type": "oblique", "e1": p["er"], "e2": 1, "theta": 30},
    "c7-vswr": lambda p: {"type": "tline", "Z0": f"{p['Z0']} Ω", "ZL": f"{p['R']} {'+' if p['X'] >= 0 else '−'} j{abs(p['X'])} Ω"},
    "c7-return-loss": lambda p: {"type": "tline", "Z0": f"{p['Z0']} Ω", "ZL": f"{p['R']} {'+' if p['X'] >= 0 else '−'} j{abs(p['X'])} Ω"},
    "c7-qwt": lambda p: {"type": "tline", "Z0": f"{p['Z0']} Ω", "ZL": f"{p['R']} Ω"},
    "c8-wg-cutoff": lambda p: {"type": "waveguide", "a": p["a"], "b": _nice(p["a"] / 2, 4)},
    "c8-wg-lambdag": lambda p: {"type": "waveguide", "a": 22.86, "b": 10.16},
    "c8-dipole-P": lambda p: {"type": "dipole", "L": 0.5},
    "c8-array-steer": lambda p: {"type": "array", "N": p["N"], "d": p["d"]},
}
for _t in T:
    _t["x"] = _t["x"] or _EXPL.get(_t["id"])
    _t["fig"] = _t["fig"] or _FIGS.get(_t["id"])


# ---------------- solver adapters → (engine result, SI answer, chapter action)
def _spread(p):
    f = 1e9
    r = dm.compare(f, r_max_lambda=5)
    k = dm._k(f, 1, 1, 0)[0]
    lam = 2 * math.pi / k.real
    r1 = 40 * lam   # far zone: Hankel asymptote error < 1e-3 dB
    lv = 20 * math.log10(abs(dm.psi(p["dim"], k, np.array(p["k"] * r1))) / abs(dm.psi(p["dim"], k, np.array(r1))))
    return _with(r, dlevel=lv), lv, {"chapter": "dimensions", "params": {"f": f}}



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
