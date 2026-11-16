"""Magnetostatics (Ulaby ch. 5, Cheng ch. 6).

wires      – parallel infinite wires ⊥ to the page: B, field lines (= contours of A_z),
             forces per unit length.
loops      – coaxial circular loops (single, Helmholtz, solenoid): exact elliptic-integral
             field, field lines (= contours of the flux function ψ = ρA_φ).
ampere     – symmetric current distributions solved with Ampère's law.
inductance – solenoid, coax, toroid, two-wire line.
"""
import numpy as np
import contourpy
from scipy import integrate, special
from .constants import MU0
from .derivation import Derivation, fmt

MAX_WIRES = 8


# ---------------------------------------------------------------- straight wires
def _wireB(W, X, Y):
    Bx, By, A = np.zeros_like(X, float), np.zeros_like(X, float), np.zeros_like(X, float)
    with np.errstate(divide="ignore", invalid="ignore"):
        for I, x, y in W:
            dx, dy = X - x, Y - y
            r2 = dx * dx + dy * dy
            Bx += -MU0 * I / (2 * np.pi) * dy / r2
            By += MU0 * I / (2 * np.pi) * dx / r2
            A += -MU0 * I / (4 * np.pi) * np.log(r2)
    return Bx, By, A


def wires(currents, probe=(0.0, 0.5), span=1.0, n=161):
    """currents: list of {I (A, + = out of page / +z), x, y (m)}."""
    if not 0 < len(currents) <= MAX_WIRES:
        raise ValueError(f"need 1…{MAX_WIRES} wires")
    W = np.array([[c["I"], c["x"], c["y"]] for c in currents], float)
    if np.any(W[:, 0] == 0):
        raise ValueError("currents must be non-zero")
    P = W[:, 1:]
    if len(W) > 1 and min(np.hypot(*(P[i] - P[j])) for i in range(len(P)) for j in range(i)) < 1e-6:
        raise ValueError("two wires at the same position")
    D = Derivation()
    xs = np.linspace(-span, span, n)
    X, Y = np.meshgrid(xs, xs)
    Bx, By, A = _wireB(W, X, Y)
    Am = np.where(np.isfinite(A), A, np.nan)
    lo, hi = np.nanpercentile(Am, 1), np.nanpercentile(Am, 99.5)
    gen = contourpy.contour_generator(xs, xs, np.nan_to_num(Am, nan=hi))
    lines = []
    for L in np.linspace(lo, hi, 30)[1:-1]:
        for seg in gen.lines(L):
            if len(seg) > 4:
                lines.append({"x": seg[:, 0].tolist(), "y": seg[:, 1].tolist()})

    px, py = map(float, probe)
    dmin = float(np.min(np.hypot(P[:, 0] - px, P[:, 1] - py)))
    if dmin < 1e-6:
        raise ValueError("probe is on a wire")
    bx, by, a0 = (float(v) for v in _wireB(W, np.array(px), np.array(py)))
    D.step("Field of one infinite wire", r"\mathbf B_i=\hat\phi_i\,\frac{\mu_0I_i}{2\pi r_i}=\frac{\mu_0I_i}{2\pi}\frac{\hat z\times(\mathbf r-\mathbf r_i)}{|\mathbf r-\mathbf r_i|^2}")
    D.step("Superposition", rf"\mathbf B=\sum_i\mathbf B_i=({fmt(bx)},\ {fmt(by)})", [bx, by], "T")
    D.step("|B| at probe", rf"|\mathbf B|={fmt(np.hypot(bx, by))}", float(np.hypot(bx, by)), "T",
           note=f"H = B/μ0 = {np.hypot(bx, by) / MU0:.4g} A/m")
    D.step("Vector potential", r"A_z=-\frac{\mu_0}{2\pi}\sum_iI_i\ln r_i,\qquad\mathbf B=\nabla\times(\hat zA_z)",
           note="B is tangent to the curves A_z = const, so those curves are the field lines")
    # forces per unit length
    F = []
    for i, (I, x, y) in enumerate(W):
        o = np.delete(W, i, axis=0)
        if len(o):
            ox, oy, _ = _wireB(o, np.array(x), np.array(y))
            F.append([float(-I * oy), float(I * ox)])   # F' = I ẑ × B
        else:
            F.append([0.0, 0.0])
    F = np.array(F)
    if len(W) > 1:
        D.step("Force per unit length on each wire", r"\mathbf F'_i=I_i\,\hat z\times\mathbf B_{\text{others}}(\mathbf r_i)",
               note="parallel currents attract, antiparallel repel")
    # checks
    contrib = []
    for i, (I, x, y) in enumerate(W):
        others = np.delete(P, i, axis=0)
        rc = 0.4 * (np.min(np.hypot(*(others - [x, y]).T)) if len(others) else span)
        t = np.linspace(0, 2 * np.pi, 256, endpoint=False)
        cx, cy = x + rc * np.cos(t), y + rc * np.sin(t)
        Bxc, Byc, _ = _wireB(W, cx, cy)
        circ = np.sum(Bxc * (-np.sin(t)) + Byc * np.cos(t)) * rc * 2 * np.pi / len(t)
        D.check(rf"\oint\mathbf B\cdot d\mathbf l=\mu_0I_{{{i + 1}}} \text{{ (circle around wire {i + 1})}}", MU0 * I, circ, 1e-10,
                "256-point periodic trapezoid (spectrally accurate)")
    if len(W) > 1:
        Rb = 3 * (np.abs(P).max() + 0.1 * span)
        t = np.linspace(0, 2 * np.pi, 1024, endpoint=False)
        Bxc, Byc, _ = _wireB(W, Rb * np.cos(t), Rb * np.sin(t))
        circ = np.sum(Bxc * (-np.sin(t)) + Byc * np.cos(t)) * Rb * 2 * np.pi / len(t)
        D.check(r"\oint\mathbf B\cdot d\mathbf l=\mu_0\sum I \text{ (circle around all)}", MU0 * W[:, 0].sum(), circ, 1e-8,
                f"r = {Rb:.3g} m", scale=MU0 * np.abs(W[:, 0]).sum())
        D.check(r"\sum_i\mathbf F'_i=0 \text{ (Newton's third law)}", 0.0, np.abs(F.sum(0)).max(), 1e-12, "sum of forces",
                scale=max(np.abs(F).max(), 1e-300))
        if len(W) == 2:
            d = float(np.hypot(*(P[0] - P[1])))
            D.check(r"|F'|=\frac{\mu_0I_1I_2}{2\pi d}", MU0 * abs(W[0, 0] * W[1, 0]) / (2 * np.pi * d), float(np.hypot(*F[0])), 1e-12,
                    "closed form for two wires")
    h = 1e-4 * dmin
    f = lambda x, y: _wireB(W, np.array(x), np.array(y))
    dBx = (f(px + h, py)[0] - f(px - h, py)[0]) / (2 * h)
    dBy = (f(px, py + h)[1] - f(px, py - h)[1]) / (2 * h)
    sc = np.hypot(bx, by) / dmin + 1e-300
    D.check(r"\nabla\cdot\mathbf B=0 \text{ at probe}", 0.0, float(dBx + dBy), 1e-6, "central differences", scale=sc)
    curlA = [(f(px, py + h)[2] - f(px, py - h)[2]) / (2 * h), -(f(px + h, py)[2] - f(px - h, py)[2]) / (2 * h)]
    D.check(r"\mathbf B=\nabla\times\mathbf A \text{ at probe}", 0.0, float(np.hypot(curlA[0] - bx, curlA[1] - by)), 1e-6,
            "central differences of A_z", scale=np.hypot(bx, by) + 1e-300)
    Bm = np.hypot(Bx, By)
    return {**D.out(B=[bx, by], B_mag=float(np.hypot(bx, by)), A=a0),
            "forces": F.tolist(), "field_lines": lines,
            "grid": {"x": xs.tolist(), "y": xs.tolist(),
                     "Bmag": np.nan_to_num(np.log10(np.clip(Bm, np.nanpercentile(Bm, 2), np.nanpercentile(Bm, 99.5)))).tolist()},
            "wires": [{"I": float(I), "x": float(x), "y": float(y)} for I, x, y in W]}


