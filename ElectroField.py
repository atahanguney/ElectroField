"""
ElectroField.py - Multi-Dimensional Electromagnetics & Surface Velocity Solver
Standalone Python numerical solver (NumPy/Matplotlib) + WebGL Workbench Launcher.
"""

import os
import sys
import webbrowser
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

# 1. Fundamental Physical Constants
C0 = 2.99792458e8                  # Speed of light in vacuum (m/s)
EPS0 = 8.854187817e-12             # Vacuum permittivity (F/m)
MU0 = 4 * np.pi * 1e-7             # Vacuum permeability (H/m)


def run_numerical_proof(freq_ghz=2.4, eps_r=1.0, mu_r=1.0, e0_amp=120.0, sigma=0.05):
    """Calculates phase velocity, tangential surface velocity, Poynting flux, and skin depth."""
    f_hz = freq_ghz * 1e9
    eps = EPS0 * eps_r
    mu = MU0 * mu_r

    v_phase = C0 / np.sqrt(eps_r * mu_r)
    v_surface = v_phase * np.exp(-sigma * 0.04)
    eta = np.sqrt(mu / eps)
    poynting_flux = (e0_amp ** 2) / (2.0 * eta)
    skin_depth = 1.0 / np.sqrt(np.pi * f_hz * mu * max(sigma, 1e-6))

    print("=" * 56)
    print(" ELECTROFIELD - MATHEMATICAL PROOF & TELEMETRY REPORT")
    print("=" * 56)
    print(f" Wave Frequency (f)        : {freq_ghz:.2f} GHz")
    print(f" Relative Permittivity (er): {eps_r:.2f}")
    print(f" Relative Permeability (ur): {mu_r:.2f}")
    print(f" Phase Velocity (v_p)      : {v_phase:.3e} m/s")
    print(f" Surface Velocity (v_s)    : {v_surface:.3e} m/s")
    print(f" Intrinsic Impedance (eta) : {eta:.2f} Ohms")
    print(f" Poynting Vector |S_avg|   : {poynting_flux:.3f} W/m^2")
    print(f" Skin Depth (delta_s)      : {skin_depth * 1000:.2f} mm")
    print("=" * 56)


def launch_3d_matplotlib_preview(freq_ghz=2.4, eps_r=1.0, mu_r=1.0, e0_amp=120.0, sigma=0.05):
    """Generates a 3D surface manifold and tangential surface velocity quiver plot in Python."""
    x = np.linspace(-7, 7, 50)
    y = np.linspace(-7, 7, 50)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2) + 1e-6
    k = (freq_ghz * 0.45) * np.sqrt(eps_r * mu_r)

    Z = np.sin(R * k) * (e0_amp / 120.0) * np.exp(-sigma * R * 0.2)
    dZdx, dZdy = np.gradient(Z)

    fig = plt.figure(figsize=(11, 7), facecolor='#050811')
    ax = fig.add_subplot(111, projection='3d', facecolor='#050811')
    ax.plot_surface(X, Y, Z, cmap=cm.cool, linewidth=0.3, antialiased=True, alpha=0.85)
    ax.quiver(
        X[::5, ::5], Y[::5, ::5], Z[::5, ::5],
        -dZdx[::5, ::5], -dZdy[::5, ::5], 0.2,
        color='#f59e0b', length=0.6
    )
    ax.set_title("ElectroField 3D Electromagnetic Manifold & Surface Velocity Vectors", color='white')
    ax.tick_params(colors='white')
    plt.show()


def get_resource_path(relative_path):
    """Finds the correct path whether running as a .py script or a compiled .exe release."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


if __name__ == "__main__":
    # 1. Print mathematical verification in terminal
    run_numerical_proof()

    # 2. Automatically open the interactive 1D-4D WebGL Workbench (index.html) if present
    html_file = get_resource_path("index.html")
    if os.path.exists(html_file):
        print("\n[INFO] Launching ElectroField 3D/4D Interactive Workbench (index.html)...")
        webbrowser.open(f"file://{html_file}")

    # 3. Open standalone Python Matplotlib 3D window
    print("[INFO] Opening standalone Python 3D Matplotlib surface plot...")
    launch_3d_matplotlib_preview()
