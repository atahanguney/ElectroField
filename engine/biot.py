"""Biot–Savart law, evaluated as an explicit sum of current elements (Ulaby §5-2, Cheng §6-6).

    dH = I dl × R̂ / (4π R²)          [A/m],   B = μ H
The line integral is computed with N midpoint elements and compared with the closed forms:
  finite segment   H = I/(4πr) (cos θ1 − cos θ2)
  infinite wire    H = I/(2πr)
  circular loop    H_z = I a² / (2 (a² + z²)^{3/2})   (on the axis)
  square loop      H = 2√2 I / (π a)                    (centre, side a)
"""
import numpy as np
from .constants import MU0
from .derivation import Derivation, fmt


def _sum(I, src, dl, P):
    """Σ I dl × R̂ / (4πR²) over elements at positions src (N,3) with vectors dl (N,3)."""
    R = np.asarray(P, float) - src
    Rm = np.linalg.norm(R, axis=1)
    dH = I * np.cross(dl, R) / (4 * np.pi * Rm[:, None] ** 3)
    return dH.sum(0), dH


def _segment_elements(z1, z2, N):
    zs = np.linspace(z1, z2, N + 1)
    mid = 0.5 * (zs[1:] + zs[:-1])
    src = np.stack([0 * mid, 0 * mid, mid], -1)
    dl = np.tile([0.0, 0.0, (z2 - z1) / N], (N, 1))
    return src, dl, mid


def segment(I=1.0, z1=-0.5, z2=0.5, r=0.2, N=200, mu_r=1.0):
    """Straight wire on the z-axis from z1 to z2 carrying I (+z); field point (r, 0, 0)."""
    if r <= 0 or z2 <= z1 or N < 2 or N > 20000:
        raise ValueError("need r > 0, z2 > z1 and 2 ≤ N ≤ 20000")
    D = Derivation()
    D.step("Biot–Savart law", r"d\mathbf H=\frac{I\,d\mathbf l\times\hat{\mathbf R}}{4\pi R^2}\quad[\mathrm{A/m}]",
           note="dl points along the current; R̂ points from the element to the field point")
    D.step("Geometry", r"d\mathbf l=\hat z\,dz,\quad \mathbf R=\hat r\,r-\hat z\,z,\quad d\mathbf l\times\mathbf R=\hat\phi\,r\,dz",
           note="every element gives dH along +φ̂ (right-hand rule), so only magnitudes add")
    c1, c2 = z1 / np.hypot(z1, r), z2 / np.hypot(z2, r)
    H_cf = I / (4 * np.pi * r) * (c2 - c1)
    D.step("Integrate", rf"H_\phi=\frac{{I r}}{{4\pi}}\int_{{z_1}}^{{z_2}}\frac{{dz}}{{(r^2+z^2)^{{3/2}}}}=\frac{{I}}{{4\pi r}}\left[\frac{{z}}{{\sqrt{{r^2+z^2}}}}\right]_{{z_1}}^{{z_2}}={fmt(H_cf)}",
           H_cf, "A/m", note="the bracket is cos θ1 − cos θ2 with θ measured from the wire direction")
    H_inf = I / (2 * np.pi * r)
    D.step("Infinite-wire limit", rf"z_1\to-\infty,\ z_2\to\infty:\ H_\phi=\frac{{I}}{{2\pi r}}={fmt(H_inf)}", H_inf, "A/m")
    src, dl, mid = _segment_elements(z1, z2, N)
    Hn, dH = _sum(I, src, dl, [r, 0, 0])
    D.step("Numerical sum", rf"\mathbf H\approx\sum_{{k=1}}^{{{N}}}\frac{{I\,\Delta\mathbf l_k\times\mathbf R_k}}{{4\pi R_k^3}},\ H_\phi={fmt(Hn[1])}", Hn[1], "A/m")
    B = MU0 * mu_r * Hn[1]
    D.step("Flux density", rf"B=\mu H={fmt(B)}", B, "T")
    D.check(r"\sum\text{ of current elements}=\text{closed form}", H_cf, Hn[1], 2 * ((z2 - z1) / N / r) ** 2 + 1e-12,
            f"{N} midpoint elements; midpoint-rule error ∝ (Δz/r)²")
    D.check(r"H_r=H_z=0 \text{ (field is purely azimuthal)}", 0.0, float(np.hypot(Hn[0], Hn[2])), 1e-9, "vector sum", scale=abs(Hn[1]))
    conv = []
    for n in (4, 8, 16, 32, 64, 128, 256, 512):
        s, d_, _ = _segment_elements(z1, z2, n)
        v = _sum(I, s, d_, [r, 0, 0])[0][1]
        conv.append({"N": n, "H": float(v), "rel_error": abs(v - H_cf) / abs(H_cf)})
    errs = [c["rel_error"] for c in conv]
    order = float(np.polyfit(np.log([c["N"] for c in conv[-4:]]), np.log(errs[-4:]), 1)[0])
    D.check(r"\text{error}\propto N^{-2}\ \text{(midpoint rule)}", -2.0, order, 0.1, "slope of log error vs log N for N = 64…512", scale=2.0)
    if z1 < 0 < z2 and abs(z1 + z2) < 1e-12:
        L = z2 - z1
        D.check(r"\text{symmetric segment: }H=\frac{I L}{4\pi r\sqrt{r^2+L^2/4}}", I * L / (4 * np.pi * r * np.sqrt(r * r + L * L / 4)), H_cf, 1e-12, "θ1 = π − θ2")
    return {**D.out(H=Hn[1], H_closed=H_cf, H_infinite=H_inf, B=B, ratio_to_infinite=H_cf / H_inf),
            "elements": {"z": mid.tolist(), "dH": dH[:, 1].tolist()}, "convergence": conv,
            "geometry": {"z1": z1, "z2": z2, "r": r}}