# ---------------------------------------------------------------- circular loops (exact)
def _loopB(a, z0, I, rho, z):
    """Exact field of a circular loop (radius a, plane z = z0) via complete elliptic integrals."""
    rho = np.maximum(np.asarray(rho, float), 1e-12 * a)
    dz = np.asarray(z, float) - z0
    q = (a + rho) ** 2 + dz ** 2
    m = np.clip(4 * a * rho / q, 0, 1 - 1e-15)
    K, E = special.ellipk(m), special.ellipe(m)
    den = (a - rho) ** 2 + dz ** 2
    c = MU0 * I / (2 * np.pi)
    with np.errstate(divide="ignore", invalid="ignore"):   # singular only on the wire itself
        Bz = c / np.sqrt(q) * (K + (a * a - rho * rho - dz * dz) / den * E)
        Br = c * dz / (rho * np.sqrt(q)) * (-K + (a * a + rho * rho + dz * dz) / den * E)
    Br = np.where(rho < 1e-9 * a, 0.0, Br)
    Bz, Br = np.nan_to_num(Bz, nan=0.0, posinf=0.0, neginf=0.0), np.nan_to_num(Br, nan=0.0, posinf=0.0, neginf=0.0)
    k = np.sqrt(m)
    psi = MU0 * I * np.sqrt(a * rho) / (np.pi * np.maximum(k, 1e-15)) * ((1 - m / 2) * K - E)   # ρ A_φ
    return Br, Bz, psi


