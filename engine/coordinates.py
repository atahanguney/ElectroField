"""Orthogonal coordinate systems (Ulaby ch. 3, Cheng ch. 2 notation).

Cartesian (x, y, z) | Cylindrical (r, phi, z) | Spherical (R, theta, phi)
Angles are radians internally. Lengths in metres.

Everything follows from the metric scale factors h_i = |dr/du_i|:
    dl  = sum_i  u_i_hat h_i du_i
    ds_i = h_j h_k du_j du_k
    dv  = h1 h2 h3 du1 du2 du3   (= |det J|)
The checks verify that numerically from the coordinate map itself.
"""
import numpy as np
from scipy import integrate
from .derivation import Derivation, fmt

SYSTEMS = {
    "cartesian":   {"coords": ["x", "y", "z"], "tex": ["x", "y", "z"], "angle": [0, 0, 0]},
    "cylindrical": {"coords": ["r", "phi", "z"], "tex": ["r", r"\phi", "z"], "angle": [0, 1, 0]},
    "spherical":   {"coords": ["R", "theta", "phi"], "tex": ["R", r"\theta", r"\phi"], "angle": [0, 1, 1]},
}

# symbolic scale factors, dl, ds, dv as TeX (shown next to the numbers)
TEX = {
    "cartesian": {"h": ["1", "1", "1"],
                  "dl": r"d\mathbf{l}=\hat{x}\,dx+\hat{y}\,dy+\hat{z}\,dz",
                  "ds": [r"ds_x=dy\,dz", r"ds_y=dx\,dz", r"ds_z=dx\,dy"],
                  "dv": r"dv=dx\,dy\,dz"},
    "cylindrical": {"h": ["1", "r", "1"],
                    "dl": r"d\mathbf{l}=\hat{r}\,dr+\hat{\phi}\,r\,d\phi+\hat{z}\,dz",
                    "ds": [r"ds_r=r\,d\phi\,dz", r"ds_\phi=dr\,dz", r"ds_z=r\,dr\,d\phi"],
                    "dv": r"dv=r\,dr\,d\phi\,dz"},
    "spherical": {"h": ["1", "R", r"R\sin\theta"],
                  "dl": r"d\mathbf{l}=\hat{R}\,dR+\hat{\theta}\,R\,d\theta+\hat{\phi}\,R\sin\theta\,d\phi",
                  "ds": [r"ds_R=R^2\sin\theta\,d\theta\,d\phi", r"ds_\theta=R\sin\theta\,dR\,d\phi",
                         r"ds_\phi=R\,dR\,d\theta"],
                  "dv": r"dv=R^2\sin\theta\,dR\,d\theta\,d\phi"},
}


def to_cart(system, u1, u2, u3):
    if system == "cartesian":
        return np.asarray(u1, float), np.asarray(u2, float), np.asarray(u3, float)
    if system == "cylindrical":
        return u1 * np.cos(u2), u1 * np.sin(u2), u3 + 0 * u1
    if system == "spherical":
        return (u1 * np.sin(u2) * np.cos(u3), u1 * np.sin(u2) * np.sin(u3), u1 * np.cos(u2))
    raise ValueError(f"unknown system {system!r}")


def from_cart(system, x, y, z):
    if system == "cartesian":
        return np.array([x, y, z], float)
    if system == "cylindrical":
        return np.array([np.hypot(x, y), np.arctan2(y, x) % (2 * np.pi), z])
    R = np.sqrt(x * x + y * y + z * z)
    th = np.arccos(z / R) if R > 0 else 0.0
    return np.array([R, th, np.arctan2(y, x) % (2 * np.pi)])


def scale_factors(system, u):
    u1, u2, _ = u
    return {"cartesian": np.array([1.0, 1.0, 1.0]),
            "cylindrical": np.array([1.0, u1, 1.0]),
            "spherical": np.array([1.0, u1, u1 * np.sin(u2)])}[system]


