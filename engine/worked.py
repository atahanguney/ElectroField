"""Worked problems: original exam-level problems with engine-verified solutions.

Problems are written in our own words; `ref` names the textbook section that covers the
concept (Ulaby & Ravaioli, Fundamentals of Applied Electromagnetics; Cheng, Field and Wave
Electromagnetics). Each problem runs one engine route — the solution steps and independent
checks shown on the page are the engine's — and lists the requested answers.
"""
import math

from .constants import C0, EPS0
from . import routes
import numpy as np

from .explain import render, X, S, W, Sweep, Series, V as EV

P = []
TOPICS = {"dimensions": "1-D, 2-D and 3-D waves", "coordinates": "Vectors & coordinates", "electrostatics": "Electrostatics",
          "images": "Method of images", "magnetostatics": "Magnetostatics & Biot–Savart", "maxwell": "Maxwell & boundaries",
          "waves": "Plane waves", "reflection": "Reflection & transmission", "tlines": "Transmission lines", "radiation": "Waveguides & antennas"}


def p(topic, ref, level, title, text, fig, route, params, answers, approach, simple, x=None, kind="numeric"):
    P.append(dict(id=f"{topic[:3]}{sum(1 for x in P if x['topic'] == topic) + 1}", topic=topic, ref=ref, level=level, title=title,
                  text=text, fig=fig, route=route, params=params, answers=answers, approach=approach, simple=simple, x=x, kind=kind))


def px(topic, ref, level, title, text, fig, route, params, answers, x, kind):
    """A problem with a written explanation (engine/explain.py); kind is 'numeric' or 'concept'."""
    if kind not in ("numeric", "concept"):
        raise ValueError("kind must be 'numeric' or 'concept'")
    p(topic, ref, level, title, text, fig, route, params, answers, x["idea"], "", x=x, kind=kind)


V = lambda k: (lambda r: r["values"][k])
LAM = lambda f: C0 / f
_sens = lambda ch, d: (lambda r: next(s for s in r["sensitivity"] if s["change"] == ch)[d])

# ---------------------------------------------------------------- 1-D / 2-D / 3-D
T = "dimensions"
# Explained (engine/explain.py): 7 numerical + 8 conceptual. Levels are 20 log10 of |ψ| ratios from the engine.
_sens3 = lambda ch, d: (lambda r, p: next(s for s in r["sensitivity"] if s["change"] == ch)[d])
_prof = lambda d: (lambda r, p: r["profiles"][d]["mag"])
_PROFILES = Series(lambda r, p: r["r"], [("1-D (plane wave)", _prof("1D")), ("2-D (line source)", _prof("2D"), "S"), ("3-D (point source)", _prof("3D"), "E")],
                   "distance r (m)", "relative amplitude |ψ|", logx=True, logy=True)
_DV = {"lam": EV("wavelength"), "b": EV("beta"), "a": EV("alpha"), "ro": EV("r_obs"), "l1": EV("level_1D"), "l2": EV("level_2D"), "l3": EV("level_3D")}

px(T, "Ulaby & Ravaioli Sec. 9-1", "basic", "Point source: doubling the distance",
   "A small Wi-Fi antenna radiates at 2.4 GHz in free space. You stand 10 m away and then step back to 20 m. "
   "Treating the antenna as a point source and ignoring reflections, by how many decibels does the field level change?",
   {"type": "dims", "dim": "3D"}, "dim/compare", {"f": 2.4e9, "r_max_lambda": 10}, [("Δ level", _sens("double the distance", "3D"), "dB", 1)],
   X(asked="The change in field level, in dB, when the distance from a point source doubles.",
     idea="A point source spreads its power over spheres of area 4πR². The same power through a larger sphere means a weaker field, with |E| ∝ 1/R.",
     steps=[S("Ratio of field amplitudes at 2R and R.", r"\frac{|E(2R)|}{|E(R)|}=\frac{R}{2R}=\frac12"),
            S("Convert to decibels with 20 log₁₀ because E is a field quantity.", r"\Delta L=20\log_{10}\tfrac12=«d»\ \text{dB}"),
            S("The frequency does not enter: 1/R spreading is the same at any frequency in a lossless medium.")],
     answer="ΔL = «d» dB (the field halves, the power density drops to a quarter)",
     whatif=[W("…the source were a long line (cylindrical wave)?", lambda p: p, "Power then spreads over 2πρℓ, so |E| ∝ 1/√ρ: ΔL = «d2» dB.", r"\Delta L=20\log_{10}\tfrac{1}{\sqrt2}=«d2»\ \text{dB}"),
             W("…the signal travelled along a lossless cable instead?", lambda p: p, "A guided TEM wave does not spread: ΔL = «d1» dB.", r"\Delta L=«d1»\ \text{dB}")],
     mistake="Writing −3 dB. That is the change in power for a factor 2, but here the power density changes by a factor 4.",
     vals={"d": _sens3("double the distance", "3D"), "d2": _sens3("double the distance", "2D"), "d1": _sens3("double the distance", "1D")}), "numeric")

