"""Worked problems: original exam-level problems with engine-verified solutions.

Problems are written in our own words; `ref` names the textbook section that covers the
concept (Ulaby & Ravaioli, Fundamentals of Applied Electromagnetics; Cheng, Field and Wave
Electromagnetics). Each problem runs one engine route — the solution steps and independent
checks shown on the page are the engine's — and lists the requested answers.
"""
import math

from .constants import C0
from . import routes
import numpy as np

from .constants import EPS0
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
p(T, "Ulaby & Ravaioli Sec. 9-1", "basic", "Point source: doubling the distance",
  "A small Wi-Fi antenna radiates at 2.4 GHz in free space. By how many decibels does the field level change when you move from 10 m to 20 m away (far field, no loss)?",
  {"type": "dims", "dim": "3D"}, "dim/compare", {"f": 2.4e9, "r_max_lambda": 10}, [("Δ level", _sens("double the distance", "3D"), "dB", 1)],
  "A point source produces a spherical wave; power spreads over 4πR², so |E| ∝ 1/R and the level changes by 20 log₁₀(1/2).",
  "Twice as far means the same power is spread over a sphere with four times the area: the field halves, which is −6 dB.")
p(T, "Cheng Sec. 10-1 (line sources)", "basic", "Line source: doubling the distance",
  "A very long straight current filament radiates a cylindrical wave in lossless air. In the far zone, how much does the field level change when the distance is doubled?",
  {"type": "dims", "dim": "2D"}, "dim/compare", {"f": 1e9, "r_max_lambda": 20}, [("Δ level", _sens("double the distance", "2D"), "dB", 1)],
  "A line source spreads power over a cylinder of area 2πρℓ, so |E| ∝ 1/√ρ (Hankel-function asymptote) and Δ = 10 log₁₀(1/2).",
  "Power spreads over a circle instead of a sphere, so it thins out more slowly: about −3 dB per doubling.")
p(T, "Ulaby & Ravaioli Sec. 2-2", "basic", "Lossless line: doubling the distance",
  "A signal travels along a lossless coaxial cable. How does its amplitude at 200 m compare with that at 100 m?",
  {"type": "dims", "dim": "1D"}, "dim/compare", {"f": 1e9, "r_max_lambda": 10}, [("Δ level", _sens("double the distance", "1D"), "dB", 1)],
  "A TEM wave on a lossless line is one-dimensional: e^{−jβz} has constant magnitude.",
  "Nothing spreads out inside a cable, so without loss the signal is just as strong further along.")
p(T, "Ulaby & Ravaioli Sec. 1-4", "basic", "Free-space wavelength",
  "Find the wavelength of a 900 MHz GSM signal in free space.",
  {"type": "dims", "dim": "1D"}, "dim/compare", {"f": 9e8}, [("λ", V("wavelength"), "m", 1)],
  "λ = c/f with c = 299 792 458 m/s.", "Wavelength = speed ÷ frequency.")
p(T, "Ulaby & Ravaioli Sec. 7-2", "basic", "Wavelength in a dielectric",
  "What is the wavelength of a 1 GHz wave inside a lossless dielectric with εr = 4?",
  {"type": "dims", "dim": "1D"}, "dim/compare", {"f": 1e9, "eps_r": 4}, [("λ", V("wavelength"), "m", 1)],
  "In a lossless medium u = c/√(εrμr), so λ = c/(f√εr).", "The wave slows down by √εr = 2, so its wavelength halves.")
p(T, "Ulaby & Ravaioli Sec. 7-4", "exam", "Attenuation in wet soil",
  "A 100 MHz wave propagates in wet soil with εr = 20 and σ = 0.05 S/m. Find the attenuation constant α.",
  {"type": "dims", "dim": "3D"}, "dim/compare", {"f": 1e8, "eps_r": 20, "sigma": 0.05}, [("α", V("alpha"), "Np/m", 1)],
  "γ = jω√(μεc) with εc = ε − jσ/ω; here σ/ωε ≈ 0.45 so neither limit applies and the exact form is used.",
  "Soil absorbs energy; α tells how quickly the amplitude dies out per metre.")
p(T, "Ulaby & Ravaioli Sec. 9-1", "exam", "Spreading over ten wavelengths",
  "Relative to its value at λ/2 from a point source, what is the field level at 10λ in free space?",
  {"type": "dims", "dim": "3D"}, "dim/compare", {"f": 1e9, "r_max_lambda": 10}, [("level", V("level_3D"), "dB", 1)],
  "|E| ∝ 1/R ⇒ level = 20 log₁₀((λ/2)/(10λ)) = 20 log₁₀(1/20).", "Twenty times further, twenty times weaker field: −26 dB.")