def unit_vectors(system, u):
    """3x3 matrix whose columns are u1_hat, u2_hat, u3_hat in Cartesian components."""
    _, u2, u3 = u
    if system == "cartesian":
        return np.eye(3)
    if system == "cylindrical":
        c, s = np.cos(u2), np.sin(u2)
        return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]])
    st, ct, sp, cp = np.sin(u2), np.cos(u2), np.sin(u3), np.cos(u3)
    return np.array([[st * cp, ct * cp, -sp], [st * sp, ct * sp, cp], [ct, -st, 0.0]])


def jacobian_numeric(system, u, h=1e-6):
    """Central-difference d(x,y,z)/d(u1,u2,u3) straight from the coordinate map."""
    J = np.zeros((3, 3))
    for i in range(3):
        up, um = np.array(u, float), np.array(u, float)
        up[i] += h
        um[i] -= h
        J[:, i] = (np.array(to_cart(system, *up)) - np.array(to_cart(system, *um))) / (2 * h)
    return J


def _exact_finite_volume(system, u, d):
    a, b = np.asarray(u, float), np.asarray(u, float) + d
    if system == "cartesian":
        return float(np.prod(d))
    if system == "cylindrical":
        return (b[0] ** 2 - a[0] ** 2) / 2 * d[1] * d[2]
    return (b[0] ** 3 - a[0] ** 3) / 3 * (np.cos(a[1]) - np.cos(b[1])) * d[2]


def _faces(system, u, d, n=10):
    """Six curved faces of the finite element [u, u+d] as surface grids."""
    out = []
    for i in range(3):
        j, k = [m for m in range(3) if m != i]
        s = np.linspace(u[j], u[j] + d[j], n)
        t = np.linspace(u[k], u[k] + d[k], n)
        S, T = np.meshgrid(s, t)
        for side in (0, 1):
            g = [None] * 3
            g[i] = np.full_like(S, u[i] + side * d[i])
            g[j], g[k] = S, T
            x, y, z = to_cart(system, *g)
            out.append({"axis": i, "side": side, "x": x.tolist(), "y": y.tolist(), "z": z.tolist()})
    return out


def _edges(system, u, d, n=24):
    """The three dl edges leaving the corner point (the ones Ulaby draws)."""
    out = []
    for i in range(3):
        g = [np.full(n, float(u[m])) for m in range(3)]
        g[i] = np.linspace(u[i], u[i] + d[i], n)
        x, y, z = to_cart(system, *g)
        out.append({"axis": i, "x": x.tolist(), "y": y.tolist(), "z": z.tolist()})
    return out


# ---------------------------------------------------------------------------
# Dimensioned drawings (Ulaby Figs. 3-8 … 3-10 style): 2-D sections and 3-D guides.
# Pure geometry generated from the same map, so labels always match the numbers.
def _arc(r, a0, a1, n=48, cx=0.0, cy=0.0, from_vertical=False):
    t = np.linspace(a0, a1, n)
    if from_vertical:            # angle measured from +vertical axis (θ in a meridian plane)
        return (cx + r * np.sin(t)).tolist(), (cy + r * np.cos(t)).tolist()
    return (cx + r * np.cos(t)).tolist(), (cy + r * np.sin(t)).tolist()


class _View:
    def __init__(self, title, xlabel, ylabel):
        self.d = {"title": title, "xlabel": xlabel, "ylabel": ylabel, "paths": [], "labels": []}

    def path(self, x, y, kind, closed=False):
        x, y = list(map(float, x)), list(map(float, y))
        if closed:
            x, y = x + x[:1], y + y[:1]
        self.d["paths"].append({"x": x, "y": y, "kind": kind})

    def label(self, x, y, text, kind="dim"):
        self.d["labels"].append({"x": float(x), "y": float(y), "text": text, "kind": kind})


def _m(v):
    return f"{v:.3g} m"


