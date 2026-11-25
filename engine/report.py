"""Physical verification report: reference problems per module.

For each case the *theoretical* value is written out here from the textbook closed
form with plain `math` (no engine code), the *numerical* value comes from the engine
route the website uses, and the report lists both with the percentage error.
"""
import math

from .constants import C0, EPS0, ETA0, K_E, MU0
from . import routes

PI = math.pi
CASES = []


def case(module, problem, formula, theory, route, params, pick, unit, tol_pct=1e-6, ref=""):
    CASES.append(dict(module=module, problem=problem, formula=formula, theory=theory, route=route,
                      params=params, pick=pick, unit=unit, tol_pct=tol_pct, ref=ref))


# ---- 0 · 1-D / 2-D / 3-D
case("1-D, 2-D, 3-D waves", "Point source, lossless: level change when distance doubles", r"20\log_{10}(1/2)",
     20 * math.log10(0.5), "dim/compare", {"f": 1e9, "r_max_lambda": 10}, lambda r: _sens(r, "double the distance", "3D"), "dB", 1e-6, "Ulaby §9-1")
case("1-D, 2-D, 3-D waves", "Line source, far zone: level change when distance doubles", r"10\log_{10}(1/2)",
     10 * math.log10(0.5), "dim/compare", {"f": 1e9, "r_max_lambda": 10}, lambda r: _sens(r, "double the distance", "2D"), "dB", 1.0, "Cheng §10")
case("1-D, 2-D, 3-D waves", "Plane wave, lossless: level change when distance doubles", "0",
     0.0, "dim/compare", {"f": 1e9, "r_max_lambda": 10}, lambda r: _sens(r, "double the distance", "1D"), "dB", None, "Ulaby §7-2")

# ---- 1 · coordinates
case("Coordinate systems", "Spherical dv at R = 2 m, θ = 60°, dR = 1 mm, dθ = dφ = 0.01°", r"R^2\sin\theta\,dR\,d\theta\,d\phi",
     4 * math.sin(PI / 3) * 1e-3 * math.radians(0.01) ** 2, "coords/element",
     {"system": "spherical", "u1": 2, "u2": 60, "u3": 0, "d1": 1e-3, "d2": 0.01, "d3": 0.01}, lambda r: r["values"]["dv"], "m³", 1e-9, "Ulaby §3-2.3")
case("Coordinate systems", "Cartesian (2, 3, −1) → spherical R", r"\sqrt{x^2+y^2+z^2}",
     math.sqrt(14), "coords/convert", {"src": "cartesian", "dst": "spherical", "u1": 2, "u2": 3, "u3": -1}, lambda r: r["values"]["point"][0], "m", 1e-9, "Ulaby §3-3")
case("Coordinate systems", "Cartesian (2, 3, −1) → spherical θ", r"\cos^{-1}(z/R)",
     math.degrees(math.acos(-1 / math.sqrt(14))), "coords/convert", {"src": "cartesian", "dst": "spherical", "u1": 2, "u2": 3, "u3": -1}, lambda r: r["values"]["point"][1], "°", 1e-9, "Ulaby §3-3")

# ---- 2 · electrostatics
case("Electrostatics", "|E| of a 1 nC point charge at 0.5 m", r"\frac{q}{4\pi\varepsilon_0R^2}",
     K_E * 1e-9 / 0.25, "es/charges", {"charges": [{"q": 1e-9, "x": 0, "y": 0}], "probe": [0.5, 0]}, lambda r: r["values"]["E_mag"], "V/m", 1e-9, "Ulaby §4-3")
case("Electrostatics", "Uniform sphere ρv = 1 µC/m³, a = 0.1 m: |E| at R = 0.3 m", r"\frac{\rho_va^3}{3\varepsilon_0R^2}",
     1e-6 * 0.1 ** 3 / (3 * EPS0 * 0.09), "es/gauss", {"kind": "sphere", "rho": 1e-6, "a": 0.1, "r": 0.3}, lambda r: r["values"]["E"], "V/m", 1e-9, "Ulaby §4-4")