p(T, "Ulaby & Ravaioli Sec. 7-2", "basic", "Doubling the frequency",
  "A 1 GHz wave travels in free space. What becomes its wavelength if the frequency is doubled?",
  {"type": "dims", "dim": "1D"}, "dim/compare", {"f": 1e9}, [("new λ", lambda r: next(s for s in r["sensitivity"] if s["change"] == "double the frequency")["lambda"], "m", 1)],
  "λ = u/f: doubling f halves λ when u is fixed.", "Faster oscillation, same speed ⇒ shorter waves.")

# ---------------------------------------------------------------- coordinates
T = "coordinates"
p(T, "Ulaby & Ravaioli Sec. 3-2.3", "basic", "Spherical volume element",
  "At R = 2 m, θ = 30°, a small spherical volume has dR = 1 cm, dθ = dφ = 1°. Find dv.",
  {"type": "coord", "system": "spherical"}, "coords/element", {"system": "spherical", "u1": 2, "u2": 30, "u3": 0, "d1": 0.01, "d2": 1, "d3": 1},
  [("dv", V("dv"), "cm³", 1e6)], "dv = R² sin θ dR dθ dφ with angles in radians.", "Volume = (radial step) × (arc R dθ) × (arc R sin θ dφ).")
p(T, "Ulaby & Ravaioli Sec. 3-2.2", "basic", "Patch on a cylinder",
  "On a cylinder of radius 0.5 m, a patch spans dφ = 5° and dz = 2 cm. Find its area.",
  {"type": "coord", "system": "cylindrical"}, "coords/element", {"system": "cylindrical", "u1": 0.5, "u2": 0, "u3": 0, "d1": 0.01, "d2": 5, "d3": 0.02},
  [("ds_r", lambda r: r["values"]["ds"][0], "cm²", 1e4)], "ds_r = r dφ dz.", "Unroll the patch: width r·dφ, height dz.")
p(T, "Ulaby & Ravaioli Sec. 3-2.3", "basic", "Arc length in θ",
  "On a sphere of radius 3 m, how long is the arc swept when θ changes by 2°?",
  {"type": "coord", "system": "spherical"}, "coords/element", {"system": "spherical", "u1": 3, "u2": 60, "u3": 0, "d1": 0.01, "d2": 2, "d3": 1},
  [("R dθ", lambda r: r["values"]["dl"][1], "cm", 100)], "dl_θ = R dθ (scale factor h_θ = R).", "Arc = radius × angle in radians.")
p(T, "Ulaby & Ravaioli Sec. 3-3", "basic", "Cartesian → spherical (R)",
  "Express the point (3, 4, 5) m in spherical coordinates. Find R.",
  {"type": "coord", "system": "spherical", "point": [3, 4, 5]}, "coords/convert", {"src": "cartesian", "dst": "spherical", "u1": 3, "u2": 4, "u3": 5},
  [("R", lambda r: r["values"]["point"][0], "m", 1)], "R = √(x² + y² + z²).", "Straight-line distance from the origin.")
p(T, "Ulaby & Ravaioli Sec. 3-3", "basic", "Cartesian → spherical (θ)",
  "For the same point (3, 4, 5) m, find the polar angle θ.",
  {"type": "coord", "system": "spherical", "point": [3, 4, 5]}, "coords/convert", {"src": "cartesian", "dst": "spherical", "u1": 3, "u2": 4, "u3": 5},
  [("θ", lambda r: r["values"]["point"][1], "°", 1)], "θ = cos⁻¹(z/R).", "Angle down from the z-axis.")
p(T, "Ulaby & Ravaioli Sec. 3-3", "basic", "Cartesian → cylindrical",
  "Convert (1, 1, 1) m to cylindrical coordinates. Find r and φ.",
  {"type": "coord", "system": "cylindrical", "point": [1, 1, 1]}, "coords/convert", {"src": "cartesian", "dst": "cylindrical", "u1": 1, "u2": 1, "u3": 1},
  [("r", lambda r: r["values"]["point"][0], "m", 1), ("φ", lambda r: r["values"]["point"][1], "°", 1)], "r = √(x² + y²), φ = atan2(y, x).", "r is the distance from the z-axis, φ the compass angle from +x.")