def _deg(v):
    return f"{np.degrees(v):.1f}°"


def _sector(view, s0, s1, t0, t1, vertical, edges):
    """Annular sector between radii s0..s1 and angles t0..t1, edges = (radial kind, arc kind)."""
    ai = _arc(s0, t0, t1, from_vertical=vertical)
    ao = _arc(s1, t1, t0, from_vertical=vertical)
    view.path(ai[0] + ao[0], ai[1] + ao[1], "element", closed=True)
    f = (lambda s, t: (s * np.sin(t), s * np.cos(t))) if vertical else (lambda s, t: (s * np.cos(t), s * np.sin(t)))
    p0, p1 = f(s0, t0), f(s1, t0)
    view.path([p0[0], p1[0]], [p0[1], p1[1]], edges[0])
    view.path(*ai, edges[1])
    return f


def views(system, u, d):
    u1, u2, u3 = map(float, u)
    d1, d2, d3 = map(float, d)
    out = []
    if system == "cartesian":
        for (a, b, da, db, na, nb, ka, kb) in ((u1, u2, d1, d2, "x", "y", "edge0", "edge1"),
                                              (u1, u3, d1, d3, "x", "z", "edge0", "edge2")):
            v = _View(f"{na}{nb}-plane projection", f"{na} (m)", f"{nb} (m)")
            v.path([a, a + da, a + da, a], [b, b, b + db, b + db], "element", closed=True)
            v.path([a, a + da], [b, b], ka)
            v.path([a, a], [b, b + db], kb)
            v.path([0, a], [b, b], "guide"); v.path([a, a], [0, b], "guide")
            v.label(a + da / 2, b, f"d{na} = {_m(da)}", ka); v.label(a, b + db / 2, f"d{nb} = {_m(db)}", kb)
            v.label(a / 2, b, f"{na} = {_m(a)}", "guide"); v.label(a, b / 2, f"{nb} = {_m(b)}", "guide")
            out.append(v.d)
        return out

    if system == "cylindrical":
        r, ph, z, dr, dph, dz = u1, u2, u3, d1, d2, d3
        v = _View("Top view — plane z = const", "x (m)", "y (m)")
        v.path(*_arc(r, 0, 2 * np.pi, 120), "faint")
        v.path([0, (r + dr) * 1.15], [0, 0], "axis")
        for t in (ph, ph + dph):
            v.path([0, (r + dr) * np.cos(t)], [0, (r + dr) * np.sin(t)], "guide")
        f = _sector(v, r, r + dr, ph, ph + dph, False, ("edge0", "edge1"))
        v.path(*_arc(0.3 * r, 0, ph), "angle")
        v.label(*f(0.3 * r + 0.08 * r, ph / 2), f"φ = {_deg(ph)}", "angle")
        v.label(*f(r / 2, ph), f"r = {_m(r)}", "guide")
        v.label(*f(r + dr / 2, ph - 0.12), f"dr = {_m(dr)}", "edge0")
        v.label(*f(r - 0.12 * r, ph + dph / 2), f"r dφ = {_m(r * dph)}", "edge1")
        v.label(*f(r + dr + 0.12 * r, ph + dph / 2), f"dφ = {_deg(dph)}", "angle")
        out.append(v.d)
        v = _View("Side view — half-plane φ = const", "distance from z-axis r (m)", "z (m)")
        v.path([0, 0], [min(0, z) - 0.2, max(0, z + dz) + 0.3], "axis")
        v.path([0, (r + dr) * 1.2], [0, 0], "axis")
        v.path([r, r + dr, r + dr, r], [z, z, z + dz, z + dz], "element", closed=True)
        v.path([r, r + dr], [z, z], "edge0"); v.path([r, r], [z, z + dz], "edge2")
        v.path([0, r], [z, z], "guide"); v.path([r, r], [0, z], "guide")
        v.label(r / 2, z, f"r = {_m(r)}", "guide"); v.label(r, z / 2 if z else -0.1, f"z = {_m(z)}", "guide")
        v.label(r + dr / 2, z, f"dr = {_m(dr)}", "edge0"); v.label(r, z + dz / 2, f"dz = {_m(dz)}", "edge2")
        out.append(v.d)
        return out

    R, th, ph, dR, dth, dph = u1, u2, u3, d1, d2, d3
    v = _View("Meridian section — half-plane φ = const", "distance from z-axis (m)", "z (m)")
    v.path([0, 0], [-(R + dR) * 1.1, (R + dR) * 1.15], "axis")
    v.path([0, (R + dR) * 1.15], [0, 0], "axis")
    v.path(*_arc(R, 0, np.pi, 90, from_vertical=True), "faint")
    v.path([0, (R + dR) * np.sin(th)], [0, (R + dR) * np.cos(th)], "guide")
    f = _sector(v, R, R + dR, th, th + dth, True, ("edge0", "edge1"))
    v.path(*_arc(0.3 * R, 0, th, from_vertical=True), "angle")
    v.label(*f(0.38 * R, th / 2), f"θ = {_deg(th)}", "angle")
    v.label(*f(R / 2, th - 0.1), f"R = {_m(R)}", "guide")
    v.label(*f(R + dR / 2, th - 0.12), f"dR = {_m(dR)}", "edge0")
    v.label(*f(R * 0.86, th + dth / 2), f"R dθ = {_m(R * dth)}", "edge1")
    rho = R * np.sin(th)
    v.path([0, rho], [R * np.cos(th)] * 2, "guide2")
    v.label(rho / 2, R * np.cos(th), f"R sinθ = {_m(rho)}", "guide2")
    out.append(v.d)
    v = _View("Top view — the circle of radius R sinθ swept by dφ", "x (m)", "y (m)")
    v.path([0, rho * 1.3 + 0.1], [0, 0], "axis")
    v.path(*_arc(rho, 0, 2 * np.pi, 120), "guide2")
    for t in (ph, ph + dph):
        v.path([0, rho * np.cos(t)], [0, rho * np.sin(t)], "guide")
    v.path(*_arc(rho, ph, ph + dph), "edge2")
    v.path(*_arc(0.3 * max(rho, 1e-3), 0, ph), "angle")
    g = lambda s, t: (s * np.cos(t), s * np.sin(t))
    v.label(*g(0.38 * rho, ph / 2), f"φ = {_deg(ph)}", "angle")
    v.label(*g(rho * 1.12, ph + dph / 2), f"R sinθ dφ = {_m(rho * dph)}", "edge2")
    v.label(*g(rho * 0.5, ph + dph), f"R sinθ = {_m(rho)}", "guide2")
    out.append(v.d)
    return out