px(T, "Cheng Sec. 10-1 (line sources)", "basic", "Line source: doubling the distance",
   "A long straight wire carrying an RF current acts as a line source and radiates a cylindrical wave into lossless air at 1 GHz. "
   "In the far zone, by how much does the field level change when the distance from the wire doubles?",
   {"type": "dims", "dim": "2D"}, "dim/compare", {"f": 1e9, "r_max_lambda": 20}, [("Δ level", _sens("double the distance", "2D"), "dB", 1)],
   X(asked="The level change for a cylindrical wave when ρ doubles.",
     idea="A line source spreads its power over a cylinder of area 2πρℓ, which grows only linearly with ρ. The power density falls as 1/ρ and the field as 1/√ρ.",
     steps=[S("Exact solution of the 2-D wave equation and its far-zone form.", r"\psi=H_0^{(2)}(k\rho)\ \xrightarrow{k\rho\gg1}\ \sqrt{\tfrac{2}{\pi k\rho}}\,e^{-j(k\rho-\pi/4)}"),
            S("Amplitude ratio for ρ → 2ρ.", r"\frac{|\psi(2\rho)|}{|\psi(\rho)|}=\frac{1}{\sqrt2}"),
            S("In decibels.", r"\Delta L=20\log_{10}\tfrac{1}{\sqrt2}=«d»\ \text{dB}")],
     answer="ΔL = «d» dB",
     whatif=[W("…the same question were asked for a point source?", lambda p: p, "Spherical spreading is faster: ΔL = «d3» dB.", r"\Delta L=«d3»\ \text{dB}"),
             W("…the frequency were 100 MHz?", lambda p: {**p, "f": 1e8}, "Far-zone spreading does not depend on frequency: ΔL = «d» dB.", r"\Delta L=«d»\ \text{dB}")],
     mistake="Using 1/ρ for a line source. The field of a static line charge falls as 1/ρ, but the radiated field falls as 1/√ρ.",
     vals={"d": _sens3("double the distance", "2D"), "d3": _sens3("double the distance", "3D")}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 7-2, 9-1", "exam", "Three geometries at ten wavelengths",
   "A 1 GHz wave travels in lossless free space. Compare three cases: a plane wave (1-D), a cylindrical wave from a line source (2-D) and a spherical wave from a point source (3-D). "
   "For each, find the field level at 10λ relative to its level at λ/2.",
   {"type": "dims", "dim": "3D"}, "dim/compare", {"f": 1e9, "r_max_lambda": 10},
   [("1-D", V("level_1D"), "dB", 1), ("2-D", V("level_2D"), "dB", 1), ("3-D", V("level_3D"), "dB", 1)],
   X(asked="Three levels: 20 log₁₀ |ψ(10λ)/ψ(λ/2)| for plane, cylindrical and spherical waves.",
     idea="The same wavenumber governs all three; only the geometry of spreading differs. The distance ratio is 20, so each answer is 20 log₁₀ of 20 to the power 0, ½ or 1.",
     steps=[S("Plane wave: nothing spreads, so the amplitude is constant.", r"L_{1D}=«l1»\ \text{dB}"),
            S("Cylindrical wave: |ψ| ∝ 1/√ρ in the far zone; the engine uses the exact Hankel function because λ/2 is not yet far from the source.", r"L_{2D}=20\log_{10}\Big|\frac{H_0^{(2)}(k\cdot10\lambda)}{H_0^{(2)}(k\lambda/2)}\Big|=«l2»\ \text{dB}"),
            S("Spherical wave: |ψ| ∝ 1/R exactly.", r"L_{3D}=20\log_{10}\frac{\lambda/2}{10\lambda}=«l3»\ \text{dB}")],
     answer="1-D: «l1» dB, 2-D: «l2» dB, 3-D: «l3» dB",
     whatif=[W("…the medium absorbed (εr = 4, σ = 0.01 S/m)?", lambda p: {**p, "eps_r": 4, "sigma": 0.01}, "All three lose the same extra dB per metre: 1-D «l1», 2-D «l2», 3-D «l3» dB.", r"L=L_{spread}-20\log_{10}(e)\,\alpha\,\Delta r"),
             W("…the observation point were at 20λ?", lambda p: {**p, "r_max_lambda": 20}, "Spreading grows only logarithmically: 2-D «l2» dB, 3-D «l3» dB.", r"L_{3D}=«l3»\ \text{dB}")],
     mistake="Assuming every wave falls as 1/R. Only a point source does; how a wave weakens depends on the shape of its wavefronts.",
     plot=_PROFILES, evidence_say="Engine profiles on log–log axes: slopes 0, −½ and −1.", vals=_DV), "numeric")

px(T, "Ulaby & Ravaioli Sec. 7-2", "basic", "Wavelength in a dielectric",
   "A 1 GHz signal passes from air into a large block of lossless plastic with εr = 4. Find its wavelength inside the plastic, and compare it with the free-space wavelength.",
   {"type": "dims", "dim": "1D"}, "dim/compare", {"f": 1e9, "eps_r": 4}, [("λ", V("wavelength"), "m", 1)],
   X(asked="The wavelength in the dielectric, and how it compares with λ₀.",
     idea="The source fixes the frequency. The medium sets the speed, u = c/√εr, so the wavelength λ = u/f shrinks by √εr.",
     steps=[S("Phase constant in the dielectric.", r"\beta=\frac{\omega\sqrt{\varepsilon_r}}{c}=«b»\ \text{rad/m}"),
            S("Wavelength.", r"\lambda=\frac{2\pi}{\beta}=\frac{c}{f\sqrt{\varepsilon_r}}=«lam»\ \text{m}"),
            S("In free space it would be «l0» m, so the plastic shortens it by √εr = 2.")],
     answer="λ = «lam» m (free space: «l0» m)",
     whatif=[W("…the frequency were doubled?", lambda p: {**p, "f": 2e9}, "λ halves to «lam» m.", r"\lambda=«lam»\ \text{m}"),
             W("…the block were glass (εr = 6.25)?", lambda p: {**p, "eps_r": 6.25}, "√εr = 2.5, so λ = «lam» m.", r"\lambda=«lam»\ \text{m}")],
     mistake="Dividing by εr instead of √εr, or changing the frequency instead of the wavelength at the boundary.",
     vals={"b": EV("beta"), "lam": EV("wavelength"), "l0": lambda r, p: C0 / p["f"]}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 7-4", "exam", "Attenuation in wet soil",
   "A 100 MHz ground-penetrating signal travels in wet soil with εr = 20 and σ = 0.05 S/m (typical values). "
   "Find the attenuation constant α, and the loss in dB for every metre travelled.",
   {"type": "dims", "dim": "3D"}, "dim/compare", {"f": 1e8, "eps_r": 20, "sigma": 0.05}, [("α", V("alpha"), "Np/m", 1)],
   X(asked="α in Np/m and the same attenuation in dB/m.",
     idea="The loss tangent σ/ωε decides which formula applies. Here it is close to 0.5, so neither the low-loss nor the good-conductor shortcut is safe and the exact formula is needed.",
     steps=[S("Loss tangent.", r"\frac{\sigma}{\omega\varepsilon}=\frac{0.05}{2\pi\cdot10^8\cdot20\varepsilon_0}=«lt»"),
            S("Exact attenuation constant.", r"\alpha=\omega\sqrt{\frac{\mu\varepsilon}{2}\Big[\sqrt{1+\big(\tfrac{\sigma}{\omega\varepsilon}\big)^2}-1\Big]}=«a»\ \text{Np/m}"),
            S("In decibels, 1 Np = 20 log₁₀ e dB.", r"\alpha_{dB}=«adb»\ \text{dB/m}")],
     answer="α = «a» Np/m = «adb» dB/m",
     whatif=[W("…the soil dried out to σ = 0.005 S/m?", lambda p: {**p, "sigma": 0.005}, "Now σ/ωε ≪ 1 and the low-loss formula works: α = «a» Np/m.", r"\alpha\approx\frac{\sigma}{2}\sqrt{\frac{\mu}{\varepsilon}}=«a»\ \text{Np/m}"),
             W("…the frequency were 1 GHz?", lambda p: {**p, "f": 1e9}, "α = «a» Np/m: higher frequencies penetrate less.", r"\alpha=«a»\ \text{Np/m}")],
     mistake="Using the low-loss approximation α ≈ (σ/2)√(μ/ε) when σ/ωε is not small. Here it would be noticeably off.",
     vals={"a": EV("alpha"), "adb": lambda r, p: r["values"]["alpha"] * 20 * math.log10(math.e), "lt": lambda r, p: p["sigma"] / (2 * math.pi * p["f"] * p["eps_r"] * EPS0)}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 7-4, 9-1", "exam", "Spreading plus absorption",
   "A point source radiates at 1 GHz inside a large lossy medium with εr = 4 and σ = 0.01 S/m. "
   "Find the field level at 10 wavelengths from the source relative to its level at half a wavelength, and say how much of it is due to absorption.",
   {"type": "dims", "dim": "3D"}, "dim/compare", {"f": 1e9, "eps_r": 4, "sigma": 0.01, "r_max_lambda": 10}, [("level", V("level_3D"), "dB", 1)],
   X(asked="The total level drop over 10λ for a point source in a lossy medium, split into spreading and absorption.",
     idea="The spherical-wave solution is ψ = e^(−jkR)/R with a complex k = β − jα. The 1/R part is spreading and the e^(−αR) part is absorption; in dB they add.",
     steps=[S("Wavenumber in the medium.", r"\beta=«b»\ \text{rad/m},\qquad\alpha=«a»\ \text{Np/m},\qquad\lambda=«lam»\ \text{m}"),
            S("Total level from the exact solution.", r"L=20\log_{10}\frac{|\psi(10\lambda)|}{|\psi(\lambda/2)|}=«l3»\ \text{dB}"),
            S("The plane-wave (1-D) level contains only the absorption part.", r"L_{abs}=-20\log_{10}(e)\,\alpha\,(9.5\lambda)=«l1»\ \text{dB}"),
            S("The rest is spherical spreading, the same as in a lossless medium.", r"L_{spread}=L-L_{abs}=«ls»\ \text{dB}")],
     answer="L = «l3» dB, of which «l1» dB is absorption",
     whatif=[W("…the medium were lossless?", lambda p: {**p, "sigma": 0}, "Only spreading remains: L = «l3» dB.", r"L=20\log_{10}\tfrac{1}{20}=«l3»\ \text{dB}"),
             W("…the observation point were at 20λ?", lambda p: {**p, "r_max_lambda": 20}, "Absorption doubles roughly in dB while spreading adds only 6 dB: L = «l3» dB.", r"L=«l3»\ \text{dB}")],
     mistake="Adding the two effects as amplitude ratios. They multiply as ratios, so they add in dB.",
     vals={**_DV, "ls": lambda r, p: r["values"]["level_3D"] - r["values"]["level_1D"]}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 7-4", "basic", "Plane wave in a lossy medium",
   "A 300 MHz plane wave travels through a slightly conducting material with εr = 9 and σ = 0.005 S/m. "
   "How many dB weaker is the field after travelling from half a wavelength to ten wavelengths?",
   {"type": "dims", "dim": "1D"}, "dim/compare", {"f": 3e8, "eps_r": 9, "sigma": 0.005, "r_max_lambda": 10}, [("level", V("level_1D"), "dB", 1)],
   X(asked="The attenuation of a plane wave over 9.5 wavelengths in a lossy medium.",
     idea="A plane wave does not spread, so all of its weakening comes from absorption, |ψ| = e^(−αz).",
     steps=[S("Attenuation constant and wavelength.", r"\alpha=«a»\ \text{Np/m},\qquad\lambda=«lam»\ \text{m}"),
            S("Path length between the two points.", r"\Delta z=10\lambda-\lambda/2=«dz»\ \text{m}"),
            S("Loss in dB.", r"L=-20\log_{10}(e)\,\alpha\,\Delta z=«l1»\ \text{dB}")],
     answer="L = «l1» dB",
     whatif=[W("…the material were lossless?", lambda p: {**p, "sigma": 0}, "No absorption and no spreading: L = «l1» dB.", r"L=0"),
             W("…the conductivity were doubled?", lambda p: {**p, "sigma": 0.01}, "In this low-loss regime α ∝ σ, so the loss roughly doubles: «l1» dB.", r"L=«l1»\ \text{dB}")],
     mistake="Applying 1/R spreading to a plane wave. A plane wave has flat wavefronts that do not grow.",
     vals={**_DV, "dz": lambda r, p: 9.5 * r["values"]["wavelength"]}), "numeric")

# ---- conceptual
_fs = {"f": 1e9, "r_max_lambda": 10}
px(T, "Ulaby & Ravaioli Sec. 7-2", "basic", "Why a plane wave does not weaken",
   "In a lossless medium a uniform plane wave keeps the same amplitude however far it travels, while the wave from a lamp clearly gets weaker with distance. "
   "Explain the difference in terms of energy.",
   {"type": "dims", "dim": "1D"}, "dim/compare", _fs, [],
   X(asked="Why a plane wave's amplitude is constant while a real source's field falls off.",
     idea="Energy flows along the direction of travel. Whether the field weakens depends on whether the cross-section that carries this energy grows.",
     steps=[S("A plane wave has flat, infinite wavefronts: the area that carries a given share of power never grows."),
            S("With no loss, the power through any wavefront is the same, so the power density and the field stay the same."),
            S("A lamp is a small source: its wavefronts are spheres whose area grows as R², so the same power is spread ever thinner.")],
     answer_text="Energy conservation fixes the answer. In a lossless medium the power crossing each wavefront is the same at every distance. "
                 "A uniform plane wave has flat wavefronts of unlimited extent, so a tube of rays keeps its cross-section and the power density, hence the field amplitude, stays constant. "
                 "A lamp is effectively a point source: its wavefronts are spheres of area 4πR², so the power density falls as 1/R² and the field as 1/R. "
                 "A plane wave is the far-zone limit of such a wave over a region small compared with R, where the 1/R change is negligible.",
     evidence_say="Engine amplitude profiles from λ/20 to 10λ: the 1-D curve is flat, the 3-D curve falls with slope −1.",
     plot=_PROFILES, mistake="Treating a plane wave as a real, finite beam. It is a model for a small patch of a wavefront far from the source.",
     vals={}), "concept")

px(T, "Ulaby & Ravaioli Sec. 9-1", "basic", "Why a point source falls off as 1/R",
   "Starting from energy conservation, show why the field of a point source in a lossless medium is proportional to 1/R, and why its power density is proportional to 1/R².",
   {"type": "dims", "dim": "3D"}, "dim/compare", _fs, [],
   X(asked="A derivation of the 1/R law for a point source from energy conservation.",
     idea="All radiated power must cross every sphere centred on the source, and power density is proportional to |E|².",
     steps=[S("The same power P passes through every sphere.", r"P=S(R)\cdot4\pi R^2=\text{const}"),
            S("So the power density falls as 1/R², and since S ∝ |E|², the field falls as 1/R.", r"S\propto\frac{1}{R^2},\qquad|E|\propto\frac1R"),
            S("The exact solution of the 3-D wave equation, ψ = e^(−jkR)/R, has the same 1/R amplitude.")],
     answer_text="The power P leaving the source has nowhere to go but outwards, so the same P crosses every sphere of radius R. "
                 "Spread over the area 4πR², the power density is S = P/(4πR²), which falls as 1/R². "
                 "Power density is proportional to the square of the field, S = |E|²/2η in a plane-wave-like far zone, so |E| falls as 1/R. "
                 "The spherical solution of the Helmholtz equation, e^(−jkR)/R, shows the same 1/R amplitude directly.",
     evidence_say="Engine check: the 3-D profile has a log–log slope of −1, and the power through spheres of different radius is the same.",
     plot=_PROFILES, mistake="Mixing up the 1/R field law with the 1/R² law for power density or for the static Coulomb field.",
     vals={}), "concept")

px(T, "Cheng Sec. 10-1 (line sources)", "exam", "Why a line source falls off as 1/√ρ",
   "A very long wire radiates a cylindrical wave. Why does its far field fall off as 1/√ρ and not as 1/ρ like the static field of a line charge?",
   {"type": "dims", "dim": "2D"}, "dim/compare", _fs, [],
   X(asked="The reason for 1/√ρ for a radiating line source, and why it differs from a static line charge.",
     idea="Radiated power must cross every coaxial cylinder; a static field carries no power and obeys Gauss's law instead.",
     steps=[S("Radiated power per unit length crosses every cylinder of radius ρ.", r"P'=S(\rho)\cdot2\pi\rho=\text{const}\ \Rightarrow\ S\propto\frac1\rho"),
            S("Field amplitude goes as the square root of power density.", r"|E|\propto\frac{1}{\sqrt\rho}"),
            S("A static line charge obeys Gauss's law, ∮D·ds = Q, which fixes D·2πρ and gives 1/ρ: a different law for a different kind of field.")],
     answer_text="For radiation the conserved quantity is power. Per unit length of wire, the same power crosses every coaxial cylinder of area 2πρ, "
                 "so the power density falls as 1/ρ and the field, which goes as its square root, falls as 1/√ρ. "
                 "The exact solution is the Hankel function H₀⁽²⁾(kρ), which approaches √(2/πkρ)·e^(−jkρ) once kρ ≫ 1. "
                 "The static field of a line charge carries no power; Gauss's law conserves flux of D instead, which gives E ∝ 1/ρ.",
     evidence_say="Engine check: the 2-D profile approaches slope −½ on log–log axes, and its independent check compares H₀⁽²⁾ with the asymptote.",
     plot=_PROFILES, mistake="Carrying a static result (E ∝ 1/ρ) over to a radiated wave.",
     vals={}), "concept")

px(T, "Cheng Sec. 10-1", "exam", "What 'far zone' means for a line source",
   "The 1/√ρ law for a cylindrical wave is called a far-zone result. What exactly must be large for it to hold, and what happens closer in?",
   {"type": "dims", "dim": "2D"}, "dim/compare", {"f": 1e9, "r_max_lambda": 3}, [],
   X(asked="The condition behind the far-zone law, and the behaviour near the source.",
     idea="The exact field is a Hankel function. Its simple asymptotic form needs kρ ≫ 1, which means ρ much larger than λ/2π.",
     steps=[S("Exact cylindrical solution and its large-argument form.", r"H_0^{(2)}(k\rho)\approx\sqrt{\frac{2}{\pi k\rho}}\,e^{-j(k\rho-\pi/4)}\qquad(k\rho\gg1)"),
            S("The condition is on kρ = 2πρ/λ, so 'far' is measured in wavelengths, not metres."),
            S("Close to the wire, H₀⁽²⁾ grows like a logarithm instead of 1/√ρ, and the field is mostly reactive (stored, not radiated).")],
     answer_text="The asymptotic form of H₀⁽²⁾(kρ) is accurate when kρ ≫ 1, that is when the distance is much larger than λ/2π. "
                 "So 'far' is relative to the wavelength: a few wavelengths at 1 GHz is a few tens of centimetres, at 1 MHz it is hundreds of metres. "
                 "Closer in, the exact Hankel function departs from the 1/√ρ law: its magnitude grows logarithmically towards the wire and part of the field is stored energy rather than radiation. "
                 "Results such as −3 dB per doubling of distance should only be used in the far zone.",
     evidence_say="Engine profile within the first three wavelengths: near the wire the 2-D curve is not yet a straight line of slope −½.",
     plot=Series(lambda r, p: r["r"], [("2-D (line source)", _prof("2D"), "S")], "distance ρ (m)", "relative amplitude |ψ|", logx=True, logy=True),
     mistake="Using the far-zone law at a fixed number of metres without checking it against the wavelength.",
     vals={}), "concept")

px(T, "Ulaby & Ravaioli Sec. 1-6", "basic", "Why 20 log₁₀ for fields and 10 log₁₀ for power",
   "Doubling the distance from a point source is said to cost '6 dB'. Explain why the same change is 6 dB whether you talk about the field or the power density, "
   "and why the formulas look different (20 log₁₀ versus 10 log₁₀).",
   {"type": "dims", "dim": "3D"}, "dim/compare", _fs, [],
   X(asked="Why decibels of fields use 20 log₁₀ and decibels of power use 10 log₁₀, giving the same number.",
     idea="The decibel is defined for power ratios. Power goes as the square of the field, and the logarithm turns that square into a factor 2.",
     steps=[S("Definition for power.", r"L=10\log_{10}\frac{S_2}{S_1}"),
            S("With S ∝ |E|², the square comes out of the logarithm as a factor 2.", r"L=10\log_{10}\frac{|E_2|^2}{|E_1|^2}=20\log_{10}\frac{|E_2|}{|E_1|}"),
            S("For a point source and a doubled distance both forms give «d» dB.")],
     answer_text="A decibel is defined as 10 log₁₀ of a power ratio. Power density is proportional to the square of the field, "
                 "so 10 log₁₀(|E₂|²/|E₁|²) = 20 log₁₀(|E₂|/|E₁|). Both formulas describe the same physical change and give the same number of decibels. "
                 "Doubling the distance from a point source halves the field (20 log₁₀ ½) and quarters the power density (10 log₁₀ ¼): both are about −6 dB. "
                 "Using 10 log₁₀ on a field ratio would wrongly give −3 dB.",
     evidence_say="Engine: the level change for doubling the distance from a point source is «d» dB.",
     mistake="Using 10 log₁₀ on voltages or fields, which halves every decibel figure.",
     vals={"d": _sens3("double the distance", "3D")}), "concept")

px(T, "Ulaby & Ravaioli Sec. 7-4, 9-1", "exam", "Far away: spreading or absorption?",
   "In a slightly lossy medium a point source loses field strength both by spreading and by absorption. "
   "Which of the two dominates close to the source, which far away, and why?",
   {"type": "dims", "dim": "3D"}, "dim/compare", {"f": 1e9, "eps_r": 4, "sigma": 0.01, "r_max_lambda": 50}, [],
   X(asked="How the balance between spreading loss and absorption changes with distance.",
     idea="In decibels, spreading grows with the logarithm of distance, while absorption grows in proportion to distance.",
     steps=[S("Spreading: 20 log₁₀(R₁/R₂), which adds a fixed 6 dB for every doubling of R."),
            S("Absorption: 20 log₁₀(e)·α·R, which adds the same number of dB for every metre."),
            S("A logarithm always loses to a straight line in the end, so absorption dominates far from the source; here α = «a» Np/m.")],
     answer_text="Near the source the distance doubles over very short paths, and each doubling costs 6 dB of spreading, while the path is too short for much absorption. "
                 "Far from the source a doubling of distance still costs only 6 dB of spreading, but the absorbed dB grow in proportion to the extra path length. "
                 "Since α·R eventually outgrows any logarithm, absorption dominates at large distances, however small α is. "
                 "This is why a lossy medium has a practical range limit, while in a lossless one a sensitive enough receiver can always detect the signal.",
     evidence_say="Engine profiles out to 50λ in εr = 4, σ = 0.01 S/m: the 1-D curve, which has no spreading, shows the absorption alone; it becomes steeper than the 3-D spreading slope at large distance.",
     plot=_PROFILES, mistake="Assuming the two effects scale the same way with distance.",
     vals={"a": EV("alpha")}), "concept")

px(T, "Ulaby & Ravaioli Sec. 2-1, 7-2", "basic", "Why a coaxial cable carries a 1-D wave",
   "Inside a coaxial cable the field pattern between the conductors looks like that of a line source, yet the signal travelling along the cable does not weaken with distance (ignoring loss). "
   "Why does it behave like a one-dimensional plane wave?",
   {"type": "dims", "dim": "1D"}, "dim/compare", _fs, [],
   X(asked="Why a TEM wave on a coax does not spread, even though its cross-sectional field looks like a line source's.",
     idea="What matters for spreading is the direction of power flow. On the cable, power flows along the axis, through a cross-section of fixed size.",
     steps=[S("The transverse fields fall as 1/r across the gap, but that is the shape of the field in each cross-section, not spreading along the path."),
            S("The power travels along z, confined between the conductors, through an annulus whose area does not change with z."),
            S("So the wave is one-dimensional in z, ψ = e^(−jkz), with constant amplitude in a lossless line.")],
     answer_text="The 1/r shape across the gap describes how the field is distributed within one cross-section; it does not change as the wave moves along the cable. "
                 "Power flows along the axis and is trapped between the conductors, so it always crosses the same annular area. "
                 "With no loss, the same power through the same area means the same field amplitude at every distance: the wave is effectively one-dimensional, "
                 "described by e^(−jβz). Real cables lose a little power in the conductors and dielectric, which gives the familiar dB-per-metre cable loss.",
     evidence_say="Engine: the 1-D level stays at «l1» dB from λ/2 to 10λ.",
     mistake="Confusing the transverse field profile (1/r across the gap) with spreading along the direction of travel.",
     vals={"l1": EV("level_1D")}), "concept")

px(T, "Ulaby & Ravaioli Sec. 9-1, Cheng Sec. 11-2", "exam", "Is the 1/R law exact near a point source?",
   "For the idealised point source used here the field is ψ = e^(−jkR)/R at every distance. Real antennas, such as a short dipole, have additional terms close in. "
   "What are they, and why does the simple model not show them?",
   {"type": "dims", "dim": "3D"}, "dim/compare", {"f": 1e9, "r_max_lambda": 3}, [],
   X(asked="Whether 1/R holds at all distances, and what near-field terms a real antenna adds.",
     idea="A scalar point source has only one solution of the 3-D Helmholtz equation with spherical symmetry. A real antenna radiates a vector field with an angular pattern, which brings in higher powers of 1/R.",
     steps=[S("For a spherically symmetric scalar wave, e^(−jkR)/R solves the Helmholtz equation exactly at every R > 0.", r"\nabla^2\psi+k^2\psi=0,\qquad\psi=\frac{e^{-jkR}}{R}"),
            S("A short dipole's fields contain 1/R, 1/R² and 1/R³ terms: only the 1/R term carries power to infinity."),
            S("The extra terms dominate for kR ≪ 1, inside about λ/2π, and are negligible for kR ≫ 1.")],
     answer_text="For the scalar, spherically symmetric source used here, e^(−jkR)/R is an exact solution at every distance, so 1/R holds even close to it. "
                 "Real antennas radiate vector fields with direction-dependent patterns, and their exact fields contain higher powers: a short dipole's E-field has 1/R, 1/R² and 1/R³ terms. "
                 "Within roughly λ/2π the 1/R³ term (quasi-static, stored energy) dominates; only the 1/R term carries net power away. "
                 "That is why far-field results such as 6 dB per doubling of distance should be applied a few wavelengths or more from a real antenna.",
     evidence_say="Engine check: the 3-D profile keeps a log–log slope of −1 right down to λ/20 for this scalar source.",
     plot=Series(lambda r, p: r["r"], [("3-D (point source)", _prof("3D"), "E")], "distance R (m)", "relative amplitude |ψ|", logx=True, logy=True),
     mistake="Applying far-field formulas to measurements taken within a wavelength of a real antenna.",
     vals={}), "concept")

# ---------------------------------------------------------------- coordinates
T = "coordinates"
# Explained (engine/explain.py): 7 numerical + 8 conceptual. Angles from the routes are in degrees.
_pt = lambda i: (lambda r, p: r["values"]["point"][i])
_vc = lambda i: (lambda r, p: r["values"]["vector"][i])
_el = lambda k, i=None: (lambda r, p: r["values"][k] if i is None else r["values"][k][i])
_cart_sph = lambda x, y, z, A=None: {"src": "cartesian", "dst": "spherical", "u1": x, "u2": y, "u3": z, **({"A1": A[0], "A2": A[1], "A3": A[2]} if A else {})}

px(T, "Ulaby & Ravaioli Sec. 3-2.3", "basic", "Spherical volume element",
   "Around the point R = 2 m, θ = 30°, φ = 0, a small region spans dR = 1 cm, dθ = 1° and dφ = 1°. "
   "Find its volume with the differential volume element, and compare with the exact volume of that region.",
   {"type": "coord", "system": "spherical"}, "coords/element", {"system": "spherical", "u1": 2, "u2": 30, "u3": 0, "d1": 0.01, "d2": 1, "d3": 1},
   [("dv", V("dv"), "cm³", 1e6)],
   X(asked="The volume of a small spherical region, first with dv and then exactly.",
     idea="In spherical coordinates the three sides of a small box are dR, R dθ and R sin θ dφ. Angles must be in radians and multiplied by their scale factors.",
     steps=[S("Scale factors at this point.", r"h_R=1,\quad h_\theta=R=«h2»\ \text{m},\quad h_\phi=R\sin\theta=«h3»\ \text{m}"),
            S("The three edge lengths (angle steps in radians).", r"dl_R=«l1»,\quad dl_\theta=«l2»,\quad dl_\phi=«l3»\ \text{m}"),
            S("Their product is the volume element.", r"dv=R^2\sin\theta\,dR\,d\theta\,d\phi=«dv»\ \text{cm}^3"),
            S("The exact volume, integrated over the region, is «ex» cm³; the small difference comes from treating the region as a box.")],
     answer="dv = «dv» cm³ (exact: «ex» cm³)",
     whatif=[W("…the region were at the equator (θ = 90°)?", lambda p: {**p, "u2": 90}, "sin θ = 1 there, so the φ edge is longest: dv = «dv» cm³.", r"dv=«dv»\ \text{cm}^3"),
             W("…the angle steps were 10° each?", lambda p: {**p, "d2": 10, "d3": 10}, "dv = «dv» cm³ while the exact value is «ex» cm³: the larger the steps, the worse the box approximation.", r"dv=«dv}\ \text{cm}^3".replace("«dv}", "«dv»"))],
     mistake="Leaving dθ and dφ in degrees, which inflates dv by (180/π)².",
     vals={"h2": _el("scale", 1), "h3": _el("scale", 2), "l1": _el("dl", 0), "l2": _el("dl", 1), "l3": _el("dl", 2),
           "dv": lambda r, p: r["values"]["dv"] * 1e6, "ex": lambda r, p: r["values"]["exact_finite_volume"] * 1e6}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 3-2.2", "basic", "Patch on a cylinder",
   "A curved sensor is glued to the side of a pipe of radius 0.5 m. It covers dφ = 5° around the pipe and dz = 2 cm along it. Find its area.",
   {"type": "coord", "system": "cylindrical"}, "coords/element", {"system": "cylindrical", "u1": 0.5, "u2": 0, "u3": 0, "d1": 0.01, "d2": 5, "d3": 0.02},
   [("ds_r", lambda r: r["values"]["ds"][0], "cm²", 1e4)],
   X(asked="The area of a patch on the surface r = constant.",
     idea="Unrolled, the patch is a rectangle: one side is the arc r dφ, the other the straight length dz.",
     steps=[S("Arc length around the pipe (angle in radians).", r"dl_\phi=r\,d\phi=«l2»\ \text{m}"),
            S("Length along the pipe.", r"dl_z=dz=«l3»\ \text{m}"),
            S("Area of the unrolled rectangle.", r"ds_r=r\,d\phi\,dz=«ds»\ \text{cm}^2")],
     answer="ds_r = «ds» cm²",
     whatif=[W("…the pipe had twice the radius?", lambda p: {**p, "u1": 1.0}, "The arc doubles, so ds_r = «ds» cm².", r"ds_r=«ds»\ \text{cm}^2"),
             W("…the patch lay on the flat end of the pipe, spanning dr = 1 cm and dφ = 5°?", lambda p: p, "Then ds_z = r dr dφ = «dsz» cm².", r"ds_z=r\,dr\,d\phi=«dsz»\ \text{cm}^2")],
     mistake="Multiplying dφ in degrees by r.",
     vals={"l2": _el("dl", 1), "l3": _el("dl", 2), "ds": lambda r, p: r["values"]["ds"][0] * 1e4, "dsz": lambda r, p: r["values"]["ds"][2] * 1e4}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 3-3", "basic", "Cartesian → spherical",
   "Express the point P = (3, 4, 5) m in spherical coordinates (R, θ, φ).",
   {"type": "coord", "system": "spherical", "point": [3, 4, 5]}, "coords/convert", _cart_sph(3, 4, 5),
   [("R", lambda r: r["values"]["point"][0], "m", 1), ("θ", lambda r: r["values"]["point"][1], "°", 1), ("φ", lambda r: r["values"]["point"][2], "°", 1)],
   X(asked="The three spherical coordinates of P.",
     idea="R is the distance from the origin, θ the angle down from +z, and φ the angle of the point's shadow on the xy-plane, measured from +x.",
     steps=[S("Distance from the origin.", r"R=\sqrt{x^2+y^2+z^2}=«R»\ \text{m}"),
            S("Polar angle from the z component.", r"\theta=\cos^{-1}\frac{z}{R}=«th»^\circ"),
            S("Azimuth from x and y, with the quadrant taken into account.", r"\phi=\operatorname{atan2}(y,x)=«ph»^\circ")],
     answer="P = («R» m, «th»°, «ph»°)",
     whatif=[W("…the point were (−3, −4, 5)?", lambda p: {**p, "u1": -3, "u2": -4}, "R and θ do not change, but φ moves to the third quadrant: φ = «ph»°.", r"\phi=\operatorname{atan2}(-4,-3)=«ph»^\circ"),
             W("…z were −5?", lambda p: {**p, "u3": -5}, "The point is below the xy-plane, so θ = «th}°.".replace("«th}", "«th»"), r"\theta=«th»^\circ")],
     mistake="Computing φ as tan⁻¹(y/x) without checking the quadrant, which gives the wrong answer whenever x < 0.",
     vals={"R": _pt(0), "th": _pt(1), "ph": _pt(2)}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 3-3", "basic", "Cartesian → cylindrical",
   "A sensor sits at P = (1, 1, 1) m. Give its cylindrical coordinates (r, φ, z).",
   {"type": "coord", "system": "cylindrical", "point": [1, 1, 1]}, "coords/convert", {"src": "cartesian", "dst": "cylindrical", "u1": 1, "u2": 1, "u3": 1},
   [("r", lambda r: r["values"]["point"][0], "m", 1), ("φ", lambda r: r["values"]["point"][1], "°", 1)],
   X(asked="The radial distance r from the z-axis, the azimuth φ and the height z.",
     idea="Cylindrical coordinates keep z and replace x, y by polar coordinates in the xy-plane.",
     steps=[S("Distance from the z-axis (not from the origin).", r"r=\sqrt{x^2+y^2}=«r»\ \text{m}"),
            S("Azimuth.", r"\phi=\operatorname{atan2}(y,x)=«ph»^\circ"),
            S("z is unchanged: z = «z» m.")],
     answer="P = («r» m, «ph»°, «z» m)",
     whatif=[W("…the spherical R were asked?", lambda p: {**p, "dst": "spherical"}, "R includes z: R = «r» m (the first spherical coordinate).", r"R=\sqrt{r^2+z^2}=«r»\ \text{m}"),
             W("…the point were (−1, 1, 1)?", lambda p: {**p, "u1": -1}, "φ moves to the second quadrant: φ = «ph»°.", r"\phi=«ph»^\circ")],
     mistake="Taking r as the distance from the origin. That is the spherical R; cylindrical r ignores z.",
     vals={"r": _pt(0), "ph": _pt(1), "z": _pt(2)}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 3-3.1", "exam", "Vector components in cylindrical",
   "At the point P = (1, 1, 0) m a field has the value A = x̂ + 2ŷ + 3ẑ. Find its cylindrical components A_r, A_φ and A_z at P.",
   {"type": "coord", "system": "cylindrical", "point": [1, 1, 0]}, "coords/convert",
   {"src": "cartesian", "dst": "cylindrical", "u1": 1, "u2": 1, "u3": 0, "A1": 1, "A2": 2, "A3": 3},
   [("A_r", lambda r: r["values"]["vector"][0], "", 1), ("A_φ", lambda r: r["values"]["vector"][1], "", 1), ("A_z", lambda r: r["values"]["vector"][2], "", 1)],
   X(asked="The components of A along r̂, φ̂ and ẑ at P.",
     idea="A component is a projection on a unit vector. At P the unit vectors r̂ and φ̂ point in directions set by the point's azimuth φ.",
     steps=[S("Azimuth of P.", r"\phi=«ph»^\circ"),
            S("Unit vectors at P.", r"\hat r=\cos\phi\,\hat x+\sin\phi\,\hat y,\qquad\hat\phi=-\sin\phi\,\hat x+\cos\phi\,\hat y"),
            S("Project A on each.", r"A_r=«ar»,\qquad A_\phi=«ap»,\qquad A_z=«az»")],
     answer="A_r = «ar», A_φ = «ap», A_z = «az»",
     whatif=[W("…the same A were given at P = (0, 1, 0)?", lambda p: {**p, "u1": 0}, "At φ = 90° r̂ = ŷ and φ̂ = −x̂: A_r = «ar», A_φ = «ap».", r"A_r=«ar},\ A_\phi=«ap»".replace("«ar}", "«ar»")),
             W("…the magnitude |A| were asked?", lambda p: p, "The length does not depend on the coordinate system: |A| = «mag».", r"|\mathbf A|=\sqrt{A_r^2+A_\phi^2+A_z^2}=«mag»")],
     mistake="Using the angle of the vector A instead of the azimuth of the point P in the unit vectors.",
     vals={"ph": _pt(1), "ar": _vc(0), "ap": _vc(1), "az": _vc(2), "mag": lambda r, p: math.sqrt(sum(v * v for v in r["values"]["vector"]))}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 3-3.2", "exam", "Vector components in spherical",
   "At the point P = (3, 4, 5) m a field has the value A = x̂ + 2ŷ + 3ẑ. Find its spherical components A_R, A_θ and A_φ at P.",
   {"type": "coord", "system": "spherical", "point": [3, 4, 5]}, "coords/convert", _cart_sph(3, 4, 5, (1, 2, 3)),
   [("A_R", lambda r: r["values"]["vector"][0], "", 1), ("A_θ", lambda r: r["values"]["vector"][1], "", 1), ("A_φ", lambda r: r["values"]["vector"][2], "", 1)],
   X(asked="The components of A along R̂, θ̂ and φ̂ at P.",
     idea="Find θ and φ of the point, write the three spherical unit vectors in Cartesian form there, and project A on each.",
     steps=[S("Angles of P.", r"\theta=«th»^\circ,\qquad\phi=«ph»^\circ"),
            S("Spherical unit vectors at P.", r"\hat R=(\sin\theta\cos\phi,\ \sin\theta\sin\phi,\ \cos\theta),\quad\hat\theta=(\cos\theta\cos\phi,\ \cos\theta\sin\phi,\ -\sin\theta),\quad\hat\phi=(-\sin\phi,\ \cos\phi,\ 0)"),
            S("Project A on each.", r"A_R=«ar»,\qquad A_\theta=«at»,\qquad A_\phi=«ap»")],
     answer="A_R = «ar», A_θ = «at», A_φ = «ap»",
     whatif=[W("…P were (3, 4, −5)?", lambda p: {**p, "u3": -5}, "θ changes, so A_R and A_θ change: A_R = «ar», A_θ = «at»; A_φ stays «ap».", r"A_R=«ar»"),
             W("…the magnitude were asked?", lambda p: p, "|A| = «mag», the same as √(1² + 2² + 3²).", r"|\mathbf A|=«mag»")],
     mistake="Writing θ̂ with +sin θ in the z component. θ̂ points away from the +z axis, so its z component is −sin θ.",
     vals={"th": _pt(1), "ph": _pt(2), "ar": _vc(0), "at": _vc(1), "ap": _vc(2), "mag": lambda r, p: math.sqrt(sum(v * v for v in r["values"]["vector"]))}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 3-3", "basic", "Cylindrical → Cartesian",
   "A point is given in cylindrical coordinates as (r, φ, z) = (2 m, 60°, 1 m), and a field there is A = r̂ + φ̂. "
   "Find the point's Cartesian coordinates and the Cartesian components of A.",
   {"type": "coord", "system": "cylindrical", "point": [1, 1.732, 1]}, "coords/convert",
   {"src": "cylindrical", "dst": "cartesian", "u1": 2, "u2": 60, "u3": 1, "A1": 1, "A2": 1, "A3": 0},
   [("x", lambda r: r["values"]["point"][0], "m", 1), ("A_x", lambda r: r["values"]["vector"][0], "", 1), ("A_y", lambda r: r["values"]["vector"][1], "", 1)],
   X(asked="x, y of the point and A_x, A_y of the field.",
     idea="The point converts with x = r cos φ, y = r sin φ. The vector converts with the same angle, through the Cartesian components of r̂ and φ̂.",
     steps=[S("Position.", r"x=r\cos\phi=«x»\ \text{m},\qquad y=r\sin\phi=«y»\ \text{m}"),
            S("Unit vectors at φ = 60° in Cartesian form.", r"\hat r=(\cos\phi,\sin\phi,0),\qquad\hat\phi=(-\sin\phi,\cos\phi,0)"),
            S("Add the contributions of r̂ and φ̂.", r"A_x=\cos\phi-\sin\phi=«ax»,\qquad A_y=\sin\phi+\cos\phi=«ay»")],
     answer="P = («x», «y», 1) m; A_x = «ax», A_y = «ay»",
     whatif=[W("…φ were 0?", lambda p: {**p, "u2": 0}, "Then r̂ = x̂ and φ̂ = ŷ: A_x = «ax», A_y = «ay».", r"A=«ax}\,\hat x+«ay»\,\hat y".replace("«ax}", "«ax»")),
             W("…A were only φ̂?", lambda p: {**p, "A1": 0}, "A_x = «ax», A_y = «ay»: the azimuthal direction at 60°.", r"\hat\phi=(«ax»,\ «ay»,\ 0)")],
     mistake="Converting the point but leaving the vector components unchanged. Vectors need the unit-vector conversion too.",
     vals={"x": _pt(0), "y": _pt(1), "ax": _vc(0), "ay": _vc(1)}), "numeric")

# ---- conceptual
_sph = {"system": "spherical", "u1": 2, "u2": 30, "u3": 0, "d1": 0.01, "d2": 1, "d3": 1}
px(T, "Ulaby & Ravaioli Sec. 3-2", "basic", "Why angles need scale factors",
   "In Cartesian coordinates a small step is simply dx, dy, dz. In spherical coordinates a step dθ or dφ is not a length. "
   "Explain the factors R and R sin θ, and why the φ step shrinks near the poles.",
   {"type": "coord", "system": "spherical"}, "coords/element", _sph, [],
   X(asked="Why spherical length elements are dR, R dθ and R sin θ dφ.",
     idea="An angle turns into a length only through the radius of the circle it sweeps along.",
     steps=[S("Changing θ moves the point along a circle of radius R, so the arc is R dθ."),
            S("Changing φ moves it along a circle of latitude, whose radius is the distance to the z-axis, R sin θ."),
            S("Near the poles sin θ → 0: the latitude circles shrink to a point, and so does the φ step.", r"dl_\phi=R\sin\theta\,d\phi")],
     answer_text="Only R is a length; θ and φ are angles. A small change dθ moves the point along a great circle of radius R, so the distance covered is R dθ. "
                 "A small change dφ moves it around a circle of latitude, whose radius is the distance from the z-axis, R sin θ, so the distance is R sin θ dφ. "
                 "These factors, h_θ = R and h_φ = R sin θ, are the scale factors. "
                 "Near a pole the latitude circle is tiny, so the same dφ covers almost no distance; at the equator it covers the most.",
     evidence_say="Engine runs at R = 2 m with dφ = 1°: the φ edge dl_φ grows with sin θ from the pole to the equator.",
     plot=Sweep("u2", [5, 15, 30, 60, 90], [("dl_φ = R sin θ dφ", _el("dl", 2), "S"), ("dl_θ = R dθ", _el("dl", 1))], "polar angle θ (°)", "edge length (m)"),
     mistake="Writing dl_φ = R dφ, forgetting sin θ.",
     vals={}), "concept")

px(T, "Ulaby & Ravaioli Sec. 3-2.3", "exam", "When is dv = R² sin θ dR dθ dφ exact?",
   "The spherical volume element treats a small region as a rectangular box. When does that give the exact volume, and how does the error behave as the steps grow?",
   {"type": "coord", "system": "spherical"}, "coords/element", _sph, [],
   X(asked="The status of dv as an approximation, and how its error depends on the step size.",
     idea="dv is the leading term of the exact volume. The region's real sides are curved, and its edges have different lengths on the inner and outer faces.",
     steps=[S("The exact volume of the region is an integral.", r"V=\int\!\!\int\!\!\int R^2\sin\theta\,dR\,d\theta\,d\phi"),
            S("dv evaluates the integrand once, at the corner point, and multiplies by the steps."),
            S("Its relative error grows with the step sizes and vanishes as they shrink, so dv is exact only in the limit.")],
     answer_text="dv = R² sin θ dR dθ dφ is exact only in the limit of infinitesimal steps. For finite steps the region is a curved wedge, "
                 "not a box: the outer face is larger than the inner one and sin θ changes across the region. "
                 "dv evaluates the integrand at one corner, so its relative error grows roughly in proportion to the steps. "
                 "That is why integrals over volumes are computed by summing many small elements, or analytically, rather than with one large dv.",
     evidence_say="Engine: dv (box formula) against the exact integrated volume as the angle steps grow from 1° to 20°.",
     plot=Sweep("d2", [1, 5, 10, 20], [("box formula dv", lambda r, p: r["values"]["dv"] * 1e6), ("exact volume", lambda r, p: r["values"]["exact_finite_volume"] * 1e6, "S")],
                "angle step dθ (°)", "volume (cm³)"),
     mistake="Using one large volume element for a finite region and calling the result exact.",
     vals={}), "concept")

px(T, "Ulaby & Ravaioli Sec. 3-3.1", "exam", "Unit vectors that change direction",
   "In Cartesian coordinates x̂ is the same everywhere, but in cylindrical coordinates r̂ is not. "
   "Why does this matter when you add two vectors given at different points, or when you integrate a vector field?",
   {"type": "coord", "system": "cylindrical"}, "coords/convert", {"src": "cylindrical", "dst": "cartesian", "u1": 1, "u2": 0, "u3": 0, "A1": 1, "A2": 0, "A3": 0}, [],
   X(asked="The consequence of position-dependent unit vectors for adding and integrating vectors.",
     idea="r̂ and φ̂ point in directions that depend on φ. Components along them at different points refer to different directions.",
     steps=[S("At azimuth φ the radial unit vector is r̂ = cos φ x̂ + sin φ ŷ.", r"\hat r(\phi=0)=\hat x,\qquad\hat r(\phi=90^\circ)=\hat y"),
            S("So 'A_r = 1' at two points describes two different vectors."),
            S("Before adding or integrating, convert to Cartesian components, whose unit vectors are constant.")],
     answer_text="The cylindrical and spherical unit vectors rotate with the point. A radial unit vector at φ = 0 is x̂, at φ = 90° it is ŷ. "
                 "Adding r-components taken at two different points therefore adds lengths along two different directions, which is meaningless. "
                 "The same trap appears in integrals: ∫ r̂ dφ around a circle is zero, not 2π r̂. "
                 "The safe method is to express the vectors in Cartesian components (or another fixed basis) before adding or integrating, and convert back afterwards if needed.",
     evidence_say="Engine runs of r̂ in Cartesian components as φ goes from 0° to 90°: its x part falls as cos φ while its y part rises as sin φ.",
     plot=Sweep("u2", [0, 15, 30, 45, 60, 75, 90], [("x component of r̂", _vc(0)), ("y component of r̂", _vc(1), "S")], "azimuth φ (°)", "component of r̂"),
     mistake="Pulling r̂ or φ̂ outside an integral over φ as if they were constant.",
     vals={}), "concept")

px(T, "Ulaby & Ravaioli Sec. 3-3", "basic", "Why θ stops at 180° but φ goes to 360°",
   "In spherical coordinates θ runs from 0 to 180° while φ runs from 0 to 360°. Why not both to 360°?",
   {"type": "coord", "system": "spherical", "point": [1, 1, -1]}, "coords/convert", _cart_sph(1, 1, -1), [],
   X(asked="Why the ranges of θ and φ differ.",
     idea="Each point in space must get one set of coordinates. φ already sweeps a full circle around the z-axis, so θ only needs to go from the top to the bottom.",
     steps=[S("φ turns the half-plane containing the z-axis through a full turn, 0 to 360°."),
            S("Within that half-plane, θ from 0 (along +z) to 180° (along −z) already reaches every direction."),
            S("Letting θ go beyond 180° would describe the same points twice, with φ shifted by 180°.")],
     answer_text="Spherical coordinates must label every point once. The azimuth φ rotates a half-plane bounded by the z-axis through a full turn, which takes 360°. "
                 "Inside each half-plane, θ measured from +z reaches straight down to −z at 180°, so every direction is already covered. "
                 "A θ of 200° would point into the opposite half-plane, which is the same as θ = 160° with φ increased by 180°: a duplicate label. "
                 "For example, (1, 1, −1) has θ = «th»°, above 90° because it lies below the xy-plane, and φ = «ph»°.",
     evidence_say="Engine conversion of (1, 1, −1): θ = «th»°, φ = «ph»°.",
     mistake="Measuring θ from the xy-plane (that is latitude or elevation) instead of from the +z axis.",
     vals={"th": _pt(1), "ph": _pt(2)}), "concept")

px(T, "Ulaby & Ravaioli Sec. 3-3", "basic", "Does the length of a vector depend on the coordinates?",
   "The field A = x̂ + 2ŷ + 3ẑ has very different-looking components in spherical coordinates at the point (3, 4, 5). Is its magnitude different there? Why or why not?",
   {"type": "coord", "system": "spherical", "point": [3, 4, 5]}, "coords/convert", _cart_sph(3, 4, 5, (1, 2, 3)), [],
   X(asked="Whether a change of coordinate system can change a vector's length.",
     idea="A coordinate system only describes the vector; it does not change it. All three systems use orthonormal unit vectors, and a rotation between orthonormal bases preserves length.",
     steps=[S("The spherical unit vectors at a point are orthonormal, like x̂, ŷ, ẑ."),
            S("The conversion is a rotation matrix, which keeps lengths and angles."),
            S("So |A| from spherical components equals √(1² + 2² + 3²): here «mag».", r"\sqrt{A_R^2+A_\theta^2+A_\phi^2}=«mag»")],
     answer_text="No. The vector is a physical quantity; the coordinate system is only a way of writing it down. "
                 "At any point the spherical unit vectors R̂, θ̂, φ̂ are mutually perpendicular and of unit length, just like x̂, ŷ, ẑ, so converting between them is a rotation. "
                 "Rotations preserve lengths and angles, so √(A_R² + A_θ² + A_φ²) equals √(A_x² + A_y² + A_z²). "
                 "The individual components change because they measure projections on different directions; the length and the direction in space do not.",
     evidence_say="Engine: the spherical components give |A| = «mag»; its check confirms that the unit vectors at the point are orthonormal.",
     mistake="Adding components from different systems, e.g. A_x + A_R, which mixes projections on different directions.",
     vals={"mag": lambda r, p: math.sqrt(sum(v * v for v in r["values"]["vector"]))}), "concept")

px(T, "Ulaby & Ravaioli Sec. 3-2", "basic", "Cylindrical r versus spherical R",
   "Both cylindrical and spherical coordinates have a 'radial' coordinate. For the point (3, 4, 5) m, what is the difference between the cylindrical r and the spherical R?",
   {"type": "coord", "system": "spherical", "point": [3, 4, 5]}, "coords/convert", _cart_sph(3, 4, 5), [],
   X(asked="The meaning of r and R, and their values at (3, 4, 5).",
     idea="Cylindrical r is the distance from the z-axis. Spherical R is the distance from the origin. They differ whenever z ≠ 0.",
     steps=[S("Spherical R: straight-line distance from the origin.", r"R=\sqrt{x^2+y^2+z^2}=«R»\ \text{m}"),
            S("Cylindrical r: distance from the z-axis, ignoring z.", r"r=\sqrt{x^2+y^2}=R\sin\theta=«r»\ \text{m}"),
            S("They are equal only in the xy-plane (θ = 90°).")],
     answer_text="Cylindrical r measures how far the point is from the z-axis; spherical R measures how far it is from the origin. "
                 "They are related by r = R sin θ, and R = √(r² + z²). For (3, 4, 5) m the point is «r» m from the z-axis and «R» m from the origin. "
                 "The difference matters in formulas: the field of a line charge falls as 1/r, the field of a point charge as 1/R². "
                 "Mixing them up is one of the commonest sources of wrong answers.",
     evidence_say="Engine: R = «R» m and θ = «th»°, so r = R sin θ = «r» m.",
     mistake="Using R where r is meant (or the reverse) in field formulas.",
     vals={"R": _pt(0), "th": _pt(1), "r": lambda r, p: r["values"]["point"][0] * math.sin(math.radians(r["values"]["point"][1]))}), "concept")

px(T, "Ulaby & Ravaioli Sec. 3-2.3", "exam", "Why the sphere's surface integrates to 4πa²",
   "Show that integrating the surface element ds_R = R² sin θ dθ dφ over a sphere of radius a gives 4πa², and explain where the sin θ comes from.",
   {"type": "coord", "system": "spherical"}, "coords/element", {"system": "spherical", "u1": 1, "u2": 60, "u3": 0, "d1": 0.01, "d2": 1, "d3": 1}, [],
   X(asked="A derivation of the surface area of a sphere from ds_R.",
     idea="The surface element is the product of the two tangential edges, R dθ and R sin θ dφ. Integrating over all θ and φ adds up every patch.",
     steps=[S("Surface element on R = a.", r"ds_R=(a\,d\theta)(a\sin\theta\,d\phi)=a^2\sin\theta\,d\theta\,d\phi"),
            S("Integrate φ over a full turn and θ from pole to pole.", r"\oint ds_R=a^2\int_0^{2\pi}\!d\phi\int_0^{\pi}\sin\theta\,d\theta=a^2\cdot2\pi\cdot2=4\pi a^2"),
            S("sin θ is there because patches near the poles are narrower: their φ edge is a sin θ dφ.")],
     answer_text="On the sphere R = a, a small patch has sides a dθ (along a meridian) and a sin θ dφ (along a circle of latitude), so ds_R = a² sin θ dθ dφ. "
                 "Integrating φ from 0 to 2π gives 2π, and integrating sin θ from 0 to π gives 2, so the total is 4πa². "
                 "The sin θ is essential: without it the integral would be 2π²a², because patches near the poles would be counted as wide as those at the equator.",
     evidence_say="Engine check: summing ds_R numerically over a sphere reproduces 4πa².",
     mistake="Dropping sin θ, or integrating θ from 0 to 2π, which counts the sphere twice.",
     vals={}), "concept")

px(T, "Ulaby & Ravaioli Sec. 3-2", "exam", "Why the order R̂, θ̂, φ̂ matters",
   "The spherical unit vectors are always listed as (R̂, θ̂, φ̂), with R̂ × θ̂ = φ̂. What would go wrong if you used the order (R̂, φ̂, θ̂) in a cross product or a curl?",
   {"type": "coord", "system": "spherical"}, "coords/element", _sph, [],
   X(asked="The role of right-handedness in the order of the unit vectors.",
     idea="Cross products and curls are defined for right-handed bases. Swapping two basis vectors makes the basis left-handed and flips the sign of every cross product.",
     steps=[S("In a right-handed basis the first two vectors cross to the third.", r"\hat R\times\hat\theta=\hat\phi,\quad\hat\theta\times\hat\phi=\hat R,\quad\hat\phi\times\hat R=\hat\theta"),
            S("With the order (R̂, φ̂, θ̂) the same determinant formula would give R̂ × φ̂ = θ̂, but in fact R̂ × φ̂ = −θ̂."),
            S("Every cross product, curl and therefore every B from Biot–Savart or force F = qv × B would come out with the wrong sign.")],
     answer_text="The order is chosen so that the basis is right-handed, like (x̂, ŷ, ẑ): R̂ × θ̂ = φ̂ and its cyclic versions. "
                 "Cross products and curls computed with the usual determinant formulas assume this. "
                 "Listing the vectors as (R̂, φ̂, θ̂) makes the basis left-handed, and the same formulas then give every cross product with the wrong sign. "
                 "Magnetic fields from Biot–Savart, the Lorentz force and the direction of the Poynting vector would all point the wrong way.",
     evidence_say="Engine check: R̂ × θ̂ = φ̂ holds at the point used here, confirming a right-handed basis.",
     mistake="Writing the spherical components in the order (R, φ, θ) and then using the standard curl formula.",
     vals={}), "concept")

# ---------------------------------------------------------------- electrostatics
T = "electrostatics"
nC = 1e-9
# Explained (engine/explain.py): 7 numerical + 8 conceptual.
_pair = {"charges": [{"q": 2 * nC, "x": -0.1, "y": 0}, {"q": -2 * nC, "x": 0.1, "y": 0}], "probe": [0, 0.1]}
_GP = lambda k: (lambda r, p: r["profile"][k])

px(T, "Ulaby & Ravaioli Sec. 4-3", "basic", "Field of a point charge",
   "A 5 nC point charge sits in free space. Find the magnitude of the electric field and the potential (taking V = 0 at infinity) at a point 0.3 m away.",
   {"type": "charges", "charges": [[5, 0, 0]], "probe": [0.3, 0]}, "es/charges", {"charges": [{"q": 5 * nC, "x": 0, "y": 0}], "probe": [0.3, 0]},
   [("|E|", V("E_mag"), "V/m", 1), ("V", V("V"), "V", 1)],
   X(asked="|E| and V at 0.3 m from a 5 nC charge.",
     idea="Coulomb's law gives the field of a point charge, radial and falling as 1/R²; the potential, its line integral from infinity, falls as 1/R.",
     steps=[S("Field magnitude.", r"|\mathbf E|=\frac{q}{4\pi\varepsilon_0R^2}=«E»\ \text{V/m}"),
            S("Potential with V(∞) = 0.", r"V=\frac{q}{4\pi\varepsilon_0R}=«V»\ \text{V}"),
            S("Check: for a point charge |E| = V/R, which holds here.")],
     answer="|E| = «E» V/m, V = «V» V",
     whatif=[W("…the distance were doubled?", lambda p: {**p, "probe": [0.6, 0]}, "E falls to a quarter («E» V/m), V only to a half («V» V).", r"|\mathbf E|\propto\frac1{R^2},\qquad V\propto\frac1R"),
             W("…the charge were −5 nC?", lambda p: {**p, "charges": [{"q": -5 * nC, "x": 0, "y": 0}]}, "|E| is unchanged («E» V/m) but points inward, and V becomes «V» V.", r"V=«V»\ \text{V}")],
     mistake="Using 1/R for the field or 1/R² for the potential.",
     vals={"E": EV("E_mag"), "V": EV("V")}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 4-3", "exam", "Field of a charge pair",
   "Charges of +2 nC and −2 nC sit at (−0.1, 0) m and (0.1, 0) m in free space. Find the electric field (magnitude and direction) at P = (0, 0.1) m.",
   {"type": "charges", "charges": [[2, -0.1, 0], [-2, 0.1, 0]], "probe": [0, 0.1]}, "es/charges", _pair, [("|E|", V("E_mag"), "V/m", 1)],
   X(asked="The total electric field vector at P.",
     idea="Superpose the two Coulomb fields as vectors. By symmetry the y-components cancel and the x-components add.",
     steps=[S("Both charges are the same distance R = √2 × 0.1 m from P.", r"R_1=R_2=R=\sqrt{0.1^2+0.1^2}\ \text{m}"),
            S("Each field has magnitude q/(4πε₀R²); the positive charge pushes away from (−0.1, 0), the negative one pulls toward (0.1, 0).", r"|\mathbf E_1|=|\mathbf E_2|=\frac{q}{4\pi\varepsilon_0R^2}"),
            S("Add the components: both point partly in +x and their y parts cancel.", r"E_x=«ex}\ \text{V/m},\qquad E_y=«ey»\ \text{V/m}".replace("«ex}", "«ex»")),
            S("Magnitude.", r"|\mathbf E|=«E»\ \text{V/m}\ \text{along}\ +\hat x")],
     answer="E = «E» V/m along +x",
     whatif=[W("…both charges were +2 nC?", lambda p: {**p, "charges": [{"q": 2 * nC, "x": -0.1, "y": 0}, {"q": 2 * nC, "x": 0.1, "y": 0}]},
               "Now the x-parts cancel and the y-parts add: E_x = «ex» V/m, E_y = «ey» V/m.", r"|\mathbf E|=«E»\ \text{V/m}"),
             W("…the potential at P were asked?", lambda p: p, "V = «V» V: equal distances and opposite charges cancel.", r"V=\frac{1}{4\pi\varepsilon_0}\Big(\frac{q}{R}-\frac{q}{R}\Big)=«V»")],
     mistake="Adding the two magnitudes, which ignores that half of each field cancels.",
     vals={"ex": EV("E", 0), "ey": EV("E", 1), "E": EV("E_mag"), "V": EV("V")}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 4-4", "exam", "Inside a charged sphere",
   "A non-conducting sphere of radius 5 cm carries a uniform volume charge density of 2 µC/m³ in free space. Find |E| at 2 cm from its centre, and at 8 cm.",
   {"type": "sphere", "a": 0.05, "r": 0.02}, "es/gauss", {"kind": "sphere", "rho": 2e-6, "a": 0.05, "r": 0.02}, [("|E| at 2 cm", V("E"), "V/m", 1)],
   X(asked="|E| inside the sphere (2 cm), and outside it (8 cm) as a follow-up.",
     idea="Spherical symmetry: D is radial and the same on any concentric sphere, so Gauss's law needs only the enclosed charge.",
     steps=[S("Charge inside the Gaussian sphere of radius R = 2 cm, which lies inside the charge.", r"Q_{enc}=\rho_v\tfrac43\pi R^3=«Q»\ \text{C}"),
            S("Gauss's law.", r"D\,4\pi R^2=Q_{enc}\ \Rightarrow\ D=\frac{\rho_vR}{3}=«D»\ \text{C/m}^2"),
            S("Field.", r"E=\frac{D}{\varepsilon_0}=\frac{\rho_vR}{3\varepsilon_0}=«E»\ \text{V/m}")],
     answer="|E(2 cm)| = «E» V/m",
     whatif=[W("…the point were at 8 cm (outside)?", lambda p: {**p, "r": 0.08}, "All the charge is enclosed and the sphere acts like a point charge: E = «E» V/m.", r"E=\frac{\rho_va^3}{3\varepsilon_0R^2}=«E»\ \text{V/m}"),
             W("…the point were at the surface (5 cm)?", lambda p: {**p, "r": 0.05}, "Both formulas give the maximum field: E = «E» V/m.", r"E=\frac{\rho_va}{3\varepsilon_0}=«E»\ \text{V/m}")],
     mistake="Using the total charge for a point inside. Only the charge closer to the centre than R counts.",
     plot=Series(_GP("r"), [("|E|", _GP("E"), "E")], "distance from centre R (m)", "|E| (V/m)"),
     evidence_say="Engine profile: E rises linearly inside the sphere and falls as 1/R² outside.",
     vals={"Q": EV("Q_enc"), "D": EV("D"), "E": EV("E")}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 4-4", "basic", "Infinite line charge",
   "A long straight wire carries 10 nC per metre in air. Find the electric field 0.5 m from the wire, and the potential difference between 0.5 m and 1 m.",
   {"type": "line", "r": 0.5}, "es/gauss", {"kind": "line", "rho": 1e-8, "a": 0.01, "b": 1, "r": 0.5}, [("|E|", V("E"), "V/m", 1)],
   X(asked="|E| at 0.5 m, and V(0.5 m) − V(1 m).",
     idea="Cylindrical symmetry: a coaxial cylinder of length ℓ is the Gaussian surface. Only its curved side carries flux.",
     steps=[S("Gauss's law on a cylinder of radius r.", r"E\cdot2\pi r\ell=\frac{\rho_\ell\ell}{\varepsilon_0}\ \Rightarrow\ E=\frac{\rho_\ell}{2\pi\varepsilon_0r}=«E»\ \text{V/m}"),
            S("Integrate E from 0.5 m to 1 m for the potential difference.", r"V(0.5)-V(1)=\frac{\rho_\ell}{2\pi\varepsilon_0}\ln\frac{1}{0.5}=«dv»\ \text{V}")],
     answer="|E| = «E» V/m; V(0.5 m) − V(1 m) = «dv» V",
     whatif=[W("…the distance were doubled?", lambda p: {**p, "r": 1.0}, "E ∝ 1/r: «E» V/m.", r"E=«E»\ \text{V/m}"),
             W("…the potential at 0.5 m were asked, with V = 0 at infinity?", lambda p: p, "It cannot be: for an infinite line the potential diverges logarithmically, so a finite reference distance must be chosen.", None)],
     mistake="Taking V = 0 at infinity for an infinite line charge.",
     vals={"E": EV("E"), "dv": EV("V")}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 4-9", "basic", "Coaxial capacitance",
   "A coaxial cable has an inner conductor of radius 1 mm, an outer conductor of radius 4 mm, and polyethylene insulation (εr = 2.25). Find its capacitance per metre.",
   {"type": "coax", "a": 1, "b": 4}, "es/capacitor", {"kind": "coax", "a": 1e-3, "b": 4e-3, "eps_r": 2.25, "length": 1}, [("C′", V("C"), "pF/m", 1e12)],
   X(asked="The capacitance per unit length of the coax.",
     idea="Put charge ρℓ on the inner conductor, find E with Gauss's law, integrate across the gap for V, and divide.",
     steps=[S("Field in the insulation.", r"E=\frac{\rho_\ell}{2\pi\varepsilon r}"),
            S("Voltage between the conductors.", r"V=\frac{\rho_\ell}{2\pi\varepsilon}\ln\frac{b}{a}"),
            S("Capacitance per metre.", r"C'=\frac{2\pi\varepsilon}{\ln(b/a)}=«C»\ \text{pF/m}")],
     answer="C′ = «C» pF/m",
     whatif=[W("…the insulation were air?", lambda p: {**p, "eps_r": 1}, "C′ ∝ ε: «C» pF/m.", r"C'=«C»\ \text{pF/m}"),
             W("…the outer radius were 8 mm?", lambda p: {**p, "b": 8e-3}, "ln(b/a) grows from ln 4 to ln 8, so C′ drops to «C» pF/m.", r"C'=«C»\ \text{pF/m}")],
     mistake="Using log₁₀ instead of the natural logarithm.",
     vals={"C": lambda r, p: r["values"]["C"] * 1e12}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 4-9, 4-10", "basic", "Parallel-plate capacitor and energy",
   "Two plates of area 10 cm² are 0.5 mm apart, with a dielectric of εr = 4 between them, and 12 V is applied. Neglecting fringing, find the capacitance, the stored energy and the field in the gap.",
   {"type": "plates", "d": 0.5}, "es/capacitor", {"kind": "parallel", "A": 1e-3, "d": 5e-4, "eps_r": 4, "V0": 12},
   [("C", V("C"), "pF", 1e12), ("W", V("W"), "nJ", 1e9)],
   X(asked="C, the stored energy W and the field E between the plates.",
     idea="With fringing neglected the field is uniform, E = V/d, and the charge on each plate is Q = εEA.",
     steps=[S("Capacitance.", r"C=\frac{\varepsilon A}{d}=«C»\ \text{pF}"),
            S("Uniform field.", r"E=\frac{V}{d}=«E»\ \text{V/m}"),
            S("Stored energy.", r"W=\tfrac12CV^2=«W»\ \text{nJ}")],
     answer="C = «C» pF, W = «W» nJ, E = «E» V/m",
     whatif=[W("…the voltage were doubled?", lambda p: {**p, "V0": 24}, "W ∝ V², so it quadruples to «W» nJ.", r"W=«W»\ \text{nJ}"),
             W("…the gap were filled with air?", lambda p: {**p, "eps_r": 1}, "C and W at fixed V drop by 4: C = «C» pF, W = «W» nJ.", r"C=«C»\ \text{pF}")],
     mistake="Forgetting εr in C, or the ½ in the energy.",
     vals={"C": lambda r, p: r["values"]["C"] * 1e12, "W": lambda r, p: r["values"]["W"] * 1e9, "E": EV("E_max")}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 4-9", "basic", "Spherical capacitor",
   "Two concentric metal spheres of radii 5 cm and 10 cm are separated by air. Find the capacitance, and its limit when the outer sphere is moved very far away.",
   {"type": "coax", "a": 5, "b": 10, "label": "a = 5 cm, b = 10 cm (concentric spheres)"}, "es/capacitor", {"kind": "spherical", "a": 0.05, "b": 0.1, "eps_r": 1},
   [("C", V("C"), "pF", 1e12)],
   X(asked="C of two concentric spheres, and the isolated-sphere limit.",
     idea="Charge Q on the inner sphere gives a point-charge field between the spheres; integrate it to get V.",
     steps=[S("Field between the spheres.", r"E=\frac{Q}{4\pi\varepsilon R^2}"),
            S("Potential difference.", r"V=\frac{Q}{4\pi\varepsilon}\Big(\frac1a-\frac1b\Big)"),
            S("Capacitance.", r"C=\frac{4\pi\varepsilon}{1/a-1/b}=«C»\ \text{pF}")],
     answer="C = «C» pF",
     whatif=[W("…the outer sphere were very far away?", lambda p: {**p, "b": 10.0}, "With b = 10 m (200a), C is within 0.5 % of 4πε₀a, the capacitance of an isolated sphere: «C» pF.", r"C\to4\pi\varepsilon a=«C»\ \text{pF}"),
             W("…the gap were filled with εr = 3?", lambda p: {**p, "eps_r": 3}, "C = «C» pF.", r"C=«C»\ \text{pF}")],
     mistake="Writing 1/b − 1/a, which gives a negative capacitance.",
     vals={"C": lambda r, p: r["values"]["C"] * 1e12}), "numeric")

# ---- conceptual
px(T, "Ulaby & Ravaioli Sec. 4-5", "basic", "Zero potential, non-zero field",
   "On the perpendicular bisector of a +q, −q pair the potential is zero everywhere, yet the electric field there is not. How can both be true?",
   {"type": "charges", "charges": [[2, -0.1, 0], [-2, 0.1, 0]], "probe": [0, 0.1]}, "es/charges", _pair, [],
   X(asked="How V = 0 and E ≠ 0 can hold at the same point.",
     idea="E is minus the gradient of V. A potential that is zero along a line can still change across that line.",
     steps=[S("Every point of the bisector is equally far from +q and −q, so their potentials cancel.", r"V=\frac{1}{4\pi\varepsilon_0}\Big(\frac{q}{R}-\frac{q}{R}\Big)=0"),
            S("E = −∇V depends on how V changes in space. Along the bisector V does not change, but across it, towards the charges, it does."),
            S("So E points across the bisector, here along +x, with magnitude «E» V/m.")],
     answer_text="V = 0 is the value of the potential; the field is its rate of change, E = −∇V. "
                 "On the bisector the contributions of +q and −q cancel, so V is zero all along that line, and therefore E has no component along it. "
                 "Stepping off the bisector towards +q raises V and stepping towards −q lowers it, so V changes across the line and E points from the positive side to the negative side. "
                 "A zero value of the potential says nothing about the field, just as a road at sea level can still be steep.",
     evidence_say="Engine at (0, 0.1) m: V = «V» V while |E| = «E» V/m; its check confirms E = −∇V there.",
     mistake="Concluding that E = 0 wherever V = 0.",
     vals={"V": EV("V"), "E": EV("E_mag")}), "concept")

px(T, "Ulaby & Ravaioli Sec. 4-4", "exam", "Why E grows inside a charged sphere",
   "For a uniformly charged solid sphere, the field inside grows in proportion to the distance from the centre, while outside it falls as 1/R². Explain both, and why the field is largest at the surface.",
   {"type": "sphere", "a": 0.05, "r": 0.03}, "es/gauss", {"kind": "sphere", "rho": 2e-6, "a": 0.05, "r": 0.03}, [],
   X(asked="The shape of E(R) inside and outside a uniformly charged sphere.",
     idea="Gauss's law: E·4πR² = Q_enc/ε₀. Inside, the enclosed charge grows as R³; outside, it is the total Q.",
     steps=[S("Inside: Q_enc ∝ R³, while the surface grows as R², so E ∝ R.", r"E=\frac{\rho_vR}{3\varepsilon_0}\quad(R<a)"),
            S("Outside: Q_enc is fixed, so E ∝ 1/R², like a point charge.", r"E=\frac{\rho_va^3}{3\varepsilon_0R^2}\quad(R>a)"),
            S("The two formulas meet at R = a, where E reaches its maximum.")],
     answer_text="Gauss's law sets E·4πR² equal to the enclosed charge over ε₀. Inside the sphere the enclosed charge is ρv·(4/3)πR³, which grows faster than the area 4πR², "
                 "so E = ρvR/(3ε₀) increases linearly from zero at the centre. Outside, the whole charge is enclosed and fixed, so E falls as 1/R², exactly as if the charge sat at the centre. "
                 "Both formulas give the same value at R = a, so E is continuous and peaks at the surface. At the centre E = 0 by symmetry.",
     evidence_say="Engine profile of |E| from the centre outwards: a straight rise to the surface, then a 1/R² fall.",
     plot=Series(_GP("r"), [("|E|", _GP("E"), "E")], "distance from centre R (m)", "|E| (V/m)"),
     mistake="Treating the inside like a conductor (E = 0) or like a point charge (E ∝ 1/R²).",
     vals={}), "concept")

px(T, "Ulaby & Ravaioli Sec. 4-4", "basic", "Why a charged sheet's field does not fade",
   "The field of a large, uniformly charged flat sheet has the same strength at 1 cm and at 1 m from it. Why does it not weaken with distance, unlike that of a point charge?",
   {"type": "plates", "d": None}, "es/gauss", {"kind": "sheet", "rho": 1e-9, "r": 0.3}, [],
   X(asked="Why E of an infinite sheet is independent of distance.",
     idea="By symmetry the field lines are straight and perpendicular to the sheet: they never spread apart, so their density cannot fall.",
     steps=[S("Use a pill-box with faces of area A on both sides of the sheet.", r"2EA=\frac{\rho_sA}{\varepsilon_0}\ \Rightarrow\ E=\frac{\rho_s}{2\varepsilon_0}=«E»\ \text{V/m}"),
            S("The face area A cancels and no distance appears: the field is uniform on each side."),
            S("A real sheet of finite size looks infinite only from distances much smaller than its width; far away it acts like a point charge.")],
     answer_text="For an infinite sheet, symmetry forces E to be perpendicular to the sheet and equal at equal distances. "
                 "A pill-box straddling the sheet then gives 2EA = ρsA/ε₀, so E = ρs/(2ε₀), with no distance in the result. "
                 "Geometrically, the field lines are parallel straight lines that never spread apart, so the line density, and therefore E, stays the same. "
                 "A point charge's lines spread over spheres, which is why its field falls as 1/R². "
                 "A finite sheet behaves this way only close to its surface compared with its size.",
     evidence_say="Engine: E = «E» V/m for ρs = 1 nC/m², the same at any distance in the infinite-sheet model.",
     mistake="Applying the infinite-sheet result far from a finite plate.",
     vals={"E": EV("E")}), "concept")

px(T, "Ulaby & Ravaioli Sec. 4-5", "exam", "E can jump but V cannot",
   "At the surface of a charged sheet the electric field jumps, but the potential is continuous. Why must V be continuous, even where E is not?",
   {"type": "sphere", "a": 0.05, "r": 0.05}, "es/gauss", {"kind": "shell", "rho": 1e-8, "a": 0.05, "r": 0.05}, [],
   X(asked="Why the potential is continuous across a surface charge.",
     idea="V is the line integral of E. A finite E over a vanishing distance contributes nothing to the integral.",
     steps=[S("The potential difference across a thin layer of thickness Δh is the field times Δh.", r"V_1-V_2=-\int\mathbf E\cdot d\mathbf l\approx E\,\Delta h"),
            S("As Δh → 0 with E finite, the difference goes to zero, even if E differs on the two sides."),
            S("Only an infinite field, such as that of a dipole layer, could make V jump.")],
     answer_text="The potential is defined by the line integral of the field, V₁ − V₂ = −∫E·dl. "
                 "Crossing a surface charge means integrating a finite field over an infinitely short path, so the potential change across the surface is zero, even though E is different on the two sides. "
                 "The jump in E is a jump in the slope of V, not in V itself. "
                 "For a charged spherical shell, E is zero inside and Q/(4πε₀R²) outside, while V is constant inside and continuous at R = a.",
     evidence_say="Engine profile for a charged spherical shell: |E| steps up at the surface while V has only a kink there.",
     plot=Series(_GP("r"), [("|E| (V/m)", _GP("E"), "E"), ("V (V)", _GP("V"))], "distance from centre R (m)", "value"),
     mistake="Assuming the potential must be zero wherever the field is zero (inside a shell it is constant, not zero).",
     vals={}), "concept")

px(T, "Ulaby & Ravaioli Sec. 4-9", "exam", "Where a coaxial cable breaks down",
   "In a coaxial cable under voltage, where is the electric field strongest, and why does insulation breakdown normally start there? How does the inner radius affect it?",
   {"type": "coax", "a": 1, "b": 4}, "es/capacitor", {"kind": "coax", "a": 1e-3, "b": 4e-3, "eps_r": 2.25, "V0": 1000}, [],
   X(asked="The location of the maximum field in a coax and the role of the inner radius.",
     idea="Between the conductors E = V/(r ln(b/a)), which is largest at the smallest radius, r = a.",
     steps=[S("Field in the gap.", r"E(r)=\frac{V}{r\ln(b/a)},\qquad E_{max}=E(a)=«Em»\ \text{V/m}\ \text{at 1 kV}"),
            S("Breakdown starts where E first reaches the dielectric strength: at the inner conductor's surface."),
            S("A thinner inner conductor raises E(a), but a thicker one shrinks ln(b/a); the best compromise is a = b/e.")],
     answer_text="Gauss's law gives E = V/(r ln(b/a)) between the conductors, so the field is strongest at the surface of the inner conductor, r = a. "
                 "Insulation fails where the field first exceeds its dielectric strength, so breakdown starts there. "
                 "Making the inner conductor thinner concentrates the field further; making it thicker reduces ln(b/a), which also raises E(a). "
                 "For a fixed outer radius the breakdown voltage E_bd·a·ln(b/a) is largest when ln(b/a) = 1, i.e. a = b/e.",
     evidence_say="Engine runs at 1 kV with b = 4 mm: the maximum field at the inner conductor as a varies; the minimum sits near a = b/e.",
     plot=Sweep("a", [0.4e-3, 0.8e-3, 1.2e-3, 1.47e-3, 2e-3, 2.6e-3, 3.2e-3], [("E_max at r = a", EV("E_max"), "E")], "inner radius a (m)", "E_max (V/m)"),
     mistake="Thinking the field is uniform across the gap, as in a parallel-plate capacitor.",
     vals={"Em": EV("E_max")}), "concept")

px(T, "Ulaby & Ravaioli Sec. 4-10", "exam", "Dielectric in a capacitor: more or less energy?",
   "A dielectric slab is slid into an air-filled capacitor. Does the stored energy go up or down (a) if the capacitor stays connected to the battery, and (b) if it was charged and then disconnected?",
   {"type": "plates", "d": 0.5}, "es/capacitor", {"kind": "parallel", "A": 1e-3, "d": 5e-4, "eps_r": 1, "V0": 12}, [],
   X(asked="The change of stored energy when εr increases at fixed V and at fixed Q.",
     idea="C = εA/d grows by εr. Which formula for W to use depends on what stays fixed: V (battery connected) or Q (isolated).",
     steps=[S("Battery connected, V fixed: W = ½CV² grows with C.", r"W=\tfrac12CV^2\propto\varepsilon_r"),
            S("Disconnected, Q fixed: W = Q²/2C shrinks as C grows.", r"W=\frac{Q^2}{2C}\propto\frac{1}{\varepsilon_r}"),
            S("In case (b) the field does work pulling the slab in; in case (a) the battery supplies twice the energy gained by the capacitor.")],
     answer_text="Inserting the dielectric multiplies C by εr. (a) With the battery connected V stays fixed, so W = ½CV² rises by εr; "
                 "the battery delivers extra charge and supplies twice the energy increase, the other half going into the mechanical work of pulling the slab in. "
                 "(b) With the capacitor isolated, Q stays fixed and W = Q²/2C falls by εr; the lost energy is the work done by the field drawing the slab in. "
                 "In both cases the slab is pulled into the gap.",
     evidence_say="Engine runs at a fixed 12 V: the stored energy grows in proportion to εr.",
     plot=Sweep("eps_r", [1, 2, 3, 4, 6], [("W at fixed V", lambda r, p: r["values"]["W"] * 1e9, "E")], "relative permittivity εr", "stored energy (nJ)"),
     mistake="Using W = ½CV² when the charge, not the voltage, is fixed.",
     vals={}), "concept")

px(T, "Ulaby & Ravaioli Sec. 4-9", "basic", "When is C = εA/d accurate?",
   "The parallel-plate formula C = εA/d ignores fringing. For what plate geometry is it a good approximation, and in which direction does fringing change the true capacitance?",
   {"type": "plates", "d": 0.5}, "es/capacitor", {"kind": "parallel", "A": 1e-3, "d": 5e-4, "eps_r": 1, "V0": 1}, [],
   X(asked="The validity condition of C = εA/d and the effect of fringing.",
     idea="The formula assumes a uniform field confined between the plates. Near the edges the field bulges outwards, which the formula ignores.",
     steps=[S("The uniform-field picture holds over most of the plates if the gap is much smaller than their width: d ≪ √A."),
            S("Fringing adds field, and therefore charge, near the edges, so the true C is a little larger than εA/d."),
            S("For 10 cm² plates 0.5 mm apart the plate width is tens of times the gap, so the formula is good to a few per cent.",r"C=\frac{\varepsilon_0A}{d}=«C»\ \text{pF}")],
     answer_text="C = εA/d assumes the field is uniform and stays between the plates. That is accurate when the gap is much smaller than the plate dimensions, d ≪ √A, "
                 "because the edge region where the field bulges outwards is then a small fraction of the area. "
                 "Fringing fields add extra charge near the edges, so the real capacitance is slightly larger than εA/d, never smaller. "
                 "For plates whose width is comparable to the gap the formula fails badly and a numerical field solution is needed.",
     evidence_say="Engine (fringing neglected): C = «C» pF for 10 cm² plates 0.5 mm apart in air.",
     mistake="Assuming fringing reduces C.",
     vals={"C": lambda r, p: r["values"]["C"] * 1e12}), "concept")

px(T, "Ulaby & Ravaioli Sec. 4-4", "exam", "Gauss's law: always true, not always useful",
   "Gauss's law holds for any closed surface and any charge distribution. Why can it give the field of a point charge or a sphere in one line, but not the field of two charges?",
   {"type": "charges", "charges": [[2, -0.1, 0], [-2, 0.1, 0]], "probe": [0, 0.1]}, "es/charges", _pair, [],
   X(asked="Why Gauss's law determines E only for highly symmetric charge distributions.",
     idea="Gauss's law fixes the total flux, an integral of E. To get E itself you must already know that E is constant and perpendicular on the surface.",
     steps=[S("The law fixes only the surface integral.", r"\oint\mathbf E\cdot d\mathbf s=\frac{Q_{enc}}{\varepsilon_0}"),
            S("With spherical, cylindrical or planar symmetry, E is constant on a suitable surface and comes out of the integral."),
            S("For a charge pair no such surface exists: a sphere around both encloses zero net charge, yet E on it is not zero.")],
     answer_text="Gauss's law is always true, but it only states the total flux through a closed surface. "
                 "To extract E you need a surface on which symmetry makes E constant in size and perpendicular to the surface, so the integral becomes E times the area. "
                 "Point charges, spheres, infinite lines and planes have such surfaces. For two charges there is none: "
                 "a sphere enclosing a +q, −q pair has zero net flux, yet the field on it is far from zero, because outward and inward flux cancel. "
                 "Such problems are solved by superposition of Coulomb fields instead.",
     evidence_say="Engine checks for the ±2 nC pair: the flux through a sphere around each charge is q/ε₀, and through a sphere around both it is zero, while |E| at (0, 0.1) is «E» V/m.",
     mistake="Concluding that E = 0 on a surface because the enclosed charge is zero.",
     vals={"E": EV("E_mag")}), "concept")

# ---------------------------------------------------------------- images
T = "images"
# Explained (engine/explain.py): 7 numerical + 8 conceptual. Grounded, perfectly conducting planes.
_rs = lambda k: (lambda r, p: r["rho_s"][k])

px(T, "Ulaby & Ravaioli Sec. 4-11", "basic", "Force from the image",
   "A 1 nC point charge is held 0.4 m above a large grounded metal plate in air. With what force is it pulled towards the plate?",
   {"type": "plane", "d": 0.4}, "img/plane", {"Q": 1e-9, "d": 0.4}, [("F", V("F"), "nN", 1e9)],
   X(asked="The attractive force between a point charge and a grounded plane.",
     idea="Above the plate, the field of the charge plus the induced surface charge equals the field of the charge plus an image −Q at the mirror point, 2d away.",
     steps=[S("Replace the plate by an image charge −Q at distance d below its surface.", r"Q'=-Q\ \text{at}\ z=-d"),
            S("The real charge feels the image's Coulomb force across the distance 2d.", r"F=\frac{Q^2}{4\pi\varepsilon_0(2d)^2}=\frac{Q^2}{16\pi\varepsilon_0d^2}=«F»\ \text{nN}")],
     answer="F = «F» nN, towards the plate",
     whatif=[W("…the charge were twice as close (0.2 m)?", lambda p: {**p, "d": 0.2}, "F ∝ 1/d², so it quadruples to «F» nN.", r"F=«F»\ \text{nN}"),
             W("…the charge were −1 nC?", lambda p: {**p, "Q": -1e-9}, "The image flips sign too, so the force is still attractive and equal: «F» nN.", r"F\propto Q^2")],
     mistake="Using the distance d instead of 2d between the charge and its image.",
     vals={"F": lambda r, p: r["values"]["F"] * 1e9}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 4-11", "exam", "Induced charge under the charge",
   "A 1 nC charge is 0.4 m above a grounded plane. Find the induced surface charge density on the plane directly beneath it, and the total charge induced on the plane.",
   {"type": "plane", "d": 0.4}, "img/plane", {"Q": 1e-9, "d": 0.4}, [("ρs(0)", V("rho_s0"), "nC/m²", 1e9)],
   X(asked="ρs at the foot of the perpendicular, and the total induced charge.",
     idea="At a conductor surface ρs = ε₀E_n. The field at the plane is the field of the charge and its image, which is purely normal there.",
     steps=[S("Normal field at a point on the plane a distance x from the foot of the perpendicular.", r"E_z(x)=-\frac{2Qd}{4\pi\varepsilon_0(x^2+d^2)^{3/2}}"),
            S("Surface charge density.", r"\rho_s(x)=\varepsilon_0E_z=-\frac{Qd}{2\pi(x^2+d^2)^{3/2}}"),
            S("Directly beneath the charge (x = 0).", r"\rho_s(0)=-\frac{Q}{2\pi d^2}=«rs»\ \text{nC/m}^2"),
            S("Integrating ρs over the whole plane gives exactly −Q.", r"\iint\rho_s\,ds=-Q")],
     answer="ρs(0) = «rs» nC/m²; total induced charge = −Q",
     whatif=[W("…the charge were at 0.2 m?", lambda p: {**p, "d": 0.2}, "ρs(0) ∝ 1/d², so it becomes «rs» nC/m², while the total is still −Q.", r"\rho_s(0)=«rs»\ \text{nC/m}^2"),
             W("…the charge were −1 nC?", lambda p: {**p, "Q": -1e-9}, "The induced charge is positive: ρs(0) = «rs» nC/m².", r"\rho_s(0)=«rs»\ \text{nC/m}^2")],
     mistake="Expecting the total induced charge to depend on d. It is always −Q; only how it is spread out changes.",
     plot=Series(_rs("x"), [("engine (numerical)", lambda r, p: [v * 1e9 for v in r["rho_s"]["num"]], "E"), ("closed form", lambda r, p: [v * 1e9 for v in r["rho_s"]["closed"]])],
                 "distance along the plane x (m)", "ρs (nC/m²)"),
     evidence_say="Engine: ρs along the plane from the field (numerical) and from the closed form agree.",
     vals={"rs": lambda r, p: r["values"]["rho_s0"] * 1e9}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 4-11", "basic", "Closer charge, larger force",
   "A −3 nC charge is held 10 cm above a grounded plate. Find the force on it, and say whether it is attracted or repelled.",
   {"type": "plane", "d": 0.1}, "img/plane", {"Q": -3e-9, "d": 0.1}, [("F", V("F"), "µN", 1e6)],
   X(asked="The magnitude and direction of the force on a negative charge near a grounded plane.",
     idea="The image of −Q is +Q at the mirror point. Opposite charges attract, whatever the sign of the real charge.",
     steps=[S("Image charge.", r"Q'=-Q=+3\ \text{nC at}\ z=-d"),
            S("Coulomb force at distance 2d.", r"F=\frac{Q^2}{16\pi\varepsilon_0d^2}=«F»\ \mu\text{N}"),
            S("The charge and its image have opposite signs, so the force is attractive.")],
     answer="F = «F» µN, attractive",
     whatif=[W("…the distance were doubled?", lambda p: {**p, "d": 0.2}, "F ∝ 1/d²: «F» µN.", r"F=«F»\ \mu\text{N}"),
             W("…the charge were +3 nC?", lambda p: {**p, "Q": 3e-9}, "Same magnitude, «F» µN, still attractive.", r"F=«F»\ \mu\text{N}")],
     mistake="Expecting a negative charge to be repelled by a grounded plate. The plate always supplies charge of the opposite sign.",
     vals={"F": lambda r, p: r["values"]["F"] * 1e6}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 4-10, 4-11", "exam", "Energy of charge and plane",
   "A 2 nC charge is 0.2 m above a grounded plane. Find the electrostatic energy of the system, i.e. the work needed to bring the charge in from infinity.",
   {"type": "plane", "d": 0.2}, "img/plane", {"Q": 2e-9, "d": 0.2}, [("W", V("W"), "nJ", 1e9)],
   X(asked="The work done in assembling the charge–plane system.",
     idea="Integrate the image force while bringing the charge in. The image moves with the charge, so the result is half of what a fixed charge −Q at 2d would give.",
     steps=[S("Force at height z.", r"F(z)=\frac{Q^2}{16\pi\varepsilon_0z^2}\ \text{(towards the plane)}"),
            S("Work done by an external agent moving the charge from ∞ to d.", r"W=-\int_\infty^d F(z)\,dz=-\frac{Q^2}{16\pi\varepsilon_0d}=«W»\ \text{nJ}"),
            S("The energy is negative: the system gives out energy as the charge approaches the plane.")],
     answer="W = «W» nJ",
     whatif=[W("…the charge were twice as far?", lambda p: {**p, "d": 0.4}, "W ∝ 1/d: «W» nJ.", r"W=«W»\ \text{nJ}"),
             W("…the force at d were asked?", lambda p: p, "F = «F» nN; note that W = −F·d.", r"F=\frac{Q^2}{16\pi\varepsilon_0d^2}=«F»\ \text{nN}")],
     mistake="Using the energy of two real charges, −Q²/(8πε₀d). The image is not a real charge, so the true value is half of that.",
     vals={"W": lambda r, p: r["values"]["W"] * 1e9, "F": lambda r, p: r["values"]["F"] * 1e9}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 4-7, 4-11", "exam", "Image in a dielectric",
   "A 1 nC charge is 0.5 m above a grounded metal plane, with the whole upper region filled with oil (εr = 2.5). Find the force on the charge.",
   {"type": "plane", "d": 0.5}, "img/plane", {"Q": 1e-9, "d": 0.5, "eps_r": 2.5}, [("F", V("F"), "nN", 1e9)],
   X(asked="The image force when the charge sits in a uniform dielectric.",
     idea="The image construction is unchanged: −Q at the mirror point. Only the permittivity of the medium between them changes.",
     steps=[S("Image charge −Q at 2d from the real charge."),
            S("Coulomb force in a medium of permittivity ε = εrε₀.", r"F=\frac{Q^2}{16\pi\varepsilon d^2}=«F»\ \text{nN}"),
            S("The polarised oil screens the field, so the force is εr times weaker than in air.")],
     answer="F = «F» nN",
     whatif=[W("…the oil were removed?", lambda p: {**p, "eps_r": 1}, "F = «F» nN, larger by εr.", r"F=«F»\ \text{nN}"),
             W("…the oil were water (εr = 80)?", lambda p: {**p, "eps_r": 80}, "F = «F» nN.", r"F=«F»\ \text{nN}")],
     mistake="Changing the size of the image charge. For a conducting plane under a uniform dielectric the image is still −Q.",
     vals={"F": lambda r, p: r["values"]["F"] * 1e9}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 4-11", "exam", "Charge in a 90° corner",
   "A 1 nC charge sits at (0.3, 0.5) m inside a corner formed by two grounded, perpendicular metal walls along the x- and y-axes. Find the magnitude of the force on it.",
   {"type": "corner", "x0": 0.3, "y0": 0.5}, "img/corner", {"Q": 1e-9, "x0": 0.3, "y0": 0.5}, [("|F|", lambda r: math.hypot(*r["values"]["F"]), "nN", 1e9)],
   X(asked="The total force on a charge between two perpendicular grounded planes.",
     idea="Three images make both walls zero-potential: −Q at (−x₀, y₀), −Q at (x₀, −y₀) and +Q at (−x₀, −y₀).",
     steps=[S("Image charges.", r"-Q\ (-x_0,y_0),\qquad -Q\ (x_0,-y_0),\qquad +Q\ (-x_0,-y_0)"),
            S("Add the three Coulomb forces on the real charge.", r"F_x=«fx»\ \text{nN},\qquad F_y=«fy»\ \text{nN}"),
            S("Magnitude.", r"|\mathbf F|=«F»\ \text{nN}")],
     answer="|F| = «F» nN",
     whatif=[W("…the charge sat on the diagonal at (0.3, 0.3)?", lambda p: {**p, "y0": 0.3}, "By symmetry the force points straight into the corner: |F| = «F» nN.", r"|\mathbf F|=«F»\ \text{nN}"),
             W("…only the wall y = 0 existed?", lambda p: p, "Then only one image would be needed and the force would be Q²/(16πε₀y₀²), straight down.", None)],
     mistake="Forgetting the third image (+Q at the opposite corner). Without it neither wall is at zero potential.",
     vals={"fx": lambda r, p: r["values"]["F"][0] * 1e9, "fy": lambda r, p: r["values"]["F"][1] * 1e9, "F": lambda r, p: math.hypot(*r["values"]["F"]) * 1e9}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 4-11", "exam", "Field near the plane",
   "A 2 nC charge is 0.3 m above a grounded plane (the plane y = 0). Find |E| at the point (0.06, 0.18) m.",
   {"type": "plane", "d": 0.3, "probe": [0.2, 0.18]}, "es/charges", {"charges": [{"q": 2e-9, "x": 0, "y": 0.3}], "ground": True, "probe": [0.06, 0.18]},
   [("|E|", V("E_mag"), "V/m", 1)],
   X(asked="The electric field at a point between the charge and the plane.",
     idea="In the region above the plane, the field equals that of the charge plus its image −Q at (0, −0.3) m.",
     steps=[S("Image charge −2 nC at (0, −0.3) m; superpose the two Coulomb fields at the probe.", r"\mathbf E=\mathbf E_Q+\mathbf E_{-Q}"),
            S("Components.", r"E_x=«ex»\ \text{V/m},\qquad E_y=«ey»\ \text{V/m}"),
            S("Magnitude.", r"|\mathbf E|=«E»\ \text{V/m}")],
     answer="|E| = «E» V/m",
     whatif=[W("…the plane were removed?", lambda p: {**p, "ground": False}, "Only the real charge remains: |E| = «E» V/m.", r"|\mathbf E|=«E»\ \text{V/m}"),
             W("…the probe were on the plane, at (0.06, 0)?", lambda p: {**p, "probe": [0.06, 0.0]}, "There the field is purely normal (E_x = «ex» V/m): |E| = «E» V/m.", r"E_x=«ex}".replace("«ex}", "«ex»"))],
     mistake="Including the image when evaluating the field below the plane. There, inside the conductor, E = 0.",
     vals={"ex": EV("E", 0), "ey": EV("E", 1), "E": EV("E_mag")}), "numeric")

# ---- conceptual
_pl = {"Q": 1e-9, "d": 0.4}
px(T, "Ulaby & Ravaioli Sec. 4-11", "exam", "Why the image method is allowed",
   "The image charge does not exist. Why is it nevertheless legitimate to use it to compute the field above a grounded plane?",
   {"type": "plane", "d": 0.4}, "img/plane", _pl, [],
   X(asked="The justification for replacing a conductor by an image charge.",
     idea="The uniqueness theorem: a solution of Laplace's/Poisson's equation that meets the boundary conditions is the only solution.",
     steps=[S("Above the plane the real problem is: the given charge Q, and V = 0 on the plane and at infinity."),
            S("The pair Q, −Q produces exactly V = 0 on the mirror plane, with the same charge in the upper region."),
            S("Same equation, same charges, same boundary values in the region: by uniqueness, the same field there.")],
     answer_text="The field above the plane is fixed by Poisson's equation with the given charge and the boundary condition V = 0 on the plane (and at infinity). "
                 "The uniqueness theorem says only one potential satisfies both. "
                 "The charge Q together with an image −Q at the mirror point makes V = 0 on the whole plane and has the same charges in the upper region, so it must give the correct field there. "
                 "The image is a calculating device that reproduces the effect of the induced surface charge; it says nothing about the region below the plane.",
     evidence_say="Engine checks: the image field equals the field computed from the induced surface charge at a test point, and V = 0 on the plane.",
     mistake="Thinking the image describes the field inside the conductor too.",
     vals={}), "concept")

px(T, "Ulaby & Ravaioli Sec. 4-11", "exam", "Where does the induced charge sit, and how much is there?",
   "A point charge Q is held above a grounded plane. How is the induced charge distributed over the plane, and what is its total?",
   {"type": "plane", "d": 0.4}, "img/plane", _pl, [],
   X(asked="The shape and total of the induced surface charge.",
     idea="ρs = ε₀E_n at the conductor; E_n comes from the charge and its image.",
     steps=[S("The density is strongest right below the charge and falls off as the distance grows.", r"\rho_s(x)=-\frac{Qd}{2\pi(x^2+d^2)^{3/2}}"),
            S("Integrated over the infinite plane it gives −Q, independent of d.", r"\iint\rho_s\,ds=-Q"),
            S("Moving the charge closer concentrates the same total into a smaller spot.")],
     answer_text="The induced charge has the opposite sign to Q and is concentrated beneath it: ρs = −Qd/(2π(x² + d²)^(3/2)), "
                 "which peaks at the foot of the perpendicular and falls off as 1/x³ far away. "
                 "Its total is exactly −Q for any height d, as Gauss's law requires: all field lines leaving Q end on the plane. "
                 "Bringing the charge closer makes the spot narrower and taller, keeping the same total.",
     evidence_say="Engine: ρs(0) = «rs» nC/m² for Q = 1 nC at 0.4 m; its check integrates ρs over the plane and recovers −Q.",
     plot=Series(_rs("x"), [("ρs (nC/m²)", lambda r, p: [v * 1e9 for v in r["rho_s"]["closed"]], "E")], "distance along the plane x (m)", "ρs (nC/m²)"),
     mistake="Thinking the induced charge is spread uniformly, or that its total depends on the distance.",
     vals={"rs": lambda r, p: r["values"]["rho_s0"] * 1e9}), "concept")

px(T, "Ulaby & Ravaioli Sec. 4-10, 4-11", "exam", "Why the energy is half of the 'two-charge' value",
   "A student computes the energy of a charge Q above a grounded plane as that of Q and its image, −Q²/(8πε₀d). The correct answer is half of that. Explain why.",
   {"type": "plane", "d": 0.4}, "img/plane", _pl, [],
   X(asked="Why W = −Q²/(16πε₀d) and not the two-charge value.",
     idea="The image is not a real charge, and the field exists only in the upper half-space. Energy is stored only where the real field is.",
     steps=[S("The real field fills only the region above the plane; below it E = 0."),
            S("The two-charge formula counts the field energy of both half-spaces, which by symmetry is twice the real one."),
            S("Equivalently, the work of bringing Q in from infinity, integrating the image force, gives the half value.", r"W=-\int_\infty^d\frac{Q^2}{16\pi\varepsilon_0z^2}dz=-\frac{Q^2}{16\pi\varepsilon_0d}")],
     answer_text="The image charge is a fiction that reproduces the field above the plane; below the plane, inside the metal, the real field is zero. "
                 "The energy of two real charges Q and −Q, −Q²/(8πε₀d), includes the field energy of both half-spaces, which are mirror images and hold equal shares. "
                 "Only the upper half is real, so the true energy is half: −Q²/(16πε₀d). "
                 "The same result follows from integrating the image force while moving the charge in, because the image moves too as the charge approaches.",
     evidence_say="Engine for Q = 1 nC at 0.4 m: W = «W» nJ and F = «F» nN, consistent with W = −F·d.",
     mistake="Treating the image like a fixed real charge when computing work or energy.",
     vals={"W": lambda r, p: r["values"]["W"] * 1e9, "F": lambda r, p: r["values"]["F"] * 1e9}), "concept")

px(T, "Ulaby & Ravaioli Sec. 4-11", "basic", "The image is valid only on one side",
   "With the image charge in place, the 'field' below the grounded plane would look like that of a charge −Q. What is the real field below the plane, and why?",
   {"type": "plane", "d": 0.4}, "img/plane", _pl, [],
   X(asked="The field in the region occupied by the conductor.",
     idea="The image solution is constructed to be correct only in the region that contains the real charge and is bounded by the conductor.",
     steps=[S("Below the surface is the conductor, where the electrostatic field is zero."),
            S("The image was chosen only to satisfy V = 0 on the plane as seen from above."),
            S("Its field below the plane is a mathematical artefact and must not be used.")],
     answer_text="Below the plane is the grounded conductor, and inside a conductor in electrostatic equilibrium E = 0. "
                 "The image solution is only guaranteed to be correct in the region where the uniqueness argument was applied: above the plane, where the real charge is. "
                 "The field that the pair Q, −Q would produce below the plane is not physical. "
                 "In general, an image construction is valid only in the region that contains the real charges and is bounded by the surfaces whose boundary conditions it reproduces.",
     evidence_say="Engine check: on the plane the potential of Q and its image is zero, matching the grounded conductor.",
     mistake="Using the image field inside the conductor or behind the mirror plane.",
     vals={}), "concept")

px(T, "Ulaby & Ravaioli Sec. 4-11", "exam", "Which corners can be solved with images?",
   "A charge between two grounded planes meeting at 90° needs three images. How many are needed for 60°, and why can a 70° corner not be handled with a finite set of point images?",
   {"type": "corner", "x0": 0.3, "y0": 0.5}, "img/corner", {"Q": 1e-9, "x0": 0.3, "y0": 0.5}, [],
   X(asked="The rule that decides when a wedge has a finite image solution.",
     idea="Images come from repeated reflections in the two planes. The reflections close up into a finite set only if the wedge angle divides 180° evenly.",
     steps=[S("Reflecting a charge alternately in the two planes rotates it in steps of twice the wedge angle."),
            S("For an angle 180°/n the pattern closes after 2n charges, i.e. 2n − 1 images.", r"\alpha=\frac{180^\circ}{n}\ \Rightarrow\ 2n-1\ \text{images}"),
            S("90° gives n = 2 and three images; 60° gives n = 3 and five; 70° does not divide 180° and never closes.")],
     answer_text="Each image is a mirror reflection of a charge in one of the planes. Reflecting alternately in the two planes rotates the charge around the corner in steps of twice the wedge angle α. "
                 "If α = 180°/n for a whole number n, the reflections return to the start after 2n charges, so 2n − 1 images make both planes zero-potential. "
                 "A 90° corner (n = 2) needs three, a 60° corner (n = 3) five. "
                 "For 70° the reflections never repeat and some would fall inside the physical region, so the method fails and another technique, such as a series solution, is required.",
     evidence_say="Engine check for the 90° corner: with three images, V = 0 on both walls.",
     mistake="Placing a single image behind each wall and forgetting the image of the images.",
     vals={}), "concept")

px(T, "Ulaby & Ravaioli Sec. 4-11", "basic", "Always attracted, whatever the sign",
   "Will a negatively charged particle near a grounded metal plate be attracted or repelled? What about a positive one?",
   {"type": "plane", "d": 0.4}, "img/plane", _pl, [],
   X(asked="The direction of the force on a charge near a grounded plane, for either sign.",
     idea="The image always has the opposite sign to the real charge, so the force is always attractive.",
     steps=[S("The image of Q is −Q, whatever the sign of Q.", r"Q'=-Q"),
            S("Opposite charges attract, so the force points towards the plate.", r"F=\frac{Q^2}{16\pi\varepsilon_0d^2}\propto Q^2"),
            S("Physically, the plate draws in charge of the opposite sign from ground, right under the particle.")],
     answer_text="Both are attracted. The grounded plate takes charge of the opposite sign from earth and gathers it under the particle, "
                 "which is represented by an image of opposite sign. The force depends on Q², so its direction does not depend on the sign of Q. "
                 "This is why charged dust sticks to grounded surfaces, and why a charged object is attracted even by a neutral conductor (which polarises instead of drawing charge from ground).",
     evidence_say="Engine runs for Q from −3 nC to +3 nC at 0.4 m: the attractive force is symmetric in Q.",
     plot=Sweep("Q", [-3e-9, -2e-9, -1e-9, 1e-9, 2e-9, 3e-9], [("attractive force F", lambda r, p: r["values"]["F"] * 1e9, "E")], "charge Q (C)", "F (nN)"),
     mistake="Applying 'like charges repel' between the particle and the plate. The plate's nearby charge is always of the opposite sign.",
     vals={}), "concept")

px(T, "Ulaby & Ravaioli Sec. 4-11", "exam", "Why the field meets the plane at right angles",
   "Sketches of a charge above a grounded plane always show the field lines meeting the plane perpendicularly. Why must they, and how does the image construction guarantee it?",
   {"type": "plane", "d": 0.4, "probe": [0.2, 0.0]}, "es/charges", {"charges": [{"q": 1e-9, "x": 0, "y": 0.4}], "ground": True, "probe": [0.2, 0.0]}, [],
   X(asked="Why E is normal to a conductor surface, and how the image ensures it.",
     idea="Tangential E is continuous at any boundary and zero inside a conductor, so it must be zero just outside too.",
     steps=[S("Inside the conductor E = 0, and the tangential component of E is continuous across the surface."),
            S("So just outside the surface E_t = 0, and E is purely normal."),
            S("For the mirror pair the tangential components of the two fields cancel at every point of the plane.")],
     answer_text="Inside a conductor in equilibrium E = 0, and the boundary condition that tangential E is continuous then forces E_t = 0 just outside. "
                 "The field at the surface is therefore purely normal, and the field lines meet the conductor at right angles; equivalently, the surface is an equipotential. "
                 "In the image picture, at any point on the plane the real charge and its mirror image are at equal distances, so their tangential components are equal and opposite and cancel, "
                 "while the normal components add.",
     evidence_say="Engine at the point (0.2, 0) on the plane: E_x = «ex» V/m and E_y = «ey» V/m.",
     mistake="Drawing field lines that meet a conductor at an angle.",
     vals={"ex": EV("E", 0), "ey": EV("E", 1)}), "concept")

px(T, "Cheng Sec. 4-4", "exam", "Images for a grounded sphere",
   "Can the image method be used for a point charge near a grounded metal sphere? If so, what replaces the simple mirror image?",
   {"type": "plane", "d": 0.4}, "img/plane", _pl, [],
   X(asked="The image construction for a sphere.",
     idea="For a sphere of radius a and a charge Q at distance d from its centre, a single image of different size and position makes the sphere an equipotential.",
     steps=[S("The image lies on the line to the centre, inside the sphere, at the inverse point.", r"d'=\frac{a^2}{d}"),
            S("Its size is reduced in proportion.", r"Q'=-\frac{a}{d}\,Q"),
            S("As the sphere grows, with the distance to its surface fixed, d' approaches the mirror point and Q' → −Q: the plane result.")],
     answer_text="Yes. For a grounded sphere of radius a and a charge Q at distance d from its centre, one image charge Q′ = −(a/d)Q placed at distance a²/d from the centre, "
                 "on the line joining the centre and Q, makes the potential zero everywhere on the sphere. "
                 "Unlike the plane, the image is smaller than Q, so the total induced charge is −(a/d)Q, not −Q. "
                 "For a very large sphere this reduces to the mirror image of the plane. An ungrounded, neutral sphere needs an extra charge +(a/d)Q at the centre.",
     evidence_say="For comparison, the engine's plane solution with Q = 1 nC at 0.4 m gives an attractive force of «F» nN.",
     mistake="Using the plane's mirror image (−Q at the same distance behind the surface) for a curved conductor.",
     vals={"F": lambda r, p: r["values"]["F"] * 1e9}), "concept")

# ---------------------------------------------------------------- magnetostatics & Biot–Savart
T = "magnetostatics"
# Explained (engine/explain.py): 7 numerical + 8 conceptual.
_wires2 = {"currents": [{"I": 20, "x": -0.05, "y": 0}, {"I": 30, "x": 0.05, "y": 0}], "probe": [0, 0.1]}
_ax = lambda k: (lambda r, p: r["axis"][k])
_pf = lambda k: (lambda r, p: r["profile"][k])

px(T, "Ulaby & Ravaioli Sec. 5-2", "basic", "Long straight wire",
   "A long straight cable carries a steady 15 A. Find the magnetic flux density 5 cm from its axis, and compare it with the Earth's field of about 50 µT.",
   {"type": "wires", "wires": [[15, 0, 0]]}, "ms/wires", {"currents": [{"I": 15, "x": 0, "y": 0}], "probe": [0.05, 0]}, [("B", V("B_mag"), "µT", 1e6)],
   X(asked="|B| at 5 cm from a long wire carrying 15 A.",
     idea="By symmetry the field circles the wire with constant size on any circle around it, so Ampère's law gives it directly.",
     steps=[S("Ampère's law on a circle of radius r around the wire.", r"\oint\mathbf H\cdot d\mathbf l=H\,2\pi r=I"),
            S("Flux density in air.", r"B=\frac{\mu_0I}{2\pi r}=«B»\ \mu\text{T}"),
            S("This is comparable to the Earth's field, which is why a current-carrying cable can deflect a nearby compass.")],
     answer="B = «B» µT",
     whatif=[W("…the distance were 50 cm?", lambda p: {**p, "probe": [0.5, 0]}, "B ∝ 1/r: «B» µT, well below the Earth's field.", r"B=«B»\ \mu\text{T}"),
             W("…the cable carried a return conductor 1 cm away (equal and opposite current)?", lambda p: {**p, "currents": [{"I": 15, "x": 0, "y": 0}, {"I": -15, "x": 0.01, "y": 0}]},
               "The two fields nearly cancel: B = «B» µT. This is why supply and return wires are run together.", r"B=«B»\ \mu\text{T}")],
     mistake="Using μ₀I/(2r), the field at the centre of a loop, for a straight wire.",
     vals={"B": lambda r, p: r["values"]["B_mag"] * 1e6}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 5-2.3", "basic", "Force between wires",
   "Two long parallel wires 10 cm apart carry 20 A and 30 A in the same direction. Find the force per metre between them, and say whether they attract or repel.",
   {"type": "wires", "wires": [[20, -0.05, 0], [30, 0.05, 0]]}, "ms/wires", _wires2, [("F′", lambda r: abs(r["forces"][0][0]), "mN/m", 1e3)],
   X(asked="The magnitude and sense of the force per unit length.",
     idea="Each wire sits in the other's field, B = μ₀I/(2πd), and feels I × B per metre. Currents in the same direction attract.",
     steps=[S("Field of wire 1 at wire 2.", r"B_1=\frac{\mu_0I_1}{2\pi d}"),
            S("Force per metre on wire 2.", r"F'=I_2B_1=\frac{\mu_0I_1I_2}{2\pi d}=«F»\ \text{mN/m}"),
            S("The force on the left wire points towards the right wire: the currents attract.")],
     answer="F′ = «F» mN/m, attractive",
     whatif=[W("…the second current were reversed?", lambda p: {**p, "currents": [{"I": 20, "x": -0.05, "y": 0}, {"I": -30, "x": 0.05, "y": 0}]}, "Same magnitude, «F» mN/m, now repulsive.", r"F'=«F»\ \text{mN/m}"),
             W("…the wires were 20 cm apart?", lambda p: {**p, "currents": [{"I": 20, "x": -0.1, "y": 0}, {"I": 30, "x": 0.1, "y": 0}]}, "F′ ∝ 1/d: «F» mN/m.", r"F'=«F»\ \text{mN/m}")],
     mistake="Getting the direction backwards: unlike charges, like currents attract.",
     vals={"F": lambda r, p: abs(r["forces"][0][0]) * 1e3}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 5-2.1", "exam", "Finite wire (Biot–Savart)",
   "A straight wire segment 40 cm long carries 3 A. Find H at a point 10 cm from the wire, opposite its midpoint, and compare with an infinitely long wire.",
   {"type": "segment", "L": 0.4}, "bs/segment", {"I": 3, "z1": -0.2, "z2": 0.2, "r": 0.1, "N": 400}, [("H", V("H"), "A/m", 1)],
   X(asked="H from a finite segment, by Biot–Savart, and its ratio to the infinite-wire value.",
     idea="Ampère's law needs an infinitely long wire. For a finite segment, integrate Biot–Savart along it; the result depends on the angles the segment's ends subtend.",
     steps=[S("Biot–Savart for a straight segment.", r"H=\frac{I}{4\pi r}(\sin\theta_2-\sin\theta_1)"),
            S("Here the ends subtend equal and opposite angles, so the result is", r"H=«Hc»\ \text{A/m}\ \text{(closed form)},\qquad H=«H»\ \text{A/m}\ \text{(engine, 400 elements)}"),
            S("An infinite wire would give I/(2πr) = «Hi» A/m; the segment gives «ratio» of that.")],
     answer="H = «H» A/m («ratio» of the infinite-wire value)",
     whatif=[W("…the segment were 2 m long?", lambda p: {**p, "z1": -1, "z2": 1}, "Now it looks almost infinite from 10 cm: H = «H» A/m, ratio «ratio».", r"H=«H»\ \text{A/m}"),
             W("…the point were 1 m away?", lambda p: {**p, "r": 1.0}, "From far away the segment looks short: H = «H» A/m, ratio «ratio».", r"H=«H»\ \text{A/m}")],
     mistake="Using I/(2πr) for a short wire. It holds only when the wire is much longer than the distance r.",
     vals={"H": EV("H"), "Hc": EV("H_closed"), "Hi": EV("H_infinite"), "ratio": EV("ratio_to_infinite")}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 5-2", "exam", "Square loop",
   "A square loop of side 20 cm carries 1 A. Find H at its centre, and compare it with a circular loop that fits just inside the square.",
   {"type": "square", "a": 0.2}, "bs/square", {"I": 1, "a": 0.2, "N": 200}, [("H", V("H"), "A/m", 1)],
   X(asked="H at the centre of a square loop, and the comparison with the inscribed circle.",
     idea="The four sides are identical finite segments, each at distance a/2 from the centre and subtending ±45°. Their fields add along the axis.",
     steps=[S("One side, by the finite-segment formula with θ = ±45°.", r"H_1=\frac{I}{4\pi(a/2)}\,2\sin45^\circ"),
            S("Four sides.", r"H=4H_1=\frac{2\sqrt2\,I}{\pi a}=«H»\ \text{A/m}"),
            S("A circle of radius a/2 would give I/a = «Hc» A/m, a little more: its wire is everywhere as close as the square's nearest points.")],
     answer="H = «H» A/m (inscribed circle: «Hc» A/m)",
     whatif=[W("…the side were halved?", lambda p: {**p, "a": 0.1}, "H ∝ 1/a: «H» A/m.", r"H=«H»\ \text{A/m}"),
             W("…the current were 5 A?", lambda p: {**p, "I": 5}, "H = «H» A/m.", r"H=«H»\ \text{A/m}")],
     mistake="Treating each side as an infinite wire, which overestimates the field.",
     vals={"H": EV("H"), "Hc": EV("H_inscribed_circle")}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 5-2.2", "basic", "Centre of a loop",
   "A circular loop of radius 5 cm carries 2 A. Find H and B at its centre.",
   {"type": "loop"}, "bs/loop", {"I": 2, "a": 0.05, "z": 0}, [("H", V("H"), "A/m", 1)],
   X(asked="H and B at the centre of a circular loop.",
     idea="Every element of the loop is the same distance a from the centre and perpendicular to the line joining them, so all contributions add along the axis.",
     steps=[S("Biot–Savart for one element.", r"dH=\frac{I\,dl}{4\pi a^2}"),
            S("Add around the circumference 2πa.", r"H=\frac{I}{2a}=«H»\ \text{A/m}"),
            S("In air B = μ₀H.", r"B=«B»\ \mu\text{T}")],
     answer="H = «H» A/m, B = «B» µT",
     whatif=[W("…the radius were doubled?", lambda p: {**p, "a": 0.1}, "H ∝ 1/a: «H» A/m.", r"H=«H»\ \text{A/m}"),
             W("…the point were 5 cm along the axis?", lambda p: {**p, "z": 0.05}, "H = «H» A/m, smaller by (1 + z²/a²)^(3/2).", r"H=\frac{Ia^2}{2(a^2+z^2)^{3/2}}=«H»\ \text{A/m}")],
     mistake="Using I/(2πa), the straight-wire result.",
     vals={"H": EV("H"), "B": lambda r, p: r["values"]["B"] * 1e6}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 5-2.2", "exam", "On the axis of a loop",
   "A loop of radius 10 cm carries 1 A. Find H on its axis 10 cm from the centre.",
   {"type": "loop", "z": 1}, "bs/loop", {"I": 1, "a": 0.1, "z": 0.1}, [("H", V("H"), "A/m", 1)],
   X(asked="The axial field of a loop at z = a.",
     idea="On the axis the radial parts of opposite elements cancel by symmetry; only the axial parts add.",
     steps=[S("Each element is at distance √(a² + z²); only the fraction a/√(a² + z²) of its field is axial.", r"dH_z=\frac{I\,dl}{4\pi(a^2+z^2)}\cdot\frac{a}{\sqrt{a^2+z^2}}"),
            S("Integrate around the loop.", r"H_z=\frac{Ia^2}{2(a^2+z^2)^{3/2}}=«H»\ \text{A/m}"),
            S("At z = a this is 1/(2√2) times the centre value, about 35 %.")],
     answer="H = «H» A/m",
     whatif=[W("…the point were at the centre?", lambda p: {**p, "z": 0}, "H = I/(2a) = «H» A/m.", r"H=«H»\ \text{A/m}"),
             W("…the point were ten radii away (z = 1 m)?", lambda p: {**p, "z": 1.0}, "Far away the loop is a magnetic dipole and H ∝ 1/z³: «H» A/m.", r"H\approx\frac{Ia^2}{2z^3}=«H»\ \text{A/m}")],
     mistake="Forgetting that only the axial component survives, and adding the full magnitudes.",
     plot=Series(_ax("z"), [("H on the axis", _ax("H"), "H")], "distance along the axis z (m)", "H (A/m)"),
     evidence_say="Engine axial profile: peaked at the centre and falling off symmetrically.",
     vals={"H": EV("H")}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 5-4", "basic", "Toroid",
   "A toroid of 500 turns has inner radius 4 cm and outer radius 6 cm and an air core. It carries 0.5 A. Find B at the mean radius.",
   {"type": "toroid", "a": 4, "b": 6}, "ms/ampere", {"kind": "toroid", "I": 0.5, "N": 500, "a": 0.04, "b": 0.06, "r": 0.05}, [("B", V("B"), "mT", 1e3)],
   X(asked="B inside the toroid at r = 5 cm.",
     idea="H circles inside the core with the same size on every concentric circle; such a circle links the total current NI.",
     steps=[S("Ampère's law on a circle of radius r inside the core.", r"H\,2\pi r=NI\ \Rightarrow\ H=«H»\ \text{A/m}"),
            S("Air core.", r"B=\mu_0H=«B»\ \text{mT}"),
            S("B varies as 1/r across the core: it is strongest at the inner radius.")],
     answer="B = «B» mT",
     whatif=[W("…the core were iron with μr = 1000?", lambda p: {**p, "mu_r": 1000}, "H is the same; B = «B» mT.", r"B=\mu_0\mu_rH=«B»\ \text{mT}"),
             W("…B at the inner radius were asked?", lambda p: {**p, "r": 0.04}, "B = «B» mT, the largest value in the core.", r"B=«B»\ \text{mT}")],
     mistake="Using the straight-solenoid formula with an arbitrary length.",
     vals={"H": EV("H"), "B": lambda r, p: r["values"]["B"] * 1e3}), "numeric")

# ---- conceptual
px(T, "Ulaby & Ravaioli Sec. 5-2.3", "basic", "Why like currents attract",
   "Like electric charges repel, yet two wires carrying current in the same direction attract. Explain the direction of the force using B and the force on a current.",
   {"type": "wires", "wires": [[20, -0.05, 0], [30, 0.05, 0]]}, "ms/wires", _wires2, [],
   X(asked="The direction of the magnetic force between parallel currents.",
     idea="The force on a current element is I dl × B. Find the direction of the other wire's B with the right-hand rule, then of the cross product.",
     steps=[S("Wire 1's field circles it; at wire 2 it points perpendicular to the plane of the wires."),
            S("The force on wire 2 is I₂ dl × B₁, which points back towards wire 1 when the currents are parallel."),
            S("Reversing one current reverses the cross product, so opposite currents repel.")],
     answer_text="Magnetic forces act on moving charges, F = I dl × B, not between static charges. "
                 "Wire 1's field circles it, so at wire 2 it is perpendicular to the plane of the two wires. "
                 "With both currents in the same direction, the cross product I₂ dl × B₁ points towards wire 1, so the wires attract; "
                 "reversing one current flips the direction and they repel. "
                 "The rule is the opposite of electrostatics because the force comes from a cross product, not from a radial Coulomb law.",
     evidence_say="Engine: the force on the left wire is «fx» mN/m along +x, i.e. towards the right wire.",
     mistake="Carrying 'like repels like' over from charges to currents.",
     vals={"fx": lambda r, p: r["forces"][0][0] * 1e3}), "concept")

px(T, "Ulaby & Ravaioli Sec. 5-2.1", "exam", "Why a short wire gives a weaker field",
   "Ampère's law gives H = I/(2πr) for a wire. Why does a 40 cm segment give a noticeably smaller field at 10 cm, even though Ampère's law is always true?",
   {"type": "segment", "L": 0.4}, "bs/segment", {"I": 3, "z1": -0.2, "z2": 0.2, "r": 0.1, "N": 400}, [],
   X(asked="Why Ampère's law cannot be used for a finite segment.",
     idea="Ampère's law gives H only when symmetry makes H constant around the loop. A finite segment also cannot carry a steady current on its own.",
     steps=[S("For an infinite wire, H is the same everywhere on a circle around it, so ∮H·dl = H·2πr."),
            S("A finite segment breaks that symmetry: the field also depends on position along the wire."),
            S("A steady current must flow in a closed circuit, so the rest of the circuit contributes too; Biot–Savart gives the segment's share alone.")],
     answer_text="Ampère's law is always true, but it yields H only when symmetry makes H constant along the integration path. "
                 "For an infinite wire it does; for a 40 cm segment the field near the ends is weaker than near the middle, so H·2πr is not the integral. "
                 "Moreover, a segment alone cannot carry a steady current: the rest of the circuit carries the current back and adds its own field. "
                 "Biot–Savart computes the segment's contribution, which here is «ratio» of the infinite-wire value because the far parts of an infinite wire are missing.",
     evidence_say="Engine: H = «H» A/m against I/(2πr) = «Hi» A/m for an infinite wire.",
     mistake="Applying Ampère's law with a circular path where the field is not constant along it.",
     vals={"ratio": EV("ratio_to_infinite"), "H": EV("H"), "Hi": EV("H_infinite")}), "concept")

px(T, "Ulaby & Ravaioli Sec. 5-2", "exam", "How accurate is a numerical Biot–Savart sum?",
   "The engine computes Biot–Savart by cutting the wire into N straight elements. How fast does the error shrink as N grows, and why?",
   {"type": "segment", "L": 0.4}, "bs/segment", {"I": 3, "z1": -0.2, "z2": 0.2, "r": 0.1, "N": 400}, [],
   X(asked="The convergence of a discretised Biot–Savart integral.",
     idea="Replacing the integral by a sum over N elements evaluated at their midpoints is the midpoint rule, whose error falls as 1/N² for a smooth integrand.",
     steps=[S("The field is an integral along the wire, which the engine approximates by a sum over N pieces."),
            S("With midpoint sampling the error is proportional to (length of a piece)², i.e. to 1/N².", r"\varepsilon\propto\frac{1}{N^2}"),
            S("Doubling N should cut the error by about four, which the convergence table confirms.")],
     answer_text="The Biot–Savart field is an integral along the wire. The engine evaluates it as a sum over N elements, each sampled at its midpoint, which is the midpoint rule. "
                 "For a smooth integrand its error is proportional to the square of the element length, so it falls as 1/N²: each doubling of N cuts the error by about four. "
                 "The integrand is smooth here because the field point is well away from the wire; close to the wire it varies sharply and many more elements are needed for the same accuracy.",
     evidence_say="Engine convergence table: the relative error against the closed form settles to slope −2 on log–log axes once N exceeds about ten.",
     plot=Series(lambda r, p: [c["N"] for c in r["convergence"]], [("relative error", lambda r, p: [c["rel_error"] for c in r["convergence"]], "E")],
                 "number of elements N", "relative error", logx=True, logy=True),
     mistake="Expecting a fixed number of elements to be accurate at any distance from the wire.",
     vals={}), "concept")

px(T, "Ulaby & Ravaioli Sec. 5-3.2", "exam", "Field inside a thick wire",
   "A straight wire of radius 1 cm carries 10 A spread uniformly over its cross-section. How does B vary from the axis to the surface and beyond, and where is it largest?",
   {"type": "wires", "wires": [[10, 0, 0]]}, "ms/ampere", {"kind": "wire", "I": 10, "a": 0.01, "r": 0.005}, [],
   X(asked="B(r) inside and outside a wire with uniform current density.",
     idea="Ampère's law on a circle of radius r: inside, only the current within r is enclosed, and it grows as r².",
     steps=[S("Inside (r < a) the enclosed current is I r²/a².", r"B=\frac{\mu_0Ir}{2\pi a^2}"),
            S("Outside (r > a) all of I is enclosed.", r"B=\frac{\mu_0I}{2\pi r}"),
            S("The two meet at r = a, where B is largest; at the centre B = 0.")],
     answer_text="Ampère's law on a circle of radius r gives B·2πr = μ₀I_enc. Inside the wire the enclosed current is I(r/a)², so B = μ₀Ir/(2πa²) grows linearly from zero at the axis. "
                 "Outside, the whole current is enclosed and B = μ₀I/(2πr) falls off. Both expressions agree at the surface, where B reaches its maximum. "
                 "This is the magnetic counterpart of the field of a uniformly charged cylinder.",
     evidence_say="Engine profile of B from the axis outwards: linear rise to the surface at 1 cm, then a 1/r fall.",
     plot=Series(_pf("r"), [("B", _pf("B"), "H")], "distance from the axis r (m)", "B (T)"),
     mistake="Using μ₀I/(2πr) inside the conductor.",
     vals={}), "concept")

px(T, "Ulaby & Ravaioli Sec. 5-4", "basic", "Why a toroid keeps its field inside",
   "An ideal toroid has a strong field inside its core and none outside. Use Ampère's law to explain why.",
   {"type": "toroid", "a": 4, "b": 6}, "ms/ampere", {"kind": "toroid", "I": 0.5, "N": 500, "a": 0.04, "b": 0.06, "r": 0.05}, [],
   X(asked="Why B is confined to the core of a toroid.",
     idea="Choose circles concentric with the toroid. The current they enclose decides H on them.",
     steps=[S("A circle inside the core links all N turns once: I_enc = NI, so H = NI/(2πr)."),
            S("A circle in the central hole links no current, so H = 0 there."),
            S("A circle outside the toroid passes the windings twice, once going up and once coming down: I_enc = 0, so H = 0.")],
     answer_text="Apply Ampère's law to circles around the axis of the toroid, on which H is constant by symmetry. "
                 "A circle inside the core encloses each of the N turns once, so H·2πr = NI. "
                 "A circle in the central hole encloses no current, and one outside the toroid encloses each turn twice in opposite directions, so the net current, and H, is zero in both. "
                 "Real toroids leak a little because the winding is helical and not perfectly uniform, but that is why toroidal cores are used where stray fields must be small.",
     evidence_say="Engine profile across the toroid: B is non-zero only between the inner and outer radius, and falls as 1/r there.",
     plot=Series(_pf("r"), [("B", _pf("B"), "H")], "distance from the axis r (m)", "B (T)"),
     mistake="Assuming the field is zero inside because 'the currents cancel'. They cancel only for paths outside the core.",
     vals={}), "concept")

px(T, "Ulaby & Ravaioli Sec. 5-2.2", "exam", "Helmholtz coils: a uniform field",
   "Two identical coaxial loops placed one radius apart and carrying equal currents in the same direction produce an unusually uniform field between them. Why does the spacing a give the most uniform field?",
   {"type": "loop", "z": 1}, "ms/loops", {"kind": "helmholtz", "I": 1, "a": 0.1, "pr": 0, "pz": 0.02}, [],
   X(asked="Why a spacing equal to the radius makes the field between two loops flat.",
     idea="Expand the field near the midpoint in powers of z. By symmetry the odd terms cancel; choosing the spacing to cancel the z² term leaves a field flat to fourth order.",
     steps=[S("Each loop's axial field changes with z; at the midpoint one is increasing while the other is decreasing, so the first derivatives cancel."),
            S("The second derivative of a single loop's field is zero at z = a/2, so placing the loops one radius apart makes the z² term vanish too."),
            S("The field then varies only as z⁴ near the centre, staying within a fraction of a per cent over a good part of the gap.")],
     answer_text="Near the midpoint the total field can be written as B(0) + c₁z + c₂z² + …. Because the two loops are placed symmetrically, the odd terms cancel automatically. "
                 "A single loop's axial field has an inflection point at a distance a/2 from its centre, where its second derivative is zero. "
                 "With a spacing equal to the radius, the midpoint sits at that inflection point for both loops, so the z² term vanishes as well and the first error term is of order z⁴. "
                 "That makes Helmholtz coils the standard way to produce a known, uniform field in a laboratory.",
     evidence_say="Engine axial profile of the Helmholtz pair: a broad flat top between the coils.",
     plot=Series(_ax("z"), [("B_z on the axis", _ax("Bz"), "H")], "distance along the axis z (m)", "B_z (T)"),
     mistake="Placing the coils as close together as possible, which gives a peaked rather than flat field.",
     vals={}), "concept")

px(T, "Ulaby & Ravaioli Sec. 5-3.1", "basic", "Why magnetic field lines close on themselves",
   "Electric field lines start and end on charges. Magnetic field lines have no beginning or end. Which Maxwell equation says this, and what does it rule out?",
   {"type": "wires", "wires": [[20, -0.05, 0], [30, 0.05, 0]]}, "ms/wires", _wires2, [],
   X(asked="The meaning of ∇·B = 0.",
     idea="Gauss's law for magnetism, ∮B·ds = 0, says the net magnetic flux out of any closed surface is zero: there are no magnetic charges for field lines to start or end on.",
     steps=[S("Gauss's law for magnetism.", r"\nabla\cdot\mathbf B=0\qquad\Leftrightarrow\qquad\oint_S\mathbf B\cdot d\mathbf s=0"),
            S("Every line that enters a closed surface must leave it, so lines cannot end anywhere; they close or run to infinity."),
            S("Cutting a bar magnet always produces two smaller magnets, never an isolated north pole.")],
     answer_text="Gauss's law for magnetism, ∇·B = 0, states that the magnetic flux out of any closed surface is zero. "
                 "If field lines could start or end, a small surface around that point would have net flux, so they must form closed loops (or extend to infinity). "
                 "The law expresses the absence of magnetic monopoles: magnetic fields come from currents and magnetic dipoles, never from isolated poles. "
                 "Cutting a magnet in half gives two magnets, each with both poles.",
     evidence_say="Engine field-line tracing for two parallel currents: every traced line closes around the wires.",
     mistake="Drawing magnetic field lines that start on a 'north pole' and end on a 'south pole' inside a magnet; inside, they continue from S back to N.",
     vals={}), "concept")

px(T, "Ulaby & Ravaioli Sec. 5-2.2", "exam", "A loop seen from far away",
   "Far along its axis a current loop's field falls off as 1/z³, not as 1/z or 1/z². Why, and what single quantity describes the loop from far away?",
   {"type": "loop", "z": 1}, "bs/loop", {"I": 1, "a": 0.1, "z": 0.3}, [],
   X(asked="The far-field law of a current loop and the quantity that governs it.",
     idea="Far away, opposite sides of the loop carry opposite currents and their fields nearly cancel, like the two charges of an electric dipole.",
     steps=[S("Exact axial field and its far limit.", r"H_z=\frac{Ia^2}{2(a^2+z^2)^{3/2}}\ \xrightarrow{z\gg a}\ \frac{Ia^2}{2z^3}"),
            S("Only the product I·πa², the magnetic dipole moment m = IA, survives.", r"H_z\approx\frac{m}{2\pi z^3},\qquad m=I\pi a^2"),
            S("A small loop of any shape with the same m looks identical from far away.")],
     answer_text="Seen from far away, each element of the loop is almost cancelled by the opposite element, which carries current in the opposite direction. "
                 "What remains falls off one power faster than a single current, giving 1/z³, just as an electric dipole's field does. "
                 "In the limit z ≫ a only the magnetic dipole moment m = I·πa² matters: H_z ≈ m/(2πz³) on the axis. "
                 "Any small current loop, square or circular, with the same m produces the same far field.",
     evidence_say="Engine axial profile of a 10 cm loop: beyond a few radii it approaches the dipole law.",
     plot=Series(_ax("z"), [("H on the axis", _ax("H"), "H")], "distance along the axis z (m)", "H (A/m)"),
     mistake="Using the near-field formula far away, or the far-field formula near the loop.",
     vals={}), "concept")

# ---------------------------------------------------------------- Maxwell & boundaries
T = "maxwell"
# Explained pilot (engine/explain.py): 7 numerical + 8 conceptual. Every number in the explanations is a
# «placeholder» filled from an engine run; material data: Ulaby & Ravaioli App. B unless marked "typical".
U = "Ulaby & Ravaioli Sec. "
_bE = lambda e1, e2, F1, th, rs=0.0: {"kind": "E", "eps1": e1, "eps2": e2, "F1": F1, "theta1_deg": th, "source": rs}
_bH = lambda m1, m2, F1, th: {"kind": "H", "mu1": m1, "mu2": m2, "F1": F1, "theta1_deg": th}
_ifig = lambda H=False: (lambda r, p: {"type": "interface", "e1": p["mu1" if H else "eps1"], "e2": p["mu2" if H else "eps2"], "theta": p["theta1_deg"],
                                       "theta2": r["values"]["theta2_deg"], "H": H})
_BV = {"t1": EV("F1", 0), "n1": EV("F1", 1), "t2": EV("F2", 0), "n2": EV("F2", 1), "F2": EV("F2_mag"), "th2": EV("theta2_deg")}
_norm = lambda key: (lambda r, p: (lambda a: (a / max(abs(a).max(), 1e-300)).tolist())(np.asarray(r[key], float)))

px(T, U + "4-8", "basic", "Refraction of E at a dielectric",
   "A static electric field of 100 V/m exists in air just above the flat face of a dielectric slab with εr = 5. "
   "The field makes 60° with the surface normal and the face carries no free charge. "
   "Find the magnitude of E just inside the slab and the angle it makes with the normal.",
   {"type": "interface", "e1": 1, "e2": 5, "theta": 60}, "mx/boundary", _bE(1, 5, 100, 60),
   [("|E₂|", V("F2_mag"), "V/m", 1), ("θ₂", V("theta2_deg"), "°", 1)],
   X(asked="The field just inside the slab: its magnitude |E₂| and its angle θ₂ from the normal.",
     idea="At a charge-free boundary the tangential part of E crosses unchanged, and the normal part of D = εE is continuous. "
          "So split E₁ into these two parts, carry each one across, and put E₂ back together.",
     steps=[S("Split E₁ into a part along the surface and a part along the normal.", r"E_{1t}=E_1\sin\theta_1=«t1»\ \text{V/m},\qquad E_{1n}=E_1\cos\theta_1=«n1»\ \text{V/m}"),
            S("The tangential part is continuous, so it is the same inside the slab.", r"E_{2t}=E_{1t}=«t2»\ \text{V/m}"),
            S("With no surface charge ε₁E₁n = ε₂E₂n, so the normal part shrinks by the permittivity ratio.", r"E_{2n}=\frac{\varepsilon_1}{\varepsilon_2}E_{1n}=«n2»\ \text{V/m}"),
            S("Recombine the two parts.", r"|E_2|=\sqrt{E_{2t}^2+E_{2n}^2}=«F2»\ \text{V/m},\qquad \theta_2=\tan^{-1}\frac{E_{2t}}{E_{2n}}=«th2»^\circ")],
     answer="|E₂| = «F2» V/m, at θ₂ = «th2»° from the normal.",
     whatif=[W("…only the angle θ₂ were asked?", lambda p: p, "Divide the two conditions: the magnitudes cancel and one rule for the angles is left.",
               r"\tan\theta_2=\frac{\varepsilon_{r2}}{\varepsilon_{r1}}\tan\theta_1\ \Rightarrow\ \theta_2=«th2»^\circ"),
             W("…the slab had εr = 2.5 instead?", lambda p: {**p, "eps2": 2.5}, "Only the normal part changes, so the field bends less: θ₂ = «th2»° and |E₂| = «F2» V/m.",
               r"E_{2n}=\frac{1}{2.5}E_{1n}=«n2»\ \text{V/m}"),
             W("…E₁ were normal to the face (θ₁ = 0)?", lambda p: {**p, "theta1_deg": 0}, "There is no tangential part, so E₂ is normal as well and simply ε₁/ε₂ times E₁: |E₂| = «F2» V/m.",
               r"E_2=\frac{\varepsilon_1}{\varepsilon_2}E_1=«F2»\ \text{V/m}")],
     mistake="Dividing the whole field by εr₂. Only the normal component is scaled; the tangential one is untouched.",
     fig=_ifig(), vals=_BV), "numeric")

px(T, U + "4-8", "exam", "Boundary with surface charge",
   "A flat interface separates a dielectric with εr = 2 (medium 1, above) from one with εr = 4 (medium 2, below). "
   "Just above the interface E₁ = 1 kV/m, pointing away from it at 30° from the normal. "
   "The interface carries a free surface charge ρs = 2 nC/m². Find |E₂| and its angle θ₂ from the normal just below the interface.",
   {"type": "interface", "e1": 2, "e2": 4, "theta": 30}, "mx/boundary", _bE(2, 4, 1000, 30, 2e-9),
   [("|E₂|", V("F2_mag"), "V/m", 1), ("θ₂", V("theta2_deg"), "°", 1)],
   X(asked="|E₂| and θ₂ just below a boundary that carries free surface charge.",
     idea="Tangential E is still continuous. The normal component of D now jumps by exactly the surface charge: "
          "D₁n − D₂n = ρs, with the normal pointing from medium 2 into medium 1.",
     steps=[S("Split E₁ into tangential and normal parts.", r"E_{1t}=«t1»\ \text{V/m},\qquad E_{1n}=«n1»\ \text{V/m}"),
            S("The tangential part carries over unchanged.", r"E_{2t}=E_{1t}=«t2»\ \text{V/m}"),
            S("Above the sheet D₁n = «D1» C/m². Below it the sheet's ρs has been subtracted.", r"D_{2n}=\varepsilon_1E_{1n}-\rho_s=«D2»\ \text{C/m}^2"),
            S("Convert back to E with the permittivity of medium 2.", r"E_{2n}=\frac{D_{2n}}{\varepsilon_2}=«n2»\ \text{V/m}"),
            S("Recombine.", r"|E_2|=«F2»\ \text{V/m},\qquad\theta_2=\tan^{-1}\frac{E_{2t}}{E_{2n}}=«th2»^\circ")],
     answer="|E₂| = «F2» V/m at θ₂ = «th2»° from the normal.",
     whatif=[W("…there were no surface charge?", lambda p: {**p, "source": 0.0}, "Then D₂n = D₁n and E₂n is simply ε₁E₁n/ε₂: |E₂| = «F2» V/m, θ₂ = «th2»°.",
               r"E_{2n}=\frac{\varepsilon_1}{\varepsilon_2}E_{1n}=«n2»\ \text{V/m}"),
             W("…the sheet carried −2 nC/m² instead?", lambda p: {**p, "source": -2e-9}, "A negative sheet adds to D below it: E₂n = «n2» V/m, so |E₂| = «F2» V/m.",
               r"E_{2n}=\frac{\varepsilon_1E_{1n}+|\rho_s|}{\varepsilon_2}=«n2»\ \text{V/m}"),
             W("…the question asked which ρs makes E₂ lie along the surface?", lambda p: {**p, "source": EPS0 * p["eps1"] * p["F1"] * math.cos(math.radians(p["theta1_deg"]))},
               "ρs must cancel D₁n completely, ρs = «rs» C/m². Then E₂n = 0 and θ₂ = «th2»°.", r"\rho_s=\varepsilon_1E_{1n}=«rs»\ \text{C/m}^2")],
     mistake="Writing the jump condition for E with ε₀, or with the wrong sign: the normal points from medium 2 into medium 1, so a positive ρs lowers D below the sheet.",
     fig=_ifig(), vals={**_BV, "D1": EV("flux", 0), "D2": EV("flux", 1), "rs": EV("source")}), "numeric")

px(T, U + "5-6", "exam", "H entering iron",
   "In air, a magnetic field H₁ = 10 A/m meets the flat surface of a soft-iron block (μr = 1000) at 45° from the normal. "
   "No surface current flows. Find the angle θ₂ of H inside the iron, measured from the normal, and the magnitude |H₂|.",
   {"type": "interface", "e1": 1, "e2": 1000, "theta": 45, "H": True}, "mx/boundary", _bH(1, 1000, 10, 45),
   [("θ₂", V("theta2_deg"), "°", 1), ("|H₂|", V("F2_mag"), "A/m", 1)],
   X(asked="The direction (θ₂ from the normal) and magnitude of H just inside the iron.",
     idea="The magnetic conditions mirror the electric ones: with no surface current, tangential H is continuous and normal B = μH is continuous. "
          "Iron's large μ therefore squeezes the normal component of H.",
     steps=[S("Split H₁ into tangential and normal parts.", r"H_{1t}=H_1\sin\theta_1=«t1»\ \text{A/m},\qquad H_{1n}=H_1\cos\theta_1=«n1»\ \text{A/m}"),
            S("Tangential H is continuous.", r"H_{2t}=H_{1t}=«t2»\ \text{A/m}"),
            S("Normal B is continuous, so the normal H drops by the factor μr.", r"H_{2n}=\frac{\mu_1}{\mu_2}H_{1n}=«n2»\ \text{A/m}"),
            S("Recombine. The tiny normal part makes θ₂ almost 90°.", r"\theta_2=\tan^{-1}\frac{H_{2t}}{H_{2n}}=«th2»^\circ,\qquad|H_2|=«F2»\ \text{A/m}")],
     answer="θ₂ = «th2»° (H runs almost along the surface), |H₂| = «F2» A/m.",
     whatif=[W("…the block had μr = 100?", lambda p: {**p, "mu2": 100}, "The normal part is cut by 100 instead of 1000: θ₂ = «th2»°.",
               r"\tan\theta_2=\frac{\mu_2}{\mu_1}\tan\theta_1\ \Rightarrow\ \theta_2=«th2»^\circ"),
             W("…the normal component of B were asked?", lambda p: p, "B_n is continuous, so it is the same on both sides: B₂n = B₁n = «Bn» T.",
               r"B_{2n}=B_{1n}=\mu_0H_{1n}=«Bn»\ \text{T}")],
     mistake="Expecting H to point straight into the iron. It is the reverse: inside high-μ material H lies almost along the surface.",
     fig=_ifig(True), vals={**_BV, "Bn": EV("flux", 0)}), "numeric")

px(T, U + "6-5", "basic", "Generator driving a load",
   "A 50-turn rectangular coil, 20 cm × 20 cm, spins at 60 revolutions per second about an axis perpendicular to a uniform field B = 0.3 T. "
   "Its terminals feed a 10 Ω resistor. Neglecting the coil's own resistance and inductance, find the peak EMF and the average power delivered to the resistor.",
   {"type": "generator", "N": 50, "R": 10}, "mx/faraday", {"mode": "motional", "N": 50, "B0": 0.3, "w": 0.2, "l": 0.2, "f": 60, "R": 10},
   [("V̂", V("V_peak"), "V", 1), ("P_av", V("P_av"), "W", 1)],
   X(asked="The amplitude V̂ of the generated voltage and the average power in the 10 Ω load.",
     idea="The flux through the coil changes because the coil turns: Φ = BA cos Ωt. "
          "Faraday's law turns that rate of change into an EMF, and the resistor sees a sinusoidal voltage.",
     steps=[S("Coil area and angular speed.", r"A=wl=«A»\ \text{m}^2,\qquad \Omega=2\pi f=«W»\ \text{rad/s}"),
            S("Flux through all N turns and its time derivative give the EMF.", r"N\Phi=NBA\cos\Omega t\ \Rightarrow\ V_{emf}=-N\frac{d\Phi}{dt}=NBA\Omega\sin\Omega t"),
            S("The peak is the amplitude of that sine.", r"\hat V=NBA\Omega=«V»\ \text{V}"),
            S("A sine of amplitude V̂ delivers V̂²/2R to a resistor on average.", r"P_{av}=\frac{\hat V^2}{2R}=«P»\ \text{W}")],
     answer="V̂ = «V» V and P_av = «P» W.",
     whatif=[W("…the coil spun twice as fast?", lambda p: {**p, "f": 2 * p["f"]}, "V̂ doubles to «V» V and, since P ∝ V̂², the power quadruples to «P» W.",
               r"\hat V\propto\Omega,\qquad P_{av}\propto\Omega^2"),
             W("…the load were 20 Ω?", lambda p: {**p, "R": 20}, "The EMF is set by the motion alone and stays «V» V; the power halves to «P» W.",
               r"P_{av}=\frac{\hat V^2}{2R}=«P»\ \text{W}")],
     mistake="Using f instead of Ω = 2πf in V̂ = NBAΩ, which makes the answer 2π times too small.",
     vals={"A": EV("A"), "W": EV("omega"), "V": EV("V_peak"), "P": EV("P_av")}), "numeric")

px(T, U + "6-2", "basic", "EMF in a tilted loop",
   "A stationary 10-turn square loop, 10 cm on a side, sits in a uniform field B(t) = 0.05 cos(2π·1000 t) T. "
   "The field direction makes 30° with the loop's normal. Find the peak induced EMF.",
   {"type": "tloop", "N": 10, "alpha": 30}, "mx/faraday", {"mode": "transformer", "N": 10, "B0": 0.05, "w": 0.1, "l": 0.1, "f": 1000, "alpha_deg": 30},
   [("V̂", V("V_peak"), "V", 1)],
   X(asked="The amplitude of the EMF induced in a loop that does not move.",
     idea="Only the component of B along the loop's normal threads the loop. "
          "The loop is fixed, so all of the EMF comes from B changing in time (transformer EMF).",
     steps=[S("Flux through one turn: only B cos α counts.", r"\Phi(t)=B_0A\cos\alpha\cos\omega t,\qquad A=«A»\ \text{m}^2"),
            S("Faraday's law for N turns.", r"V_{emf}=-N\frac{d\Phi}{dt}=NB_0A\,\omega\cos\alpha\,\sin\omega t"),
            S("Read off the amplitude.", r"\hat V=NB_0A\,\omega\cos\alpha=«V»\ \text{V}")],
     answer="V̂ = «V» V.",
     whatif=[W("…B were along the normal (α = 0)?", lambda p: {**p, "alpha_deg": 0}, "All of B threads the loop and the EMF is the largest possible: V̂ = «V» V.",
               r"\hat V=NB_0A\,\omega=«V»\ \text{V}"),
             W("…the field alternated at 50 Hz?", lambda p: {**p, "f": 50}, "The EMF is proportional to ω, so it drops to V̂ = «V» V.", r"\hat V\propto\omega")],
     mistake="Using sin α, i.e. measuring the angle from the loop's plane instead of from its normal.",
     vals={"A": EV("A"), "V": EV("V_peak")}), "numeric")

px(T, U + "6-7", "basic", "Wet soil: conductor or dielectric?",
   "Moist soil has εr = 20 and σ = 0.05 S/m (typical values), taken as constant with frequency. "
   "At what frequency are the conduction and displacement current densities equal in magnitude? Below that frequency, which one dominates?",
   {"type": "medium", "label": "moist soil"}, "mx/currents", {"eps_r": 20, "sigma": 0.05, "f": 1e6},
   [("f_c", V("fc"), "MHz", 1e-6)],
   X(asked="The crossover frequency f_c where |J_c| = |J_d|, and which current wins below it.",
     idea="In ∇×H = σE + jωεE the conduction term σE does not depend on frequency while the displacement term ωεE grows with it. "
          "They are equal where σ = ωε.",
     steps=[S("Ratio of the two current densities.", r"\frac{|J_c|}{|J_d|}=\frac{\sigma}{\omega\varepsilon}"),
            S("Set the ratio to 1 and solve for f.", r"f_c=\frac{\sigma}{2\pi\varepsilon_0\varepsilon_r}=«fc»\ \text{MHz}"),
            S("Below f_c the ratio is larger than 1, so conduction current dominates and the soil acts as a poor conductor.")],
     answer="f_c = «fc» MHz; below it conduction current dominates.",
     whatif=[W("…the ratio at 1 GHz were asked?", lambda p: {**p, "f": 1e9}, "|J_c|/|J_d| = «ratio»: displacement current is now the larger one, but neither is negligible, so the soil is a quasi-conductor (0.01 < σ/ωε < 100 in Ulaby's classification).",
               r"\frac{\sigma}{\omega\varepsilon}=«ratio»"),
             W("…the soil dried out to σ = 0.001 S/m?", lambda p: {**p, "sigma": 1e-3}, "f_c is proportional to σ and falls to «fc» MHz.", r"f_c\propto\sigma")],
     mistake="Calling a material a conductor or a dielectric without saying at which frequency.",
     vals={"fc": lambda r, p: r["values"]["fc"] / 1e6, "ratio": EV("ratio")}), "numeric")

px(T, U + "6-10", "basic", "Charge relaxation: copper vs distilled water",
   "Excess free charge is placed inside a block of copper (σ = 5.8 × 10⁷ S/m, εr = 1). "
   "How long does it take for the charge density inside to fall to 1/e of its initial value?",
   {"type": "medium", "label": "copper"}, "mx/currents", {"eps_r": 1, "sigma": 5.8e7, "f": 1e6},
   [("τ_r", V("tau"), "s", 1)],
   X(asked="The relaxation time τ_r after which the interior charge density has dropped to 1/e.",
     idea="Combine charge continuity ∇·J = −∂ρv/∂t with Ohm's law J = σE and Gauss's law ∇·E = ρv/ε. "
          "The result is a first-order decay with time constant ε/σ.",
     steps=[S("Substitute J = σE into the continuity equation and use Gauss's law.", r"\frac{\partial\rho_v}{\partial t}=-\sigma\,\nabla\cdot\mathbf E=-\frac{\sigma}{\varepsilon}\rho_v"),
            S("Solve the first-order equation.", r"\rho_v(t)=\rho_{v0}\,e^{-t/\tau_r},\qquad\tau_r=\frac{\varepsilon}{\sigma}"),
            S("Insert copper's values.", r"\tau_r=\frac{\varepsilon_0}{\sigma}=«tau»\ \text{s}"),
            S("This time is far shorter than the interval between electron collisions in the metal, so the real decay is slower than the model says. "
              "It is still instantaneous for any practical purpose.")],
     answer="τ_r = «tau» s for copper.",
     whatif=[W("…distilled water (εr = 81, σ = 2 × 10⁻⁴ S/m) were asked?", lambda p: {**p, "eps_r": 81, "sigma": 2e-4}, "τ_r = «tau» s: many orders of magnitude slower than copper, yet still very short.",
               r"\tau_r=\frac{81\,\varepsilon_0}{2\times10^{-4}}=«tau»\ \text{s}"),
             W("…sea water (εr = 81, σ = 4 S/m) were asked?", lambda p: {**p, "eps_r": 81, "sigma": 4}, "τ_r = «tau» s.", r"\tau_r=\varepsilon/\sigma=«tau»\ \text{s}")],
     mistake="Thinking the charge leaves the conductor. It moves to the surface and stays there.",
     vals={"tau": EV("tau")}), "numeric")

# ---- conceptual
_e40 = _bE(1, 4, 100, 40)
px(T, U + "4-8", "basic", "Why tangential E cannot jump",
   "Explain why the tangential component of a static electric field is the same on both sides of any boundary, whatever the two materials are. "
   "Is the normal component continuous as well?",
   {"type": "interface", "e1": 1, "e2": 4, "theta": 40}, "mx/boundary", _e40, [],
   X(asked="A reason, from Maxwell's equations, why E_t is continuous, and whether E_n is.",
     idea="In electrostatics ∮E·dl = 0 around any closed path. Apply it to a thin rectangle that straddles the boundary.",
     steps=[S("Take a rectangle of length Δl with one long side in each medium and let its height shrink to zero."),
            S("The short sides then contribute nothing, and the two long sides give the tangential fields.", r"\oint\mathbf E\cdot d\mathbf l=(E_{1t}-E_{2t})\,\Delta l=0\ \Rightarrow\ E_{1t}=E_{2t}"),
            S("The normal component is fixed by Gauss's law instead, which involves ε, so E_n generally jumps.")],
     answer_text="Because the electrostatic field is conservative: its line integral around any closed loop is zero. "
                 "A loop hugging the boundary picks up only the tangential components on its two long sides, and these must cancel, so E₁t = E₂t for any pair of materials. "
                 "The normal component is governed by Gauss's law, which constrains D = εE rather than E. With different permittivities E_n therefore jumps; "
                 "without surface charge it changes by the factor ε₁/ε₂.",
     evidence_say="Engine runs with E₁ = 100 V/m at 40° from the normal: E₂t stays at «t» V/m for every εr₂ in the plot, while E₂n falls as 1/εr₂.",
     plot=Sweep("eps2", [1, 2, 4, 8, 16], [("tangential E₂t", EV("F2", 0), "E"), ("normal E₂n", EV("F2", 1))], "relative permittivity of medium 2, εr₂", "field in medium 2 (V/m)", logx=True),
     mistake="Assuming E_n is continuous too. Without surface charge it is D_n that is continuous.",
     vals={"t": EV("F2", 0)}), "concept")

px(T, U + "4-8", "exam", "What a surface charge does to D",
   "A thin sheet of free charge ρs lies on the boundary between two dielectrics. "
   "Which field component changes across the sheet, and by how much? Why does the size of the jump not depend on the two permittivities?",
   {"type": "interface", "e1": 1, "e2": 4, "theta": 40}, "mx/boundary", _e40, [],
   X(asked="Which component jumps at a charged boundary, by how much, and why ε does not enter.",
     idea="Apply Gauss's law ∮D·ds = Q_free to a flat pill-box that encloses a patch ΔS of the sheet.",
     steps=[S("Shrink the pill-box height to zero, so only its two faces of area ΔS carry flux."),
            S("The enclosed free charge is ρs ΔS, so the normal D changes by ρs.", r"\hat n_2\cdot(\mathbf D_1-\mathbf D_2)=\rho_s"),
            S("D counts only free charge, so ε does not appear; E_n jumps by a material-dependent amount because E also feels the bound charge.")],
     answer_text="Only the normal component of D jumps, by exactly ρs: D₁n − D₂n = ρs, with the normal pointing from medium 2 into medium 1. "
                 "Tangential E is unaffected, because the loop argument still applies. "
                 "The jump is independent of ε₁ and ε₂ because D is defined so that its flux counts free charge only; the bound polarisation charge of each dielectric is already built into ε. "
                 "The normal E, by contrast, jumps by an amount that does depend on the materials.",
     evidence_say="Engine runs (E₁ = 100 V/m at 40°, εr₁ = 1, εr₂ = 4): D₁n stays fixed while D₂n falls one-for-one with ρs, so the gap between the curves is always ρs.",
     plot=Sweep("source", [0, 2e-10, 4e-10, 6e-10], [("D₁n above the sheet", EV("flux", 0), "E"), ("D₂n below the sheet", EV("flux", 1))],
                "surface charge ρs (C/m²)", "normal D (C/m²)"),
     mistake="Putting ρs into a condition on E with ε₀. The clean statement is for D.",
     vals={}), "concept")

px(T, U + "5-6", "exam", "Why H in iron hugs the surface",
   "A magnetic field passes from air into a material with very large permeability (μr ≫ 1) at an oblique angle. "
   "Without calculating, predict the direction of H inside the material, and explain how this is used to shield sensitive equipment.",
   {"type": "interface", "e1": 1, "e2": 1000, "theta": 30, "H": True}, "mx/boundary", _bH(1, 1000, 1, 30), [],
   X(asked="The direction of H inside a high-μ material, and why that shields.",
     idea="Combine the two magnetic boundary conditions into a refraction law for field lines.",
     steps=[S("Tangential H is continuous and normal B = μH is continuous."),
            S("Dividing the two conditions gives the refraction law.", r"\frac{\tan\theta_2}{\tan\theta_1}=\frac{\mu_2}{\mu_1}"),
            S("For μ₂/μ₁ in the thousands tan θ₂ is huge, so θ₂ is close to 90°: H runs almost parallel to the surface.")],
     answer_text="Inside the high-μ material H and B bend toward the surface and run almost parallel to it, for any outside angle except those within a tiny fraction of a degree of the normal (θ₂ ≈ 90° needs μr tan θ₁ ≫ 1). "
                 "Field lines therefore prefer to travel inside the material, along its walls. "
                 "A closed box of such material collects the flux and guides it around the enclosed space, so the field inside the box is much weaker. "
                 "This is magnetic shielding with mu-metal or soft iron.",
     evidence_say="Engine runs with H₁ at 30° from the normal: θ₂ climbs toward 90° as μr₂ grows (at μr₂ = 1000 it is «th»°).",
     plot=Sweep("mu2", [1, 3, 10, 30, 100, 300, 1000], [("θ₂ of H₂", EV("theta2_deg"), "H")], "relative permeability of medium 2, μr₂", "angle of H₂ from the normal, θ₂ (°)", logx=True),
     mistake="Thinking H goes straight into the iron. That happens only at, or extremely close to, normal incidence.",
     vals={"th": EV("theta2_deg")}), "concept")

_gen = {"mode": "motional", "N": 50, "B0": 0.3, "w": 0.2, "l": 0.2, "f": 60, "R": 10}
px(T, U + "6-5", "exam", "Zero flux, maximum EMF",
   "A 50-turn, 20 cm × 20 cm coil spins at 60 rev/s in a uniform B = 0.3 T, about an axis perpendicular to B. "
   "At the instant the plane of the coil is parallel to B, no flux passes through it. Is the induced EMF zero at that instant? Explain.",
   {"type": "generator", "N": 50}, "mx/faraday", _gen, [],
   X(asked="Whether the EMF vanishes at the moment the flux through the coil is zero.",
     idea="The EMF depends on how fast the flux changes, not on how much flux there is.",
     steps=[S("The flux varies as cos Ωt and the EMF as sin Ωt.", r"N\Phi=NBA\cos\Omega t,\qquad V_{emf}=NBA\Omega\sin\Omega t"),
            S("The flux is zero where cos Ωt = 0, and there sin Ωt = ±1."),
            S("So the EMF is at its peak, «V» V, at the very instant the flux is zero.")],
     answer_text="No, it is at its maximum. With the coil's plane parallel to B the flux through it is zero, but it is changing fastest: "
                 "the two sides parallel to the rotation axis cut across the field lines at full speed. "
                 "Faraday's law depends on dΦ/dt, and for Φ ∝ cos Ωt the slope is steepest where Φ crosses zero. "
                 "Conversely, when the coil faces the field squarely the flux is largest but momentarily not changing, and the EMF is zero.",
     evidence_say="Engine curves over two revolutions: every zero of the flux lines up with a peak of the EMF.",
     plot=Series(lambda r, p: r["t"], [("flux NΦ", _norm("Phi"), "H"), ("EMF", _norm("emf"))], "time t (s)", "normalised (peak = 1)"),
     mistake="Linking the EMF to the flux itself rather than to its rate of change.",
     vals={"V": EV("V_peak")}), "concept")

px(T, U + "6-1", "basic", "Which way does the induced current flow?",
   "A fixed loop sits in a uniform field B(t) = B₀ cos ωt directed along the loop's normal. "
   "While the flux through the loop is increasing, does the induced current create a field that adds to B or opposes it? "
   "What would go wrong if it were the other way round?",
   {"type": "tloop", "N": 1, "alpha": 0}, "mx/faraday", {"mode": "transformer", "N": 1, "B0": 0.05, "w": 0.1, "l": 0.1, "f": 1000}, [],
   X(asked="The direction of the induced field relative to B while the flux grows, and why it must be so.",
     idea="Faraday's law carries a minus sign, V_emf = −N dΦ/dt. That sign is Lenz's law.",
     steps=[S("A positive EMF drives current in the sense that, by the right-hand rule, makes flux along the chosen normal."),
            S("While Φ rises dΦ/dt > 0, so V_emf < 0: the current flows the other way and its own flux opposes the change."),
            S("When Φ falls the sign reverses and the induced flux props it up.")],
     answer_text="It opposes the change. While the flux is increasing, the induced current circulates so that its own field points against B inside the loop; "
                 "while the flux is decreasing, the induced field points along B. This is Lenz's law, the minus sign in Faraday's law. "
                 "If it were the other way, a small increase in flux would induce a current that increases the flux further, a runaway that would create energy from nothing.",
     evidence_say="Engine curves: wherever the flux curve rises, the EMF curve is negative, and wherever it falls, the EMF is positive.",
     plot=Series(lambda r, p: r["t"], [("flux NΦ", _norm("Phi"), "H"), ("EMF", _norm("emf"))], "time t (s)", "normalised (peak = 1)"),
     mistake="Saying the induced field always opposes B. It opposes the change in flux, so while the flux is falling the induced field points along B.",
     vals={}), "concept")

px(T, U + "6-7", "exam", "Why Ampère's law needs displacement current",
   "A capacitor is being charged through its leads by a current i(t). Apply ∮H·dl = I_enclosed to a circle around one lead, "
   "first with a flat disc as the surface and then with a bulging surface that passes between the plates without touching the wire. "
   "Why do the two choices disagree without Maxwell's correction, and how does displacement current fix it?",
   {"type": "plates"}, "mx/currents", {"eps_r": 1, "sigma": 0, "f": 1e6}, [],
   X(asked="Why the original Ampère law is inconsistent for a charging capacitor, and what the displacement term repairs.",
     idea="Ampère's law must give the same current for every surface bounded by the same loop. "
          "Charge piling up on the plates breaks that unless a term ∂D/∂t is added.",
     steps=[S("Flat disc: the wire pierces it, so the enclosed current is i."),
            S("Bulging surface: no wire crosses it, so the conduction current through it is zero, which contradicts the first result."),
            S("Between the plates D grows as charge builds up; the flux of ∂D/∂t through the gap equals i.",
              r"\oint\mathbf H\cdot d\mathbf l=\int_S\Big(\mathbf J+\frac{\partial\mathbf D}{\partial t}\Big)\cdot d\mathbf s")],
     answer_text="Without the extra term the enclosed current is i for the disc and zero for the bulging surface, although both share the same boundary circle, "
                 "so H around the circle would have two values. Maxwell added the displacement current density ∂D/∂t. "
                 "In the gap D equals the plate charge density, which grows as charge arrives, and the flux of ∂D/∂t through the gap is exactly the current in the lead. "
                 "Every surface then gives the same total, in agreement with charge conservation. "
                 "The same term lets a changing E produce H in empty space, the basis of electromagnetic waves.",
     evidence_say="For scale: in vacuum at 1 MHz, a field of 1 V/m carries a displacement current density of «Jd» A/m², and it grows in proportion to frequency.",
     mistake="Picturing displacement current as charge crossing the gap. No charge crosses; the field between the plates is changing.",
     vals={"Jd": EV("Jd")}), "concept")

px(T, U + "6-7, 7-4", "exam", "Sea water: conductor at 1 kHz, dielectric at 100 GHz?",
   "Sea water has σ ≈ 4 S/m and εr ≈ 81. In the constant-εr model it is a good conductor at 1 kHz but a low-loss dielectric at 100 GHz. "
   "Explain the change, and say what this simple model leaves out at the high-frequency end.",
   {"type": "medium", "label": "sea water"}, "mx/currents", {"eps_r": 81, "sigma": 4, "f": 1e3}, [],
   X(asked="Why the same material is a conductor at low frequency and a dielectric at high frequency, and where the model fails.",
     idea="Compare the conduction and displacement terms of Ampère–Maxwell. Their ratio σ/ωε falls as 1/f.",
     steps=[S("Conduction current σE is fixed while displacement current ωεE grows with frequency.", r"\frac{|J_c|}{|J_d|}=\frac{\sigma}{\omega\varepsilon}"),
            S("At 1 kHz the ratio is «r1», so conduction dominates."),
            S("The two are equal at f_c = «fc» GHz; well above that, at 100 GHz, displacement current dominates in this model.",
              r"f_c=\frac{\sigma}{2\pi\varepsilon}=«fc»\ \text{GHz}")],
     answer_text="The conduction term σE does not change with frequency, while the displacement term ωεE rises in proportion to it. "
                 "Their ratio is enormous at 1 kHz, so sea water acts as a conductor and radio barely penetrates it. "
                 "The ratio passes through 1 at f_c = «fc» GHz, and at 100 GHz it is below 0.01, Ulaby's threshold for a low-loss dielectric. "
                 "The model leaves out that water's own permittivity is not constant: the dipole relaxation of water molecules, centred near 20 GHz, "
                 "lowers εr to under 10 at 100 GHz and adds a large loss of its own (Meissner & Wentz, 2004). Real sea water at 100 GHz is therefore far lossier than σ alone predicts.",
     evidence_say="Engine runs of σ/ωε from 1 kHz to 100 GHz: a straight line on log–log axes with slope −1, crossing 1 at f_c.",
     plot=Sweep("f", [1e3, 1e5, 1e7, 1e9, 1e11], EV("ratio"), "frequency f (Hz)", "|J<sub>c</sub>| / |J<sub>d</sub>|", logx=True, logy=True),
     mistake="Treating 'conductor' and 'dielectric' as fixed labels of a material. They describe it at a given frequency.",
     vals={"r1": EV("ratio"), "fc": lambda r, p: r["values"]["fc"] / 1e9}), "concept")

px(T, U + "6-10", "basic", "Why excess charge lives on the surface",
   "Excess charge is placed on a solid copper sphere. Why does all of it end up on the outer surface, and how quickly does that happen?",
   {"type": "medium", "label": "copper"}, "mx/currents", {"eps_r": 1, "sigma": 5.8e7, "f": 1e6}, [],
   X(asked="Why a conductor's excess charge sits on its surface, and the time scale for getting there.",
     idea="Inside a conductor any free charge density decays as e^(−t/τ_r) with τ_r = ε/σ. "
          "In equilibrium E = 0 inside, and Gauss's law then leaves no room for interior charge.",
     steps=[S("Continuity, Ohm's law and Gauss's law give exponential decay of interior charge.", r"\rho_v(t)=\rho_{v0}e^{-t/\tau_r},\qquad\tau_r=\frac{\varepsilon}{\sigma}"),
            S("For copper the model gives τ_r = «tau» s, effectively instant."),
            S("Once the charges stop moving E = 0 inside, so a Gaussian surface drawn anywhere inside the metal encloses no charge.")],
     answer_text="Like charges repel, and in a conductor they are free to move, so they push each other apart until no force acts on any of them, that is, until E = 0 throughout the metal. "
                 "Gauss's law applied to any closed surface drawn inside the metal then encloses zero charge, so the excess charge can only sit on the outer surface. "
                 "The relaxation model ρv ∝ e^(−σt/ε) shows how fast this happens: for copper the time constant is so short that the redistribution is instantaneous on any circuit time scale.",
     evidence_say="Engine: τ_r = «tau» s for copper; its independent check integrates dρ/dt = −σρ/ε numerically and agrees.",
     mistake="Thinking the charge spreads through the volume, as it would in an insulator.",
     vals={"tau": EV("tau")}), "concept")

# ---------------------------------------------------------------- plane waves
T = "waves"
# Explained (engine/explain.py): 7 numerical + 8 conceptual.
_mag = lambda key: (lambda r, p: [math.hypot(a, b) for a, b in zip(r["field"][key]["re"], r["field"][key]["im"])])
_fz = lambda r, p: r["field"]["z"]
_WV = {"lt": EV("loss_tangent"), "a": EV("alpha"), "b": EV("beta"), "adb": EV("alpha_dB"), "eta": EV("eta_mag"), "ph": EV("eta_phase_deg"),
       "vp": EV("vp"), "lam": EV("wavelength"), "S": EV("S_av0")}
_ds = lambda unit: (lambda r, p: r["values"]["skin_depth"] * unit)

px(T, "Ulaby & Ravaioli Sec. 7-5", "basic", "Skin depth of copper",
   "A 10 MHz current flows in a copper conductor (σ = 5.8 × 10⁷ S/m). How deep below the surface does it penetrate, measured by the skin depth?",
   {"type": "slab", "label": "copper"}, "waves/solve", {"f": 1e7, "sigma": 5.8e7}, [("δs", V("skin_depth"), "µm", 1e6)],
   X(asked="The skin depth δs of copper at 10 MHz.",
     idea="In a good conductor the fields decay as e^(−z/δs) with δs = 1/√(πfμσ). First confirm that copper is a good conductor at this frequency.",
     steps=[S("Loss tangent: enormous, so the good-conductor formulas apply.", r"\frac{\sigma}{\omega\varepsilon}=«lt»"),
            S("Attenuation constant.", r"\alpha=\sqrt{\pi f\mu_0\sigma}=«a»\ \text{Np/m}"),
            S("Skin depth.", r"\delta_s=\frac1\alpha=«d»\ \mu\text{m}")],
     answer="δs = «d» µm",
     whatif=[W("…the frequency were 1 GHz?", lambda p: {**p, "f": 1e9}, "δs ∝ 1/√f: «d» µm, which is why RF circuits use plated or polished surfaces.", r"\delta_s=«d»\ \mu\text{m}"),
             W("…the metal were stainless steel (σ ≈ 1.4 × 10⁶ S/m)?", lambda p: {**p, "sigma": 1.4e6}, "δs ∝ 1/√σ: «d» µm.", r"\delta_s=«d»\ \mu\text{m}")],
     mistake="Using δs = 1/(πfμσ) without the square root.",
     plot=Series(_fz, [("|E| inside the copper", _mag("E"), "E")], "depth z (m)", "|E| (relative)"),
     evidence_say="Engine field profile: |E| falls to 1/e of its surface value at z = δs.",
     vals={**_WV, "d": _ds(1e6)}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 7-5", "basic", "Skin depth of aluminium at 60 Hz",
   "Overhead power lines carry 60 Hz current in aluminium conductors (σ = 3.5 × 10⁷ S/m). Find the skin depth, and explain why very thick conductors are made of strands around a steel core rather than solid aluminium.",
   {"type": "slab", "label": "aluminium"}, "waves/solve", {"f": 60, "sigma": 3.5e7}, [("δs", V("skin_depth"), "mm", 1e3)],
   X(asked="δs of aluminium at power-line frequency, and its practical consequence.",
     idea="Even at 60 Hz the current crowds towards the surface of a good conductor; metal much deeper than δs carries little current.",
     steps=[S("Good-conductor skin depth.", r"\delta_s=\frac{1}{\sqrt{\pi f\mu_0\sigma}}=«d»\ \text{mm}"),
            S("In a solid conductor much thicker than about 2δs, the core carries little current but adds weight and cost."),
            S("So large conductors use a steel core for strength, with aluminium strands where the current actually flows.")],
     answer="δs = «d» mm",
     whatif=[W("…the line ran at 50 Hz?", lambda p: {**p, "f": 50}, "δs = «d» mm, slightly deeper.", r"\delta_s=«d»\ \text{mm}"),
             W("…the conductor were copper?", lambda p: {**p, "sigma": 5.8e7}, "δs = «d» mm.", r"\delta_s=«d»\ \text{mm}")],
     mistake="Assuming skin effect matters only at radio frequencies. For thick power conductors it matters at 50–60 Hz.",
     vals={**_WV, "d": _ds(1e3)}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 7-4", "exam", "Attenuation in sea water",
   "A 1 MHz radio wave travels through sea water (εr = 81, σ = 4 S/m). Find the attenuation in dB per metre, and the depth at which the signal has lost 100 dB.",
   {"type": "slab", "label": "sea water"}, "waves/solve", {"f": 1e6, "eps_r": 81, "sigma": 4}, [("α", V("alpha_dB"), "dB/m", 1)],
   X(asked="α in dB/m and the depth for 100 dB of loss.",
     idea="Check the regime with the loss tangent; sea water at 1 MHz is a good conductor, so α ≈ √(πfμσ). Then convert to dB.",
     steps=[S("Loss tangent.", r"\frac{\sigma}{\omega\varepsilon}=«lt»"),
            S("Attenuation constant (exact formula, which here equals the good-conductor value).", r"\alpha=«a»\ \text{Np/m}"),
            S("In dB per metre.", r"\alpha_{dB}=20\log_{10}(e)\,\alpha=«adb»\ \text{dB/m}"),
            S("Depth for 100 dB.", r"z=\frac{100}{\alpha_{dB}}=«z»\ \text{m}")],
     answer="α = «adb» dB/m; 100 dB is lost within «z» m",
     whatif=[W("…the frequency were 10 kHz?", lambda p: {**p, "f": 1e4}, "α ∝ √f: «adb» dB/m, which is why submarines use very low frequencies.", r"\alpha_{dB}=«adb»\ \text{dB/m}"),
             W("…it were fresh water (σ ≈ 0.01 S/m)?", lambda p: {**p, "sigma": 0.01}, "Now σ/ωε ≈ «lt» and the loss is far smaller: «adb» dB/m.", r"\alpha_{dB}=«adb»\ \text{dB/m}")],
     mistake="Treating sea water as a dielectric with εr = 81 at radio frequencies.",
     vals={**_WV, "z": lambda r, p: 100 / r["values"]["alpha_dB"]}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 7-4", "exam", "Is it a low-loss dielectric?",
   "A dielectric has εr = 4 and σ = 0.01 S/m. At 1 GHz, find its loss tangent and attenuation constant, and decide which approximation, if any, is valid.",
   {"type": "slab", "label": "εr = 4, σ = 0.01 S/m"}, "waves/solve", {"f": 1e9, "eps_r": 4, "sigma": 0.01},
   [("ε″/ε′", V("loss_tangent"), "", 1), ("α", V("alpha"), "Np/m", 1)],
   X(asked="The loss tangent, α, and the applicable regime.",
     idea="Ulaby classifies media by ε″/ε′ = σ/ωε: below 0.01 low-loss, above 100 good conductor, in between quasi-conductor.",
     steps=[S("Loss tangent.", r"\frac{\varepsilon''}{\varepsilon'}=\frac{\sigma}{\omega\varepsilon}=«lt»"),
            S("It lies between 0.01 and 100, so this is a quasi-conductor and the exact formula is required.", r"\alpha=\omega\sqrt{\frac{\mu\varepsilon}{2}\Big[\sqrt{1+(\varepsilon''/\varepsilon')^2}-1\Big]}=«a»\ \text{Np/m}"),
            S("The low-loss shortcut (σ/2)√(μ/ε) happens to be close here because ε″/ε′ is still well below 1.")],
     answer="ε″/ε′ = «lt», α = «a» Np/m",
     whatif=[W("…σ were 10⁻⁴ S/m?", lambda p: {**p, "sigma": 1e-4}, "ε″/ε′ = «lt»: low-loss, α = «a» Np/m.", r"\alpha=«a»\ \text{Np/m}"),
             W("…the frequency were 10 MHz?", lambda p: {**p, "f": 1e7}, "ε″/ε′ = «lt»: now a quasi-conductor near the good-conductor end, α = «a» Np/m.", r"\alpha=«a»\ \text{Np/m}")],
     mistake="Calling a material 'low-loss' or 'conducting' without computing σ/ωε at the frequency of interest.",
     vals=_WV), "numeric")

px(T, "Ulaby & Ravaioli Sec. 7-3", "basic", "Phase velocity and wavelength in a dielectric",
   "A 1 GHz plane wave travels in a lossless dielectric with εr = 9. Find its phase velocity, wavelength and intrinsic impedance.",
   {"type": "slab", "label": "εr = 9"}, "waves/solve", {"f": 1e9, "eps_r": 9}, [("u_p", V("vp"), "m/s", 1), ("λ", V("wavelength"), "cm", 100)],
   X(asked="u_p, λ and η in the dielectric.",
     idea="Everything scales with √εr: the wave is slower, shorter, and has a lower E/H ratio.",
     steps=[S("Phase velocity.", r"u_p=\frac{c}{\sqrt{\varepsilon_r}}=«vp»\ \text{m/s}"),
            S("Wavelength.", r"\lambda=\frac{u_p}{f}=«lamc»\ \text{cm}"),
            S("Intrinsic impedance.", r"\eta=\frac{\eta_0}{\sqrt{\varepsilon_r}}=«eta»\ \Omega")],
     answer="u_p = «vp» m/s, λ = «lamc» cm, η = «eta» Ω",
     whatif=[W("…εr were 2.25?", lambda p: {**p, "eps_r": 2.25}, "u_p = «vp» m/s, λ = «lamc» cm, η = «eta» Ω.", r"\sqrt{\varepsilon_r}=1.5"),
             W("…the frequency were 2 GHz?", lambda p: {**p, "f": 2e9}, "u_p and η do not change; λ halves to «lamc» cm.", r"\lambda=«lamc»\ \text{cm}")],
     mistake="Dividing by εr instead of √εr.",
     vals={**_WV, "lamc": lambda r, p: r["values"]["wavelength"] * 100}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 7-7", "basic", "Power density of a plane wave",
   "A plane wave in free space has an electric field amplitude of 100 V/m. Find the amplitude of H and the time-average power density.",
   {"type": "slab", "label": "free space"}, "waves/solve", {"f": 1e9, "E0": 100}, [("S_av", V("S_av0"), "W/m²", 1)],
   X(asked="|H| and the average Poynting vector for E₀ = 100 V/m.",
     idea="In a plane wave H = E/η and the average power density is half the product of the amplitudes.",
     steps=[S("Intrinsic impedance of free space.", r"\eta_0=\sqrt{\mu_0/\varepsilon_0}=«eta»\ \Omega"),
            S("Magnetic field amplitude.", r"H_0=\frac{E_0}{\eta_0}=«H»\ \text{A/m}"),
            S("Average power density.", r"S_{av}=\frac{E_0^2}{2\eta_0}=«S»\ \text{W/m}^2")],
     answer="H₀ = «H» A/m, S_av = «S» W/m²",
     whatif=[W("…E₀ were 200 V/m?", lambda p: {**p, "E0": 200}, "S ∝ E₀²: «S» W/m².", r"S_{av}=«S»\ \text{W/m}^2"),
             W("…the wave were in a dielectric with εr = 4?", lambda p: {**p, "eps_r": 4}, "η halves, so for the same E₀ the power density doubles: «S» W/m².", r"S_{av}=\frac{E_0^2}{2\eta}=«S»\ \text{W/m}^2")],
     mistake="Forgetting the ½ for time-averaging, or using rms and peak values inconsistently.",
     vals={**_WV, "H": lambda r, p: p["E0"] / r["values"]["eta_mag"]}), "numeric")

px(T, "Ulaby & Ravaioli Sec. 7-4, 7-5", "exam", "Microwave in muscle",
   "Muscle tissue at 2.45 GHz (the microwave-oven frequency) has εr ≈ 52.7 and σ ≈ 1.74 S/m (typical values). Find the skin depth, i.e. the depth at which the field drops to 1/e.",
   {"type": "slab", "label": "muscle tissue"}, "waves/solve", {"f": 2.45e9, "eps_r": 52.7, "sigma": 1.74}, [("δs", V("skin_depth"), "cm", 100)],
   X(asked="The penetration depth of 2.45 GHz fields in muscle.",
     idea="Muscle at this frequency is a quasi-conductor, so neither shortcut applies and δs = 1/α must come from the exact α.",
     steps=[S("Loss tangent.", r"\frac{\sigma}{\omega\varepsilon}=«lt»"),
            S("Exact attenuation constant.", r"\alpha=«a»\ \text{Np/m}"),
            S("Skin depth.", r"\delta_s=\frac1\alpha=«d»\ \text{cm}")],
     answer="δs = «d» cm",
     whatif=[W("…fat tissue (εr ≈ 5.3, σ ≈ 0.1 S/m) were asked?", lambda p: {**p, "eps_r": 5.3, "sigma": 0.1}, "Lower loss, deeper penetration: δs = «d» cm.", r"\delta_s=«d»\ \text{cm}"),
             W("…the good-conductor formula were used anyway?", lambda p: p, "It would give 1/√(πfμσ) = «dgc» cm, a clear overestimate of the loss.", r"\delta_s\approx\frac{1}{\sqrt{\pi f\mu_0\sigma}}=«dgc»\ \text{cm}")],
     mistake="Applying the good-conductor skin-depth formula to tissue, where σ/ωε is of order 1.",
     vals={**_WV, "d": _ds(100), "dgc": lambda r, p: 100 / math.sqrt(math.pi * p["f"] * 4e-7 * math.pi * p["sigma"])}), "numeric")

# ---- conceptual
px(T, "Ulaby & Ravaioli Sec. 7-2", "basic", "What η₀ ≈ 377 Ω means",
   "The 'intrinsic impedance of free space' is about 377 Ω. There is no resistor in empty space, so what does this number describe?",
   {"type": "slab", "label": "free space"}, "waves/solve", {"f": 1e9}, [],
   X(asked="The physical meaning of η₀.",
     idea="In a plane wave E and H are locked together; η is their ratio, fixed by μ and ε of the medium.",
     steps=[S("From Maxwell's equations for a plane wave, E and H are perpendicular, in phase in a lossless medium, and in a fixed ratio.", r"\eta_0=\frac{|E|}{|H|}=\sqrt{\frac{\mu_0}{\varepsilon_0}}=«eta»\ \Omega"),
            S("It sets how much power a given field carries: S = |E|²/2η₀."),
            S("No energy is dissipated: the 'impedance' describes the wave, not a loss.")],
     answer_text="η₀ is the ratio of the electric to the magnetic field amplitude in a plane wave travelling in vacuum, |E|/|H| = √(μ₀/ε₀) ≈ «eta» Ω. "
                 "It has units of ohms because E is in V/m and H in A/m, but nothing is dissipated: it describes how the two fields are tied together, "
                 "and how much power a given E carries, S = |E|²/(2η₀). "
                 "It plays the same role as the characteristic impedance of a transmission line, which is why mismatched impedances cause reflections in both.",
     evidence_say="Engine: η₀ = «eta» Ω with phase «ph}°, i.e. E and H in phase.".replace("«ph}", "«ph»"),
     mistake="Thinking free space 'resists' or absorbs the wave.",
     vals=_WV), "concept")

px(T, "Ulaby & Ravaioli Sec. 7-5", "exam", "Why H lags E by 45° in a good conductor",
   "In a lossless medium E and H are in phase. In a good conductor H lags E by 45°. Why, and what does it mean for the power flow?",
   {"type": "slab", "label": "copper"}, "waves/solve", {"f": 1e7, "sigma": 5.8e7}, [],
   X(asked="The phase of the intrinsic impedance in a good conductor.",
     idea="η = √(jωμ/(σ + jωε)). When σ ≫ ωε, the square root of j gives a 45° phase.",
     steps=[S("Good-conductor limit.", r"\eta\approx\sqrt{\frac{j\omega\mu}{\sigma}}=(1+j)\sqrt{\frac{\pi f\mu}{\sigma}}"),
            S("So |η| is tiny and its phase is 45°.", r"|\eta|=«eta»\ \Omega,\qquad\angle\eta=«ph»^\circ"),
            S("A phase difference between E and H means part of the field energy is exchanged back and forth while the rest is absorbed.")],
     answer_text="In a good conductor the conduction current dominates, and the intrinsic impedance becomes η ≈ (1 + j)√(πfμ/σ). "
                 "The factor (1 + j) has a phase of 45°, so H lags E by 45°. "
                 "Its magnitude is tiny, of order milliohms for metals, which means E is very small for a given H: a metal surface is almost a short circuit. "
                 "Because E and H are not in phase, the time-average Poynting vector is smaller than |E||H|/2, and the power that does enter is absorbed within a few skin depths.",
     evidence_say="Engine runs at 10 MHz as σ grows: the phase of η rises from 0° (dielectric) to 45° (good conductor).",
     plot=Sweep("sigma", [1e-6, 1e-4, 1e-3, 1e-2, 1e-1, 1, 1e3, 5.8e7], [("phase of η", EV("eta_phase_deg"), "S")], "conductivity σ (S/m)", "phase of η (°)", logx=True),
     mistake="Assuming E and H are always in phase in a plane wave.",
     vals=_WV), "concept")

px(T, "Ulaby & Ravaioli Sec. 7-4", "exam", "Low-loss, quasi-conductor, good conductor",
   "Why do textbooks classify media by σ/ωε rather than by σ alone? Can the same material be a good conductor at one frequency and low-loss at another?",
   {"type": "slab", "label": "lossy medium"}, "waves/solve", {"f": 1e6, "eps_r": 10, "sigma": 0.01}, [],
   X(asked="The meaning of σ/ωε and its frequency dependence.",
     idea="σ/ωε is the ratio of conduction to displacement current. It falls as 1/f, so the same material changes class with frequency.",
     steps=[S("Ratio of the two current densities in Ampère–Maxwell.", r"\frac{|J_c|}{|J_d|}=\frac{\sigma}{\omega\varepsilon}=\frac{\varepsilon''}{\varepsilon'}"),
            S("Ulaby's classes: below 0.01 low-loss dielectric, 0.01 to 100 quasi-conductor, above 100 good conductor."),
            S("Because ω is in the denominator, raising the frequency moves a material from 'conductor' towards 'dielectric'.")],
     answer_text="The behaviour of a wave depends on which current dominates in Ampère–Maxwell: conduction current σE or displacement current jωεE. "
                 "Their ratio, σ/ωε, is the loss tangent ε″/ε′. Ulaby calls a medium a low-loss dielectric below 0.01, a good conductor above 100, and a quasi-conductor in between. "
                 "Since ω appears in the denominator, the class changes with frequency: a moist soil with σ = 0.01 S/m and εr = 10 is a good conductor at low audio frequencies, "
                 "a quasi-conductor at about «lt» at 1 MHz, and close to low-loss in the gigahertz range.",
     evidence_say="Engine runs of σ/ωε for this soil from 1 kHz to 10 GHz: a straight line of slope −1 crossing all three classes.",
     plot=Sweep("f", [1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9, 1e10], [("σ/ωε", EV("loss_tangent"), "S")], "frequency f (Hz)", "loss tangent σ/ωε", logx=True, logy=True),
     mistake="Labelling a material a conductor or insulator without stating the frequency.",
     vals=_WV), "concept")

px(T, "Ulaby & Ravaioli Sec. 7-5", "basic", "Why RF current flows on the surface",
   "At high frequency the current in a copper wire is concentrated in a thin layer at its surface. Why does the field not penetrate further, and what does this do to the wire's resistance?",
   {"type": "slab", "label": "copper"}, "waves/solve", {"f": 1e8, "sigma": 5.8e7}, [],
   X(asked="The cause of the skin effect and its effect on resistance.",
     idea="Inside a good conductor the field obeys a diffusion-like equation and decays exponentially with depth, with length scale δs.",
     steps=[S("In a good conductor the fields decay as e^(−z/δs) from the surface.", r"\delta_s=\frac{1}{\sqrt{\pi f\mu\sigma}}=«d»\ \mu\text{m}"),
            S("Induced eddy currents oppose changes of the field in the interior, pushing the current outwards."),
            S("The current effectively uses a layer about δs thick, so the AC resistance rises roughly as √f.")],
     answer_text="Inside a good conductor the time-varying field induces eddy currents that oppose it, so the field, and with it the current density, decays exponentially with depth as e^(−z/δs). "
                 "At 100 MHz in copper δs is only «d» µm, so the current flows in a very thin skin. "
                 "The conductor behaves as if only a layer about δs thick carried the current, and its AC resistance rises in proportion to 1/δs, that is as √f. "
                 "This is why RF conductors are often silver-plated: only the surface layer matters.",
     evidence_say="Engine field profile in copper at 100 MHz: |E| (and the current density σE) fall to 1/e at one skin depth.",
     plot=Series(_fz, [("|E| inside the copper", _mag("E"), "E")], "depth z (m)", "|E| (relative)"),
     mistake="Using the DC resistance of a wire at radio frequencies.",
     vals={**_WV, "d": _ds(1e6)}), "concept")

px(T, "Ulaby & Ravaioli Sec. 7-5", "exam", "Wavelength inside a good conductor",
   "In a good conductor the wavelength equals 2π times the skin depth. Why, and what does it say about how far a wave travels in a metal?",
   {"type": "slab", "label": "sea water"}, "waves/solve", {"f": 1e6, "eps_r": 81, "sigma": 4}, [],
   X(asked="Why λ = 2πδs in a good conductor, and its meaning.",
     idea="In a good conductor α = β. The phase constant sets the wavelength and the attenuation constant sets the skin depth, so they are tied together.",
     steps=[S("Good-conductor limit.", r"\alpha\approx\beta\approx\sqrt{\pi f\mu\sigma}"),
            S("So the wavelength and the skin depth are linked.", r"\lambda=\frac{2\pi}{\beta}=2\pi\delta_s"),
            S("After one wavelength the amplitude has fallen by e^(−2π), about 0.2 %: the wave dies within a single wavelength.")],
     answer_text="When σ ≫ ωε the propagation constant is γ ≈ (1 + j)√(πfμσ), so α and β are equal. "
                 "The wavelength is 2π/β and the skin depth is 1/α, hence λ = 2πδs. For sea water at 1 MHz, λ = «lam» m and δs = «d» m. "
                 "Over one wavelength the amplitude drops by a factor e^(2π), more than 500, so a wave in a good conductor hardly completes one oscillation before it is gone. "
                 "It is better thought of as a diffusing field than as a travelling wave.",
     evidence_say="Engine: λ = «lam» m and δs = «d» m, a ratio of «ratio».",
     mistake="Using the free-space or εr-based wavelength inside a conductor.",
     vals={**_WV, "d": _ds(1), "ratio": lambda r, p: r["values"]["wavelength"] / r["values"]["skin_depth"]}), "concept")

px(T, "Ulaby & Ravaioli Sec. 7-5", "exam", "Why a good conductor is dispersive",
   "In a lossless dielectric every frequency travels at c/√εr. In sea water the phase velocity depends strongly on frequency. Why, and what happens to a pulse?",
   {"type": "slab", "label": "sea water"}, "waves/solve", {"f": 1e5, "eps_r": 81, "sigma": 4}, [],
   X(asked="The frequency dependence of u_p in a conductor, and its effect on pulses.",
     idea="In a good conductor β = √(πfμσ) grows only as √f, so u_p = ω/β grows as √f.",
     steps=[S("Phase velocity in a good conductor.", r"u_p=\frac{\omega}{\beta}=\sqrt{\frac{4\pi f}{\mu\sigma}}"),
            S("It rises with √f: higher frequencies travel faster."),
            S("A pulse contains many frequencies, which drift apart and spread the pulse out (dispersion), while they are also attenuated at different rates.")],
     answer_text="In a lossless dielectric β = ω√(με) is proportional to ω, so u_p = ω/β is the same for every frequency. "
                 "In a good conductor β = √(πfμσ) grows only as the square root of frequency, so u_p = √(4πf/μσ) increases with frequency. "
                 "The medium is dispersive: the frequency components of a pulse travel at different speeds and are attenuated by different amounts, so the pulse spreads and distorts. "
                 "For sea water at 100 kHz u_p is only «vp» m/s, far below c.",
     evidence_say="Engine runs of u_p in sea water from 1 kHz to 10 MHz: slope ½ on log–log axes.",
     plot=Sweep("f", [1e3, 1e4, 1e5, 1e6, 1e7], [("u_p", EV("vp"), "S")], "frequency f (Hz)", "phase velocity u_p (m/s)", logx=True, logy=True),
     mistake="Using u_p = c/√εr in a conducting medium.",
     vals=_WV), "concept")

px(T, "Ulaby & Ravaioli Sec. 7-7", "basic", "Power decays twice as fast as the field",
   "In a lossy medium the field amplitude decays as e^(−αz). How does the power density decay, and why is the attenuation in dB the same for both?",
   {"type": "slab", "label": "εr = 4, σ = 0.01 S/m"}, "waves/solve", {"f": 1e9, "eps_r": 4, "sigma": 0.01}, [],
   X(asked="The decay of S compared with E, and the dB consistency.",
     idea="Power density goes as the square of the field, so the exponent doubles.",
     steps=[S("Field and power density.", r"|E|\propto e^{-\alpha z},\qquad S_{av}\propto|E|^2\propto e^{-2\alpha z}"),
            S("In dB: 20 log₁₀ of the field ratio equals 10 log₁₀ of the power ratio.", r"20\log_{10}e^{-\alpha z}=10\log_{10}e^{-2\alpha z}"),
            S("So one value, α_dB = «adb» dB/m here, describes both.")],
     answer_text="Power density is proportional to |E|², so if the field decays as e^(−αz) the power density decays as e^(−2αz): twice the exponent. "
                 "That is why the 'power penetration depth' is half the skin depth. "
                 "In decibels nothing changes: 20 log₁₀ of a field ratio and 10 log₁₀ of the corresponding power ratio give the same number, here «adb» dB/m. "
                 "Mixing the two conventions is a frequent source of factor-of-two errors.",
     evidence_say="Engine profiles: S_av falls twice as fast (in nepers) as |E|.",
     plot=Series(_fz, [("|E| (relative)", lambda r, p: [v / max(_mag("E")(r, p)) for v in _mag("E")(r, p)], "E"),
                       ("S_av (relative)", lambda r, p: [v / max(r["field"]["S_av"]) for v in r["field"]["S_av"]], "S")], "distance z (m)", "relative value"),
     mistake="Using e^(−αz) for power, or halving the dB figure for power.",
     vals=_WV), "concept")

px(T, "Ulaby & Ravaioli Sec. 7-4", "exam", "What the imaginary part of ε means",
   "Lossy media are described by a complex permittivity εc = ε′ − jε″. What is physically 'imaginary' about ε″, and how is it related to σ?",
   {"type": "slab", "label": "εr = 4, σ = 0.01 S/m"}, "waves/solve", {"f": 1e9, "eps_r": 4, "sigma": 0.01}, [],
   X(asked="The meaning of ε″ and its link to conductivity.",
     idea="In Ampère–Maxwell the conduction current σE can be folded into the displacement term as an extra imaginary part of ε.",
     steps=[S("Combine the two current terms.", r"\nabla\times\mathbf H=(\sigma+j\omega\varepsilon')\mathbf E=j\omega\Big(\varepsilon'-j\frac{\sigma}{\omega}\Big)\mathbf E"),
            S("So ε″ = σ/ω collects every loss mechanism, conduction or dielectric friction.", r"\varepsilon''=\frac{\sigma}{\omega},\qquad\frac{\varepsilon''}{\varepsilon'}=«lt»"),
            S("The 'imaginary' part is the component of current in phase with E, which dissipates power.")],
     answer_text="Nothing about the loss is imaginary. Writing εc = ε′ − jε″ is a bookkeeping device in phasor notation: "
                 "the part of the current 90° ahead of E (displacement current, stored energy) goes with ε′, and the part in phase with E (conduction or dielectric friction, dissipated energy) goes with ε″. "
                 "For a conductor ε″ = σ/ω; measured ε″ of materials such as water also includes molecular relaxation losses. "
                 "The ratio ε″/ε′, here «lt», decides how lossy the medium is.",
     evidence_say="Engine: ε″/ε′ = «lt» for εr = 4, σ = 0.01 S/m at 1 GHz, giving α = «a» Np/m.",
     mistake="Treating ε″ as unphysical, or forgetting that it depends on frequency.",
     vals=_WV), "concept")

# ---------------------------------------------------------------- reflection
T = "reflection"
p(T, "Ulaby & Ravaioli Sec. 8-1", "basic", "Air to glass, normal incidence",
  "A wave in air hits glass (εr = 2.25) at normal incidence. Find |Γ|.",
  {"type": "normal", "e2": 2.25}, "rf/normal", {"f": 1e9, "eps2": 2.25}, [("|Γ|", V("Gamma_mag"), "", 1)],
  "Γ = (η₂ − η₁)/(η₂ + η₁) with η = η₀/√εr.", "Glass reflects a fifth of the field amplitude.")
p(T, "Ulaby & Ravaioli Sec. 8-1", "basic", "Transmitted power into glass",
  "For the same air–glass interface, what fraction of the power is transmitted?",
  {"type": "normal", "e2": 2.25}, "rf/normal", {"f": 1e9, "eps2": 2.25}, [("T", V("T"), "", 1)],
  "T = 1 − |Γ|² for lossless media.", "4 % bounces back, 96 % goes through.")
p(T, "Ulaby & Ravaioli Sec. 8-1", "basic", "Air to water",
  "A 1 GHz wave in air hits still water (take εr = 81, lossless). Find the reflected power fraction.",
  {"type": "normal", "e2": 81}, "rf/normal", {"f": 1e9, "eps2": 81}, [("R", V("R"), "", 1)],
  "|Γ| = (9 − 1)/(9 + 1); R = |Γ|².", "Water reflects most of a radio wave.")
p(T, "Ulaby & Ravaioli Sec. 8-1", "exam", "Air to sea water",
  "A 1 MHz wave in air hits sea water (εr = 81, σ = 4 S/m). Find the reflected power fraction.",
  {"type": "normal", "e2": 81}, "rf/normal", {"f": 1e6, "eps2": 81, "s2": 4}, [("R", V("R"), "", 1)],
  "η₂ is complex and small (good conductor), so Γ ≈ −1.", "The sea acts almost like a mirror for low-frequency radio.")
p(T, "Ulaby & Ravaioli Sec. 8-4", "basic", "Brewster angle",
  "Find the Brewster angle from air into a dielectric with εr = 4.",
  {"type": "oblique", "e1": 1, "e2": 4, "theta": 63.4}, "rf/oblique", {"eps1": 1, "eps2": 4, "theta_deg": 30}, [("θB", V("theta_B"), "°", 1)],
  "tan θB = n₂/n₁ = 2.", "At this angle the parallel polarisation is not reflected at all.")
p(T, "Ulaby & Ravaioli Sec. 8-3", "basic", "Critical angle",
  "Light travels in glass (n = 1.5) toward air. Find the critical angle.",
  {"type": "oblique", "e1": 2.25, "e2": 1, "theta": 41.8}, "rf/oblique", {"eps1": 2.25, "eps2": 1, "theta_deg": 30}, [("θc", V("theta_c"), "°", 1)],
  "sin θc = n₂/n₁.", "Beyond this angle no light escapes — the principle of optical fibres.")
p(T, "Ulaby & Ravaioli Sec. 8-3", "exam", "Oblique incidence, perpendicular",
  "A TE (perpendicular) wave in air hits glass (εr = 2.25) at 45°. Find the reflected power fraction.",
  {"type": "oblique", "e1": 1, "e2": 2.25, "theta": 45}, "rf/oblique", {"eps1": 1, "eps2": 2.25, "theta_deg": 45}, [("R⊥", V("R_perp"), "", 1)],
  "Snell gives θt; then Γ⊥ = (η₂ cos θi − η₁ cos θt)/(η₂ cos θi + η₁ cos θt).", "At a slant, more of the TE wave reflects than at normal incidence.")
p(T, "Ulaby & Ravaioli Sec. 8-3", "exam", "Oblique incidence, parallel",
  "For the same 45° air–glass case, find the reflected power fraction for TM (parallel) polarisation.",
  {"type": "oblique", "e1": 1, "e2": 2.25, "theta": 45}, "rf/oblique", {"eps1": 1, "eps2": 2.25, "theta_deg": 45}, [("R∥", V("R_par"), "", 1)],
  "Γ∥ = (η₂ cos θt − η₁ cos θi)/(η₂ cos θt + η₁ cos θi).", "Near the Brewster angle the TM reflection becomes very small.")
p(T, "Ulaby & Ravaioli Sec. 8-1", "basic", "Standing-wave ratio in air",
  "A wave in air is normally incident on a lossless dielectric with εr = 9. Find the standing-wave ratio in the air.",
  {"type": "normal", "e2": 9}, "rf/normal", {"f": 1e9, "eps2": 9}, [("S", V("S"), "", 1)],
  "|Γ| = (3 − 1)/(3 + 1) = 0.5 ⇒ S = (1 + |Γ|)/(1 − |Γ|).", "The field in front of the interface swings between 1.5 and 0.5 of the incident value.")

# ---------------------------------------------------------------- transmission lines
T = "tlines"
p(T, "Ulaby & Ravaioli Sec. 2-6", "basic", "Resistive mismatch",
  "A 50 Ω line is terminated in 100 Ω. Find |Γ| and the VSWR.",
  {"type": "tline", "Z0": "50 Ω", "ZL": "100 Ω"}, "tl/line", {"Z0": 50, "RL": 100, "XL": 0}, [("|Γ|", V("Gamma_mag"), "", 1), ("VSWR", V("S"), "", 1)],
  "Γ = (Z_L − Z₀)/(Z_L + Z₀), S = (1 + |Γ|)/(1 − |Γ|).", "A load twice Z₀ gives VSWR 2.")
p(T, "Ulaby & Ravaioli Sec. 2-6", "exam", "Complex load",
  "A 50 Ω line feeds Z_L = 25 − j30 Ω. Find |Γ| and the VSWR.",
  {"type": "tline", "Z0": "50 Ω", "ZL": "25 − j30 Ω"}, "tl/line", {"Z0": 50, "RL": 25, "XL": -30}, [("|Γ|", V("Gamma_mag"), "", 1), ("VSWR", V("S"), "", 1)],
  "Compute Γ with complex arithmetic; only |Γ| enters S.", "Both the resistance and the reactance mismatch cause reflection.")
p(T, "Ulaby & Ravaioli Sec. 2-8", "basic", "Return loss",
  "A 75 Ω antenna is connected to a 50 Ω line. Find the return loss.",
  {"type": "tline", "Z0": "50 Ω", "ZL": "75 Ω"}, "tl/line", {"Z0": 50, "RL": 75, "XL": 0}, [("RL", V("return_loss_dB"), "dB", 1)],
  "RL = −20 log₁₀|Γ| with Γ = 0.2.", "Higher return loss means less is reflected; 14 dB is acceptable for many systems.")
p(T, "Ulaby & Ravaioli Sec. 2-11", "exam", "Quarter-wave transformer at the voltage minimum",
  "A 200 Ω resistive load terminates a 50 Ω line. A quarter-wave transformer is inserted at the first voltage minimum. What characteristic impedance Z_T is needed?",
  {"type": "tline", "Z0": "50 Ω", "ZL": "200 Ω"}, "tl/line", {"Z0": 50, "RL": 200, "XL": 0}, [("Z_T", lambda r: r["match"]["quarter_wave"]["Z_T"], "Ω", 1)],
  "S = 4, so at d_min the line looks like the real resistance Z₀/S = 12.5 Ω; a λ/4 section of Z_T = √(Z₀ · Z₀/S) transforms it to Z₀. (Placed directly at the load it would be √(Z₀R_L) = 100 Ω.)",
  "A quarter-wave line turns an impedance Z into Z_T²/Z, so choose Z_T as the geometric mean of the two resistances it connects.")
p(T, "Ulaby & Ravaioli Sec. 2-8", "basic", "λ/4 impedance inverter",
  "A λ/4 section of 50 Ω line (1 GHz, air) is terminated in 100 Ω. Find Z_in.",
  {"type": "tline", "Z0": "50 Ω", "ZL": "100 Ω", "l": "λ/4"}, "tl/line", {"Z0": 50, "RL": 100, "XL": 0, "f": 1e9, "length": LAM(1e9) / 4},
  [("Re Z_in", lambda r: r["values"]["Zin"]["re"], "Ω", 1)], "Z_in = Z₀²/Z_L for βl = π/2.", "A quarter wavelength of line 'inverts' the load.")
p(T, "Ulaby & Ravaioli Sec. 2-8", "exam", "Shorted stub",
  "A 50 Ω air line λ/8 long (1 GHz) is short-circuited at the end. Find its input reactance.",
  {"type": "tline", "Z0": "50 Ω", "ZL": "short", "l": "λ/8"}, "tl/line", {"Z0": 50, "RL": 0, "XL": 0, "f": 1e9, "length": LAM(1e9) / 8},
  [("X_in", lambda r: r["values"]["Zin"]["im"], "Ω", 1)], "Short: Z_in = jZ₀ tan βl with βl = π/4.", "A short piece of shorted line behaves like an inductor.")
p(T, "Ulaby & Ravaioli Sec. 2-6", "exam", "Position of the voltage maximum",
  "Z_L = 100 + j50 Ω on a 50 Ω air line at 1 GHz. How far from the load is the first voltage maximum?",
  {"type": "tline", "Z0": "50 Ω", "ZL": "100 + j50 Ω"}, "tl/line", {"Z0": 50, "RL": 100, "XL": 50, "f": 1e9}, [("d_max", V("d_max"), "cm", 100)],
  "d_max = θr λ/(4π) with θr the phase of Γ_L.", "The phase of the reflection decides where incident and reflected waves add up.")
p(T, "Ulaby & Ravaioli Sec. 2-7", "exam", "Power to a mismatched load",
  "A 10 V, 50 Ω generator feeds a 100 Ω load through a lossless 50 Ω line. Find the power delivered to the load.",
  {"type": "tline", "Z0": "50 Ω", "ZL": "100 Ω"}, "tl/line", {"Z0": 50, "RL": 100, "XL": 0, "Vg": 10, "Zg": 50}, [("P_L", V("P_L"), "mW", 1e3)],
  "P_L = |V₀⁺|²(1 − |Γ|²)/(2Z₀); with a matched source the available power is |V_g|²/(8R_g).", "The mismatch sends 1/9 of the available power back.")
p(T, "Ulaby & Ravaioli Sec. 2-11", "exam", "Single-stub matching",
  "Match Z_L = 100 + j50 Ω to a 50 Ω air line at 1 GHz with a shorted shunt stub. Find the first stub position d.",
  {"type": "tline", "Z0": "50 Ω", "ZL": "100 + j50 Ω", "stub": True}, "tl/line", {"Z0": 50, "RL": 100, "XL": 50, "f": 1e9},
  [("d", lambda r: r["match"]["stub"][0]["d"], "cm", 100), ("stub length", lambda r: r["match"]["stub"][0]["l_stub"], "cm", 100)],
  "Find d where Re{Y(d)} = Y₀, then a stub of susceptance −B cancels Im{Y(d)}.", "Walk along the line until the load looks like 50 Ω plus a reactance, then cancel the reactance.")

# ---------------------------------------------------------------- waveguides & antennas
T = "radiation"
p(T, "Ulaby & Ravaioli Sec. 8-10", "basic", "WR-90 cut-off",
  "Find the cut-off frequency of the TE₁₀ mode of a WR-90 guide (a = 22.86 mm, b = 10.16 mm, air).",
  {"type": "waveguide", "a": 22.86, "b": 10.16}, "ra/waveguide", {"a": 22.86e-3, "b": 10.16e-3, "f": 10e9}, [("f_c", V("fc"), "GHz", 1e-9)],
  "f₁₀ = c/(2a).", "Half a wavelength must fit across the broad wall.")
p(T, "Ulaby & Ravaioli Sec. 8-10", "exam", "Guide wavelength",
  "In WR-90 at 10 GHz (TE₁₀), find the guide wavelength.",
  {"type": "waveguide", "a": 22.86, "b": 10.16}, "ra/waveguide", {"a": 22.86e-3, "b": 10.16e-3, "f": 10e9}, [("λg", V("lambda_g"), "cm", 100)],
  "λg = λ/√(1 − (f_c/f)²).", "Inside a guide the wave zig-zags, so its pattern repeats over a longer distance than in free space.")
p(T, "Ulaby & Ravaioli Sec. 8-10", "basic", "Second mode",
  "Find the cut-off of the TE₂₀ mode of WR-90.",
  {"type": "waveguide", "a": 22.86, "b": 10.16}, "ra/waveguide", {"a": 22.86e-3, "b": 10.16e-3, "f": 15e9, "mode": "TE", "m": 2, "n": 0},
  [("f_c", V("fc"), "GHz", 1e-9)], "f₂₀ = c/a.", "Twice the cut-off of TE₁₀: the single-mode band of WR-90 lies between them.")
p(T, "Ulaby & Ravaioli Sec. 8-10", "exam", "Dielectric-filled guide",
  "The same guide (a = 22.86 mm) is filled with PTFE (εr = 2.1). Find the TE₁₀ cut-off.",
  {"type": "waveguide", "a": 22.86, "b": 10.16}, "ra/waveguide", {"a": 22.86e-3, "b": 10.16e-3, "eps_r": 2.1, "f": 10e9}, [("f_c", V("fc"), "GHz", 1e-9)],
  "f_c = c/(2a√εr).", "Filling slows the wave so a lower frequency already fits.")
p(T, "Ulaby & Ravaioli Sec. 9-3", "basic", "Half-wave dipole power",
  "A half-wave dipole is fed with a peak current of 2 A. Find the radiated power.",
  {"type": "dipole", "L": 0.5}, "ra/dipole", {"length_lambda": 0.5, "I0": 2}, [("R_rad", V("R_rad"), "Ω", 1), ("P_rad", V("P_rad"), "W", 1)],
  "P = ½I₀²R_rad with R_rad = 30 Cin(2π) ≈ 73 Ω.", "The antenna behaves like a 73 Ω resistor that turns power into radiation.")
p(T, "Ulaby & Ravaioli Sec. 9-1", "basic", "Short dipole directivity",
  "Find the directivity of a short (Hertzian) dipole.",
  {"type": "dipole", "L": 0.05}, "ra/dipole", {"length_lambda": 0.05}, [("D", V("D"), "", 1)],
  "F = sin²θ ⇒ D = 4π/∫sin²θ dΩ = 3/2.", "Even the simplest antenna radiates 1.5 times more broadside than an isotropic source.")
p(T, "Ulaby & Ravaioli Sec. 10-4", "exam", "Broadside array",
  "Eight isotropic elements spaced λ/2 are fed in phase. Find the directivity.",
  {"type": "array", "N": 8, "d": 0.5}, "ra/array", {"N": 8, "d_lambda": 0.5, "delta_deg": 0}, [("D", V("D"), "", 1)],
  "Integrate |AF|² over the sphere; for long arrays D ≈ 2Nd/λ.", "More elements in a row make a sharper fan-shaped beam.")
p(T, "Ulaby & Ravaioli Sec. 10-4", "exam", "End-fire array",
  "Ten elements spaced λ/4 have a progressive phase of −90°. In which direction does the beam point?",
  {"type": "array", "N": 10, "d": 0.25}, "ra/array", {"N": 10, "d_lambda": 0.25, "delta_deg": -90}, [("θ₀", V("theta0"), "°", 1)],
  "cos θ₀ = −δ/(kd) = 1 ⇒ θ₀ = 0 (along the array axis).", "The delays line up so all elements add along the row.")
p(T, "Ulaby & Ravaioli Sec. 9-3", "exam", "Full-wave dipole",
  "Find the directivity of a dipole one wavelength long.",
  {"type": "dipole", "L": 1}, "ra/dipole", {"length_lambda": 1}, [("D", V("D"), "", 1)],
  "Integrate F(θ) = [(cos(π cos θ) + 1)/sin θ]² numerically.", "A longer dipole concentrates more power broadside.")


# ---------------------------------------------------------------- API
def catalog():
    return {"topics": TOPICS, "problems": [{k: v for k, v in x.items() if k not in ("answers", "route", "params", "x")}
                                           | {"answer_labels": [a[0] for a in x["answers"]], "has_explain": x["x"] is not None} for x in P]}


def solve(pid):
    x = next((q for q in P if q["id"] == pid), None)
    if x is None:
        raise ValueError(f"unknown problem {pid!r}")
    r = routes.call(x["route"], x["params"])
    ans = []
    for label, pick, unit, scale in x["answers"]:
        v = pick(r)
        v = v.real if isinstance(v, complex) else float(v)
        ans.append({"label": label, "value": v * scale, "unit": unit})
    ex = render(x["x"], lambda q: routes.call(x["route"], q), x["params"], r) if x["x"] else None
    return {"id": pid, "answers": ans, "steps": r.get("steps", []), "checks": r.get("checks", []), "all_passed": bool(r.get("all_passed", True)),
            "route": x["route"], "params": x["params"], "explain": ex}
