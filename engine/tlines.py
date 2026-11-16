"""Lossless transmission lines (Ulaby ch. 2, Cheng ch. 9).

Load at z = 0, generator at z = −l, d = distance from the load toward the generator.
    Γ_L = (Z_L − Z0)/(Z_L + Z0),  Γ(d) = Γ_L e^{−j2βd}
    Z_in(d) = Z0 (Z_L + jZ0 tan βd)/(Z0 + jZ_L tan βd)
"""
import numpy as np
from .constants import C0
from .derivation import Derivation, fmt


def _zin(Z0, ZL, bd):
    t = np.tan(bd)
    if np.isinf(ZL):
        return -1j * Z0 / t
    return Z0 * (ZL + 1j * Z0 * t) / (Z0 + 1j * ZL * t)


def _abcd(Z0, bd, ZL):
    """Independent route: ABCD matrix of a line section, Zin = (A ZL + B)/(C ZL + D)."""
    A, B, Cc, Dd = np.cos(bd), 1j * Z0 * np.sin(bd), 1j * np.sin(bd) / Z0, np.cos(bd)
    return (A * ZL + B) / (Cc * ZL + Dd)


def line(Z0=50.0, RL=100.0, XL=50.0, f=1e9, length=0.3, vf=1.0, Vg=10.0, Zg=50.0, n=400):
    if Z0 <= 0 or f <= 0 or length <= 0 or not 0 < vf <= 1 or RL < 0:
        raise ValueError("need Z0 > 0, f > 0, l > 0, 0 < vf ≤ 1, R_L ≥ 0")
    D = Derivation()
    ZL = complex(RL, XL)
    up = vf * C0
    lam = up / f
    beta = 2 * np.pi / lam
    D.step("Phase constant", rf"\beta=\frac{{2\pi f}}{{u_p}}=\frac{{2\pi}}{{\lambda}},\ \lambda={fmt(lam)}", beta, "rad/m",
           note=f"u_p = {vf:g}·c; line length l = {length / lam:.4g} λ")
    GL = (ZL - Z0) / (ZL + Z0)
    D.step("Load reflection coefficient", rf"\Gamma_L=\frac{{Z_L-Z_0}}{{Z_L+Z_0}}={fmt(abs(GL))}\angle{np.degrees(np.angle(GL)):.2f}^\circ", GL, "")
    S = (1 + abs(GL)) / (1 - abs(GL)) if abs(GL) < 1 else np.inf
    D.step("VSWR", rf"S=\frac{{1+|\Gamma|}}{{1-|\Gamma|}}={fmt(S)}", S, "")
    RLdB = -20 * np.log10(abs(GL)) if abs(GL) > 0 else np.inf
    D.step("Return loss", rf"RL=-20\log_{{10}}|\Gamma|={fmt(RLdB)}", RLdB, "dB")
    th = np.angle(GL)
    dmax = (th * lam / (4 * np.pi)) % (lam / 2)
    dmin = (dmax + lam / 4) % (lam / 2)
    D.step("Voltage maxima / minima", rf"d_{{max}}=\frac{{\theta_r\lambda}}{{4\pi}}={fmt(dmax)},\ \ d_{{min}}=d_{{max}}\pm\frac{{\lambda}}{{4}}={fmt(dmin)}", [dmax, dmin], "m")
    Zin = _zin(Z0, ZL, beta * length)
    D.step("Input impedance", rf"Z_{{in}}=Z_0\frac{{Z_L+jZ_0\tan\beta l}}{{Z_0+jZ_L\tan\beta l}}={fmt(Zin.real)}{'+' if Zin.imag >= 0 else '-'}j{fmt(abs(Zin.imag))}", Zin, "Ω")
    # generator and power
    Vin = Vg * Zin / (Zin + Zg)
    Iin = Vin / Zin
    Pin = 0.5 * (Vin * np.conj(Iin)).real
    # V(d) = V0+ (e^{jβd} + Γ_L e^{−jβd}); fix V0+ from V(l) = Vin
    V0p = Vin / (np.exp(1j * beta * length) + GL * np.exp(-1j * beta * length))
    d = np.linspace(0, length, n)
    V = V0p * (np.exp(1j * beta * d) + GL * np.exp(-1j * beta * d))
    I = V0p / Z0 * (np.exp(1j * beta * d) - GL * np.exp(-1j * beta * d))
    PL = 0.5 * (V[0] * np.conj(I[0])).real
    D.step("Power delivered", rf"P_{{in}}=\tfrac12\mathrm{{Re}}(V_{{in}}I_{{in}}^*)={fmt(Pin)},\quad P_L=\frac{{|V_0^+|^2}}{{2Z_0}}(1-|\Gamma_L|^2)={fmt(PL)}", [Pin, PL], "W")
    # matching
    match = {}
    if abs(GL) > 1e-12 and np.isfinite(S):
        Rmin = Z0 / S
        ZT = np.sqrt(Z0 * Rmin)
        match["quarter_wave"] = {"d": dmin, "Z_T": ZT, "R_seen": Rmin}
        D.step("Quarter-wave transformer", rf"\text{{at }}d_{{min}}:\ Z=Z_0/S={fmt(Rmin)}\ \Rightarrow\ Z_T=\sqrt{{Z_0Z_0/S}}={fmt(ZT)}", ZT, "Ω",
               note="insert a λ/4 section of impedance Z_T at the voltage minimum")
        sols = []
        if abs(RL - Z0) > 1e-12:
            rt = np.sqrt(RL * ((Z0 - RL) ** 2 + XL ** 2) / Z0)
            ts = [(XL + rt) / (RL - Z0), (XL - rt) / (RL - Z0)]
        else:
            ts = [-XL / (2 * Z0)]
        for t in ts:
            dd = (np.arctan(t) / (2 * np.pi)) % 0.5 * lam
            Yd = 1 / _zin(Z0, ZL, beta * dd)
            B = Yd.imag
            ls = (np.arctan(1 / (B * Z0)) / (2 * np.pi)) % 0.5 * lam if abs(B) > 1e-15 else lam / 4
            sols.append({"d": dd, "B": B, "l_stub": ls})
        match["stub"] = sols
        D.step("Single shunt stub (short-circuited)", r"\tan\beta d=\frac{X_L\pm\sqrt{R_L[(Z_0-R_L)^2+X_L^2]/Z_0}}{R_L-Z_0},\quad \beta l_s=\tan^{-1}\frac{Y_0}{B}",
               [s["d"] for s in sols], "m", note="; ".join(f"d = {s['d']:.4g} m, stub = {s['l_stub']:.4g} m" for s in sols))
    # checks
    D.check(r"Z_{in}\text{ (formula)}=Z_{in}\text{ (ABCD cascade)}", _abcd(Z0, beta * length, ZL), Zin, 1e-10, "transmission-matrix method", scale=abs(Zin) + Z0)
    Gd = GL * np.exp(-2j * beta * length)
    D.check(r"Z_{in}=Z_0\frac{1+\Gamma(l)}{1-\Gamma(l)}", Z0 * (1 + Gd) / (1 - Gd) if abs(1 - Gd) > 1e-15 else np.inf, Zin, 1e-10, "rotation of Γ on the Smith chart", scale=abs(Zin) + Z0)
    D.check(r"V(l)/I(l)=Z_{in}", Zin, V[-1] / I[-1], 1e-10, "from the standing-wave arrays", scale=abs(Zin) + Z0)
    Pav = abs(Vg) ** 2 / (8 * max(np.real(Zg), 1e-12))
    D.check(r"P_{in}=P_L \text{ (lossless line)}", Pin, PL, 1e-10, "power conservation, error relative to available power", scale=Pav)
    if np.isfinite(S) and abs(GL) > 1e-9:
        dd = np.linspace(0, lam / 2, 20001)
        Vd = np.abs(np.exp(1j * beta * dd) + GL * np.exp(-1j * beta * dd))
        D.check(r"|V|_{max}/|V|_{min}=S", S, Vd.max() / Vd.min(), max(1e-6, 5e-8 * S * S), "20 001-point pattern over λ/2")
    if match.get("quarter_wave"):
        q = match["quarter_wave"]
        Zseen = _zin(Z0, ZL, beta * q["d"])
        Zq = _zin(q["Z_T"], Zseen, np.pi / 2)
        D.check(r"\text{quarter-wave match: }Z_{in}=Z_0", Z0, Zq, 1e-8, "Z_T line of λ/4 on the impedance at d_min", scale=Z0)
    for k, s in enumerate(match.get("stub", [])):
        Ytot = 1 / _zin(Z0, ZL, beta * s["d"]) + 1 / _zin(Z0, 0.0, beta * s["l_stub"])
        D.check(rf"\text{{stub solution {k + 1}: }}Y(d)+Y_{{stub}}=Y_0", 1 / Z0, Ytot, 1e-8, "line formulas for both branches", scale=1 / Z0)
    # Smith-chart locus from load to input
    dl = np.linspace(0, length, 200)
    G_loc = GL * np.exp(-2j * beta * dl)
    return {**D.out(Gamma_L=GL, Gamma_mag=abs(GL), Gamma_deg=np.degrees(th), S=S, return_loss_dB=RLdB, Zin=Zin, lambda_=lam,
                    l_over_lambda=length / lam, d_max=dmax, d_min=dmin, P_in=Pin, P_L=PL),
            "match": match, "profile": {"d": d.tolist(), "V": np.abs(V).tolist(), "I": np.abs(I).tolist()},
            "smith": {"re": G_loc.real.tolist(), "im": G_loc.imag.tolist()}}