def guides3d(system, u, d):
    """Construction lines in 3-D: projections and angle arcs that locate the point."""
    u1, u2, u3 = map(float, u)
    L, lab = [], []
    if system == "cylindrical":
        r, ph, z = u1, u2, u3
        L.append({"x": [0, r * np.cos(ph), r * np.cos(ph)], "y": [0, r * np.sin(ph), r * np.sin(ph)], "z": [0, 0, z], "kind": "guide"})
        ax, ay = _arc(0.4 * r, 0, ph)
        L.append({"x": ax, "y": ay, "z": [0] * len(ax), "kind": "angle"})
        lab += [{"x": 0.5 * r * np.cos(ph / 2), "y": 0.5 * r * np.sin(ph / 2), "z": 0, "text": "φ"},
                {"x": r * np.cos(ph) / 2, "y": r * np.sin(ph) / 2, "z": 0, "text": "r"}]
    elif system == "spherical":
        R, th, ph = u1, u2, u3
        p = np.array(to_cart(system, R, th, ph), float)
        L.append({"x": [0, p[0]], "y": [0, p[1]], "z": [0, p[2]], "kind": "guide"})
        L.append({"x": [p[0], p[0], 0], "y": [p[1], p[1], 0], "z": [p[2], 0, 0], "kind": "guide"})
        t = np.linspace(0, th, 30)
        x, y, zz = to_cart(system, 0.4 * R + 0 * t, t, ph + 0 * t)
        L.append({"x": x.tolist(), "y": y.tolist(), "z": zz.tolist(), "kind": "angle"})
        ax, ay = _arc(0.4 * R * max(np.sin(th), 0.3), 0, ph)
        L.append({"x": ax, "y": ay, "z": [0] * len(ax), "kind": "angle"})
        q = np.array(to_cart(system, 0.5 * R, th / 2, ph), float)
        lab += [{"x": q[0], "y": q[1], "z": q[2], "text": "θ"},
                {"x": 0.5 * R * np.cos(ph / 2), "y": 0.5 * R * np.sin(ph / 2), "z": 0, "text": "φ"},
                {"x": p[0] / 2, "y": p[1] / 2, "z": p[2] / 2, "text": "R"}]
    else:
        L.append({"x": [0, u1, u1, u1], "y": [0, 0, u2, u2], "z": [0, 0, 0, u3], "kind": "guide"})
    return {"lines": L, "labels": [{k: (float(v) if k != "text" else v) for k, v in l.items()} for l in lab]}


