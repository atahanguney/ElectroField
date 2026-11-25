"""Worked problems: original exam-level problems with engine-verified solutions.

Problems are written in our own words; `ref` names the textbook section that covers the
concept (Ulaby & Ravaioli, Fundamentals of Applied Electromagnetics; Cheng, Field and Wave
Electromagnetics). Each problem runs one engine route — the solution steps and independent
checks shown on the page are the engine's — and lists the requested answers.
"""
import math

from .constants import C0
from . import routes
from .explain import render

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
p(T, "Ulaby & Ravaioli Sec. 4-8", "basic", "Refraction of E at a dielectric",
  "E₁ = 100 V/m in air makes 60° with the normal of a charge-free boundary with εr = 5. Find |E₂| and θ₂.",
  {"type": "interface", "e1": 1, "e2": 5, "theta": 60}, "mx/boundary", {"kind": "E", "eps1": 1, "eps2": 5, "F1": 100, "theta1_deg": 60},
  [("|E₂|", V("F2_mag"), "V/m", 1), ("θ₂", V("theta2_deg"), "°", 1)], "E₂t = E₁t, ε₂E₂n = ε₁E₁n.", "The part along the surface passes unchanged; the normal part shrinks by 5.")
p(T, "Ulaby & Ravaioli Sec. 4-8", "exam", "Boundary with surface charge",
  "εr₁ = 2 above, εr₂ = 4 below, E₁ = 1 kV/m at 30° from the normal, and ρs = 2 nC/m² on the boundary. Find |E₂|.",
  {"type": "interface", "e1": 2, "e2": 4, "theta": 30}, "mx/boundary", {"kind": "E", "eps1": 2, "eps2": 4, "F1": 1000, "theta1_deg": 30, "source": 2e-9},
  [("|E₂|", V("F2_mag"), "V/m", 1)], "n̂₂·(D₁ − D₂) = ρs ⇒ E₂n = (ε₁E₁n − ρs)/ε₂; E₂t = E₁t.", "Surface charge makes the normal D jump by exactly ρs.")
p(T, "Ulaby & Ravaioli Sec. 5-7", "exam", "H entering iron",
  "H₁ = 10 A/m in air at 45° hits iron with μr = 1000. Find the angle of H₂ from the normal.",
  {"type": "interface", "e1": 1, "e2": 1000, "theta": 45, "H": True}, "mx/boundary", {"kind": "H", "mu1": 1, "mu2": 1000, "F1": 10, "theta1_deg": 45},
  [("θ₂", V("theta2_deg"), "°", 1)], "H₂t = H₁t, μ₂H₂n = μ₁H₁n ⇒ tan θ₂ = (μ₂/μ₁) tan θ₁.", "Inside iron, H lies almost along the surface — the basis of magnetic shielding.")
p(T, "Ulaby & Ravaioli Sec. 6-3", "basic", "AC generator",
  "A 50-turn, 20 cm × 20 cm coil rotates at 60 rev/s in B = 0.3 T. Find the peak EMF.",
  {"type": "generator"}, "mx/faraday", {"mode": "motional", "N": 50, "B0": 0.3, "w": 0.2, "l": 0.2, "f": 60},
  [("V̂", V("V_peak"), "V", 1)], "Φ = BA cos Ωt ⇒ V = NBAΩ sin Ωt.", "Spinning the coil changes the flux through it; faster spin, more voltage.")
p(T, "Ulaby & Ravaioli Sec. 6-4", "basic", "Transformer EMF",
  "A fixed 10-turn, 10 cm × 10 cm loop sits in B = 0.05 cos(2π·1000t) T normal to it. Find the peak EMF.",
  {"type": "generator"}, "mx/faraday", {"mode": "transformer", "N": 10, "B0": 0.05, "w": 0.1, "l": 0.1, "f": 1000},
  [("V̂", V("V_peak"), "V", 1)], "V = −N dΦ/dt = NB₀Aω sin ωt.", "A changing field induces a voltage even in a loop that does not move.")
p(T, "Ulaby & Ravaioli Sec. 6-7", "basic", "Conductor or dielectric?",
  "Wet soil has εr = 20 and σ = 0.05 S/m. Above what frequency does displacement current dominate?",
  {"type": "medium"}, "mx/currents", {"eps_r": 20, "sigma": 0.05, "f": 1e6}, [("f_c", V("fc"), "MHz", 1e-6)],
  "|J_c| = |J_d| when σ = ωε ⇒ f_c = σ/(2πε).", "Below f_c charges mostly flow (conductor); above it they mostly shake in place (dielectric).")
p(T, "Ulaby & Ravaioli Sec. 6-6", "exam", "Charge relaxation in copper",
  "How fast does excess charge disappear from the inside of copper (σ = 5.8 × 10⁷ S/m)? Find τ.",
  {"type": "medium"}, "mx/currents", {"eps_r": 1, "sigma": 5.8e7, "f": 1e6}, [("τ", V("tau"), "s", 1)],
  "Continuity + Gauss: ∂ρ/∂t = −(σ/ε)ρ ⇒ τ = ε/σ.", "Charge inside a metal spreads to the surface almost instantly.")
p(T, "Ulaby & Ravaioli Sec. 6-7", "basic", "Current ratio in sea water",
  "Sea water: εr = 81, σ = 4 S/m. Find |J_c|/|J_d| at 10 MHz.",
  {"type": "medium"}, "mx/currents", {"eps_r": 81, "sigma": 4, "f": 1e7}, [("|J_c|/|J_d|", V("ratio"), "", 1)],
  "|J_c|/|J_d| = σ/(ωε).", "At 10 MHz sea water still behaves mostly like a conductor.")

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
