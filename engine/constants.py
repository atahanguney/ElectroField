"""Physical constants (CODATA 2022 via scipy.constants).

Since the 2019 SI redefinition mu_0 is a measured quantity, no longer exactly
4*pi*1e-7 H/m (relative difference ~1e-10). c remains exact.
"""
from scipy import constants as _c

C0 = _c.c                # 299 792 458 m/s (exact)
EPS0 = _c.epsilon_0      # F/m
MU0 = _c.mu_0            # H/m
ETA0 = (MU0 / EPS0) ** 0.5   # ~376.73 ohm
QE = _c.e                # elementary charge, C (exact)
K_E = 1.0 / (4.0 * _c.pi * EPS0)  # Coulomb constant, N*m^2/C^2

TABLE = [
    ("c", r"c", C0, "m/s", "speed of light in vacuum (exact)"),
    ("eps0", r"\varepsilon_0", EPS0, "F/m", "vacuum permittivity"),
    ("mu0", r"\mu_0", MU0, "H/m", "vacuum permeability"),
    ("eta0", r"\eta_0=\sqrt{\mu_0/\varepsilon_0}", ETA0, "Ω", "intrinsic impedance of free space"),
    ("e", r"e", QE, "C", "elementary charge (exact)"),
    ("k", r"k=1/4\pi\varepsilon_0", K_E, "N·m²/C²", "Coulomb constant"),
]