def loop(I=1.0, a=0.1, z=0.05, N=200, mu_r=1.0):
    """Circular loop radius a in the xy-plane; field on the axis at height z, as a sum of N elements."""
    if a <= 0 or N < 3:
        raise ValueError("need a > 0 and N ≥ 3")
    D = Derivation()
    D.step("Biot–Savart law", r"d\mathbf H=\frac{I\,d\mathbf l\times\hat{\mathbf R}}{4\pi R^2}")
    D.step("Symmetry", r"\text{radial parts of }d\mathbf H\text{ cancel in pairs; only }dH_z=\frac{I\,dl}{4\pi R^2}\frac{a}{R}\text{ survives}")
    Hcf = I * a * a / (2 * (a * a + z * z) ** 1.5)
    D.step("Integrate over the loop", rf"H_z=\frac{{I a}}{{4\pi R^3}}\oint dl=\frac{{I a^2}}{{2(a^2+z^2)^{{3/2}}}}={fmt(Hcf)}", Hcf, "A/m")
    t = (np.arange(N) + 0.5) * 2 * np.pi / N
    src = np.stack([a * np.cos(t), a * np.sin(t), 0 * t], -1)
    dl = np.stack([-np.sin(t), np.cos(t), 0 * t], -1) * a * 2 * np.pi / N
    Hn, _ = _sum(I, src, dl, [0, 0, z])
    D.step("Numerical sum", rf"H_z\approx{fmt(Hn[2])}", Hn[2], "A/m")
    D.check(r"\sum\text{ elements}=\frac{Ia^2}{2(a^2+z^2)^{3/2}}", Hcf, Hn[2], 1e-10, f"{N} elements (periodic: spectrally accurate)")
    D.check(r"H_x=H_y=0 \text{ on the axis}", 0.0, float(np.hypot(Hn[0], Hn[1])), 1e-10, "radial cancellation", scale=abs(Hcf))
    zs = np.linspace(-4 * a, 4 * a, 161)
    return {**D.out(H=Hn[2], H_closed=Hcf, B=MU0 * mu_r * Hn[2]),
            "axis": {"z": zs.tolist(), "H": (I * a * a / (2 * (a * a + zs ** 2) ** 1.5)).tolist()}}


def square(I=1.0, a=0.2, N=100):
    """Square loop of side a centred at the origin; H at the centre from 4·N elements."""
    if a <= 0 or N < 2:
        raise ValueError("need a > 0, N ≥ 2")
    D = Derivation()
    D.step("Each side is a finite segment", r"H_{side}=\frac{I}{4\pi(a/2)}\left(\cos45^\circ-\cos135^\circ\right)=\frac{\sqrt2\,I}{2\pi a}")
    Hcf = 2 * np.sqrt(2) * I / (np.pi * a)
    D.step("Four sides add", rf"H=4H_{{side}}=\frac{{2\sqrt2\,I}}{{\pi a}}={fmt(Hcf)}", Hcf, "A/m")
    h = a / 2
    corners = np.array([[h, -h, 0], [h, h, 0], [-h, h, 0], [-h, -h, 0], [h, -h, 0]])
    src, dl = [], []
    for p, q in zip(corners[:-1], corners[1:]):
        s = (np.arange(N) + 0.5) / N
        src.append(p + np.outer(s, q - p)); dl.append(np.tile((q - p) / N, (N, 1)))
    Hn, _ = _sum(I, np.vstack(src), np.vstack(dl), [0, 0, 0])
    D.step("Numerical sum", rf"H_z\approx{fmt(Hn[2])}", Hn[2], "A/m")
    D.check(r"\sum\text{ elements}=\frac{2\sqrt2 I}{\pi a}", Hcf, Hn[2], 3 / N ** 2, f"4 × {N} midpoint elements")
    Hc = I / (2 * (a / 2))
    D.check(r"H_{square}/H_{circle,\ r=a/2}=\frac{2\sqrt2}{\pi}\approx0.90", 2 * np.sqrt(2) / np.pi, Hcf / Hc, 1e-12, "closed forms (circle inscribed in the square)")
    return D.out(H=Hn[2], H_closed=Hcf, H_inscribed_circle=Hc)