def _domain(system, u):
    if system == "cylindrical" and u[0] < 0:
        raise ValueError("r must be >= 0")
    if system == "spherical":
        if u[0] < 0:
            raise ValueError("R must be >= 0")
        if not 0 <= u[1] <= np.pi:
            raise ValueError("theta must lie in [0, 180] degrees")


def integral_checks(D, system, a=1.0, height=1.0):
    """Integrate the volume/surface elements over a whole body; compare to geometry."""
    if system == "spherical":
        V, _ = integrate.tplquad(lambda p, t, R: R * R * np.sin(t), 0, a, 0, np.pi, 0, 2 * np.pi)
        S, _ = integrate.dblquad(lambda p, t: a * a * np.sin(t), 0, np.pi, 0, 2 * np.pi)
        D.check(r"\int dv \text{ over sphere } = \tfrac43\pi a^3", 4 / 3 * np.pi * a ** 3, V, 1e-8, "scipy tplquad")
        D.check(r"\oint ds_R \text{ over sphere } = 4\pi a^2", 4 * np.pi * a ** 2, S, 1e-8, "scipy dblquad")
    elif system == "cylindrical":
        V, _ = integrate.tplquad(lambda z, p, r: r, 0, a, 0, 2 * np.pi, 0, height)
        S, _ = integrate.dblquad(lambda z, p: a, 0, 2 * np.pi, 0, height)
        D.check(r"\int dv \text{ over cylinder } = \pi a^2 h", np.pi * a * a * height, V, 1e-8, "scipy tplquad")
        D.check(r"\int ds_r \text{ (side) } = 2\pi a h", 2 * np.pi * a * height, S, 1e-8, "scipy dblquad")
    else:
        V, _ = integrate.tplquad(lambda z, y, x: 1.0, 0, a, 0, a, 0, a)
        D.check(r"\int dv \text{ over cube } = a^3", a ** 3, V, 1e-10, "scipy tplquad")