p(T, "Ulaby & Ravaioli Sec. 3-3.1", "exam", "Vector components in cylindrical",
  "At the point (1, 1, 0) m, the vector A = x̂ + 2ŷ + 3ẑ. Find its radial component A_r.",
  {"type": "coord", "system": "cylindrical", "point": [1, 1, 0]}, "coords/convert", {"src": "cartesian", "dst": "cylindrical", "u1": 1, "u2": 1, "u3": 0, "A1": 1, "A2": 2, "A3": 3},
  [("A_r", lambda r: r["values"]["vector"][0], "", 1)], "A_r = A·r̂ = A_x cos φ + A_y sin φ with φ = 45°.", "Project the vector on the direction pointing away from the z-axis at that point.")
p(T, "Ulaby & Ravaioli Sec. 3-3", "basic", "Cylindrical → Cartesian",
  "A point has cylindrical coordinates (2 m, 60°, 1 m). Find its x coordinate.",
  {"type": "coord", "system": "cylindrical", "point": [1, 1.732, 1]}, "coords/convert", {"src": "cylindrical", "dst": "cartesian", "u1": 2, "u2": 60, "u3": 1},
  [("x", lambda r: r["values"]["point"][0], "m", 1)], "x = r cos φ.", "Go out 2 m at 60°: the shadow on the x-axis is 1 m.")

# ---------------------------------------------------------------- electrostatics
T = "electrostatics"
nC = 1e-9
p(T, "Ulaby & Ravaioli Sec. 4-3", "basic", "Field of a point charge",
  "A 5 nC point charge is in free space. Find |E| at 0.3 m.",
  {"type": "charges", "charges": [[5, 0, 0]], "probe": [0.3, 0]}, "es/charges", {"charges": [{"q": 5 * nC, "x": 0, "y": 0}], "probe": [0.3, 0]},
  [("|E|", V("E_mag"), "V/m", 1)], "E = Q/(4πε₀R²).", "The field gets 4 times weaker when you double the distance.")
p(T, "Ulaby & Ravaioli Sec. 4-3", "exam", "Field of a charge pair",
  "Charges +2 nC at (−0.1, 0) m and −2 nC at (0.1, 0) m. Find |E| at P(0, 0.1) m.",
  {"type": "charges", "charges": [[2, -0.1, 0], [-2, 0.1, 0]], "probe": [0, 0.1]}, "es/charges",
  {"charges": [{"q": 2 * nC, "x": -0.1, "y": 0}, {"q": -2 * nC, "x": 0.1, "y": 0}], "probe": [0, 0.1]}, [("|E|", V("E_mag"), "V/m", 1)],
  "Superpose the two Coulomb fields as vectors; the y-components cancel, the x-components add.", "Both charges push/pull the test charge toward +x, so their effects add.")
p(T, "Ulaby & Ravaioli Sec. 4-5", "basic", "Potential on the bisector",
  "For the same pair (+2 nC and −2 nC, 0.2 m apart), find the potential at P(0, 0.1) m.",
  {"type": "charges", "charges": [[2, -0.1, 0], [-2, 0.1, 0]], "probe": [0, 0.1]}, "es/charges",
  {"charges": [{"q": 2 * nC, "x": -0.1, "y": 0}, {"q": -2 * nC, "x": 0.1, "y": 0}], "probe": [0, 0.1]}, [("V", V("V"), "V", 1)],
  "V = Σ Qᵢ/(4πε₀Rᵢ); the distances are equal and the charges opposite.", "Equal and opposite contributions cancel: zero volts — yet the field is not zero.")
p(T, "Ulaby & Ravaioli Sec. 4-4", "exam", "Inside a charged sphere",
  "A sphere of radius 5 cm carries a uniform charge density 2 µC/m³. Find |E| at 2 cm from the centre.",
  {"type": "sphere", "a": 0.05, "r": 0.02}, "es/gauss", {"kind": "sphere", "rho": 2e-6, "a": 0.05, "r": 0.02},
  [("|E|", V("E"), "V/m", 1)], "Gauss: D·4πR² = ρᵥ(4/3)πR³ ⇒ E = ρᵥR/(3ε₀) inside.", "Inside, only the charge closer to the centre than you counts.")
p(T, "Ulaby & Ravaioli Sec. 4-4", "basic", "Infinite line charge",
  "An infinite line carries 10 nC/m in air. Find |E| at 0.5 m.",
  {"type": "line", "r": 0.5}, "es/gauss", {"kind": "line", "rho": 1e-8, "a": 0.01, "b": 1, "r": 0.5},
  [("|E|", V("E"), "V/m", 1)], "Gauss with a cylinder: E·2πrℓ = ρₗℓ/ε₀ ⇒ E = ρₗ/(2πε₀r).", "A line spreads its field over a cylinder, so E ∝ 1/r.")
