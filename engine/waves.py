"""Uniform plane waves in a homogeneous linear medium (Ulaby ch. 7, Cheng ch. 8).

Phasor fields  E = x̂ E0 e^{-γz},  H = ŷ (E0/ηc) e^{-γz}
    εc = ε' − jε'',  ε' = ε,  ε'' = σ/ω
    γ  = α + jβ = jω√(μ εc)
    ηc = √(μ/εc)
Regimes (Ulaby): low-loss ε''/ε' < 0.01, good conductor ε''/ε' > 100.
"""
import numpy as np
from .constants import EPS0, MU0
from .derivation import Derivation, fmt

LOW_LOSS, GOOD_COND = 0.01, 100.0


def _validate(f, eps_r, mu_r, sigma):
    f, eps_r, mu_r, sigma = (np.asarray(v, float) for v in (f, eps_r, mu_r, sigma))
    if np.any(f <= 0) or np.any(eps_r < 1e-12) or np.any(mu_r < 1e-12) or np.any(sigma < 0):
        raise ValueError("need f > 0, ε_r > 0, μ_r > 0, σ ≥ 0")
    return f, eps_r, mu_r, sigma


def constants(f, eps_r=1.0, mu_r=1.0, sigma=0.0):
    """Vectorised closed-form α, β, ηc and derived quantities (no derivation log)."""
    f, eps_r, mu_r, sigma = _validate(f, eps_r, mu_r, sigma)
    w = 2 * np.pi * f
    eps, mu = EPS0 * eps_r, MU0 * mu_r
    lt = sigma / (w * eps)  # ε''/ε'  (loss tangent)
    root = np.sqrt(1 + lt ** 2)
    alpha = w * np.sqrt(mu * eps / 2 * (root - 1))
    beta = w * np.sqrt(mu * eps / 2 * (root + 1))
    eta = np.sqrt(mu / eps) / np.sqrt(1 - 1j * lt)
    with np.errstate(divide="ignore"):
        delta = np.where(alpha > 0, 1 / np.where(alpha > 0, alpha, 1), np.inf)
    return {"omega": w, "loss_tangent": lt, "alpha": alpha, "beta": beta,
            "alpha_dB": 8.686 * alpha, "eta_mag": np.abs(eta), "eta_phase_deg": np.degrees(np.angle(eta)),
            "eta": eta, "vp": w / beta, "wavelength": 2 * np.pi / beta, "skin_depth": delta}


def regime(lt):
    if lt < LOW_LOSS:
        return "low-loss dielectric"
    if lt > GOOD_COND:
        return "good conductor"
    return "quasi-conductor"