def element(system, u, d):
    """Differential element at point u with increments d (SI, radians)."""
    if system not in SYSTEMS:
        raise ValueError(f"unknown system {system!r}")
    u, d = np.asarray(u, float), np.asarray(d, float)
    _domain(system, u)
    S, T = SYSTEMS[system], TEX[system]
    D = Derivation()
    h = scale_factors(system, u)
    ct = S["tex"]

    D.step("Scale factors", r"h_1,h_2,h_3=" + r",\;".join(T["h"]),
           h, note="h_i = |∂r/∂u_i|, the length per unit change of u_i")
    D.step("Differential length", T["dl"])
    dl = h * d
    for i in range(3):
        D.step(f"dl along {S['coords'][i]}",
               rf"dl_{{{ct[i]}}}=h_{i+1}\,d{ct[i]}={fmt(h[i])}\times{fmt(d[i])}={fmt(dl[i])}", dl[i], "m")
    ds = np.array([dl[1] * dl[2], dl[0] * dl[2], dl[0] * dl[1]])
    for i in range(3):
        D.step(f"Surface element ⊥ {S['coords'][i]}", rf"{T['ds'][i]}={fmt(ds[i])}", ds[i], "m²")
    dv = float(np.prod(dl))
    D.step("Volume element", rf"{T['dv']}={fmt(dv)}", dv, "m³")

    # --- independent checks -------------------------------------------------
    J = jacobian_numeric(system, u)
    D.check(r"|\det J| \text{ (finite differences of the map) } = h_1h_2h_3",
            np.prod(h), abs(np.linalg.det(J)), 1e-6, "central differences, step 1e-6")
    U = unit_vectors(system, u)
    D.check(r"\hat u_i\cdot\hat u_j=\delta_{ij}", 0.0, np.abs(U.T @ U - np.eye(3)).max(), 1e-12,
            "max |UᵀU − I|")
    D.check(r"\hat u_1\times\hat u_2=\hat u_3 \text{ (right-handed)}", 0.0,
            np.abs(np.cross(U[:, 0], U[:, 1]) - U[:, 2]).max(), 1e-12, "cross product")
    integral_checks(D, system, a=max(float(u[0]), 0.5) if system != "cartesian" else 1.0)

    exact = _exact_finite_volume(system, u, d)
    conv = []
    for sc in (1, 0.5, 0.25, 0.125, 0.0625):
        ex = _exact_finite_volume(system, u, d * sc)
        ap = float(np.prod(scale_factors(system, u) * d * sc))
        conv.append({"scale": sc, "exact": ex, "approx": ap,
                     "rel_error": abs(ap - ex) / ex if ex else None})

    pt = np.array(to_cart(system, *u), float)
    return {**D.out(scale=h, dl=dl, ds=ds, dv=dv, exact_finite_volume=exact),
            "convergence": conv, "point": pt.tolist(), "unit_vectors": U.T.tolist(),
            "faces": _faces(system, u, d), "edges": _edges(system, u, d),
            "views": views(system, u, d), "guides": guides3d(system, u, d),
            "labels": S["coords"], "tex_labels": ct}


def convert(src, dst, u, A=None):
    """Convert point coordinates (and optionally vector components) between systems."""
    u = np.asarray(u, float)
    _domain(src, u)
    D = Derivation()
    xyz = np.array(to_cart(src, *u), float)
    v = from_cart(dst, *xyz)
    D.step("Point in Cartesian", rf"(x,y,z)=({fmt(xyz[0])},\,{fmt(xyz[1])},\,{fmt(xyz[2])})", xyz, "m")
    back = np.array(to_cart(dst, *v), float)
    D.check("round trip src → dst → Cartesian", 0.0, np.abs(back - xyz).max(), 1e-12, "max abs diff")
    res = {"point": v}
    if A is not None:
        A = np.asarray(A, float)
        Us, Ud = unit_vectors(src, u), unit_vectors(dst, v)
        M = Ud.T @ Us  # entries are dot products  dst_hat_i · src_hat_j
        Ad = M @ A
        D.step("Transformation matrix", r"A'_i=\sum_j(\hat u'_i\cdot\hat u_j)A_j", M)
        D.check(r"|\mathbf A| \text{ invariant}", np.linalg.norm(A), np.linalg.norm(Ad), 1e-12, "norm")
        res["vector"] = Ad
        res["matrix"] = M
    return {**D.out(**res), "labels": SYSTEMS[dst]["coords"]}