p(T, "Ulaby & Ravaioli Sec. 4-10", "basic", "Coaxial capacitance",
  "A coaxial cable has a = 1 mm, b = 4 mm and polyethylene (εr = 2.25). Find C per metre.",
  {"type": "coax", "a": 1, "b": 4}, "es/capacitor", {"kind": "coax", "a": 1e-3, "b": 4e-3, "eps_r": 2.25, "length": 1},
  [("C′", V("C"), "pF/m", 1e12)], "C′ = 2πε/ln(b/a).", "More insulating material constant ε, more capacitance; wider gap, less.")
p(T, "Ulaby & Ravaioli Sec. 4-10", "basic", "Parallel-plate capacitor and energy",
  "Plates of 10 cm² are 0.5 mm apart with εr = 4 and 12 V applied. Find C and the stored energy.",
  {"type": "plates", "d": 0.5}, "es/capacitor", {"kind": "parallel", "A": 1e-3, "d": 5e-4, "eps_r": 4, "V0": 12},
  [("C", V("C"), "pF", 1e12), ("W", V("W"), "nJ", 1e9)], "C = εA/d, W = ½CV².", "Bigger plates or thinner gap store more charge for the same voltage.")
p(T, "Ulaby & Ravaioli Sec. 4-10", "exam", "Coax breakdown voltage",
  "An air-filled coax has a = 1 mm and b = 3 mm. Air breaks down at 3 MV/m. What is the highest safe voltage?",
  {"type": "coax", "a": 1, "b": 3}, "es/capacitor", {"kind": "coax", "a": 1e-3, "b": 3e-3, "eps_r": 1, "E_bd": 3e6, "V0": 1},
  [("V_bd", V("V_bd"), "kV", 1e-3)], "E_max = V/(a ln(b/a)) at r = a; set E_max = E_bd.", "The field is strongest at the thin inner conductor — that is where sparks start.")
p(T, "Ulaby & Ravaioli Sec. 4-10", "basic", "Spherical capacitor",
  "Concentric spheres of radii 5 cm and 10 cm, air between. Find C.",
  {"type": "coax", "a": 5, "b": 10, "label": "spherical"}, "es/capacitor", {"kind": "spherical", "a": 0.05, "b": 0.1, "eps_r": 1},
  [("C", V("C"), "pF", 1e12)], "C = 4πε ab/(b − a).", "Two nested metal balls form a capacitor; closer surfaces give larger C.")

# ---------------------------------------------------------------- images
T = "images"
p(T, "Ulaby & Ravaioli Sec. 4-11", "basic", "Force from the image",
  "A 1 nC charge is 0.4 m above a grounded conducting plane in air. Find the force on it.",
  {"type": "plane", "d": 0.4}, "img/plane", {"Q": 1e-9, "d": 0.4}, [("F", V("F"), "nN", 1e9)],
  "Replace the plane by −Q at depth d: F = Q²/(4πε₀(2d)²).", "The plane pulls the charge like an opposite charge twice as far away.")
p(T, "Ulaby & Ravaioli Sec. 4-11", "exam", "Induced charge under the charge",
  "For the same configuration, find the induced surface charge density directly below the charge.",
  {"type": "plane", "d": 0.4}, "img/plane", {"Q": 1e-9, "d": 0.4}, [("ρs(0)", V("rho_s0"), "nC/m²", 1e9)],
  "ρs = ε₀E_z(0⁺) = −Qd/(2π(x² + d²)^{3/2}); at x = 0 this is −Q/(2πd²).", "The metal gathers opposite charge right below Q.")
p(T, "Ulaby & Ravaioli Sec. 4-11", "basic", "Closer charge, larger force",
  "A −3 nC charge sits 10 cm above a grounded plane. Find the force.",
  {"type": "plane", "d": 0.1}, "img/plane", {"Q": -3e-9, "d": 0.1}, [("F", V("F"), "µN", 1e6)],
  "F = Q²/(16πε₀d²): the sign of Q does not matter, the force is always attractive.", "Any charge, positive or negative, is attracted to a grounded metal.")
p(T, "Cheng Sec. 4-4", "exam", "Energy of charge and plane",
  "A 2 nC charge is 0.2 m above a grounded plane. Find the electrostatic energy of the system.",
  {"type": "plane", "d": 0.2}, "img/plane", {"Q": 2e-9, "d": 0.2}, [("W", V("W"), "nJ", 1e9)],
  "W = −Q²/(16πε₀d): half the energy of the free Q, −Q pair, because only z > 0 holds field.", "Bringing a charge near metal releases energy, so W is negative.")
