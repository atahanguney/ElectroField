"""Electrostatics (Ulaby ch. 4, Cheng ch. 3).

1. point_charges  – superposition of point charges in the plane z = 0, optional
                    grounded plane y = 0 (method of images); equipotentials and
                    field lines whose density is proportional to charge.
2. gauss          – symmetric distributions solved with Gauss's law.
3. capacitor      – parallel-plate, coaxial and spherical capacitors.
"""
import numpy as np
import contourpy
from scipy import integrate
from .constants import EPS0, K_E
from .derivation import Derivation, fmt

MAX_CHARGES = 8


# ---------------------------------------------------------------- superposition
def field_at(Q, P):
    """Q: (N,4) rows (q, x, y, z) in C, m.  P: (..., 3).  Returns E (...,3), V (...)."""
    P = np.asarray(P, float)
    E, V = np.zeros(P.shape), np.zeros(P.shape[:-1])
    with np.errstate(divide="ignore", invalid="ignore"):
        for q, *s in Q:
            d = P - np.asarray(s)
            r = np.linalg.norm(d, axis=-1)
            V += K_E * q / r
            E += K_E * q * d / (r ** 3)[..., None]
    return E, V


def _sphere_flux(Q, c, rs, n=48):
    """∮E·dS over a sphere (centre c, radius rs): Gauss–Legendre in cosθ × uniform φ."""
    mu, w = np.polynomial.legendre.leggauss(n)
    ph = np.linspace(0, 2 * np.pi, 2 * n, endpoint=False)
    M, PH = np.meshgrid(mu, ph, indexing="ij")
    st = np.sqrt(1 - M ** 2)
    nrm = np.stack([st * np.cos(PH), st * np.sin(PH), M], -1)
    E, _ = field_at(Q, np.asarray(c) + rs * nrm)
    return float(np.sum((E * nrm).sum(-1) * w[:, None]) * rs * rs * (2 * np.pi / (2 * n)))


def _trace(Q, seeds, sign, span, ground, stop_pts, h, nmax=1500):
    """Vectorised RK4 along ±E/|E| from all seeds at once (2-D slice z = 0)."""
    P = np.array(seeds, float)
    lines = [[p.copy()] for p in P]
    alive = np.ones(len(P), bool)

    def d(X):
        E, _ = field_at(Q, np.c_[X, np.zeros(len(X))])
        e = E[:, :2]
        return sign * e / np.maximum(np.linalg.norm(e, axis=1), 1e-300)[:, None]

    for _ in range(nmax):
        if not alive.any():
            break
        X = P[alive]
        k1 = d(X); k2 = d(X + h / 2 * k1); k3 = d(X + h / 2 * k2); k4 = d(X + h * k3)
        X = X + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        P[alive] = X
        idx = np.flatnonzero(alive)
        for j, i in enumerate(idx):
            p = X[j]
            if ground and p[1] < 0:  # reached the conductor
                prev = lines[i][-1]
                t = prev[1] / (prev[1] - p[1])
                lines[i].append(prev + t * (p - prev)); alive[i] = False; continue
            hit = [s for s in stop_pts if np.hypot(*(p - s)) < 1.5 * h]
            if hit:
                lines[i].append(np.array(hit[0])); alive[i] = False; continue
            lines[i].append(p.copy())
            if abs(p[0]) > 1.6 * span or abs(p[1]) > 1.6 * span:
                alive[i] = False
    return [np.array(l) for l in lines]


