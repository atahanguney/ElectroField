// Plain-language companions for every chapter (shown under the introduction, next to the professional derivations).
import { tex } from './ui.js';

const R = String.raw;
export const NOTES = {
  dimensions: {
    idea: 'Imagine the same amount of power leaving a source. On a cable it stays inside the cable (1-D), from a long line it spreads over growing circles (2-D), from a small antenna over growing spheres (3-D). The bigger the surface it spreads over, the faster the field gets weaker.',
    remember: ['1-D: no weakening without loss. 2-D: field ∝ 1/√ρ (−3 dB per doubling). 3-D: field ∝ 1/R (−6 dB per doubling).', 'Material loss (σ) adds e^{−αr} on top of the spreading in all three cases.'],
    mistakes: ['Mixing field and power: power falls as 1/R² when the field falls as 1/R.', 'Expecting a lossless cable to lose signal with distance.'],
  },
  coordinates: {
    idea: 'A point can be located by (x, y, z), by distance-angle-height (r, φ, z) or by distance and two angles (R, θ, φ). Moving by a small angle covers more distance when you are far from the centre — that is why r dφ or R sin θ dφ appear instead of plain dφ.',
    remember: [['Spherical volume element: ', tex(R`dv=R^2\sin\theta\,dR\,d\theta\,d\phi`)], 'Pick the system that matches the symmetry: spheres → spherical, wires and coax → cylindrical.'],
    mistakes: ['Forgetting the scale factors (writing dφ instead of r dφ).', 'Using θ and φ the other way round (θ is from the z-axis).'],
  },
  electrostatics: {
    idea: 'Charges push and pull. The electric field E is the force a tiny +1 C test charge would feel. Field lines start on + and end on −; equipotential lines cross them at right angles. Gauss’s law counts the field lines leaving a closed surface to find the charge inside.',
    remember: [['Point charge: ', tex(R`E=\frac{Q}{4\pi\varepsilon R^2}`)], 'Superposition: add the field vectors of all charges.', [tex(R`\mathbf E=-\nabla V`), ': E points from high to low potential.'], [tex(R`C=Q/V`), ' depends only on geometry and ε.']],
    mistakes: ['Adding magnitudes instead of vectors.', 'Using Gauss’s law without enough symmetry.', 'Forgetting εr when the space is filled with a dielectric.'],
  },
  magnetostatics: {
    idea: 'Currents create magnetic fields that circle around them (right-hand rule). Ampère’s law adds H around a closed path to find the current inside; Biot–Savart adds the little contributions of each piece of wire.',
    remember: [['Infinite wire: ', tex(R`H=\frac{I}{2\pi r}`)], 'Parallel currents attract, opposite currents repel.', [tex(R`\nabla\cdot\mathbf B=0`), ': B lines always close; there are no magnetic charges.']],
    mistakes: ['Wrong direction of H (use the right hand: thumb along I).', 'Confusing B (tesla) with H (A/m): B = μH.'],
  },
  maxwell: {
    idea: 'Four rules describe all electromagnetism: charges make E; there are no magnetic charges; a changing B makes E (Faraday); currents and a changing E make H (Ampère–Maxwell). At a boundary between materials, the parts of E and H along the surface carry straight through.',
    remember: [['Faraday: ', tex(R`V_{emf}=-N\frac{d\Phi}{dt}`)], 'Tangential E is continuous; normal D jumps by the surface charge; normal B is continuous.', 'Displacement current ∂D/∂t is what allows waves to travel.'],
    mistakes: ['Forgetting the minus sign (Lenz’s law).', 'Using the wrong normal direction in boundary conditions.'],
  },
  waves: {
    idea: 'A wave in a material travels with β (how fast the phase turns) and fades with α (how fast it dies out). In good conductors it dies within a "skin" a few micrometres thick; in good insulators it travels far.',
    remember: [['Skin depth: ', tex(R`\delta_s=\frac{1}{\sqrt{\pi f\mu\sigma}}`), ' in good conductors.'], 'Compare σ with ωε: σ/ωε ≫ 1 conductor, ≪ 1 dielectric.', 'Inside a dielectric the wavelength shrinks by √εr.'],
    mistakes: ['Using the good-conductor formula for a dielectric.', 'Mixing Np and dB (1 Np = 8.686 dB).'],
  },
  reflection: {
    idea: 'When a wave hits a new material, part bounces back and part goes through. The bigger the difference in impedance η, the more bounces back. At a slant, the transmitted wave bends (Snell), there is an angle with no reflection for one polarisation (Brewster) and, going into a thinner medium, an angle beyond which everything reflects.',
    remember: [[tex(R`\Gamma=\frac{\eta_2-\eta_1}{\eta_2+\eta_1}`), ', reflected power = |Γ|².'], [tex(R`n_1\sin\theta_i=n_2\sin\theta_t`)], 'Brewster: tan θB = n₂/n₁. Critical: sin θc = n₂/n₁.'],
    mistakes: ['Using |Γ| instead of |Γ|² for power.', 'Looking for a critical angle when going into a denser medium (there is none).'],
  },
  tlines: {
    idea: 'On a cable the signal goes to the load and part of it bounces back if the load does not match Z₀. The two waves add into a standing pattern. A quarter-wave of line turns a load into Z₀²/Z_L; the Smith chart is a map where moving along the cable just rotates the point.',
    remember: [[tex(R`\Gamma_L=\frac{Z_L-Z_0}{Z_L+Z_0}`), ', VSWR = (1 + |Γ|)/(1 − |Γ|).'], 'Every λ/2 the input impedance repeats.', 'Matched load: Γ = 0, VSWR = 1.'],
    mistakes: ['Measuring d from the generator instead of from the load.', 'Forgetting to normalise impedances by Z₀ on the Smith chart.'],
  },
  radiation: {
    idea: 'A metal pipe only lets through waves small enough to "fit": below the cut-off frequency nothing propagates. An antenna does the opposite — it launches the wave into space, more strongly in some directions than others. Many antennas fed with shifted phases steer the beam.',
    remember: [['Cut-off of TE₁₀: ', tex(R`f_c=\frac{c}{2a}`)], 'Half-wave dipole: R_rad ≈ 73 Ω, D ≈ 1.64 (2.15 dBi).', 'Array beam direction: cos θ₀ = −δ/(kd).'],
    mistakes: ['Expecting a waveguide to pass low frequencies.', 'Spacing array elements ≥ λ (grating lobes appear).'],
  },
};