def solve(f, eps_r=1.0, mu_r=1.0, sigma=0.0, E0=1.0, z_max=None, n=400):
    """Full derivation for one operating point, plus fields along z."""
    f, eps_r, mu_r, sigma = (float(v) for v in _validate(f, eps_r, mu_r, sigma))
    D = Derivation()
    w = D.step("Angular frequency", rf"\omega=2\pi f=2\pi({fmt(f)})", 2 * np.pi * f, "rad/s")
    eps, mu = EPS0 * eps_r, MU0 * mu_r
    D.step("Permittivity", rf"\varepsilon=\varepsilon_r\varepsilon_0={fmt(eps_r)}\,\varepsilon_0={fmt(eps)}", eps, "F/m")
    D.step("Permeability", rf"\mu=\mu_r\mu_0={fmt(mu_r)}\,\mu_0={fmt(mu)}", mu, "H/m")
    lt = D.step("Loss tangent",
                rf"\frac{{\varepsilon''}}{{\varepsilon'}}=\frac{{\sigma}}{{\omega\varepsilon}}="
                rf"\frac{{{fmt(sigma)}}}{{{fmt(w)}\cdot{fmt(eps)}}}={fmt(sigma / (w * eps))}",
                sigma / (w * eps), "", note=f"→ {regime(sigma / (w * eps))} (Ulaby thresholds 0.01 / 100)")
    c = constants(f, eps_r, mu_r, sigma)
    a, b, eta = float(c["alpha"]), float(c["beta"]), complex(c["eta"])
    D.step("Attenuation constant",
           r"\alpha=\omega\left[\frac{\mu\varepsilon'}{2}\left(\sqrt{1+(\varepsilon''/\varepsilon')^2}-1\right)\right]^{1/2}"
           rf"={fmt(a)}", a, "Np/m", note=f"= {8.686 * a:.4g} dB/m")
    D.step("Phase constant",
           r"\beta=\omega\left[\frac{\mu\varepsilon'}{2}\left(\sqrt{1+(\varepsilon''/\varepsilon')^2}+1\right)\right]^{1/2}"
           rf"={fmt(b)}", b, "rad/m")
    D.step("Intrinsic impedance",
           rf"\eta_c=\sqrt{{\frac{{\mu}}{{\varepsilon'}}}}\left(1-j\frac{{\varepsilon''}}{{\varepsilon'}}\right)^{{-1/2}}"
           rf"={fmt(abs(eta))}\angle{np.degrees(np.angle(eta)):.3f}^\circ", eta, "Ω")
    D.step("Phase velocity", rf"u_p=\omega/\beta={fmt(w / b)}", w / b, "m/s")
    D.step("Wavelength", rf"\lambda=2\pi/\beta={fmt(2 * np.pi / b)}", 2 * np.pi / b, "m")
    if a > 0:
        D.step("Skin depth", rf"\delta_s=1/\alpha={fmt(1 / a)}", 1 / a, "m",
               note="amplitude falls to 1/e ≈ 36.8 %")
    th = np.angle(eta)
    S0 = E0 ** 2 / (2 * abs(eta)) * np.cos(th)
    D.step("Time-average power density",
           rf"S_{{av}}(z)=\frac{{|E_0|^2}}{{2|\eta_c|}}e^{{-2\alpha z}}\cos\theta_\eta,\quad S_{{av}}(0)={fmt(S0)}",
           S0, "W/m²")

    # --- independent checks -------------------------------------------------
    gamma = np.sqrt(1j * w * mu * (sigma + 1j * w * eps))  # principal root ⇒ Re, Im ≥ 0
    D.check(r"\alpha \text{ vs } \mathrm{Re}\sqrt{j\omega\mu(\sigma+j\omega\varepsilon)}", gamma.real, a, 1e-9,
            "complex square root (independent of closed form)")
    D.check(r"\beta \text{ vs } \mathrm{Im}\,\gamma", gamma.imag, b, 1e-9, "complex square root")
    D.check(r"\eta_c=j\omega\mu/\gamma", 1j * w * mu / gamma, eta, 1e-9, "from Faraday's law")
    g2 = a * a + b * b  # = |γ|², the natural scale of both identities
    D.check(r"\alpha^2-\beta^2=-\omega^2\mu\varepsilon", -w * w * mu * eps, a * a - b * b, 1e-9, "Re(γ²), error / |γ|²",
            scale=g2)
    D.check(r"2\alpha\beta=\omega\mu\sigma", w * mu * sigma, 2 * a * b, 1e-9, "Im(γ²), error / |γ|²", scale=g2)
    if lt < LOW_LOSS:
        D.check(r"\text{low-loss: }\alpha\approx\frac{\sigma}{2}\sqrt{\mu/\varepsilon}",
                sigma / 2 * np.sqrt(mu / eps), a, 1e-4 if sigma else 0, "approximation, error ~ (ε''/ε')²")
    if lt > GOOD_COND:
        D.check(r"\text{good conductor: }\alpha\approx\sqrt{\pi f\mu\sigma}",
                np.sqrt(np.pi * f * mu * sigma), a, 1.0 / lt, "approximation, error ~ ε'/ε''")

    # Maxwell residuals: differentiate the phasor field numerically along z
    if z_max is None:
        z_max = min(3 / a, 4 * 2 * np.pi / b) if a > 0 else 4 * 2 * np.pi / b
    z = np.linspace(0, z_max, n)
    E = E0 * np.exp(-gamma * z)
    H = E / eta
    dz = z[1] - z[0]
    dE, dH = np.gradient(E, dz, edge_order=2), np.gradient(H, dz, edge_order=2)
    sl = slice(2, -2)
    r1 = np.abs(dE[sl] - (-1j * w * mu * H[sl])).max() / np.abs(w * mu * H[sl]).max()
    r2 = np.abs(-dH[sl] - (sigma + 1j * w * eps) * E[sl]).max() / np.abs((sigma + 1j * w * eps) * E[sl]).max()
    tol = 5 * (abs(gamma) * dz) ** 2  # 2nd-order FD truncation bound
    D.check(r"\nabla\times\mathbf E=-j\omega\mu\mathbf H \;(\partial E_x/\partial z)", 0.0, r1, tol,
            f"finite-difference residual on {n} points")
    D.check(r"\nabla\times\mathbf H=(\sigma+j\omega\varepsilon)\mathbf E \;(-\partial H_y/\partial z)", 0.0, r2,
            tol, f"finite-difference residual on {n} points")

    vals = {k: (v.item() if isinstance(v, np.ndarray) else v) for k, v in c.items()}
    vals.update(regime=regime(lt), S_av0=S0, E0=E0)
    return {**D.out(**vals),
            "field": {"z": z.tolist(), "E": {"re": E.real.tolist(), "im": E.imag.tolist()},
                      "H": {"re": H.real.tolist(), "im": H.imag.tolist()},
                      "S_av": (E0 ** 2 / (2 * abs(eta)) * np.cos(th) * np.exp(-2 * a * z)).tolist()}}


SWEEPABLE = {"f": (1e3, 1e12), "sigma": (1e-6, 1e8), "eps_r": (1, 100), "mu_r": (1, 1e4)}


def sweep(param, lo, hi, f=1e9, eps_r=1.0, mu_r=1.0, sigma=0.0, n=300):
    """α, β, |ηc|, δs … as a function of one parameter (log axis)."""
    if param not in SWEEPABLE:
        raise ValueError(f"param must be one of {list(SWEEPABLE)}")
    if not (0 < lo < hi):
        raise ValueError("need 0 < lo < hi")
    x = np.logspace(np.log10(lo), np.log10(hi), n)
    args = {"f": f, "eps_r": eps_r, "mu_r": mu_r, "sigma": sigma, param: x}
    c = constants(**args)
    # regime boundaries along the sweep (where ε''/ε' crosses 0.01 and 100)
    bounds = {}
    for name, k in (("low_loss", LOW_LOSS), ("good_conductor", GOOD_COND)):
        if param == "f" and sigma > 0:
            bounds[name] = sigma / (2 * np.pi * EPS0 * eps_r * k)
        elif param == "sigma":
            bounds[name] = k * 2 * np.pi * f * EPS0 * eps_r
        elif param == "eps_r" and sigma > 0:
            bounds[name] = sigma / (2 * np.pi * f * EPS0 * k)
    bounds = {k: v for k, v in bounds.items() if lo <= v <= hi}
    keep = ("loss_tangent", "alpha", "alpha_dB", "beta", "eta_mag", "eta_phase_deg", "vp", "wavelength", "skin_depth")
    return {"param": param, "x": x.tolist(), "boundaries": bounds,
            **{k: [None if not np.isfinite(v) else float(v) for v in np.broadcast_to(c[k], x.shape)] for k in keep}}