def point_charges(charges, ground=False, probe=(0.0, 0.0), span=1.0, n=141):
    """charges: list of {q (C), x, y (m)} in the plane z = 0."""
    if not 0 < len(charges) <= MAX_CHARGES:
        raise ValueError(f"need 1…{MAX_CHARGES} charges")
    real = np.array([[c["q"], c["x"], c["y"], 0.0] for c in charges], float)
    if np.any(real[:, 0] == 0):
        raise ValueError("charges must be non-zero")
    pos = real[:, 1:3]
    if len(real) > 1 and min(np.hypot(*(pos[i] - pos[j])) for i in range(len(pos)) for j in range(i)) < 1e-6:
        raise ValueError("two charges at the same position")
    if ground and np.any(pos[:, 1] <= 0):
        raise ValueError("with a grounded plane at y = 0 every charge needs y > 0")
    img = real * [-1, 1, -1, 1] if ground else np.zeros((0, 4))
    Q = np.vstack([real, img])
    D = Derivation()

    # ---------- grid, potential, equipotentials
    xs = np.linspace(-span, span, n)
    ys = np.linspace(0 if ground else -span, span if not ground else 2 * span, n)
    X, Y = np.meshgrid(xs, ys)
    E, V = field_at(Q, np.stack([X, Y, 0 * X], -1))
    qmax = np.abs(real[:, 0]).max()
    Vc = K_E * qmax / (0.03 * span)
    Vg = np.clip(np.nan_to_num(V, nan=0, posinf=Vc, neginf=-Vc), -Vc, Vc)
    levels = sorted({0.0, *[s * Vc * f for s in (1, -1) for f in (0.015, 0.04, 0.08, 0.15, 0.28, 0.5, 0.8)]})
    gen = contourpy.contour_generator(xs, ys, Vg)
    equip = []
    for L in levels:
        if L == 0 and np.all(real[:, 0] > 0) and not ground:
            continue
        for seg in gen.lines(L):
            if len(seg) > 3:
                equip.append({"V": L, "x": seg[:, 0].tolist(), "y": seg[:, 1].tolist()})
    Emag = np.linalg.norm(E[..., :2], axis=-1)

    # ---------- field lines: count ∝ |q| (Faraday's convention)
    h = span / 120
    nl = lambda q: max(4, int(round(18 * abs(q) / qmax)))
    r0 = 1.6 * h
    qpos, qneg = real[real[:, 0] > 0], real[real[:, 0] < 0]
    lines = []
    def seeds(rows, count):
        out = []
        for q, x, y, _ in rows:
            k = count(q)
            for t in np.linspace(0, 2 * np.pi, k, endpoint=False) + np.pi / k:
                out.append([x + r0 * np.cos(t), y + r0 * np.sin(t)])
        return out
    if len(qpos):
        for l in _trace(Q, seeds(qpos, nl), +1, span, ground, qneg[:, 1:3], h):
            lines.append(l)
    tot_pos, tot_neg = qpos[:, 0].sum() if len(qpos) else 0, -qneg[:, 0].sum() if len(qneg) else 0
    if len(qneg) and tot_neg > tot_pos and not ground:
        frac = 1 - tot_pos / tot_neg
        for l in _trace(Q, seeds(qneg, lambda q: max(2, int(round(nl(q) * frac)))), -1, span, False, qpos[:, 1:3], h):
            lines.append(l[::-1])
    flines = [{"x": l[:, 0].tolist(), "y": l[:, 1].tolist()} for l in lines if len(l) > 2]

    # ---------- probe: superposition, step by step
    P = np.array([probe[0], probe[1], 0.0])
    if ground and P[1] < 0:
        raise ValueError("probe lies inside the conductor (y < 0)")
    dmin = np.min(np.linalg.norm(Q[:, 1:] - P, axis=1))
    if dmin < 1e-6:
        raise ValueError("probe is on a charge")
    contrib = []
    for i, (q, *s) in enumerate(Q):
        Rv = P - np.array(s)
        R = np.linalg.norm(Rv)
        Ei = K_E * q * Rv / R ** 3
        contrib.append({"q": q, "image": i >= len(real), "R": R, "E": Ei[:2], "V": K_E * q / R})
    Ep, Vp = field_at(Q, P[None])
    Ep, Vp = Ep[0], float(Vp[0])
    D.step("Coulomb field of one charge", r"\mathbf E_i=\frac{q_i}{4\pi\varepsilon_0}\frac{\mathbf R-\mathbf R_i}{|\mathbf R-\mathbf R_i|^3}")
    D.step("Superposition", r"\mathbf E=\sum_i\mathbf E_i,\qquad V=\sum_i\frac{q_i}{4\pi\varepsilon_0|\mathbf R-\mathbf R_i|}")
    if ground:
        D.step("Image charges", r"q'_i=-q_i\ \text{at}\ (x_i,-y_i):\ V(y=0)=0\ \text{everywhere on the plane}",
               note="valid only in the region y > 0")
    D.step("Field at probe", rf"\mathbf E=({fmt(Ep[0])},\ {fmt(Ep[1])})", Ep[:2], "V/m")
    D.step("|E| at probe", rf"|\mathbf E|={fmt(np.linalg.norm(Ep))}", np.linalg.norm(Ep), "V/m")
    D.step("Potential at probe", rf"V={fmt(Vp)}", Vp, "V")

    # ---------- independent checks
    hh = 1e-4 * dmin
    grad = np.array([(field_at(Q, (P + hh * e)[None])[1][0] - field_at(Q, (P - hh * e)[None])[1][0]) / (2 * hh) for e in np.eye(3)])
    D.check(r"\mathbf E=-\nabla V \text{ at probe}", 0.0, np.linalg.norm(Ep + grad), 1e-6,
            "central differences of V",
            # scale by the strongest single-charge field, so the check stays meaningful where the fields cancel (E ≈ 0)
            scale=max(np.linalg.norm(Ep), max(np.linalg.norm(field_at(Q[i:i + 1], P[None])[0][0]) for i in range(len(Q)))))
    lap = sum(field_at(Q, (P + hh * e)[None])[1][0] + field_at(Q, (P - hh * e)[None])[1][0] for e in np.eye(3)) - 6 * Vp
    lap /= hh * hh
    D.check(r"\nabla^2V=0 \text{ (charge-free point)}", 0.0, lap, 1e-3, "7-point Laplacian",
            scale=abs(K_E * qmax) / dmin ** 3)
    # ∮E·dl around a small square = 0 (conservative field)
    a = 0.2 * dmin
    sq = np.array([[a, a], [-a, a], [-a, -a], [a, -a], [a, a]]) + P[:2]
    tt, ww = np.polynomial.legendre.leggauss(16)
    circ = 0.0
    for p0, p1 in zip(sq[:-1], sq[1:]):
        pts = (p0 + p1) / 2 + np.outer(tt, (p1 - p0) / 2)
        Es, _ = field_at(Q, np.c_[pts, np.zeros(len(pts))])
        circ += np.sum(ww * (Es[:, :2] @ ((p1 - p0) / 2)))
    D.check(r"\oint\mathbf E\cdot d\mathbf l=0 \text{ (square around probe)}", 0.0, circ, 1e-9,
            "Gauss–Legendre line integral", scale=np.linalg.norm(Ep) * 8 * a)
    for i, (q, x, y, _) in enumerate(real):
        others = np.delete(Q[:, 1:], i, axis=0)
        rs = 0.4 * (np.min(np.linalg.norm(others - [x, y, 0], axis=1)) if len(others) else span)
        D.check(rf"\oint\mathbf E\cdot d\mathbf s=q_{{{i + 1}}}/\varepsilon_0 \text{{ (sphere around }}q_{{{i + 1}}})",
                q / EPS0, _sphere_flux(Q, [x, y, 0], rs), 1e-9, f"48×96 Gauss–Legendre surface integral, r = {rs:.3g} m")
    if not ground and len(real) > 1:
        Rbig = 3 * (np.abs(pos).max() + span * 0.1)
        D.check(r"\oint\mathbf E\cdot d\mathbf s=Q_{tot}/\varepsilon_0 \text{ (sphere around all)}",
                real[:, 0].sum() / EPS0, _sphere_flux(Q, [0, 0, 0], Rbig), 1e-6, f"r = {Rbig:.3g} m",
                scale=np.abs(real[:, 0]).sum() / EPS0)
    if ground:
        xp = np.linspace(-3 * span, 3 * span, 201)
        _, Vplane = field_at(Q, np.c_[xp, 0 * xp, 0 * xp])
        D.check(r"V=0 \text{ on the plane } y=0", 0.0, np.abs(Vplane).max(), 1e-12, "201 sample points", scale=Vc)
        # each charge's share of ρs (from it and its image) is circularly symmetric about the point below it,
        # so integrate ε0·E_y over the plane as a radial integral per charge and add (superposition)
        def share(i):
            Qi, xi = np.vstack([real[i], img[i]]), real[i, 1]
            f = lambda s: EPS0 * field_at(Qi, np.array([[xi + s, 0.0, 0.0]]))[0][0, 1] * 2 * np.pi * s
            return integrate.quad(f, 0, np.inf, epsabs=1e-14 * qmax, epsrel=1e-10, limit=200)[0]
        Qind = sum(share(i) for i in range(len(real)))
        D.check(r"\iint\rho_s\,ds=-\sum q_i \text{ (induced charge on plane)}", -real[:, 0].sum(), Qind, 1e-5,
                r"ρs = ε0 E_y at y = 0⁺, integrated over the infinite plane (radial quad per charge)", scale=np.abs(real[:, 0]).sum())

    return {**D.out(E=Ep[:2], E_mag=np.linalg.norm(Ep), V=Vp),
            "contributions": [{k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in c.items()} for c in contrib],
            "grid": {"x": xs.tolist(), "y": ys.tolist(), "Emag": np.nan_to_num(np.log10(np.maximum(Emag, 1e-30)), nan=0).tolist()},
            "equipotentials": equip, "field_lines": flines, "levels": levels, "V_clip": Vc,
            "charges": [{"q": float(q), "x": float(x), "y": float(y), "image": i >= len(real)} for i, (q, x, y, _) in enumerate(Q)]}