def _loopsB(L, rho, z):
    Br = Bz = psi = 0.0
    for a, z0, I in L:
        b = _loopB(a, z0, I, rho, z)
        Br, Bz, psi = Br + b[0], Bz + b[1], psi + b[2]
    return Br, Bz, psi


def _biot_savart_loop(a, z0, I, P, n=2048):
    """Direct numerical Biot–Savart ∮ I dl × R / 4π|R|³ (periodic trapezoid)."""
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    src = np.stack([a * np.cos(t), a * np.sin(t), np.full_like(t, z0)], -1)
    dl = np.stack([-a * np.sin(t), a * np.cos(t), 0 * t], -1) * (2 * np.pi / n)
    R = np.asarray(P) - src
    return MU0 * I / (4 * np.pi) * np.sum(np.cross(dl, R) / (np.linalg.norm(R, axis=1) ** 3)[:, None], axis=0)


def loops(kind="loop", I=1.0, a=0.1, N=10, length=0.3, sep=None, probe=(0.05, 0.05), n=121):
    if a <= 0 or I == 0:
        raise ValueError("need a > 0 and I ≠ 0")
    if kind == "loop":
        L = [(a, 0.0, I)]
    elif kind == "helmholtz":
        s = a if sep is None else sep
        L = [(a, -s / 2, I), (a, s / 2, I)]
    elif kind == "solenoid":
        if N < 2 or length <= 0:
            raise ValueError("solenoid needs N ≥ 2 and length > 0")
        L = [(a, z, I) for z in np.linspace(-length / 2, length / 2, int(N))]
    else:
        raise ValueError("kind must be loop, helmholtz or solenoid")
    D = Derivation()
    zext = max(2.5 * a, (length / 2 + 1.5 * a) if kind == "solenoid" else 2.5 * a)
    rs, zs = np.linspace(0, 2.5 * a, n), np.linspace(-zext, zext, n)
    RR, ZZ = np.meshgrid(rs, zs)
    Br, Bz, psi = _loopsB(L, RR, ZZ)
    Bm = np.hypot(Br, Bz)
    ps = np.nan_to_num(psi)
    pmax = np.nanpercentile(np.abs(ps), 99)
    gen = contourpy.contour_generator(rs, zs, ps)
    lines = []
    for lev in np.linspace(0, pmax, 16)[1:]:
        for seg in gen.lines(lev):
            if len(seg) > 4:
                lines.append({"x": seg[:, 0].tolist(), "y": seg[:, 1].tolist()})
    pr, pz = map(float, probe)
    if pr < 0:
        raise ValueError("probe radius ρ must be ≥ 0")
    if any(abs(pr - aa) < 1e-6 and abs(pz - z0) < 1e-6 for aa, z0, _ in L):
        raise ValueError("probe lies on a conductor")
    br, bz, _ = (float(v) for v in _loopsB(L, pr, pz))
    D.step("Biot–Savart", r"\mathbf B=\frac{\mu_0}{4\pi}\oint\frac{I\,d\mathbf l\times\hat{\mathbf R}}{R^2}")
    D.step("Exact loop field", r"B_z=\frac{\mu_0I}{2\pi\sqrt{(a+\rho)^2+z^2}}\left[K(k)+\frac{a^2-\rho^2-z^2}{(a-\rho)^2+z^2}E(k)\right],\ k^2=\frac{4a\rho}{(a+\rho)^2+z^2}",
           note="K, E: complete elliptic integrals (scipy.special)")
    D.step("Field at probe", rf"(B_\rho,B_z)=({fmt(br)},\ {fmt(bz)})", [br, bz], "T")
    m = sum(I_ * np.pi * aa * aa for aa, _, I_ in L)
    D.step("Magnetic dipole moment", rf"m=\sum I\pi a^2={fmt(m)}", m, "A·m²")
    Bc = float(_loopsB(L, 0.0, 0.0)[1])
    D.step("Field at centre", rf"B_z(0,0)={fmt(Bc)}", Bc, "T")
    # checks
    P = np.array([pr, 0.0, pz])
    bs = sum(_biot_savart_loop(aa, z0, I_, P) for aa, z0, I_ in L)
    D.check(r"\text{elliptic formula}=\text{direct Biot–Savart integral}", 0.0, float(np.hypot(bs[0] - br, bs[2] - bz)), 1e-8,
            "2048-point numerical line integral per loop", scale=np.hypot(br, bz) + 1e-300)
    if kind == "loop":
        zt = 0.7 * a
        D.check(r"B_z(0,z)=\frac{\mu_0Ia^2}{2(a^2+z^2)^{3/2}} \text{ on axis}", MU0 * I * a * a / (2 * (a * a + zt * zt) ** 1.5),
                float(_loopsB(L, 0.0, zt)[1]), 1e-10, "closed form at z = 0.7a")
    zf = 60 * max(a, length)
    D.check(r"\text{far field }B_z\to\frac{\mu_0m}{2\pi z^3}", MU0 * m / (2 * np.pi * zf ** 3), float(_loopsB(L, 0.0, zf)[1]),
            3 * (max(a, length) / zf) ** 2 + 1e-9, "dipole limit at z = 60·size; error ~ (size/z)²")
    if kind == "helmholtz" and abs((sep or a) - a) < 1e-12:
        h = 1e-3 * a
        d2 = (float(_loopsB(L, 0, h)[1]) - 2 * Bc + float(_loopsB(L, 0, -h)[1])) / h ** 2
        D.check(r"\partial^2B_z/\partial z^2=0 \text{ at centre (Helmholtz spacing } d=a)", 0.0, d2, 1e-4,
                "second difference; spacing a makes the field maximally flat", scale=abs(Bc) / a ** 2)
    hh = 1e-5 * a
    if pr > 10 * hh:
        f = lambda r_, z_: _loopsB(L, r_, z_)
        div = ((pr + hh) * f(pr + hh, pz)[0] - (pr - hh) * f(pr - hh, pz)[0]) / (2 * hh * pr) + (f(pr, pz + hh)[1] - f(pr, pz - hh)[1]) / (2 * hh)
        D.check(r"\nabla\cdot\mathbf B=0 \text{ at probe}", 0.0, float(div), 1e-5, "central differences (cylindrical)",
                scale=np.hypot(br, bz) / a + 1e-300)
    return {**D.out(B=[br, bz], B_mag=float(np.hypot(br, bz)), m=m, B_center=Bc),
            "field_lines": lines, "loops": [{"a": aa, "z": z0} for aa, z0, _ in L],
            "grid": {"r": rs.tolist(), "z": zs.tolist(), "Bmag": np.log10(np.maximum(Bm, 1e-30)).tolist()},
            "axis": {"z": zs.tolist(), "Bz": [float(v) for v in _loopsB(L, 0.0, zs)[1]]}}