p(T, "Ulaby & Ravaioli Sec. 4-11", "exam", "Image in a dielectric",
  "A 1 nC charge is 0.5 m above a grounded plane in oil with εr = 2.5. Find the force.",
  {"type": "plane", "d": 0.5}, "img/plane", {"Q": 1e-9, "d": 0.5, "eps_r": 2.5}, [("F", V("F"), "nN", 1e9)],
  "Same image construction with ε = 2.5ε₀: F = Q²/(4πε(2d)²).", "The oil weakens all electric forces by 2.5.")
p(T, "Cheng Sec. 4-4", "exam", "Charge in a 90° corner",
  "A 1 nC charge is at (0.3, 0.5) m between two grounded planes x = 0 and y = 0. Find the magnitude of the force.",
  {"type": "corner", "x0": 0.3, "y0": 0.5}, "img/corner", {"Q": 1e-9, "x0": 0.3, "y0": 0.5}, [("|F|", lambda r: math.hypot(*r["values"]["F"]), "nN", 1e9)],
  "Three images: −Q at (−x₀, y₀), −Q at (x₀, −y₀), +Q at (−x₀, −y₀); sum their Coulomb forces.", "Each wall acts as a mirror, and the two mirrors also make a mirror of a mirror.")
p(T, "Ulaby & Ravaioli Sec. 4-11", "exam", "Field near the plane",
  "A 2 nC charge is 0.3 m above a grounded plane. Find |E| at the point 6 cm to the side and 18 cm above the plane.",
  {"type": "plane", "d": 0.3, "probe": [0.06, 0.18]}, "es/charges", {"charges": [{"q": 2e-9, "x": 0, "y": 0.3}], "ground": True, "probe": [0.06, 0.18]},
  [("|E|", V("E_mag"), "V/m", 1)], "Superpose the fields of Q at (0, 0.3) and −Q at (0, −0.3).", "Add the real charge and its mirror image as two ordinary charges.")
p(T, "Cheng Sec. 4-4", "basic", "Corner: equal distances",
  "A 2 nC charge is at (0.2, 0.2) m inside a grounded 90° corner. Find the magnitude of the force.",
  {"type": "corner", "x0": 0.2, "y0": 0.2}, "img/corner", {"Q": 2e-9, "x0": 0.2, "y0": 0.2}, [("|F|", lambda r: math.hypot(*r["values"]["F"]), "nN", 1e9)],
  "Images at (−0.2, 0.2), (0.2, −0.2), (−0.2, −0.2); by symmetry F points toward the corner.", "Pulled equally by both walls, the charge is drawn diagonally into the corner.")

# ---------------------------------------------------------------- magnetostatics & Biot–Savart
T = "magnetostatics"
p(T, "Ulaby & Ravaioli Sec. 5-2", "basic", "Long straight wire",
  "A long wire carries 15 A. Find B at 5 cm.",
  {"type": "wires", "wires": [[15, 0, 0]], "probe": [0.05, 0]}, "ms/wires", {"currents": [{"I": 15, "x": 0, "y": 0}], "probe": [0.05, 0]},
  [("B", V("B_mag"), "µT", 1e6)], "B = μ₀I/(2πr).", "The field circles the wire and weakens as 1/r.")
p(T, "Ulaby & Ravaioli Sec. 5-2.3", "basic", "Force between wires",
  "Parallel wires 10 cm apart carry 20 A and 30 A in the same direction. Find the force per metre.",
  {"type": "wires", "wires": [[20, -0.05, 0], [30, 0.05, 0]]}, "ms/wires", {"currents": [{"I": 20, "x": -0.05, "y": 0}, {"I": 30, "x": 0.05, "y": 0}], "probe": [0, 0.1]},
  [("F′", lambda r: math.hypot(*r["forces"][0]), "mN/m", 1e3)], "F′ = μ₀I₁I₂/(2πd); same direction ⇒ attraction.", "Currents in the same direction pull together.")
p(T, "Ulaby & Ravaioli Sec. 5-2.1", "exam", "Finite wire (Biot–Savart)",
  "A straight wire 40 cm long carries 3 A. Find H at a point 10 cm from its midpoint, on the perpendicular bisector.",
  {"type": "segment", "L": 0.4, "r": 0.1}, "bs/segment", {"I": 3, "z1": -0.2, "z2": 0.2, "r": 0.1, "N": 400},
  [("H", V("H_closed"), "A/m", 1)], "H = I(cos θ₁ − cos θ₂)/(4πr) with cos θ₁ = −cos θ₂ = 0.2/√(0.2² + 0.1²).", "A finite wire gives less than the infinite-wire value I/2πr because the far parts are missing.")