# ---------------------------------------------------------------- Gauss's law
GAUSS = {
    "sphere":   ("spherical", "Uniformly charged sphere (ρv, radius a)"),
    "shell":    ("spherical", "Spherical shell (ρs on R = a)"),
    "line":     ("cylindrical", "Infinite line charge (ρl)"),
    "cylinder": ("cylindrical", "Uniformly charged cylinder (ρv, radius a)"),
    "coax":     ("cylindrical", "Coaxial line (+ρl on r = a, −ρl on r = b)"),
    "sheet":    ("planar", "Infinite sheet (ρs on x = 0)"),
    "slab":     ("planar", "Uniform slab (ρv, |x| < a)"),
}


def _gauss_model(kind, rho, a, b, eps):
    """Closed forms: Q_enc(r) (per length / per area as appropriate), E(r), V(r), ρ(r)."""
    if kind == "sphere":
        Qe = lambda r: rho * 4 / 3 * np.pi * np.minimum(r, a) ** 3
        V = lambda r: np.where(r >= a, Qe(r) / (4 * np.pi * eps * r), rho / (6 * eps) * (3 * a * a - r * r))
        dens = lambda r: np.where(r < a, rho, 0.0)
    elif kind == "shell":
        Qe = lambda r: np.where(r > a, 4 * np.pi * a * a * rho, 0.0)
        V = lambda r: 4 * np.pi * a * a * rho / (4 * np.pi * eps * np.maximum(r, a))
        dens = lambda r: 0 * r
    elif kind == "line":
        Qe = lambda r: rho + 0 * r
        V = lambda r: rho / (2 * np.pi * eps) * np.log(b / r)
        dens = lambda r: 0 * r
    elif kind == "cylinder":
        Qe = lambda r: rho * np.pi * np.minimum(r, a) ** 2
        V = lambda r: np.where(r >= a, rho * a * a / (2 * eps) * np.log(b / r),
                               rho * a * a / (2 * eps) * np.log(b / a) + rho * (a * a - r * r) / (4 * eps))
        dens = lambda r: np.where(r < a, rho, 0.0)
    elif kind == "coax":
        Qe = lambda r: np.where((r > a) & (r < b), rho, 0.0)
        V = lambda r: np.where(r <= a, rho / (2 * np.pi * eps) * np.log(b / a),
                               np.where(r < b, rho / (2 * np.pi * eps) * np.log(b / np.maximum(r, a)), 0.0))
        dens = lambda r: 0 * r
    elif kind == "sheet":
        Qe = lambda r: rho + 0 * r
        V = lambda r: -rho * np.abs(r) / (2 * eps)
        dens = lambda r: 0 * r
    elif kind == "slab":
        Qe = lambda r: 2 * rho * np.minimum(np.abs(r), a)
        V = lambda r: np.where(np.abs(r) < a, -rho * r * r / (2 * eps), -rho * a * (2 * np.abs(r) - a) / (2 * eps))
        dens = lambda r: np.where(np.abs(r) < a, rho, 0.0)
    else:
        raise ValueError(f"kind must be one of {list(GAUSS)}")
    geo = GAUSS[kind][0]
    area = {"spherical": lambda r: 4 * np.pi * r * r, "cylindrical": lambda r: 2 * np.pi * r, "planar": lambda r: 2 + 0 * r}[geo]
    if geo == "planar":   # field is odd in x for symmetric planar charge
        E = lambda r: np.sign(r) * Qe(r) / (eps * area(r))
    else:
        E = lambda r: Qe(r) / (eps * area(r))
    return Qe, E, V, dens, area, geo