case("Electrostatics", "Coax a = 0.45 mm, b = 1.47 mm, εr = 2.25: capacitance per metre", r"\frac{2\pi\varepsilon}{\ln(b/a)}",
     2 * PI * 2.25 * EPS0 / math.log(1.47 / 0.45), "es/capacitor", {"kind": "coax", "a": 0.45e-3, "b": 1.47e-3, "eps_r": 2.25, "length": 1}, lambda r: r["values"]["C"], "F/m", 1e-9, "Ulaby §4-10")
case("Electrostatics", "Parallel plates A = 1 cm², d = 0.1 mm, εr = 4.4", r"\varepsilon A/d",
     4.4 * EPS0 * 1e-4 / 1e-4, "es/capacitor", {"kind": "parallel", "A": 1e-4, "d": 1e-4, "eps_r": 4.4}, lambda r: r["values"]["C"], "F", 1e-9, "Ulaby §4-10")

# ---- 3 · magnetostatics
case("Magnetostatics", "Infinite wire, 10 A: |B| at 0.2 m", r"\frac{\mu_0I}{2\pi r}",
     MU0 * 10 / (2 * PI * 0.2), "ms/wires", {"currents": [{"I": 10, "x": 0, "y": 0}], "probe": [0.2, 0]}, lambda r: r["values"]["B_mag"], "T", 1e-9, "Ulaby §5-2")
case("Magnetostatics", "Two wires 5 A each, 0.2 m apart: force per metre", r"\frac{\mu_0I_1I_2}{2\pi d}",
     MU0 * 25 / (2 * PI * 0.2), "ms/wires", {"currents": [{"I": 5, "x": -0.1, "y": 0}, {"I": 5, "x": 0.1, "y": 0}], "probe": [0, 0.5]},
     lambda r: math.hypot(*r["forces"][0]), "N/m", 1e-9, "Ulaby §5-2.3")
case("Magnetostatics", "Circular loop a = 0.1 m, 1 A: B at the centre", r"\frac{\mu_0I}{2a}",
     MU0 / 0.2, "ms/loops", {"kind": "loop", "I": 1, "a": 0.1}, lambda r: r["values"]["B_center"], "T", 1e-9, "Ulaby §5-2.2")
case("Magnetostatics", "Coax a = 0.45 mm, b = 1.47 mm: external inductance per metre", r"\frac{\mu_0}{2\pi}\ln\frac{b}{a}",
     MU0 / (2 * PI) * math.log(1.47 / 0.45), "ms/inductance", {"kind": "coax", "a": 0.45e-3, "b": 1.47e-3, "length": 1}, lambda r: r["values"]["L"], "H/m", 1e-9, "Ulaby §5-7")

# ---- 4 · Maxwell
case("Maxwell & boundaries", "E at 40° from normal, εr 1 → 4, no surface charge: θ₂", r"\tan^{-1}\!\left(\frac{\varepsilon_2}{\varepsilon_1}\tan\theta_1\right)",
     math.degrees(math.atan(4 * math.tan(math.radians(40)))), "mx/boundary", {"kind": "E", "eps1": 1, "eps2": 4, "F1": 10, "theta1_deg": 40}, lambda r: r["values"]["theta2_deg"], "°", 1e-9, "Ulaby §4-8")
case("Maxwell & boundaries", "Generator: 100 turns, 0.1 × 0.2 m, 0.5 T, 50 rev/s: peak EMF", r"NBA\omega",
     100 * 0.5 * 0.02 * 2 * PI * 50, "mx/faraday", {"mode": "motional", "N": 100, "B0": 0.5, "w": 0.1, "l": 0.2, "f": 50}, lambda r: r["values"]["V_peak"], "V", 0.02, "Ulaby §6-5")
case("Maxwell & boundaries", "Sea water (εr 81, σ 4 S/m): |Jc| = |Jd| frequency", r"\frac{\sigma}{2\pi\varepsilon}",
     4 / (2 * PI * 81 * EPS0), "mx/currents", {"eps_r": 81, "sigma": 4, "f": 1e6}, lambda r: r["values"]["fc"], "Hz", 1e-9, "Ulaby §6-7")
