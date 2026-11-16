"""Rectangular waveguides, dipole antennas and linear arrays (Ulaby ch. 8–10, Cheng ch. 10–11)."""
import numpy as np
from scipy import integrate, special
from .constants import C0, EPS0, MU0
from .derivation import Derivation, fmt


# ---------------------------------------------------------------- rectangular waveguide
def waveguide(a=22.86e-3, b=10.16e-3, eps_r=1.0, mu_r=1.0, f=10e9, mode="TE", m=1, n=0, grid=41):
    if a <= 0 or b <= 0 or b > a or f <= 0:
        raise ValueError("need a ≥ b > 0 and f > 0")
    if mode not in ("TE", "TM") or m < 0 or n < 0 or m + n == 0 or (mode == "TM" and (m == 0 or n == 0)):
        raise ValueError("TE needs m+n ≥ 1; TM needs m ≥ 1 and n ≥ 1")
    D = Derivation()
    u = C0 / np.sqrt(eps_r * mu_r)
    eta = np.sqrt(MU0 * mu_r / (EPS0 * eps_r))
    fc = lambda mm, nn: u / 2 * np.sqrt((mm / a) ** 2 + (nn / b) ** 2)
    f0 = fc(m, n)
    D.step("Cut-off frequency", rf"f_{{{m}{n}}}=\frac{{u}}{{2}}\sqrt{{\left(\frac{{m}}{{a}}\right)^2+\left(\frac{{n}}{{b}}\right)^2}}={fmt(f0)}", f0, "Hz")
    modes = []
    for mm in range(0, 6):
        for nn in range(0, 6):
            for kind in ("TE", "TM"):
                if mm + nn == 0 or (kind == "TM" and (mm == 0 or nn == 0)):
                    continue
                modes.append({"mode": f"{kind}{mm}{nn}", "fc": fc(mm, nn)})
    modes.sort(key=lambda x: x["fc"])
    modes = modes[:10]
    prop = f > f0
    k = 2 * np.pi * f / u
    kc = 2 * np.pi * f0 / u
    if prop:
        beta = k * np.sqrt(1 - (f0 / f) ** 2)
        D.step("Phase constant", rf"\beta=k\sqrt{{1-(f_c/f)^2}}={fmt(beta)}", beta, "rad/m")
        lg = 2 * np.pi / beta
        up, ug = u / np.sqrt(1 - (f0 / f) ** 2), u * np.sqrt(1 - (f0 / f) ** 2)
        D.step("Guide wavelength, velocities", rf"\lambda_g={fmt(lg)},\ u_p={fmt(up)},\ u_g={fmt(ug)}", [lg, up, ug], "m, m/s",
               note="u_p > u > u_g; energy travels at u_g")
        Zw = eta / np.sqrt(1 - (f0 / f) ** 2) if mode == "TE" else eta * np.sqrt(1 - (f0 / f) ** 2)
        D.step("Wave impedance", rf"Z_{{{mode}}}={'\\eta/\\sqrt{1-(f_c/f)^2}' if mode == 'TE' else '\\eta\\sqrt{1-(f_c/f)^2}'}={fmt(Zw)}", Zw, "Ω")
        alpha = 0.0
    else:
        alpha = kc * np.sqrt(1 - (f / f0) ** 2)
        beta = lg = up = ug = Zw = None
        D.step("Below cut-off (evanescent)", rf"\alpha=k_c\sqrt{{1-(f/f_c)^2}}={fmt(alpha)}", alpha, "Np/m",
               note=f"field decays by 1/e every {1 / alpha:.3g} m — no power is carried")
    others = [x for x in modes if x["fc"] < f]
    D.step("Propagating modes at f", ", ".join(x["mode"] for x in others) or r"\text{none}", len(others), "",
           note="single-mode band of the guide is between the first two cut-offs")
    # cross-section field (transverse E) for the chosen mode
    x, y = np.linspace(0, a, grid), np.linspace(0, b, max(int(grid * b / a), 11))
    X, Y = np.meshgrid(x, y)
    kx, ky = m * np.pi / a, n * np.pi / b
    if mode == "TE":   # Hz ∝ cos kx x cos ky y ; Et ∝ ẑ × ∇t Hz
        psi = np.cos(kx * X) * np.cos(ky * Y)
        Ex, Ey = ky * np.cos(kx * X) * np.sin(ky * Y), -kx * np.sin(kx * X) * np.cos(ky * Y)
    else:              # Ez ∝ sin kx x sin ky y ; Et ∝ ∇t Ez
        psi = np.sin(kx * X) * np.sin(ky * Y)
        Ex, Ey = kx * np.cos(kx * X) * np.sin(ky * Y), ky * np.sin(kx * X) * np.cos(ky * Y)
    # checks
    hx, hy = x[1] - x[0], y[1] - y[0]
    lap = (psi[1:-1, 2:] - 2 * psi[1:-1, 1:-1] + psi[1:-1, :-2]) / hx ** 2 + (psi[2:, 1:-1] - 2 * psi[1:-1, 1:-1] + psi[:-2, 1:-1]) / hy ** 2
    res = np.abs(lap + kc ** 2 * psi[1:-1, 1:-1]).max() / (kc ** 2)
    D.check(r"\nabla_t^2\psi+k_c^2\psi=0 \text{ (transverse Helmholtz)}", 0.0, res, (kc * max(hx, hy)) ** 2 / 4, "5-point Laplacian on the cross-section grid")
    Et_wall = max(np.abs(Ex[0, :]).max(), np.abs(Ex[-1, :]).max(), np.abs(Ey[:, 0]).max(), np.abs(Ey[:, -1]).max())
    D.check(r"E_{tan}=0 \text{ on the conducting walls}", 0.0, Et_wall, 1e-12, "tangential E at y = 0, b and x = 0, a",
            scale=max(np.abs(Ex).max(), np.abs(Ey).max(), 1e-300))
    if prop:
        D.check(r"u_p\,u_g=u^2", u * u, up * ug, 1e-12, "dispersion relation")
        D.check(r"\beta^2+k_c^2=k^2", k * k, beta ** 2 + kc ** 2, 1e-12, "separation of variables")
    fs = np.linspace(0.5 * modes[0]["fc"], 2.6 * modes[0]["fc"], 300)
    disp = {mm["mode"]: [float(2 * np.pi * ff / u * np.sqrt(1 - (mm["fc"] / ff) ** 2)) if ff > mm["fc"] else None for ff in fs] for mm in modes[:5]}
    step = max(grid // 12, 1)
    return {**D.out(fc=f0, propagating=prop, beta=beta, alpha=alpha, lambda_g=lg, up=up, ug=ug, Z=Zw, n_modes=len(others)),
            "modes": modes, "dispersion": {"f": fs.tolist(), "beta": disp},
            "field": {"x": x.tolist(), "y": y.tolist(), "mag": np.hypot(Ex, Ey).tolist(),
                      "qx": X[::step, ::step].ravel().tolist(), "qy": Y[::step, ::step].ravel().tolist(),
                      "qu": Ex[::step, ::step].ravel().tolist(), "qv": Ey[::step, ::step].ravel().tolist()}}


# ---------------------------------------------------------------- dipole antennas
def dipole(length_lambda=0.5, I0=1.0, f=100e6, n=721):
    """Centre-fed thin dipole of total length l (in wavelengths), sinusoidal current."""
    if not 0 < length_lambda <= 3:
        raise ValueError("0 < l/λ ≤ 3")
    D = Derivation()
    lam = C0 / f
    kl2 = np.pi * length_lambda  # k l / 2
    th = np.linspace(1e-6, np.pi - 1e-6, n)
    short = length_lambda < 0.1
    if short:
        F = np.sin(th) ** 2
        D.step("Short (Hertzian) dipole pattern", r"F(\theta)=\sin^2\theta")
        Rrad = 80 * np.pi ** 2 * length_lambda ** 2 / 4   # triangular current on a short dipole: ¼ of the uniform-current value
        D.step("Radiation resistance", rf"R_{{rad}}=20\pi^2(l/\lambda)^2={fmt(Rrad)}", Rrad, "Ω", note="short dipole with triangular current distribution")
    else:
        F = ((np.cos(kl2 * np.cos(th)) - np.cos(kl2)) / np.sin(th)) ** 2
        D.step("Pattern (sinusoidal current)", r"F(\theta)\propto\left[\frac{\cos(\frac{kl}{2}\cos\theta)-\cos\frac{kl}{2}}{\sin\theta}\right]^2")
        Pint = integrate.quad(lambda t: ((np.cos(kl2 * np.cos(t)) - np.cos(kl2)) ** 2 / np.sin(t)), 1e-9, np.pi - 1e-9, limit=400)[0]
        Rrad = 60 * Pint
        D.step("Radiation resistance", rf"R_{{rad}}=60\int_0^\pi\frac{{[\cos(\frac{{kl}}{{2}}\cos\theta)-\cos\frac{{kl}}{{2}}]^2}}{{\sin\theta}}d\theta={fmt(Rrad)}", Rrad, "Ω",
               note="referred to the current maximum")
    Fn = F / F.max()
    integral = integrate.simpson(Fn * np.sin(th), x=th) * 2 * np.pi
    Dmax = 4 * np.pi / integral
    D.step("Directivity", rf"D=\frac{{4\pi}}{{\iint F_n\,d\Omega}}={fmt(Dmax)}\ ({fmt(10 * np.log10(Dmax))}\ \text{{dBi}})", Dmax, "")
    Prad = 0.5 * I0 ** 2 * Rrad
    D.step("Radiated power", rf"P_{{rad}}=\tfrac12I_0^2R_{{rad}}={fmt(Prad)}", Prad, "W")
    half = th[Fn >= 0.5]
    hpbw = np.degrees(half.max() - half.min()) if len(half) else None
    # checks
    if short:
        D.check(r"D=1.5 \text{ (short dipole)}", 1.5, Dmax, 1e-6, "Simpson integration of the pattern")
    if abs(length_lambda - 0.5) < 1e-12:
        Cin = np.euler_gamma + np.log(2 * np.pi) - special.sici(2 * np.pi)[1]
        D.check(r"R_{rad}=30\,\mathrm{Cin}(2\pi)\approx73.1\,\Omega", 30 * Cin, Rrad, 1e-8, "closed form with the cosine integral")
        D.check(r"D=\frac{120}{R_{rad}}\approx1.64", 120 / (30 * Cin), Dmax, 1e-5, "closed form vs numerical pattern integral")
    if not short:
        D.check(r"D=\frac{120\,F_{max}}{R_{rad}} \text{ (power-balance route)}", 120 * F.max() / Rrad, Dmax, 1e-4, "η₀/π relation between pattern and R_rad")
    return {**D.out(R_rad=Rrad, D=Dmax, D_dBi=10 * np.log10(Dmax), P_rad=Prad, hpbw_deg=hpbw, wavelength=lam, length=length_lambda * lam),
            "pattern": {"theta_deg": np.degrees(th).tolist(), "F": Fn.tolist()}}


# ---------------------------------------------------------------- uniform linear array
def array(N=8, d_lambda=0.5, delta_deg=0.0, n=1441):
    """N isotropic elements along z, spacing d, progressive phase δ (multiply by the element pattern for real elements)."""
    if not 1 <= N <= 64 or d_lambda <= 0:
        raise ValueError("1 ≤ N ≤ 64, d > 0")
    D = Derivation()
    th = np.linspace(0, np.pi, n)
    kd = 2 * np.pi * d_lambda
    dl = np.radians(delta_deg)
    psi = kd * np.cos(th) + dl
    with np.errstate(invalid="ignore", divide="ignore"):
        AF = np.where(np.abs(np.sin(psi / 2)) < 1e-12, 1.0, np.sin(N * psi / 2) / (N * np.sin(psi / 2)))
    D.step("Array factor", r"AF(\theta)=\frac{\sin(N\psi/2)}{N\sin(\psi/2)},\quad\psi=kd\cos\theta+\delta")
    # direct sum (independent)
    direct = np.abs(np.exp(1j * np.outer(psi, np.arange(N))).sum(1)) / N
    P = AF ** 2
    c0 = -dl / kd
    if abs(c0) <= 1:
        th0 = np.degrees(np.arccos(c0))
        D.step("Main-beam direction", rf"\cos\theta_0=-\frac{{\delta}}{{kd}}\ \Rightarrow\ \theta_0={th0:.3f}^\circ", th0, "°", note="θ measured from the array axis")
    else:
        th0 = None
        D.step("Main beam", r"|\delta|>kd:\ \text{no visible main beam}")
    integral = integrate.simpson(P * np.sin(th), x=th) * 2 * np.pi
    Dmax = 4 * np.pi * P.max() / integral
    D.step("Directivity", rf"D={fmt(Dmax)}\ ({fmt(10 * np.log10(Dmax))}\ \text{{dBi}})", Dmax, "")
    grating = d_lambda >= 1 / (1 + abs(c0)) if abs(c0) <= 1 else False
    if grating:
        D.step("Grating lobes", rf"d/\lambda\ge\frac{{1}}{{1+|\cos\theta_0|}}", note="extra full-strength beams appear")
    D.check(r"\text{closed-form }AF=\left|\tfrac1N\sum e^{jn\psi}\right|", 0.0, np.abs(np.abs(AF) - direct).max(), 1e-10, "direct phasor sum over all elements")
    if th0 is not None:
        af0 = float(np.abs(np.exp(1j * (kd * np.cos(np.radians(th0)) + dl) * np.arange(N)).sum()) / N)
        D.check(r"|AF(\theta_0)|=1 \text{ (all elements in phase)}", 1.0, af0, 1e-12, "direct phasor sum at the predicted angle")
        D.check(r"\text{sampled pattern peaks at }\theta_0", th0, float(np.degrees(th[int(np.argmax(np.abs(AF)))])), 0.01, "argmax on a 0.125° grid",
                scale=180.0)
    if abs(delta_deg) < 1e-12 and N * d_lambda >= 2 and d_lambda < 1:
        D.check(r"\text{broadside: }D\approx2Nd/\lambda", 2 * N * d_lambda, Dmax, 0.15, "long-array approximation (±15 %)")
    return {**D.out(D=Dmax, D_dBi=10 * np.log10(Dmax), theta0=th0, grating=bool(grating)),
            "pattern": {"theta_deg": np.degrees(th).tolist(), "AF": np.abs(AF).tolist()}}