# ---------------------------------------------------------------- Ampère's law
AMPERE = {
    "wire": "Solid round wire (I uniform, radius a)",
    "tube": "Hollow conductor (a < r < b)",
    "coax": "Coaxial cable (+I inner radius a, −I outer shell b…c)",
    "toroid": "Toroid (N turns, a < r < b)",
    "solenoid": "Ideal solenoid (n turns/m, radius a)",
}


def _ampere_model(kind, I, a, b, c, N):
    if kind == "wire":
        Ienc = lambda r: I * np.minimum(r / a, 1) ** 2
        J = lambda r: np.where(r < a, I / (np.pi * a * a), 0.0)
    elif kind == "tube":
        Ienc = lambda r: I * np.clip((r * r - a * a) / (b * b - a * a), 0, 1)
        J = lambda r: np.where((r > a) & (r < b), I / (np.pi * (b * b - a * a)), 0.0)
    elif kind == "coax":
        Ienc = lambda r: np.where(r < a, I * (r / a) ** 2, np.where(r < b, I, I * (1 - np.clip((r * r - b * b) / (c * c - b * b), 0, 1))))
        J = lambda r: np.where(r < a, I / (np.pi * a * a), np.where((r > b) & (r < c), -I / (np.pi * (c * c - b * b)), 0.0))
    elif kind == "toroid":
        Ienc = lambda r: np.where((r > a) & (r < b), N * I, 0.0)
        J = None
    elif kind == "solenoid":
        Ienc = None
        J = None
    else:
        raise ValueError(f"kind must be one of {list(AMPERE)}")
    return Ienc, J


