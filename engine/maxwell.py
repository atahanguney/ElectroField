"""Time-varying fields and boundary conditions (Ulaby ch. 6 & §4-8, §5-7; Cheng ch. 7).

boundary  – E/D or H/B across a planar interface (y = 0), medium 1 in y > 0,
            n̂₂ = +ŷ points from medium 2 into medium 1. Tangential axis = x.
faraday   – transformer EMF (stationary loop, B(t)) and motional EMF (rotating loop).
currents  – conduction vs displacement current, charge relaxation.
"""
import numpy as np
from scipy import integrate
from .constants import EPS0, MU0
from .derivation import Derivation, fmt


def boundary(kind="E", eps1=1.0, eps2=4.0, mu1=1.0, mu2=1.0, F1=1.0, theta1_deg=40.0, source=0.0, pec=False):
    """kind 'E': F1 = |E1| (V/m), source = ρs (C/m²).  kind 'H': F1 = |H1| (A/m), source = Js_z (A/m).
    theta1 is the angle of the medium-1 field from the normal n̂₂ (0° = normal, 90° = tangential)."""
    if kind not in ("E", "H"):
        raise ValueError("kind must be 'E' or 'H'")
    if min(eps1, eps2, mu1, mu2) <= 0:
        raise ValueError("relative ε and μ must be positive")
    th = np.radians(theta1_deg)
    t1, n1 = F1 * np.sin(th), F1 * np.cos(th)
    D = Derivation()
    if kind == "E":
        m1, m2, c1, c2 = EPS0 * eps1, EPS0 * eps2, eps1, eps2
        D.step("Field in medium 1", rf"E_{{1t}}=|E_1|\sin\theta_1={fmt(t1)},\quad E_{{1n}}=|E_1|\cos\theta_1={fmt(n1)}", [t1, n1], "V/m")
        if pec:
            t2 = n2 = 0.0
            rs = m1 * n1
            D.step("Perfect conductor (medium 2)", r"\mathbf E_2=0\ \Rightarrow\ E_{1t}=0,\quad \rho_s=\hat n_2\cdot\mathbf D_1=\varepsilon_1E_{1n}",
                   rs, "C/m²", note="a tangential E at a perfect conductor is impossible" if abs(t1) > 1e-12 * F1 else "")
            source = rs
        else:
            t2 = t1
            n2 = (m1 * n1 - source) / m2
            D.step("Tangential E is continuous", rf"\hat n_2\times(\mathbf E_1-\mathbf E_2)=0\ \Rightarrow\ E_{{2t}}=E_{{1t}}={fmt(t2)}", t2, "V/m")
            D.step("Normal D jumps by ρs", rf"\hat n_2\cdot(\mathbf D_1-\mathbf D_2)=\rho_s\ \Rightarrow\ E_{{2n}}=\frac{{\varepsilon_1E_{{1n}}-\rho_s}}{{\varepsilon_2}}={fmt(n2)}", n2, "V/m")
        flux1, flux2 = m1 * n1, m2 * n2
        names = ("E", "D", "ε", "ρ_s", "V/m", "C/m²")
    else:
        m1, m2, c1, c2 = MU0 * mu1, MU0 * mu2, mu1, mu2
        D.step("Field in medium 1", rf"H_{{1t}}=|H_1|\sin\theta_1={fmt(t1)},\quad H_{{1n}}=|H_1|\cos\theta_1={fmt(n1)}", [t1, n1], "A/m")
        if pec:
            t2 = n2 = 0.0
            source = -t1
            D.step("Perfect conductor (medium 2)", r"\mathbf B_2=0\ \Rightarrow\ B_{1n}=0,\quad \mathbf J_s=\hat n_2\times\mathbf H_1\ \Rightarrow\ J_{sz}=-H_{1x}",
                   source, "A/m", note="a normal B at a perfect conductor is impossible" if abs(n1) > 1e-12 * F1 else "")
        else:
            n2 = m1 * n1 / m2
            t2 = t1 + source
            D.step("Normal B is continuous", rf"\hat n_2\cdot(\mathbf B_1-\mathbf B_2)=0\ \Rightarrow\ H_{{2n}}=\frac{{\mu_1}}{{\mu_2}}H_{{1n}}={fmt(n2)}", n2, "A/m")
            D.step("Tangential H jumps by Js", rf"\hat n_2\times(\mathbf H_1-\mathbf H_2)=\mathbf J_s\ \Rightarrow\ H_{{2x}}=H_{{1x}}+J_{{sz}}={fmt(t2)}", t2, "A/m",
                   note="Js is taken along +z (out of the page); ŷ × x̂ = −ẑ gives the sign")
        flux1, flux2 = m1 * n1, m2 * n2
        names = ("H", "B", "μ", "J_s", "A/m", "T")
    F2 = float(np.hypot(t2, n2))
    th2 = float(np.degrees(np.arctan2(abs(t2), n2))) if F2 > 0 else 0.0
    D.step("Field in medium 2", rf"|{names[0]}_2|={fmt(F2)},\quad\theta_2={th2:.3f}^\circ", F2, names[4])
    w1, w2 = 0.5 * m1 * F1 ** 2, 0.5 * m2 * F2 ** 2
    D.step("Energy density", rf"w=\tfrac12{names[2]}|{names[0]}|^2:\ w_1={fmt(w1)},\ w_2={fmt(w2)}", [w1, w2], "J/m³")

    # --- checks: the integral forms on a thin loop / pill-box straddling y = 0
    w, A = 1.0, 1.0
    tt, ww = np.polynomial.legendre.leggauss(8)
    tang = lambda side: (t1 if side > 0 else t2)
    circ = w * tang(+1) - w * tang(-1)           # top edge → +x, bottom edge → −x; sides vanish as h → 0
    num_circ = np.sum(ww * 0.5 * w * tang(+1)) - np.sum(ww * 0.5 * w * tang(-1))
    expected = 0.0 if kind == "E" else -source * w
    if not pec or kind == "H":
        D.check(rf"\oint\mathbf {names[0]}\cdot d\mathbf l \text{{ (thin loop across interface)}}", expected, num_circ, 1e-12,
                "Gauss–Legendre line integral, height → 0" + (", = −J_s·w (enclosed current, sign from loop sense)" if kind == "H" else ""),
                scale=max(abs(t1), 1e-30) * w)
    pill = (flux1 - flux2) * A
    D.check(rf"\oint\mathbf {names[1]}\cdot d\mathbf s \text{{ (thin pill-box)}}", source * A if kind == "E" else 0.0, pill, 1e-12,
            "flux out of top − flux into bottom", scale=max(abs(flux1), 1e-30) * A)
    if not pec and source == 0 and 0 < theta1_deg < 90:
        D.check(rf"\tan\theta_1/\tan\theta_2={names[2]}_1/{names[2]}_2 \text{{ (refraction of field lines)}}",
                c1 / c2, np.tan(th) / np.tan(np.radians(th2)), 1e-10, "derived from the two conditions")
    return {**D.out(F1=[t1, n1], F2=[t2, n2], F2_mag=F2, theta2_deg=th2, flux=[flux1, flux2], source=source, w=[w1, w2]),
            "kind": kind, "pec": pec}


