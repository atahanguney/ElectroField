"""1-D, 2-D and 3-D wave propagation compared (Ulaby ch. 1-2, 7, 9; Cheng ch. 8).

Same medium, same frequency, three source geometries:
  1-D  plane wave / transmission line   ψ = e^{-jkz}                 |ψ| ∝ 1          (no spreading)
  2-D  infinite line source (cylindrical) ψ = H0^(2)(kρ)               |ψ| ∝ 1/√ρ
  3-D  point source (spherical)           ψ = e^{-jkR}/R               |ψ| ∝ 1/R
k = β − jα is complex in a lossy medium, so absorption e^{-αr} multiplies every case.
Each ψ is an exact outgoing solution of the Helmholtz equation in 1, 2 or 3 dimensions.
"""
import numpy as np
from scipy import special
from . import waves
from .derivation import Derivation, fmt

DIMS = ("1D", "2D", "3D")


def _k(f, eps_r, mu_r, sigma):
    c = waves.constants(f, eps_r, mu_r, sigma)
    a, b = float(c["alpha"]), float(c["beta"])
    return b - 1j * a, a, b, c


def psi(dim, k, r):
    r = np.asarray(r, float)
    if dim == "1D":
        return np.exp(-1j * k * r)
    if dim == "2D":
        return special.hankel2(0, k * r)
    return np.exp(-1j * k * r) / r


def _radial_residual(dim, k, r0, h):
    """FD residual of the radial Helmholtz operator, relative to k²|ψ|."""
    p = lambda x: complex(psi(dim, k, np.array(x)))
    d1 = (p(r0 + h) - p(r0 - h)) / (2 * h)
    d2 = (p(r0 + h) - 2 * p(r0) + p(r0 - h)) / h ** 2
    n = {"1D": 0, "2D": 1, "3D": 2}[dim]           # (1/r^n) d/dr (r^n dψ/dr) = ψ'' + (n/r) ψ'
    res = d2 + n / r0 * d1 + k * k * p(r0)
    return abs(res) / abs(k * k * p(r0))


