"""Reflection and transmission at a planar interface z = 0 (Ulaby ch. 8, Cheng ch. 8).

Medium 1 (z < 0) carries the incident wave; medium 2 (z > 0) the transmitted one.
normal  – normal incidence, any (lossy) media: Γ, τ, standing-wave pattern, power split.
oblique – lossless media, TE (⊥) and TM (∥): Fresnel coefficients vs angle, Brewster, critical angle.
"""
import numpy as np
from .constants import EPS0, MU0
from .derivation import Derivation, fmt
from . import waves


def _gamma_eta(f, eps_r, mu_r, sigma):
    c = waves.constants(f, eps_r, mu_r, sigma)
    return complex(c["alpha"] + 1j * c["beta"]), complex(c["eta"])


def normal(f=1e9, eps1=1.0, mu1=1.0, s1=0.0, eps2=4.0, mu2=1.0, s2=0.0, E0=1.0, n=500):
    if f <= 0:
        raise ValueError("need f > 0")
    D = Derivation()
    g1, e1 = _gamma_eta(f, eps1, mu1, s1)
    g2, e2 = _gamma_eta(f, eps2, mu2, s2)
    D.step("Intrinsic impedances", rf"\eta_1={fmt(abs(e1))}\angle{np.degrees(np.angle(e1)):.2f}^\circ,\ \ \eta_2={fmt(abs(e2))}\angle{np.degrees(np.angle(e2)):.2f}^\circ", [e1, e2], "Ω")
    G = (e2 - e1) / (e2 + e1)
    t = 2 * e2 / (e2 + e1)   # same as 1 + Γ, but without cancellation when Γ ≈ −1 (good conductors)
    D.step("Reflection coefficient", rf"\Gamma=\frac{{\eta_2-\eta_1}}{{\eta_2+\eta_1}}={fmt(abs(G))}\angle{np.degrees(np.angle(G)):.2f}^\circ", G, "")
    D.step("Transmission coefficient", rf"\tau=1+\Gamma=\frac{{2\eta_2}}{{\eta_2+\eta_1}}={fmt(abs(t))}\angle{np.degrees(np.angle(t)):.2f}^\circ", t, "")
    lossless1 = s1 == 0
    S = (1 + abs(G)) / (1 - abs(G)) if abs(G) < 1 else np.inf
    lam1 = 2 * np.pi / g1.imag
    if lossless1:
        D.step("Standing-wave ratio", rf"S=\frac{{1+|\Gamma|}}{{1-|\Gamma|}}={fmt(S)}", S, "")
        th = np.angle(G)
        lmax = (th * lam1 / (4 * np.pi)) % (lam1 / 2)
        D.step("First maximum of |E₁| (distance from interface)", rf"l_{{max}}=\frac{{\theta_r\lambda_1}}{{4\pi}}+n\frac{{\lambda_1}}{{2}}={fmt(lmax)}", lmax, "m",
               note="minima are λ/4 away from maxima")
    Si = abs(E0) ** 2 / (2 * abs(e1)) * np.cos(np.angle(e1))
    Rp = abs(G) ** 2
    St = abs(t * E0) ** 2 / 2 * (1 / np.conj(e2)).real
    D.step("Power", rf"R=|\Gamma|^2={fmt(Rp)},\quad T=\frac{{S_t}}{{S_i}}={fmt(St / Si if Si else 0)}", [Rp, St / Si if Si else 0], "",
           note="T uses Re(1/η₂*) so it is valid for lossy medium 2")
    # fields
    z1 = np.linspace(-2 * lam1, 0, n)
    lam2 = 2 * np.pi / g2.imag
    zmax2 = min(2 * lam2, 3 / g2.real) if g2.real > 0 else 2 * lam2
    z2 = np.linspace(0, zmax2, n)
    E1 = E0 * (np.exp(-g1 * z1) + G * np.exp(g1 * z1))
    H1 = E0 / e1 * (np.exp(-g1 * z1) - G * np.exp(g1 * z1))
    E2 = t * E0 * np.exp(-g2 * z2)
    H2 = E2 / e2
    # checks
    D.check(r"E_{1t}(0^-)=E_{2t}(0^+)", E1[-1], E2[0], 1e-12, "tangential E continuity from the field arrays", scale=abs(E0))
    D.check(r"H_{1t}(0^-)=H_{2t}(0^+)", H1[-1], H2[0], 1e-12, "tangential H continuity — independent of how Γ was defined", scale=abs(E0 / e1))
    P1 = 0.5 * (E1[-1] * np.conj(H1[-1])).real
    P2 = 0.5 * (E2[0] * np.conj(H2[0])).real
    D.check(r"\tfrac12\mathrm{Re}(E\,H^*)\big|_{0^-}=\tfrac12\mathrm{Re}(E\,H^*)\big|_{0^+} \text{ (energy conservation)}", P1, P2, 1e-12,
            "net Poynting flux on both sides", scale=abs(Si) if Si else 1.0)
    if lossless1 and np.isfinite(S):
        # |E1(z)|² = E0²[1 + |Γ|² + 2|Γ|cos(2βz + θr)] → extremes sampled finely over one half-wavelength
        zz = np.linspace(-lam1 / 2, 0, 20001)
        env = np.abs(E0 * (np.exp(-g1 * zz) + G * np.exp(g1 * zz)))
        D.check(r"\frac{|E_1|_{max}}{|E_1|_{min}}=S \text{ (from the field pattern)}", S, env.max() / max(env.min(), 1e-300),
                max(1e-6, 5e-8 * S * S), "max/min of |E₁(z)| on 20 001 points over λ/2")
    return {**D.out(Gamma=G, tau=t, Gamma_mag=abs(G), Gamma_deg=np.degrees(np.angle(G)), S=S, R=Rp, T=St / Si if Si else 0.0,
                    lambda1=lam1, lambda2=lam2, eta1=e1, eta2=e2),
            "field": {"z1": z1.tolist(), "E1": {"re": E1.real.tolist(), "im": E1.imag.tolist()}, "H1": {"re": H1.real.tolist(), "im": H1.imag.tolist()},
                      "z2": z2.tolist(), "E2": {"re": E2.real.tolist(), "im": E2.imag.tolist()}, "H2": {"re": H2.real.tolist(), "im": H2.imag.tolist()}}}


