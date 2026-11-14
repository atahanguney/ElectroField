# ElectroField: Multi-Dimensional Electromagnetic Field & Surface Velocity Simulation

## Overview
**ElectroField** is an interactive simulation and study project developed to visualize electromagnetic wave propagation, vector fields, and surface velocity dynamics across 1D, 2D, 3D, and 4D coordinate systems. 

In standard undergraduate Electrical and Electronics Engineering courses (such as *Electromagnetic Field Theory* and *Electromagnetic Waves*), it is often difficult to imagine how differential and integral equations actually behave in 3D space or on curved surfaces. I started this project to build a practical environment where these formulas can be tested dynamically with real-time visual feedback, mathematical proofs, and a built-in question bank for self-study.

The project contains two main parts:
1. **`index.html` (WebGL Interactive Workbench & Study Portal):** A browser-based 3D/4D simulation engine, a complete theory reference guide, and a 250+ question bank.
2. **`ElectroField.py` (Python Numerical Solver):** A standalone Python script using `NumPy` and `Matplotlib` to calculate phase/surface velocities, Poynting flux, and plot 3D surface gradients.

---

## Main Features

### 1. Multi-Dimensional Visualization (1D to 4D)
* **1D Linear Space:** Simulates wave propagation along a single axis (similar to a transmission line) to observe basic attenuation and phase shift.
* **2D Planar View:** Useful for checking equipotential contours, planar waveguides, and surface current density distributions.
* **3D Volumetric Space:** Full 3D representation of Electric ($\vec{E}$) and Magnetic ($\vec{H}$) fields, tangential surface velocity vectors ($\vec{v}_s$), and Poynting power vectors ($\vec{S} = \vec{E} \times \vec{H}$).
* **4D Spacetime Projection:** Demonstrates how electric and magnetic fields combine into the 4D relativistic electromagnetic tensor ($F^{\mu\nu}$) using a 4D hypercube (Tesseract) projection.
* **Camera Perspectives:** Users can freely rotate and zoom the model, or switch between **Top View (XY)**, **Bottom View (-XY)**, **Front View (XZ)**, and **Side View (YZ)**.

### 2. Core Physics & Mathematical Proofs
The solver calculates and verifies the following concepts in real time when parameters (frequency $f$, relative permittivity $\varepsilon_r$, relative permeability $\mu_r$, field amplitude $E_0$, and conductivity $\sigma$) are changed:
* **Maxwell's Equations:** Gauss's Law for Electricity and Magnetism, Faraday's Law of Induction, and the Ampère-Maxwell Law.
* **Electrostatics & Magnetostatics:** Coulomb's Law, scalar and vector potentials, Biot-Savart Law, Lorentz force, and boundary conditions between different media.
* **Surface Velocity & Skin Effect:** Phase velocity ($v_p$), oblique tangential surface velocity ($v_s$), intrinsic impedance ($\eta$), and high-frequency skin depth ($\delta = 1/\sqrt{\pi f \mu \sigma}$).
* **Power & Energy Conservation:** Numerical comparison between the surface integral of the Poynting vector and the volume energy rate.

### 3. Theory Reference & Formula Guide
A dedicated tab in the interface explains all the equations used in the simulation in clear English. Instead of only listing formulas, it explains the physical intuition behind why the equations work, defines every symbol and unit, and shows step-by-step derivations.

### 4. Dynamic Question Bank (250+ Questions)
To make this project useful for exam preparation, I included an assessment module covering 5 main topics:
1. Maxwell & Faraday Laws
2. Electrostatics & Gauss's Law
3. Magnetostatics & Ampère's Law
4. Surface Velocity, Power & Skin Depth
5. 1D-4D Coordinate Systems & Vector Calculus

Each topic has a pool of **50 questions**. In single-topic mode, the system selects **15 random questions** from that topic, and clicking the reset button brings a new set of 15 questions. If the **"All Topics (120 Questions)"** option is selected, a general test is generated from all subjects. When the instant solution option is enabled, selecting an answer immediately shows whether it is correct or incorrect along with the mathematical solution steps.

### 5. AI Model Generator
The workbench also includes an experimental AI assistant connected to a free text API. If a user types a specific scenario in English (for example, a toroidal field at a specific frequency), the assistant updates the surface equation and simulation parameters automatically.

---

## Project Structure

```text
ElectroField/
├── ElectroField.py      # Standalone Python 3D numerical solver and plotter
├── index.html           # Interactive WebGL 3D/4D workbench, Theory Guide & Question Bank
└── README.md            # Project documentation
```

---

## How to Run the Project

### Running the Python Script (`ElectroField.py`)
Make sure you have Python 3 installed along with `numpy` and `matplotlib`.

1. Install the required libraries:
   ```bash
   pip install numpy matplotlib
   ```
2. Run the solver script:
   ```bash
   python ElectroField.py
   ```
   This will print the calculated wave and surface velocity parameters in the terminal and open an interactive 3D Matplotlib window showing the field surface and velocity vectors.

### Running the Interactive 3D/4D Workbench (`index.html`)
No installation or local server is required for the web interface. Simply double-click `index.html` to open it in any modern browser (Chrome, Edge, or Firefox).

---

## References
* Ulaby, F. T., & Ravaioli, U. *Fundamentals of Applied Electromagnetics*. Pearson.
* Griffiths, D. J. *Introduction to Electrodynamics*. Cambridge University Press.
* Cheng, D. K. *Field and Wave Electromagnetics*. Addison-Wesley.

---

## License
This project is open-source and available under the MIT License.