p(T, "Ulaby & Ravaioli Sec. 5-2", "exam", "Square loop",
  "A square loop of side 20 cm carries 1 A. Find H at its centre.",
  {"type": "square", "a": 0.2}, "bs/square", {"I": 1, "a": 0.2, "N": 200}, [("H", V("H_closed"), "A/m", 1)],
  "Four finite wires seen from r = a/2 with θ = 45°, 135°: H = 2√2 I/(πa).", "Add four equal pieces, one per side.")
p(T, "Ulaby & Ravaioli Sec. 5-2.2", "basic", "Centre of a loop",
  "A circular loop of radius 5 cm carries 2 A. Find H at its centre.",
  {"type": "loop", "a": 0.05, "z": 0}, "bs/loop", {"I": 2, "a": 0.05, "z": 0}, [("H", V("H_closed"), "A/m", 1)],
  "On the axis H = Ia²/(2(a² + z²)^{3/2}); at z = 0, H = I/(2a).", "Every piece of the loop is the same distance away and all add in the same direction.")
p(T, "Ulaby & Ravaioli Sec. 5-2.2", "exam", "On the axis of a loop",
  "A loop of radius 10 cm carries 1 A. Find H on its axis 10 cm from the centre.",
  {"type": "loop", "a": 0.1, "z": 0.1}, "bs/loop", {"I": 1, "a": 0.1, "z": 0.1}, [("H", V("H_closed"), "A/m", 1)],
  "Only the axial components survive: H = Ia²/(2(a² + z²)^{3/2}).", "Off the centre the side pieces partly cancel; what remains points along the axis.")
p(T, "Ulaby & Ravaioli Sec. 5-4", "basic", "Toroid",
  "A toroid of 500 turns, inner radius 4 cm, outer radius 6 cm, carries 0.5 A. Find B at r = 5 cm.",
  {"type": "toroid", "a": 4, "b": 6}, "ms/ampere", {"kind": "toroid", "I": 0.5, "N": 500, "a": 0.04, "b": 0.06, "r": 0.05},
  [("B", V("B"), "mT", 1e3)], "Ampère around a circle of radius r inside the core: H·2πr = NI.", "All the field stays inside the doughnut and goes round with the windings.")
p(T, "Ulaby & Ravaioli Sec. 5-7", "basic", "Solenoid inductance",
  "A 10 cm long air solenoid of radius 1 cm has 200 turns. Find its inductance.",
  {"type": "solenoid", "a": 1, "l": 10}, "ms/inductance", {"kind": "solenoid", "N": 200, "a": 0.01, "length": 0.1},
  [("L", V("L"), "µH", 1e6)], "L = μN²A/ℓ for a long solenoid.", "Inductance grows with the square of the number of turns.")
p(T, "Ulaby & Ravaioli Sec. 5-7", "basic", "Coax inductance",
  "Find the external inductance per metre of a coax with a = 0.5 mm and b = 2 mm.",
  {"type": "coax", "a": 0.5, "b": 2}, "ms/inductance", {"kind": "coax", "a": 5e-4, "b": 2e-3, "length": 1},
  [("L′", V("L"), "nH/m", 1e9)], "L′ = (μ/2π) ln(b/a).", "Same ln(b/a) as the capacitance — and L′C′ = με.")

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
   {"type": "generator", "N": 10}, "mx/faraday", {"mode": "transformer", "N": 10, "B0": 0.05, "w": 0.1, "l": 0.1, "f": 1000, "alpha_deg": 30},
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
     whatif=[W("…the ratio at 1 GHz were asked?", lambda p: {**p, "f": 1e9}, "|J_c|/|J_d| = «ratio»: displacement current dominates and the soil behaves as a lossy dielectric.",
               r"\frac{\sigma}{\omega\varepsilon}=«ratio»"),
             W("…the soil dried out to σ = 0.001 S/m?", lambda p: {**p, "sigma": 1e-3}, "f_c is proportional to σ and falls to «fc» MHz.", r"f_c\propto\sigma")],
     mistake="Calling a material a conductor or a dielectric without saying at which frequency.",
     vals={"fc": lambda r, p: r["values"]["fc"] / 1e6, "ratio": EV("ratio")}), "numeric")

