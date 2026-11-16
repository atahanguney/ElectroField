"""Method of images (Ulaby §4-11, Cheng §4-4).

A charge Q at height d above a grounded perfectly conducting plane (z = 0) produces, for z > 0,
exactly the field of Q at (0, d) together with an image −Q at (0, −d) with the plane removed.
Both configurations satisfy Poisson's equation above the plane with V = 0 on it and V → 0 at
infinity, so by the uniqueness theorem the fields are identical there.
The page draws the x–z plane; in engine.electrostatics the vertical coordinate is called y.
"""
import numpy as np
from scipy import integrate
from .constants import EPS0
from .derivation import Derivation, fmt
from . import electrostatics as es


def plane(Q=1e-9, d=0.4, eps_r=1.0, n_pts=7):
    if Q == 0 or d <= 0 or eps_r <= 0:
        raise ValueError("need Q ≠ 0, d > 0, εr > 0")
    eps = EPS0 * eps_r
    D = Derivation()
    D.step("Boundary-value problem", r"\nabla^2V=-\rho_v/\varepsilon\ (z>0),\qquad V(z=0)=0,\qquad V\to0\ \text{as}\ r\to\infty")
    D.step("Image configuration", r"Q\ \text{at}\ (0,d)\ +\ (-Q)\ \text{at}\ (0,-d),\ \text{plane removed}",
           note="satisfies the same equation for z > 0 and the same boundary values ⇒ same solution (uniqueness theorem)")
    D.step("Potential", r"V(x,z)=\frac{Q}{4\pi\varepsilon}\left[\frac{1}{\sqrt{x^2+(z-d)^2}}-\frac{1}{\sqrt{x^2+(z+d)^2}}\right]",
           note="at z = 0 both distances are equal, so V = 0 on the whole plane")
    rho0 = -Q / (2 * np.pi * d * d)
    D.step("Induced surface charge", rf"\rho_s(x)=\varepsilon E_z(x,0^+)=-\frac{{Q d}}{{2\pi (x^2+d^2)^{{3/2}}}},\quad \rho_s(0)={fmt(rho0)}", rho0, "C/m²",
           note="(3-D: x² → x² + y²). It is densest right under the charge.")
    F = Q * Q / (4 * np.pi * eps * (2 * d) ** 2)
    D.step("Force on Q (attraction toward the plane)", rf"F=\frac{{Q^2}}{{4\pi\varepsilon(2d)^2}}={fmt(F)}", F, "N")
    W = -Q * Q / (4 * np.pi * eps * 4 * d)
    D.step("Energy of the real system", rf"W=-\frac{{Q^2}}{{16\pi\varepsilon d}}={fmt(W)}", W, "J",
           note="half the energy of the Q, −Q pair: only the upper half-space holds field")
    # --- engine configurations (a) and (b)
    probe = (0.3 * d, 0.6 * d)
    a = es.point_charges([{"q": Q, "x": 0.0, "y": d}], ground=True, probe=probe, span=max(1.0, 2.5 * d))
    b = es.point_charges([{"q": Q, "x": 0.0, "y": d}, {"q": -Q, "x": 0.0, "y": -d}], ground=False, probe=probe, span=max(1.0, 2.5 * d))
    Qa = np.array([[Q, 0, d, 0], [-Q, 0, -d, 0]])
    D.check(r"\mathbf E^{(a)}=\mathbf E^{(b)}\ \text{for } z>0 \text{ (probe)}", 0.0, float(np.hypot(*(np.array(a["values"]["E"]) - np.array(b["values"]["E"])))), 1e-12,
            "engine results of the two configurations at the probe", scale=float(np.hypot(*b["values"]["E"])))
    xs = np.linspace(-5 * d, 5 * d, 401)
    _, Vp = es.field_at(Qa, np.c_[xs, 0 * xs, 0 * xs])
    D.check(r"V=0 \text{ on the plane}", 0.0, float(np.abs(Vp).max()), 1e-12, "401 points", scale=abs(Q) / (4 * np.pi * eps * d))
    Ez0, _ = es.field_at(Qa, np.c_[xs, 0 * xs, 0 * xs])
    rs_num = EPS0 * Ez0[:, 1]   # ρs = D_n; es.field_at returns the vacuum field (= εr E), so D = ε0 E_vac for any εr
    rs_cf = -Q * d / (2 * np.pi * (xs ** 2 + d * d) ** 1.5)
    D.check(r"\rho_s=\varepsilon E_n \text{ matches } -\frac{Qd}{2\pi(x^2+d^2)^{3/2}}", 0.0, float(np.abs(rs_num - rs_cf).max()), 1e-10,
            "superposed field at z = 0⁺ vs closed form", scale=abs(rho0))
    Qind = integrate.quad(lambda s: -Q * d / (2 * np.pi * (s * s + d * d) ** 1.5) * 2 * np.pi * s, 0, np.inf, epsabs=0, epsrel=1e-12)[0]
    D.check(r"\iint\rho_s\,ds=-Q", -Q, Qind, 1e-9, "∫ρs 2πs ds over the infinite plane")
    Fn = abs(es.field_at(np.array([[-Q, 0, -d, 0]]), np.array([[0, d, 0]]))[0][0][1] * Q) / eps_r
    D.check(r"F=Q\,E_{image}(0,d)", F, Fn, 1e-12, "Coulomb force from the image")
    return {**D.out(rho_s0=rho0, F=F, W=W, Q=Q, d=d), "a": a, "b": b,
            "rho_s": {"x": xs.tolist(), "num": rs_num.tolist(), "closed": rs_cf.tolist()}}


def corner(Q=1e-9, x0=0.3, y0=0.5, eps_r=1.0):
    """Charge in a 90° conducting corner (planes x = 0 and y = 0): three images."""
    if x0 <= 0 or y0 <= 0 or Q == 0:
        raise ValueError("need x0, y0 > 0 and Q ≠ 0")
    D = Derivation()
    D.step("Images for a 90° corner", r"-Q\ (-x_0,y_0),\quad -Q\ (x_0,-y_0),\quad +Q\ (-x_0,-y_0)",
           note="a corner of angle π/n needs 2n − 1 images; here n = 2 → 3 images")
    Qs = np.array([[Q, x0, y0, 0], [-Q, -x0, y0, 0], [-Q, x0, -y0, 0], [Q, -x0, -y0, 0]])
    s = np.linspace(0, 3 * max(x0, y0), 301)
    _, V1 = es.field_at(Qs, np.c_[0 * s, s, 0 * s])
    _, V2 = es.field_at(Qs, np.c_[s, 0 * s, 0 * s])
    sc = abs(Q) / (4 * np.pi * EPS0 * eps_r * min(x0, y0))
    D.check(r"V=0 \text{ on the wall } x=0", 0.0, float(np.abs(V1).max()), 1e-12, "301 points", scale=sc)
    D.check(r"V=0 \text{ on the wall } y=0", 0.0, float(np.abs(V2).max()), 1e-12, "301 points", scale=sc)
    E, _ = es.field_at(Qs[1:], np.array([[x0, y0, 0]]))
    F = Q * E[0][:2]
    D.step("Force on Q", rf"\mathbf F=Q\sum\mathbf E_{{images}}=({fmt(F[0])},\ {fmt(F[1])})", F, "N", note="pulls the charge into the corner")
    return D.out(F=F)