# inverse (design) questions: the engine root-finds on its forward model; theory solves the closed form for the unknown.
# Givens are those of question-bank seed 1 (c4-ratio-freq, c4-gen-speed, c4-rhos).
case("Maxwell & boundaries", "Inverse: εr 10, σ 3.3 S/m — frequency where |Jc|/|Jd| = 10", r"\frac{\sigma}{2\pi\varepsilon k}",
     3.3 / (2 * PI * 10 * EPS0 * 10) / 1e6, "qb/check", {"id": "c4-ratio-freq", "seed": 1}, lambda r: r["answer"], "MHz", 1e-6, "Ulaby §6-7")
case("Maxwell & boundaries", "Inverse: 50 turns, 0.086 × 0.29 m, 0.95 T — speed for 372 V peak", r"\frac{\hat V}{2\pi NBA}",
     372 / (2 * PI * 50 * 0.95 * 0.086 * 0.29), "qb/check", {"id": "c4-gen-speed", "seed": 1}, lambda r: r["answer"], "rev/s", 0.01, "Ulaby §6-5")
case("Maxwell & boundaries", "Inverse: εr 1 → 5, E₁ 1560 V/m at 58°, E₂n = 233.1 V/m — surface charge", r"\varepsilon_1E_{1n}-\varepsilon_2E_{2n}",
     EPS0 * (1560 * math.cos(math.radians(58)) - 5 * 233.1) * 1e9, "qb/check", {"id": "c4-rhos", "seed": 1}, lambda r: r["answer"], "nC/m²", 1e-6, "Ulaby §4-8")

# ---- 5 · plane waves
case("Plane waves", "Free space, 1 GHz: wavelength", r"c/f", C0 / 1e9, "waves/solve", {"f": 1e9}, lambda r: r["values"]["wavelength"], "m", 1e-9, "Ulaby §7-2")
case("Plane waves", "Free space: intrinsic impedance", r"\sqrt{\mu_0/\varepsilon_0}", ETA0, "waves/solve", {"f": 1e9}, lambda r: r["values"]["eta_mag"], "Ω", 1e-9, "Ulaby §7-2")
case("Plane waves", "Copper (σ = 5.8×10⁷ S/m) at 1 MHz: skin depth", r"1/\sqrt{\pi f\mu\sigma}",
     1 / math.sqrt(PI * 1e6 * MU0 * 5.8e7), "waves/solve", {"f": 1e6, "sigma": 5.8e7}, lambda r: r["values"]["skin_depth"], "m", 1e-4, "Ulaby §7-5")

# ---- 6 · reflection
case("Reflection", "Air → glass (εr 2.25), normal incidence: reflected power", r"\left(\frac{n_1-n_2}{n_1+n_2}\right)^2",
     ((1 - 1.5) / (1 + 1.5)) ** 2, "rf/normal", {"f": 1e9, "eps2": 2.25}, lambda r: r["values"]["R"], "", 1e-9, "Ulaby §8-1")
case("Reflection", "Air → glass: Brewster angle", r"\tan^{-1}(n_2/n_1)",
     math.degrees(math.atan(1.5)), "rf/oblique", {"eps1": 1, "eps2": 2.25, "theta_deg": 30}, lambda r: r["values"]["theta_B"], "°", 1e-9, "Ulaby §8-4")
case("Reflection", "Glass → air: critical angle", r"\sin^{-1}(n_2/n_1)",
     math.degrees(math.asin(1 / 1.5)), "rf/oblique", {"eps1": 2.25, "eps2": 1, "theta_deg": 30}, lambda r: r["values"]["theta_c"], "°", 1e-9, "Ulaby §8-3")

# ---- 7 · transmission lines
case("Transmission lines", "Z_L = 100 + j50 Ω on 50 Ω: |Γ|", r"\left|\frac{Z_L-Z_0}{Z_L+Z_0}\right|",
     abs(complex(100, 50) - 50) / abs(complex(100, 50) + 50), "tl/line", {"Z0": 50, "RL": 100, "XL": 50}, lambda r: r["values"]["Gamma_mag"], "", 1e-9, "Ulaby §2-6")