def ampere(kind, I=1.0, a=0.01, b=0.02, c=0.025, N=100, n_per_m=1000, mu_r=1.0, r=0.005, n=400):
    if kind not in AMPERE:
        raise ValueError(f"kind must be one of {list(AMPERE)}")
    if a <= 0 or r <= 0 or mu_r <= 0:
        raise ValueError("need a > 0, r > 0, μr > 0")
    if kind in ("tube", "toroid", "coax") and b <= a or kind == "coax" and c <= b:
        raise ValueError("need a < b (< c for coax)")
    mu = MU0 * mu_r
    D = Derivation()
    Ienc, J = _ampere_model(kind, I, a, b, c, N)
    D.step("Ampère's law", r"\oint_C\mathbf H\cdot d\mathbf l=I_{enc}")
    if kind == "solenoid":
        B = lambda s: np.where(s < a, mu * n_per_m * I, 0.0)
        D.step("Rectangular Amperian loop", r"H\ell=n\ell I\ \Rightarrow\ B=\mu nI\ \text{inside},\ 0\ \text{outside}",
               note="ideal (infinitely long) solenoid")
        Br = float(B(r))
        D.step("Field", rf"B(r={fmt(r)})={fmt(Br)}", Br, "T")
    else:
        D.step("Circular Amperian path", r"H_\phi\cdot2\pi r=I_{enc}(r)\ \Rightarrow\ B_\phi=\frac{\mu I_{enc}(r)}{2\pi r}")
        B = lambda s: mu * Ienc(s) / (2 * np.pi * s)
        ie = float(Ienc(r))
        D.step("Enclosed current", rf"I_{{enc}}({fmt(r)})={fmt(ie)}", ie, "A", note="N·I for the toroid" if kind == "toroid" else "")
        Br = float(B(r))
        D.step("Field", rf"B_\phi={fmt(Br)},\quad H_\phi={fmt(Br / mu)}", Br, "T")
        if J is not None:
            pts = [p for p in (a, b, c) if p < r]
            num, _ = integrate.quad(lambda s: float(J(s)) * 2 * np.pi * s, 0, r, points=pts or None, limit=200, epsrel=1e-12)
            D.check(r"I_{enc}=\int_S\mathbf J\cdot d\mathbf s \text{ (numerical)}", ie, num, 1e-9, "scipy quad over the disc",
                    scale=abs(I))
            hh = 1e-6 * r
            if all(abs(r - p) > 10 * hh for p in (a, b, c)):
                curl = ((r + hh) * float(B(r + hh)) - (r - hh) * float(B(r - hh))) / (2 * hh * r)
                D.check(r"\nabla\times\mathbf B=\mu\mathbf J \text{ at } r", mu * float(J(r)), curl, 1e-6,
                        "central difference of (1/r) d(rB)/dr", scale=mu * abs(I) / (np.pi * a * a))
        t = np.linspace(0, 2 * np.pi, 64, endpoint=False)
        circ = np.sum(np.full_like(t, Br / mu) * r) * 2 * np.pi / len(t)
        D.check(r"\oint\mathbf H\cdot d\mathbf l=I_{enc}", ie, circ, 1e-12, "64-point quadrature on the circle", scale=abs(I) * max(N, 1))
    rmax = {"wire": 3 * a, "tube": 2 * b, "coax": 1.4 * c, "toroid": 1.3 * b, "solenoid": 2 * a}[kind]
    s = np.linspace(rmax / n, rmax, n)
    return {**D.out(B=Br, H=Br / mu), "title": AMPERE[kind], "profile": {"r": s.tolist(), "B": [float(B(x)) for x in s]},
            "a": a, "b": b, "c": c, "r": r}