px(T, U + "6-10", "basic", "Charge relaxation: copper vs distilled water",
   "Excess free charge is placed inside a block of copper (σ = 5.8 × 10⁷ S/m, εr = 1). "
   "How long does it take for the charge density inside to fall to 1/e of its initial value? "
   "Compare with distilled water (εr = 81, σ = 2 × 10⁻⁴ S/m).",
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
     whatif=[W("…distilled water were asked?", lambda p: {**p, "eps_r": 81, "sigma": 2e-4}, "τ_r = «tau» s: many orders of magnitude slower than copper, yet still very short.",
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
     plot=Sweep("eps2", [1, 2, 4, 8, 16], [("tangential E₂t", EV("F2", 0)), ("normal E₂n", EV("F2", 1))], "relative permittivity of medium 2, εr₂", "field in medium 2 (V/m)", logx=True),
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
     evidence_say="Engine runs (E₁ = 100 V/m at 40°, εr from 1 to 4): D₁n stays fixed while D₂n falls one-for-one with ρs, so the gap between the curves is always ρs.",
     plot=Sweep("source", [0, 2e-10, 4e-10, 6e-10], [("D₁n above the sheet", EV("flux", 0)), ("D₂n below the sheet", EV("flux", 1))],
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
     answer_text="Inside the high-μ material H and B bend toward the surface and run almost parallel to it, whatever the angle outside, unless it is exactly normal. "
                 "Field lines therefore prefer to travel inside the material, along its walls. "
                 "A closed box of such material collects the flux and guides it around the enclosed space, so the field inside the box is much weaker. "
                 "This is magnetic shielding with mu-metal or soft iron.",
     evidence_say="Engine runs with H₁ at 30° from the normal: θ₂ climbs toward 90° as μr₂ grows (at μr₂ = 1000 it is «th»°).",
     plot=Sweep("mu2", [1, 3, 10, 30, 100, 300, 1000], EV("theta2_deg"), "relative permeability of medium 2, μr₂", "angle of H₂ from the normal, θ₂ (°)", logx=True),
     mistake="Thinking H goes straight into the iron. That happens only at exactly normal incidence.",
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
                 "the long sides of the coil cut across the field lines at full speed. "
                 "Faraday's law depends on dΦ/dt, and for Φ ∝ cos Ωt the slope is steepest where Φ crosses zero. "
                 "Conversely, when the coil faces the field squarely the flux is largest but momentarily not changing, and the EMF is zero.",
     evidence_say="Engine curves over two revolutions: every zero of the flux lines up with a peak of the EMF.",
     plot=Series(lambda r, p: r["t"], [("flux NΦ", _norm("Phi")), ("EMF", _norm("emf"))], "time t (s)", "normalised (peak = 1)"),
     mistake="Linking the EMF to the flux itself rather than to its rate of change.",
     vals={"V": EV("V_peak")}), "concept")

px(T, U + "6-1", "basic", "Which way does the induced current flow?",
   "A fixed loop sits in a uniform field B(t) = B₀ cos ωt directed along the loop's normal. "
   "While the flux through the loop is increasing, does the induced current create a field that adds to B or opposes it? "
   "What would go wrong if it were the other way round?",
   {"type": "generator", "N": 1}, "mx/faraday", {"mode": "transformer", "N": 1, "B0": 0.05, "w": 0.1, "l": 0.1, "f": 1000}, [],
   X(asked="The direction of the induced field relative to B while the flux grows, and why it must be so.",
     idea="Faraday's law carries a minus sign, V_emf = −N dΦ/dt. That sign is Lenz's law.",
     steps=[S("A positive EMF drives current in the sense that, by the right-hand rule, makes flux along the chosen normal."),
            S("While Φ rises dΦ/dt > 0, so V_emf < 0: the current flows the other way and its own flux opposes the change."),
            S("When Φ falls the sign reverses and the induced flux props it up.")],
     answer_text="It opposes the change. While the flux is increasing, the induced current circulates so that its own field points against B inside the loop; "
                 "while the flux is decreasing, the induced field points along B. This is Lenz's law, the minus sign in Faraday's law. "
                 "If it were the other way, a small increase in flux would induce a current that increases the flux further, a runaway that would create energy from nothing.",
     evidence_say="Engine curves: wherever the flux curve rises, the EMF curve is negative, and wherever it falls, the EMF is positive.",
     plot=Series(lambda r, p: r["t"], [("flux NΦ", _norm("Phi")), ("EMF", _norm("emf"))], "time t (s)", "normalised (peak = 1)"),
     mistake="Saying the induced field always opposes B. It opposes the change in flux, which may be along B.",
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
   "Sea water has σ ≈ 4 S/m and εr ≈ 81. In the constant-εr model it is a good conductor at 1 kHz but a lossy dielectric at 100 GHz. "
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
                 "The ratio passes through 1 near 1 GHz and is well below 1 at 100 GHz, where the model calls the water a lossy dielectric. "
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
p(T, "Ulaby & Ravaioli Sec. 7-5", "basic", "Skin depth of copper",
  "Find the skin depth of copper (σ = 5.8 × 10⁷ S/m) at 10 MHz.",
  {"type": "slab", "label": "copper"}, "waves/solve", {"f": 1e7, "sigma": 5.8e7}, [("δs", V("skin_depth"), "µm", 1e6)],
  "Good conductor: δs = 1/√(πfμσ).", "High-frequency current flows only in a skin about 20 µm thick.")
p(T, "Ulaby & Ravaioli Sec. 7-5", "basic", "Skin depth of aluminium at 60 Hz",
  "Find the skin depth of aluminium (σ = 3.5 × 10⁷ S/m) at 60 Hz.",
  {"type": "slab", "label": "aluminium"}, "waves/solve", {"f": 60, "sigma": 3.5e7}, [("δs", V("skin_depth"), "mm", 1e3)],
  "δs = 1/√(πfμσ).", "At power-line frequency the skin is about a centimetre — why thick cables are stranded.")
p(T, "Ulaby & Ravaioli Sec. 7-4", "exam", "Attenuation in sea water",
  "A 1 MHz wave travels in sea water (εr = 81, σ = 4 S/m). Find the attenuation in dB/m.",
  {"type": "slab", "label": "sea water"}, "waves/solve", {"f": 1e6, "eps_r": 81, "sigma": 4}, [("α", V("alpha_dB"), "dB/m", 1)],
  "σ/ωε ≈ 890 ⇒ good conductor, α ≈ √(πfμσ); 1 Np = 8.686 dB.", "Radio barely penetrates the sea: tens of dB lost per metre.")
p(T, "Ulaby & Ravaioli Sec. 7-3", "basic", "Wavelength in a dielectric",
  "Find the wavelength of a 3 GHz wave in a lossless material with εr = 4.",
  {"type": "slab", "label": "εr = 4"}, "waves/solve", {"f": 3e9, "eps_r": 4}, [("λ", V("wavelength"), "cm", 100)],
  "λ = c/(f√εr).", "Slower wave, shorter wavelength.")
p(T, "Ulaby & Ravaioli Sec. 7-2", "basic", "Impedance of free space",
  "Find the intrinsic impedance of free space.",
  {"type": "slab", "label": "free space"}, "waves/solve", {"f": 1e9}, [("η₀", V("eta_mag"), "Ω", 1)],
  "η₀ = √(μ₀/ε₀).", "The ratio of E to H in a plane wave in vacuum: about 377 Ω.")
p(T, "Ulaby & Ravaioli Sec. 7-4", "exam", "Low-loss dielectric",
  "A dielectric has εr = 4 and σ = 0.01 S/m. At 1 GHz find the loss tangent and α.",
  {"type": "slab", "label": "εr = 4, σ = 0.01"}, "waves/solve", {"f": 1e9, "eps_r": 4, "sigma": 0.01},
  [("ε″/ε′", V("loss_tangent"), "", 1), ("α", V("alpha"), "Np/m", 1)], "ε″/ε′ = σ/ωε ≈ 0.045, a quasi-conductor; the exact α formula applies.", "Small but not negligible loss: the wave fades slowly.")
p(T, "Ulaby & Ravaioli Sec. 7-3", "basic", "Phase velocity",
  "Find the phase velocity in a lossless medium with εr = 9.",
  {"type": "slab", "label": "εr = 9"}, "waves/solve", {"f": 1e9, "eps_r": 9}, [("u_p", V("vp"), "m/s", 1)],
  "u_p = c/√εr.", "Three times slower than light in vacuum.")
p(T, "Ulaby & Ravaioli Sec. 7-7", "basic", "Power density",
  "A plane wave in air has E₀ = 100 V/m. Find the time-average power density.",
  {"type": "slab", "label": "free space"}, "waves/solve", {"f": 1e9, "E0": 100}, [("S_av", V("S_av0"), "W/m²", 1)],
  "S_av = |E₀|²/(2η₀).", "Power density grows with the square of the field.")
p(T, "Ulaby & Ravaioli Sec. 7-4", "exam", "Microwave in muscle",
  "A 2.45 GHz microwave enters muscle tissue (εr = 52.7, σ = 1.74 S/m). Find the skin depth.",
  {"type": "slab", "label": "muscle"}, "waves/solve", {"f": 2.45e9, "eps_r": 52.7, "sigma": 1.74}, [("δs", V("skin_depth"), "cm", 100)],
  "σ/ωε ≈ 0.24 — neither limit; use the exact α.", "Microwave ovens heat the outer couple of centimetres of food.")

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