case("Transmission lines", "Same load: VSWR", r"\frac{1+|\Gamma|}{1-|\Gamma|}",
     (1 + math.sqrt(0.2)) / (1 - math.sqrt(0.2)), "tl/line", {"Z0": 50, "RL": 100, "XL": 50}, lambda r: r["values"]["S"], "", 1e-9, "Ulaby §2-6")
case("Transmission lines", "λ/4 line (50 Ω) on a 100 Ω load: Re Z_in", r"Z_0^2/Z_L",
     25.0, "tl/line", {"Z0": 50, "RL": 100, "XL": 0, "f": 1e9, "length": C0 / 1e9 / 4}, lambda r: r["values"]["Zin"]["re"], "Ω", 1e-7, "Ulaby §2-8")

# ---- 8 · waveguides & antennas
case("Waveguides & antennas", "WR-90 (a = 22.86 mm), TE₁₀ cut-off", r"\frac{c}{2a}",
     C0 / (2 * 22.86e-3), "ra/waveguide", {"a": 22.86e-3, "b": 10.16e-3, "f": 10e9}, lambda r: r["values"]["fc"], "Hz", 1e-9, "Ulaby §8-10")
def _cin(x, terms=40):
    """Cin(x) = ∫₀ˣ (1 − cos t)/t dt = Σ (−1)^{k+1} x^{2k} / (2k·(2k)!) — plain power series, no SciPy."""
    return sum((-1) ** (k + 1) * x ** (2 * k) / (2 * k * math.factorial(2 * k)) for k in range(1, terms))


case("Waveguides & antennas", "Half-wave dipole: radiation resistance", r"30\,\mathrm{Cin}(2\pi)\approx73.13",
     30 * _cin(2 * PI), "ra/dipole", {"length_lambda": 0.5}, lambda r: r["values"]["R_rad"], "Ω", 1e-3, "Ulaby §9-3")
case("Waveguides & antennas", "Short dipole: directivity", "3/2", 1.5, "ra/dipole", {"length_lambda": 0.05}, lambda r: r["values"]["D"], "", 1e-4, "Ulaby §9-1")
case("Waveguides & antennas", "8 elements, d = λ/4, δ = −90°: beam direction (end-fire)", r"\cos^{-1}(-\delta/kd)",
     0.0, "ra/array", {"N": 8, "d_lambda": 0.25, "delta_deg": -90}, lambda r: r["values"]["theta0"], "°", None, "Ulaby §10-4")


def _sens(r, change, dim):
    return next(s for s in r["sensitivity"] if s["change"] == change)[dim]


def run():
    rows = []
    for c in CASES:
        r = routes.call(c["route"], c["params"])
        num = float(c["pick"](r))
        th = float(c["theory"])
        if th != 0:
            err = abs(num - th) / abs(th) * 100
            ok = err <= c["tol_pct"]
        else:
            err = abs(num - th)
            ok = err <= 1e-9
        rows.append({"module": c["module"], "problem": c["problem"], "formula": c["formula"], "theory": th, "numeric": num,
                     "unit": c["unit"], "error_pct": err if th != 0 else None, "abs_error": None if th != 0 else err,
                     "tol_pct": c["tol_pct"], "passed": bool(ok), "engine_checks_passed": bool(r.get("all_passed", r.get("verified", True))),
                     "ref": c["ref"], "route": c["route"]})
    mods = []
    for m in dict.fromkeys(x["module"] for x in rows):
        sub = [x for x in rows if x["module"] == m]
        errs = [x["error_pct"] for x in sub if x["error_pct"] is not None]
        mods.append({"module": m, "cases": len(sub), "passed": sum(x["passed"] for x in sub), "max_error_pct": max(errs) if errs else 0.0})
    return {"rows": rows, "modules": mods, "all_passed": all(x["passed"] and x["engine_checks_passed"] for x in rows)}