def gauss(kind, rho, a=0.1, b=0.3, eps_r=1.0, r=0.05, rmax=None, n=400):
    """rho is ρv (C/m³), ρs (C/m²) or ρl (C/m) depending on `kind`; b is the outer
    radius (coax) or the zero-potential reference radius (line, cylinder)."""
    if kind not in GAUSS:
        raise ValueError(f"kind must be one of {list(GAUSS)}")
    if a <= 0 or eps_r <= 0 or r <= 0:
        raise ValueError("need a > 0, εr > 0, r > 0")
    if kind in ("coax", "line", "cylinder") and b <= a:
        raise ValueError("need b > a")
    eps = EPS0 * eps_r
    Qe, E, V, dens, area, geo = _gauss_model(kind, rho, a, b, eps)
    D = Derivation()
    sym = {"spherical": "R", "cylindrical": "r", "planar": "x"}[geo]
    surf = {"spherical": r"\text{sphere of radius }R:\ \oint ds=4\pi R^2",
            "cylindrical": r"\text{cylinder radius }r,\ \text{length }\ell:\ \text{side area }2\pi r\ell",
            "planar": r"\text{pill-box of face area }A\text{ from }-x\text{ to }x:\ 2A"}[geo]
    D.step("Gauss's law", r"\oint_S\mathbf D\cdot d\mathbf s=Q_{enc}")
    D.step("Symmetry → Gaussian surface", surf,
           note="by symmetry D is normal to the surface and constant on it, so the integral becomes |D| × area")
    q = float(Qe(r))
    unit_q = {"spherical": "C", "cylindrical": "C/m", "planar": "C/m²"}[geo]
    D.step("Enclosed charge", rf"Q_{{enc}}({sym}={fmt(r)})={fmt(q)}", q, unit_q,
           note={"spherical": "", "cylindrical": "per unit length", "planar": "per unit face area"}[geo])
    Dn = q / float(area(r))
    D.step("Flux density", rf"D_{sym}=Q_{{enc}}/\text{{area}}={fmt(Dn)}", Dn, "C/m²")
    Er = Dn / eps
    D.step("Field", rf"E_{sym}=D_{sym}/\varepsilon={fmt(Er)}", Er, "V/m")
    Vr = float(V(r))
    D.step("Potential", rf"V({sym})=-\int_{{\text{{ref}}}}^{{{sym}}}\mathbf E\cdot d\mathbf l={fmt(Vr)}", Vr, "V",
           note={"sphere": "reference V(∞) = 0", "shell": "reference V(∞) = 0", "line": "reference V(b) = 0",
                 "cylinder": "reference V(b) = 0", "coax": "reference: outer conductor V(b) = 0",
                 "sheet": "reference V(0) = 0", "slab": "reference V(0) = 0"}[kind])

    # ---- checks
    if kind in ("sphere", "cylinder", "slab"):
        w = {"spherical": lambda s: 4 * np.pi * s * s, "cylindrical": lambda s: 2 * np.pi * s, "planar": lambda s: 2.0}[geo]
        num, _ = integrate.quad(lambda s: float(dens(s)) * w(s), 0, r, points=[a] if a < r else None, epsrel=1e-12)
        D.check(r"Q_{enc}=\int\rho_v\,dv \text{ (numerical)}", q, num, 1e-9, "scipy quad over the Gaussian volume")
    ref = {"sphere": np.inf, "shell": np.inf, "line": b, "cylinder": b, "coax": b, "sheet": 0.0, "slab": 0.0}[kind]
    f = lambda s: float(E(s))
    pts = [p for p in (a, b) if min(r, ref) < p < max(r, ref)] if np.isfinite(ref) else None
    if np.isinf(ref):
        Vn = integrate.quad(f, r, a)[0] + integrate.quad(f, max(a, r), np.inf)[0] if r < a else integrate.quad(f, r, np.inf)[0]
    else:
        Vn = integrate.quad(f, r, ref, points=pts, limit=200)[0] if r != ref else 0.0
    D.check(r"V=-\int\mathbf E\cdot d\mathbf l \text{ (numerical)}", Vr, Vn, 1e-7, "scipy quad of E from r to reference",
            scale=max(abs(Vr), abs(float(V(a))), 1e-30))
    hh = 1e-6 * max(r, a)
    if all(abs(r - p) > 10 * hh for p in (a, b)):
        g = {"spherical": lambda s: s * s, "cylindrical": lambda s: s, "planar": lambda s: 1.0}[geo]
        div = (g(r + hh) * eps * f(r + hh) - g(r - hh) * eps * f(r - hh)) / (2 * hh) / g(r)
        D.check(r"\nabla\cdot\mathbf D=\rho_v \text{ at the Gaussian radius}", float(dens(r)), div, 1e-6,
                "central difference of the radial divergence", scale=max(abs(rho), 1e-30) if kind in ("sphere", "cylinder", "slab") else abs(Dn / max(r, a)) + 1e-30)
    if kind == "coax":
        hh2 = 1e-9 * a
        D.check(r"D_n^{+}-D_n^{-}=\rho_s \text{ at } r=a", rho / (2 * np.pi * a), eps * (f(a + hh2) - f(a - hh2)), 1e-6,
                "boundary condition on the inner conductor")
    elif kind == "sheet":
        D.check(r"D_x(0^+)-D_x(0^-)=\rho_s", rho, eps * (f(1e-9) - f(-1e-9)), 1e-9, "boundary condition on the sheet")
    elif kind != "line":
        hh2 = 1e-9 * a
        D.check(rf"D_n^+-D_n^-=\rho_s \text{{ at }} {sym}=a", rho if kind == "shell" else 0.0,
                eps * (f(a + hh2) - f(a - hh2)), 1e-6, "boundary condition", scale=max(abs(eps * f(a + hh2)), 1e-30))

    rmax = rmax or (3 * b if kind in ("coax", "line", "cylinder") else 3 * a)
    lo = -rmax if geo == "planar" else rmax * 1e-3
    s = np.linspace(lo, rmax, n)
    if geo == "planar":
        s = s[np.abs(s) > 1e-12]
    Ev = E(s)
    return {**D.out(Q_enc=q, D=Dn, E=Er, V=Vr), "geometry": geo, "title": GAUSS[kind][1],
            "profile": {"r": s.tolist(), "E": Ev.tolist(), "V": V(s).tolist(), "Q": Qe(s).tolist()},
            "a": a, "b": b, "r": r}