def compare(f=1e9, eps_r=1.0, mu_r=1.0, sigma=0.0, r_max_lambda=6.0, n=500, grid=121):
    if f <= 0 or eps_r <= 0 or mu_r <= 0 or sigma < 0 or not 0.5 <= r_max_lambda <= 50:
        raise ValueError("need f > 0, εr, μr > 0, σ ≥ 0 and 0.5 ≤ r_max/λ ≤ 50")
    k, a, b, c = _k(f, eps_r, mu_r, sigma)
    lam = 2 * np.pi / b
    D = Derivation()
    D.step("Wavenumber", rf"k=\beta-j\alpha,\ \ \beta={fmt(b)}\ \text{{rad/m}},\ \alpha={fmt(a)}\ \text{{Np/m}},\ \lambda={fmt(lam)}\ \text{{m}}", [b, a], "",
           note="the same k governs all three geometries")
    D.step("1-D (plane wave, TEM line)", r"\frac{d^2\psi}{dz^2}+k^2\psi=0\ \Rightarrow\ \psi=e^{-jkz},\ \ |\psi|=e^{-\alpha z}",
           note="energy flows through a fixed cross-section: nothing spreads")
    D.step("2-D (line source, cylindrical wave)", r"\frac1\rho\frac{d}{d\rho}\Big(\rho\frac{d\psi}{d\rho}\Big)+k^2\psi=0\ \Rightarrow\ \psi=H_0^{(2)}(k\rho)\approx\sqrt{\tfrac{2}{\pi k\rho}}e^{-j(k\rho-\pi/4)}",
           note="power spreads over a circle of circumference 2πρ → |ψ| ∝ 1/√ρ")
    D.step("3-D (point source, spherical wave)", r"\frac1{R^2}\frac{d}{dR}\Big(R^2\frac{d\psi}{dR}\Big)+k^2\psi=0\ \Rightarrow\ \psi=\frac{e^{-jkR}}{R}",
           note="power spreads over a sphere of area 4πR² → |ψ| ∝ 1/R")

    r = np.linspace(lam / 20, r_max_lambda * lam, n)
    rref = lam / 2
    prof = {}
    for d in DIMS:
        p = psi(d, k, r) / abs(psi(d, k, np.array(rref)))
        prof[d] = {"re": p.real.tolist(), "im": p.imag.tolist(), "mag": np.abs(p).tolist()}

    # ---- checks
    h = lam * 1e-3
    for d in DIMS:
        D.check(rf"\text{{{d}: }}\psi\text{{ satisfies the {d[0]}-D Helmholtz equation}}", 0.0, _radial_residual(d, k, 2.3 * lam, h), 1e-5,
                "finite-difference residual at r = 2.3λ (relative to k²ψ)")
    rr = np.linspace(2 * lam, max(r_max_lambda, 3) * lam, 200)
    if a == 0:
        # time-average power flow ∝ Im(ψ* dψ/dr) × wavefront size (1, 2πρ, 4πR²) — exact, including the near field
        dpsi = {"1D": -1j * k * psi("1D", k, rr), "2D": -k * special.hankel2(1, k * rr), "3D": psi("3D", k, rr) * (-1j * k - 1 / rr)}
        size = {"1D": np.ones_like(rr), "2D": 2 * np.pi * rr, "3D": 4 * np.pi * rr ** 2}
        for d in DIMS:
            fl = -np.imag(np.conj(psi(d, k, rr)) * dpsi[d]) * size[d]
            D.check(rf"\text{{{d}: power through the wavefront is the same at every }}r", 0.0, float((fl.max() - fl.min()) / abs(fl.mean())), 1e-10,
                    "Im(ψ* ∂ψ/∂r) × wavefront size over 200 radii (Poynting flux)")
        far = np.linspace(20 * lam, 40 * lam, 50)
        for d, slope in (("1D", 0.0), ("2D", -0.5), ("3D", -1.0)):
            s = np.polyfit(np.log(far), np.log(np.abs(psi(d, k, far))), 1)[0]
            D.check(rf"\text{{{d}: }}|\psi|\propto r^{{{slope:g}}}\text{{ (log-log slope)}}", slope, s, 1e-3, "least-squares fit for r = 20…40 λ",
                    scale=1.0)
    x = 50 / b
    D.check(r"H_0^{(2)}(k\rho)\to\sqrt{2/\pi k\rho}\,e^{-j(k\rho-\pi/4)}", complex(np.sqrt(2 / (np.pi * k * x)) * np.exp(-1j * (k * x - np.pi / 4))),
            complex(special.hankel2(0, k * x)), 1 / (8 * 50) + 1e-6, "large-argument asymptote at kρ = 50 (error ≈ 1/8kρ)")

    # ---- 2-D maps in a plane (phasor)
    L = r_max_lambda * lam / 1.5
    g = np.linspace(-L, L, grid)
    X, Y = np.meshgrid(g, g)
    R = np.maximum(np.hypot(X, Y), lam / 40)
    maps = {}
    for d in DIMS:
        if d == "1D":
            m = psi("1D", k, X - g[0]) / 1.0
        else:
            m = psi(d, k, R) / abs(psi(d, k, np.array(rref)))
        m = np.where(np.abs(m) > 3, 3 * m / np.abs(m), m)       # clip the source singularity for display
        maps[d] = {"re": np.round(m.real, 5).tolist(), "im": np.round(m.imag, 5).tolist()}

    # ---- what changes what: engine-evaluated sensitivities at r_obs
    robs = r_max_lambda * lam

    def level_db(ff=f, er=eps_r, sg=sigma, ro=robs):
        kk = _k(ff, er, mu_r, sg)[0]
        lam_ = 2 * np.pi / kk.real
        return {d: float(20 * np.log10(abs(psi(d, kk, np.array(ro))) / abs(psi(d, kk, np.array(lam_ / 2))))) for d in DIMS}, lam_

    base, _ = level_db()
    cases = [("double the frequency", dict(ff=2 * f)), ("double εr", dict(er=2 * eps_r)),
             ("σ × 10 (or add 0.01 S/m)", dict(sg=sigma * 10 if sigma > 0 else 0.01)), ("double the distance", dict(ro=2 * robs))]
    sens = []
    for name, kw in cases:
        lv, lam_ = level_db(**kw)
        sens.append({"change": name, "lambda": lam_, **{d: lv[d] - base[d] for d in DIMS}})
    D.step("Level at the observation point", r"20\log_{10}\frac{|\psi(r_{obs})|}{|\psi(\lambda/2)|}", [base[d] for d in DIMS], "dB",
           note=f"r_obs = {robs:.3g} m; 1-D, 2-D, 3-D")

    # frequency sweep of the level at r_obs (fixed physical distance)
    fs = np.logspace(np.log10(f / 10), np.log10(f * 10), 120)
    fsw = {d: [] for d in DIMS}
    for ff in fs:
        lv, _ = level_db(ff=ff)
        for d in DIMS:
            fsw[d].append(lv[d])
    return {**D.out(wavelength=lam, beta=b, alpha=a, r_obs=robs, level_1D=base["1D"], level_2D=base["2D"], level_3D=base["3D"]),
            "r": r.tolist(), "profiles": prof, "maps": {"x": g.tolist(), **maps}, "sensitivity": sens,
            "fsweep": {"f": fs.tolist(), **fsw}}