def _fresnel(n1e, n2e, e1, e2, th):
    """Lossless media. th in rad (array ok). Returns Γ⊥, τ⊥, Γ∥, τ∥, cosθt (complex beyond θc)."""
    s = n1e / n2e * np.sin(th)
    ct = np.sqrt((1 - s * s).astype(complex))
    ct = np.where(np.imag(ct) > 0, np.conj(ct), ct)  # evanescent branch: e^{-αz} into medium 2
    ci = np.cos(th)
    Gp = (e2 * ci - e1 * ct) / (e2 * ci + e1 * ct)
    Gl = (e2 * ct - e1 * ci) / (e2 * ct + e1 * ci)
    tp = 1 + Gp
    with np.errstate(divide="ignore", invalid="ignore"):
        tl = (1 + Gl) * ci / ct
    return Gp, tp, Gl, tl, ct


def oblique(eps1=1.0, mu1=1.0, eps2=2.25, mu2=1.0, theta_deg=30.0, n=361):
    if min(eps1, mu1, eps2, mu2) <= 0 or not 0 <= theta_deg < 90:
        raise ValueError("need positive ε, μ and 0 ≤ θi < 90°")
    D = Derivation()
    n1, n2 = np.sqrt(eps1 * mu1), np.sqrt(eps2 * mu2)
    e1, e2 = np.sqrt(MU0 * mu1 / (EPS0 * eps1)), np.sqrt(MU0 * mu2 / (EPS0 * eps2))
    D.step("Refractive indices and impedances", rf"n_1={fmt(n1)},\ n_2={fmt(n2)},\quad\eta_1={fmt(e1)},\ \eta_2={fmt(e2)}", [n1, n2], "")
    th = np.radians(theta_deg)
    Gp, tp, Gl, tl, ct = (complex(x) for x in _fresnel(n1, n2, e1, e2, np.array(th)))
    tir = n1 * np.sin(th) > n2
    tht = np.degrees(np.arcsin(min(n1 / n2 * np.sin(th), 1.0)))
    D.step("Snell's law", rf"n_1\sin\theta_i=n_2\sin\theta_t\ \Rightarrow\ \theta_t={tht:.3f}^\circ" + (r"\ \text{(beyond critical: evanescent)}" if tir else ""), tht, "°")
    thc = np.degrees(np.arcsin(n2 / n1)) if n2 < n1 else None
    if thc is not None:
        D.step("Critical angle", rf"\theta_c=\sin^{{-1}}(n_2/n_1)={thc:.3f}^\circ", thc, "°", note="total internal reflection above θc")
    # Brewster for TM (Ulaby eq. 8-74): sin²θB = (1 − μ2ε1/μ1ε2) / (1 − (ε1/ε2)²)
    den = 1 - (eps1 / eps2) ** 2
    num = 1 - (mu2 * eps1) / (mu1 * eps2)
    sb = num / den if den != 0 else np.nan
    thB = np.degrees(np.arcsin(np.sqrt(sb))) if 0 <= sb <= 1 else None
    if thB is not None:
        D.step("Brewster angle (∥ / TM)", rf"\sin^2\theta_B=\frac{{1-\mu_2\varepsilon_1/\mu_1\varepsilon_2}}{{1-(\varepsilon_1/\varepsilon_2)^2}}\ \Rightarrow\ \theta_B={thB:.3f}^\circ", thB, "°",
               note="non-magnetic media: tan θB = n₂/n₁")
    D.step("Perpendicular (TE)", rf"\Gamma_\perp=\frac{{\eta_2\cos\theta_i-\eta_1\cos\theta_t}}{{\eta_2\cos\theta_i+\eta_1\cos\theta_t}}={fmt(abs(Gp))}\angle{np.degrees(np.angle(Gp)):.2f}^\circ", Gp, "")
    D.step("Parallel (TM)", rf"\Gamma_\parallel=\frac{{\eta_2\cos\theta_t-\eta_1\cos\theta_i}}{{\eta_2\cos\theta_t+\eta_1\cos\theta_i}}={fmt(abs(Gl))}\angle{np.degrees(np.angle(Gl)):.2f}^\circ", Gl, "")
    ci = np.cos(th)
    Tp = 0.0 if tir else abs(tp) ** 2 * e1 * ct.real / (e2 * ci)
    Tl = 0.0 if tir else abs(tl) ** 2 * e1 * ct.real / (e2 * ci)
    D.step("Reflectivity / transmissivity", rf"R_\perp={fmt(abs(Gp) ** 2)},\ T_\perp={fmt(Tp)};\quad R_\parallel={fmt(abs(Gl) ** 2)},\ T_\parallel={fmt(Tl)}",
           [abs(Gp) ** 2, Tp, abs(Gl) ** 2, Tl], "")
    # checks
    D.check(r"\text{TE: } (1-\Gamma_\perp)\frac{\cos\theta_i}{\eta_1}=\tau_\perp\frac{\cos\theta_t}{\eta_2} \text{ (tangential H)}",
            (1 - Gp) * ci / e1, tp * ct / e2, 1e-12, "boundary condition not used to define τ⊥")
    if not tir:
        D.check(r"\text{TM: } \frac{1-\Gamma_\parallel}{\eta_1}=\frac{\tau_\parallel}{\eta_2} \text{ (tangential H)}", (1 - Gl) / e1, tl / e2, 1e-12,
                "boundary condition not used to define τ∥")
        D.check(r"R_\perp+T_\perp=1", 1.0, abs(Gp) ** 2 + Tp, 1e-12, "power balance (lossless)")
        D.check(r"R_\parallel+T_\parallel=1", 1.0, abs(Gl) ** 2 + Tl, 1e-12, "power balance (lossless)")
        D.check(r"k_1\sin\theta_i=k_2\sin\theta_t \text{ (phase matching)}", n1 * np.sin(th), n2 * np.sin(np.radians(tht)), 1e-12, "Snell")
    else:
        D.check(r"|\Gamma_\perp|=|\Gamma_\parallel|=1 \text{ beyond } \theta_c", 1.0, max(abs(Gp), abs(Gl)), 1e-12, "total internal reflection")
    if thB is not None:
        G_B = complex(_fresnel(n1, n2, e1, e2, np.array(np.radians(thB)))[2])
        D.check(r"\Gamma_\parallel(\theta_B)=0", 0.0, abs(G_B), 1e-10, "Fresnel evaluated at the Brewster angle")
    G0 = (e2 - e1) / (e2 + e1)
    D.check(r"\theta_i\to0:\ \Gamma_\perp=\Gamma_\parallel=\frac{\eta_2-\eta_1}{\eta_2+\eta_1}", G0, complex(_fresnel(n1, n2, e1, e2, np.array(0.0))[2]), 1e-12, "normal-incidence limit")
    # sweep
    ths = np.radians(np.linspace(0, 89.9, n))
    sGp, stp, sGl, stl, sct = _fresnel(n1, n2, e1, e2, ths)
    with np.errstate(invalid="ignore"):
        sTp = np.where(np.abs(np.imag(sct)) > 1e-12, 0.0, np.abs(stp) ** 2 * e1 * sct.real / (e2 * np.cos(ths)))
        sTl = np.where(np.abs(np.imag(sct)) > 1e-12, 0.0, np.abs(stl) ** 2 * e1 * sct.real / (e2 * np.cos(ths)))
    return {**D.out(theta_t=tht, tir=bool(tir), theta_c=thc, theta_B=thB, Gamma_perp=Gp, Gamma_par=Gl,
                    R_perp=abs(Gp) ** 2, T_perp=Tp, R_par=abs(Gl) ** 2, T_par=Tl),
            "sweep": {"theta": np.degrees(ths).tolist(), "R_perp": (np.abs(sGp) ** 2).tolist(), "R_par": (np.abs(sGl) ** 2).tolist(),
                      "T_perp": np.nan_to_num(sTp).tolist(), "T_par": np.nan_to_num(sTl).tolist(),
                      "ph_perp": np.degrees(np.angle(sGp)).tolist(), "ph_par": np.degrees(np.angle(sGl)).tolist()}}