# ---------------------------------------------------------------- capacitors
DIELECTRIC_STRENGTH_AIR = 3e6  # V/m


def capacitor(kind, V0=1.0, eps_r=1.0, A=1e-2, d=1e-3, a=1e-3, b=3.5e-3, length=1.0, E_bd=DIELECTRIC_STRENGTH_AIR, n=300):
    if V0 <= 0 or eps_r <= 0:
        raise ValueError("need V0 > 0 and εr > 0")
    eps = EPS0 * eps_r
    D = Derivation()
    D.step("Method", r"\text{assume }\pm Q\ \to\ \mathbf E\text{ by Gauss}\ \to\ V=-\int_{-}^{+}\mathbf E\cdot d\mathbf l\ \to\ C=Q/V")
    if kind == "parallel":
        if A <= 0 or d <= 0:
            raise ValueError("need A > 0, d > 0")
        C = eps * A / d
        E = lambda s: V0 / d + 0 * s
        lo, hi, w = 0.0, d, lambda s: A
        D.step("Field (fringing neglected)", rf"E=\frac{{\rho_s}}{{\varepsilon}}=\frac{{Q}}{{\varepsilon A}},\quad V=Ed\ \Rightarrow\ C=\frac{{\varepsilon A}}{{d}}={fmt(C)}", C, "F")
    elif kind == "coax":
        if not 0 < a < b or length <= 0:
            raise ValueError("need 0 < a < b and length > 0")
        C = 2 * np.pi * eps * length / np.log(b / a)
        E = lambda s: V0 / (s * np.log(b / a))
        lo, hi, w = a, b, lambda s: 2 * np.pi * s * length
        D.step("Field", r"E_r=\frac{Q}{2\pi\varepsilon\ell r},\quad V=\frac{Q}{2\pi\varepsilon\ell}\ln\frac{b}{a}")
        D.step("Capacitance", rf"C=\frac{{2\pi\varepsilon\ell}}{{\ln(b/a)}}={fmt(C)}", C, "F",
               note=f"per metre: {C / length:.4g} F/m. For fixed b, E_max is smallest when b/a = e ≈ 2.718")
    elif kind == "spherical":
        if not 0 < a < b:
            raise ValueError("need 0 < a < b")
        C = 4 * np.pi * eps * a * b / (b - a)
        E = lambda s: V0 * a * b / ((b - a) * s * s)
        lo, hi, w = a, b, lambda s: 4 * np.pi * s * s
        D.step("Field", r"E_R=\frac{Q}{4\pi\varepsilon R^2},\quad V=\frac{Q}{4\pi\varepsilon}\left(\frac1a-\frac1b\right)")
        D.step("Capacitance", rf"C=\frac{{4\pi\varepsilon ab}}{{b-a}}={fmt(C)}", C, "F")
    else:
        raise ValueError("kind must be parallel, coax or spherical")
    Q = C * V0
    W = 0.5 * C * V0 ** 2
    Emax = float(E(lo))
    D.step("Charge", rf"Q=CV_0={fmt(Q)}", Q, "C")
    D.step("Stored energy", rf"W_e=\tfrac12CV_0^2={fmt(W)}", W, "J")
    D.step("Maximum field", rf"E_{{max}}={fmt(Emax)}", Emax, "V/m",
           note=f"{100 * Emax / E_bd:.3g} % of the dielectric strength {E_bd:.3g} V/m")
    D.step("Breakdown voltage", rf"V_{{bd}}=V_0\,E_{{bd}}/E_{{max}}={fmt(V0 * E_bd / Emax)}", V0 * E_bd / Emax, "V")

    def quad_r(g):   # radial geometries: integrate in u = ln r so 1/r^n integrands stay smooth for any b/a
        if lo > 0:
            return integrate.quad(lambda u: g(np.exp(u)) * np.exp(u), np.log(lo), np.log(hi), epsrel=1e-13)[0]
        return integrate.quad(g, lo, hi, epsrel=1e-12)[0]
    Vn = quad_r(lambda s: float(E(s)))
    D.check(r"\int_a^b E\,dl=V_0", V0, Vn, 1e-10, "scipy quad of the Gauss field")
    Wn = quad_r(lambda s: 0.5 * eps * float(E(s)) ** 2 * w(s))
    D.check(r"\tfrac12CV_0^2=\int\tfrac12\varepsilon E^2\,dv", W, Wn, 1e-9, "field-energy integral over the dielectric")
    s1, s2 = lo + 0.25 * (hi - lo), lo + 0.75 * (hi - lo)
    D.check(r"Q=\oint\mathbf D\cdot d\mathbf s \text{ same on any surface between plates}",
            eps * float(E(s1)) * w(s1), eps * float(E(s2)) * w(s2), 1e-12, "Gauss at two different radii")
    if kind == "coax":
        pp = eps * 2 * np.pi * a * length / (b - a)
        D.check(r"b\to a:\ C\to\varepsilon(2\pi a\ell)/(b-a) \text{ (parallel-plate limit)}", pp, C, (b - a) / a,
                "approximation, error ≈ (b−a)/2a")
    s = np.linspace(lo, hi, n)
    Vs = np.array([V0 - integrate.quad(lambda t: float(E(t)), lo, x)[0] for x in s[:: max(n // 60, 1)]])
    return {**D.out(C=C, Q=Q, W=W, E_max=Emax, V_bd=V0 * E_bd / Emax),
            "profile": {"s": s.tolist(), "E": [float(E(x)) for x in s], "sV": s[:: max(n // 60, 1)].tolist(), "V": Vs.tolist()}}