# ---------------------------------------------------------------- inductance
def inductance(kind, I=1.0, N=100, a=0.01, b=0.02, length=0.1, h=0.01, d=0.1, mu_r=1.0):
    mu = MU0 * mu_r
    if min(a, length, mu_r) <= 0 or I == 0:
        raise ValueError("need positive dimensions, μr > 0 and I ≠ 0")
    D = Derivation()
    D.step("Definition", r"L=\frac{\Lambda}{I}=\frac{N\Phi}{I},\qquad W_m=\tfrac12LI^2=\int\frac{B^2}{2\mu}dv")
    if kind == "solenoid":
        A = np.pi * a * a
        L = mu * N * N * A / length
        B = mu * N * I / length
        D.step("Long solenoid", rf"B=\mu\frac{{N}}{{\ell}}I,\ \Lambda=NBA\ \Rightarrow\ L=\frac{{\mu N^2A}}{{\ell}}={fmt(L)}", L, "H",
               note=f"valid for ℓ ≫ a (here ℓ/a = {length / a:.3g}); end effects neglected")
        Wn = B * B / (2 * mu) * A * length
        flux = integrate.quad(lambda s: B * 2 * np.pi * s, 0, a)[0]
        D.check(r"\Lambda=N\int_SB\,ds", L * I, N * flux, 1e-10, "scipy quad over the cross-section")
    elif kind == "coax":
        if b <= a:
            raise ValueError("need b > a")
        L = mu / (2 * np.pi) * np.log(b / a) * length
        D.step("Coax (external)", rf"L=\frac{{\mu\ell}}{{2\pi}}\ln\frac{{b}}{{a}}={fmt(L)}", L, "H",
               note=f"{L / length:.4g} H/m; internal inductance μ/8π per metre of a solid inner conductor is not included")
        Bf = lambda s: mu * I / (2 * np.pi * s)
        Wn = integrate.quad(lambda s: Bf(s) ** 2 / (2 * mu) * 2 * np.pi * s * length, a, b, epsrel=1e-12)[0]
        flux = integrate.quad(Bf, a, b, epsrel=1e-12)[0] * length
        D.check(r"\Lambda=\int_a^bB\,\ell\,dr", L * I, flux, 1e-10, "flux through the dielectric")
    elif kind == "toroid":
        if b <= a or h <= 0:
            raise ValueError("need b > a and h > 0")
        L = mu * N * N * h / (2 * np.pi) * np.log(b / a)
        D.step("Toroid (rectangular core)", rf"B=\frac{{\mu NI}}{{2\pi r}},\ L=\frac{{\mu N^2h}}{{2\pi}}\ln\frac{{b}}{{a}}={fmt(L)}", L, "H")
        Bf = lambda s: mu * N * I / (2 * np.pi * s)
        Wn = integrate.quad(lambda s: Bf(s) ** 2 / (2 * mu) * 2 * np.pi * s * h, a, b, epsrel=1e-12)[0]
        flux = N * integrate.quad(lambda s: Bf(s) * h, a, b, epsrel=1e-12)[0]
        D.check(r"\Lambda=N\int_a^bB\,h\,dr", L * I, flux, 1e-10, "flux through the core")
    elif kind == "twowire":
        if d <= 2 * a:
            raise ValueError("need d > 2a")
        L = mu / np.pi * np.arccosh(d / (2 * a)) * length
        D.step("Two-wire line", rf"L=\frac{{\mu\ell}}{{\pi}}\cosh^{{-1}}\frac{{d}}{{2a}}={fmt(L)}", L, "H",
               note=f"{L / length:.4g} H/m (external, includes proximity effect)")
        Bf = lambda x: mu * I / (2 * np.pi) * (1 / x + 1 / (d - x))
        flux = integrate.quad(Bf, a, d - a, epsrel=1e-12)[0] * length
        D.check(r"\text{thin-wire flux } \tfrac{\mu\ell}{\pi}\ln\tfrac{d-a}{a}\approx L I", L * I, flux, 2 * (a / d) / np.log(d / a),
                "filament model; relative difference ≈ (a/d)/ln(d/a)")
        Wn = 0.5 * flux * I
    else:
        raise ValueError("kind must be solenoid, coax, toroid or twowire")
    W = 0.5 * L * I * I
    D.step("Stored energy", rf"W_m=\tfrac12LI^2={fmt(W)}", W, "J")
    if kind != "twowire":
        D.check(r"\tfrac12LI^2=\int\frac{B^2}{2\mu}dv", W, Wn, 1e-10, "field-energy integral")
    return D.out(L=L, W=W, L_per_m=L / length if kind in ("coax", "twowire") else None)