def faraday(mode="motional", B0=0.1, f=50.0, w=0.1, l=0.2, N=1, R=1.0, alpha_deg=0.0, n=400):
    """mode 'transformer': stationary loop w×l, B = B0 cos(ωt) at angle α to the loop normal.
       mode 'motional'   : loop rotates about its x-side axis at Ω = 2πf in static B0 ẑ (an AC generator)."""
    if mode not in ("transformer", "motional"):
        raise ValueError("mode must be transformer or motional")
    if min(w, l, f, N, R) <= 0:
        raise ValueError("w, l, f, N, R must be positive")
    W = 2 * np.pi * f
    A = w * l
    D = Derivation()
    T = 1 / f
    t = np.linspace(0, 2 * T, n)
    ca = np.cos(np.radians(alpha_deg))
    D.step("Faraday's law", r"V_{emf}=-N\frac{d\Phi}{dt},\qquad \Phi=\int_S\mathbf B\cdot d\mathbf s")
    if mode == "transformer":
        Phi = B0 * A * ca * np.cos(W * t)
        emf = N * B0 * A * ca * W * np.sin(W * t)
        D.step("Flux", rf"\Phi(t)=B_0A\cos\alpha\cos\omega t,\quad A=wl={fmt(A)}", A, "m²")
        D.step("Transformer EMF", rf"V_{{emf}}=NB_0A\omega\cos\alpha\,\sin\omega t,\quad \hat V={fmt(N * B0 * A * W * ca)}", N * B0 * A * W * ca, "V")
    else:
        Phi = B0 * A * np.cos(W * t)
        emf = N * B0 * A * W * np.sin(W * t)
        D.step("Flux through rotating loop", rf"\Phi(t)=B_0A\cos\Omega t,\quad A={fmt(A)}", A, "m²")
        D.step("Motional EMF", rf"V_{{emf}}=\oint(\mathbf u\times\mathbf B)\cdot d\mathbf l=NB_0A\Omega\sin\Omega t,\quad\hat V={fmt(N * B0 * A * W)}", N * B0 * A * W, "V")
    Vpk = float(np.max(np.abs(emf)))
    I = emf / R
    P = float(np.mean(emf[: n // 2] ** 2) / R) if n > 2 else 0.0
    D.step("Current and average power", rf"I=V_{{emf}}/R,\quad P_{{av}}=\hat V^2/2R={fmt(Vpk ** 2 / (2 * R))}", Vpk ** 2 / (2 * R), "W",
           note="loop self-inductance neglected")

    # --- checks
    tf = np.linspace(0, 2 * T, 20001)
    Phif = (B0 * A * ca if mode == "transformer" else B0 * A) * np.cos(W * tf)
    emf_num = -N * np.gradient(Phif, tf, edge_order=2)
    emf_ref = N * (B0 * A * ca if mode == "transformer" else B0 * A) * W * np.sin(W * tf)
    D.check(r"V_{emf}=-N\,d\Phi/dt \text{ (numerical derivative)}", 0.0, np.abs(emf_num - emf_ref).max(), 1e-6,
            "finite differences on 20 001 samples", scale=max(np.abs(emf_ref).max(), 1e-30))
    if mode == "motional":
        # independent route: integrate (u × B)·dl around the moving loop
        ts = np.linspace(0, T, 13)[1:-1]
        gl, gw = np.polynomial.legendre.leggauss(6)
        lineint = []
        for tk in ts:
            e1 = np.array([1.0, 0, 0]); e2 = np.array([0, np.cos(W * tk), np.sin(W * tk)])
            cs = [(-w / 2, -l / 2), (w / 2, -l / 2), (w / 2, l / 2), (-w / 2, l / 2), (-w / 2, -l / 2)]
            s = 0.0
            for (u0, v0), (u1, v1) in zip(cs[:-1], cs[1:]):
                for g, gwt in zip(gl, gw):
                    uu, vv = (u0 + u1) / 2 + g * (u1 - u0) / 2, (v0 + v1) / 2 + g * (v1 - v0) / 2
                    p = uu * e1 + vv * e2
                    vel = W * np.cross(e1, p)
                    dl = ((u1 - u0) * e1 + (v1 - v0) * e2) / 2
                    s += gwt * np.dot(np.cross(vel, [0, 0, B0]), dl)
            lineint.append(N * s)
        D.check(r"\oint(\mathbf u\times\mathbf B)\cdot d\mathbf l=-N\,d\Phi/dt \text{ (motional = flux rule)}", 0.0,
                np.abs(np.array(lineint) - N * B0 * A * W * np.sin(W * ts)).max(), 1e-10,
                "Gauss–Legendre line integral at 11 instants", scale=N * B0 * A * W)
    D.check(r"\hat V=N\,\omega\,\hat\Phi", N * W * np.abs(Phi).max(), Vpk, 2e-4, "peak of sampled curves (sampling error)")
    return {**D.out(A=A, V_peak=Vpk, I_peak=Vpk / R, P_av=Vpk ** 2 / (2 * R), omega=W),
            "t": t.tolist(), "Phi": (N * Phi).tolist(), "emf": emf.tolist(), "I": I.tolist()}


def currents(eps_r=81.0, sigma=4.0, f=1e6, E0=1.0, n=200):
    if eps_r <= 0 or sigma < 0 or f <= 0:
        raise ValueError("need εr > 0, σ ≥ 0, f > 0")
    eps = EPS0 * eps_r
    w = 2 * np.pi * f
    D = Derivation()
    D.step("Ampère–Maxwell", r"\nabla\times\mathbf H=\underbrace{\sigma\mathbf E}_{\mathbf J_c}+\underbrace{j\omega\varepsilon\mathbf E}_{\mathbf J_d}")
    Jc, Jd = sigma * E0, w * eps * E0
    D.step("Conduction current density", rf"|J_c|=\sigma E_0={fmt(Jc)}", Jc, "A/m²")
    D.step("Displacement current density", rf"|J_d|=\omega\varepsilon E_0={fmt(Jd)}", Jd, "A/m²", note="90° ahead of Jc")
    D.step("Ratio", rf"|J_c|/|J_d|=\sigma/\omega\varepsilon={fmt(Jc / Jd)}", Jc / Jd, "")
    fc = sigma / (2 * np.pi * eps) if sigma > 0 else 0.0
    D.step("Crossover frequency", rf"f_c=\frac{{\sigma}}{{2\pi\varepsilon}}={fmt(fc)}", fc, "Hz", note="below f_c the medium behaves as a conductor")
    tau = eps / sigma if sigma > 0 else np.inf
    D.step("Charge relaxation time", rf"\rho_v(t)=\rho_{{v0}}e^{{-t/\tau_r}},\ \tau_r=\varepsilon/\sigma={fmt(tau)}", tau, "s",
           note="from continuity ∇·J = −∂ρ/∂t with J = σE and Gauss ∇·E = ρ/ε")
    if sigma > 0:
        sol = integrate.solve_ivp(lambda t, y: -sigma / eps * y, (0, 5 * tau), [1.0], rtol=1e-11, atol=1e-14, dense_output=True)
        D.check(r"\rho_v(\tau_r)/\rho_{v0}=e^{-1} \text{ (ODE } \dot\rho=-\sigma\rho/\varepsilon)", np.exp(-1), sol.sol(tau)[0], 1e-8, "scipy solve_ivp (RK45)")
        D.check(r"|J_c|=|J_d| \text{ at } f_c", 1.0, sigma / (2 * np.pi * fc * eps), 1e-12, "substitution")
    fs = np.logspace(np.log10(max(fc, 1) / 1e4), np.log10(max(fc, 1) * 1e4), n) if sigma > 0 else np.logspace(0, 12, n)
    return {**D.out(Jc=Jc, Jd=Jd, ratio=Jc / Jd, fc=fc, tau=tau), "sweep": {"f": fs.tolist(), "ratio": (sigma / (2 * np.pi * fs * eps)).tolist()}}
