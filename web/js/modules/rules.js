// Rules — notation, conventions and identities of EM field theory, for beginners and professionals.
import { h, tex, sci, simple } from '../ui.js';
import { api } from '../api.js';

const R = String.raw;
const T = (head, rows) => h('div', { class: 'tablewrap' }, h('table', { class: 't' },
  h('thead', {}, h('tr', {}, head.map((x) => h('th', { scope: 'col' }, x)))),
  h('tbody', {}, rows.map((r) => h('tr', {}, r.map((c) => h('td', {}, typeof c === 'string' && c.startsWith('$') ? tex(c.slice(1)) : c)))))));

export function render(view, ch) {
  const consts = h('div');
  view.append(h('div', { class: 'eyebrow' }, 'REFERENCE'), h('h1', {}, ch.title),
    h('p', { class: 'lede' }, 'The conventions this site (and Ulaby & Ravaioli, Cheng) follows, collected in one place. Most exam mistakes are not about physics but about a sign, a unit vector or the order of a cross product — check them here.'),
    simple({ idea: 'A hat (^) means "direction only, length 1". Bold letters are vectors. R always points from the source (charge or current) to the point where you want the field. Before adding fields, write each one as magnitude × unit vector.',
      remember: ['x̂ × ŷ = ẑ (and cyclic). Swap the order and the sign flips.', 'Angles: θ is measured from the +z axis, φ from the +x axis in the xy-plane.', 'In phasor form the time factor e^{jωt} is implied; a wave e^{−jβz} travels in +z.'],
      mistakes: ['Writing R from the field point to the source.', 'Adding magnitudes of vectors that point in different directions.', 'Forgetting that r̂, φ̂, R̂, θ̂ change direction from point to point.'] }),

    h('h2', {}, '1. Notation'),
    T(['Symbol', 'Meaning', 'Example'], [
      [R`$\mathbf A`, 'vector (bold)', R`$\mathbf E,\ \mathbf H,\ \mathbf J`], [R`$A=|\mathbf A|`, 'magnitude', R`$|\mathbf E|=\sqrt{E_x^2+E_y^2+E_z^2}`],
      [R`$\hat{\mathbf a}=\mathbf A/|\mathbf A|`, 'unit vector (hat): direction only, length 1', R`$\hat x,\ \hat r,\ \hat\phi,\ \hat R,\ \hat\theta,\ \hat n`],
      [R`$\tilde{\mathbf E}(z)`, 'phasor (complex amplitude)', R`$\mathbf E(z,t)=\mathrm{Re}\{\tilde{\mathbf E}(z)e^{j\omega t}\}`], [R`$\tilde{\mathbf H}^*`, 'complex conjugate', R`$\mathbf S_{av}=\tfrac12\mathrm{Re}\{\tilde{\mathbf E}\times\tilde{\mathbf H}^*\}`],
      [R`$\mathbf R=\mathbf r-\mathbf r'`, 'from source point r′ to field point r', R`$\hat{\mathbf R}=\mathbf R/R`]]),

    h('h2', {}, '2. Vector algebra'),
    h('div', { class: 'formula-box' },
      tex(R`\mathbf A\cdot\mathbf B=AB\cos\theta_{AB}=A_xB_x+A_yB_y+A_zB_z,\qquad \mathbf A\times\mathbf B=\hat n\,AB\sin\theta_{AB}=\begin{vmatrix}\hat x&\hat y&\hat z\\A_x&A_y&A_z\\B_x&B_y&B_z\end{vmatrix}`, true),
      tex(R`\hat x\times\hat y=\hat z,\ \ \hat y\times\hat z=\hat x,\ \ \hat z\times\hat x=\hat y\qquad \hat r\times\hat\phi=\hat z,\ \ \hat R\times\hat\theta=\hat\phi,\qquad \mathbf B\times\mathbf A=-\mathbf A\times\mathbf B`, true),
      tex(R`\mathbf A\cdot(\mathbf B\times\mathbf C)=\mathbf B\cdot(\mathbf C\times\mathbf A),\qquad \mathbf A\times(\mathbf B\times\mathbf C)=\mathbf B(\mathbf A\cdot\mathbf C)-\mathbf C(\mathbf A\cdot\mathbf B)\ \ (\text{"BAC − CAB"})`, true)),
    h('p', { class: 'prose' }, 'Right-hand rule: point the fingers of the right hand along A, curl them toward B; the thumb gives A × B. For a current, thumb along I ⇒ fingers give the direction of H.'),

    h('h2', {}, '3. Coordinate systems'),
    T(['Item', 'Cartesian (x, y, z)', 'Cylindrical (r, φ, z)', 'Spherical (R, θ, φ)'], [
      ['Unit vectors', R`$\hat x,\hat y,\hat z`, R`$\hat r,\hat\phi,\hat z`, R`$\hat R,\hat\theta,\hat\phi`],
      ['Ranges', '−∞ … ∞', 'r ≥ 0, 0 ≤ φ < 2π', 'R ≥ 0, 0 ≤ θ ≤ π, 0 ≤ φ < 2π'],
      ['Scale factors', '1, 1, 1', '1, r, 1', R`$1,\ R,\ R\sin\theta`],
      ['dl', R`$\hat x\,dx+\hat y\,dy+\hat z\,dz`, R`$\hat r\,dr+\hat\phi\,r\,d\phi+\hat z\,dz`, R`$\hat R\,dR+\hat\theta\,R\,d\theta+\hat\phi\,R\sin\theta\,d\phi`],
      ['dv', R`$dx\,dy\,dz`, R`$r\,dr\,d\phi\,dz`, R`$R^2\sin\theta\,dR\,d\theta\,d\phi`],
      ['From Cartesian', '—', R`$r=\sqrt{x^2+y^2},\ \phi=\tan^{-1}(y/x)`, R`$R=\sqrt{x^2+y^2+z^2},\ \theta=\cos^{-1}(z/R)`],
      ['To Cartesian', '—', R`$x=r\cos\phi,\ y=r\sin\phi`, R`$x=R\sin\theta\cos\phi,\ z=R\cos\theta`]]),
    h('p', { class: 'prose' }, 'Use the quadrant of (x, y) for φ (atan2), not the plain arctangent. Cylindrical and spherical unit vectors depend on position: you may only add their components at the same point.'),

    h('h2', {}, '4. Differential operators'),
    T(['Operator', 'Cartesian', 'Cylindrical', 'Spherical'], [
      ['∇V', R`$\hat x\partial_xV+\hat y\partial_yV+\hat z\partial_zV`, R`$\hat r\partial_rV+\hat\phi\frac1r\partial_\phi V+\hat z\partial_zV`, R`$\hat R\partial_RV+\hat\theta\frac1R\partial_\theta V+\hat\phi\frac{1}{R\sin\theta}\partial_\phi V`],
      ['∇·A', R`$\partial_xA_x+\partial_yA_y+\partial_zA_z`, R`$\frac1r\partial_r(rA_r)+\frac1r\partial_\phi A_\phi+\partial_zA_z`, R`$\frac{1}{R^2}\partial_R(R^2A_R)+\frac{1}{R\sin\theta}\partial_\theta(A_\theta\sin\theta)+\frac{1}{R\sin\theta}\partial_\phi A_\phi`],
      ['∇²V', R`$\partial_x^2V+\partial_y^2V+\partial_z^2V`, R`$\frac1r\partial_r(r\partial_rV)+\frac{1}{r^2}\partial_\phi^2V+\partial_z^2V`, R`$\frac{1}{R^2}\partial_R(R^2\partial_RV)+\frac{1}{R^2\sin\theta}\partial_\theta(\sin\theta\,\partial_\theta V)+\frac{1}{R^2\sin^2\theta}\partial_\phi^2V`]]),
    h('div', { class: 'formula-box' }, tex(R`\nabla\times\mathbf A=\frac{1}{h_1h_2h_3}\begin{vmatrix}h_1\hat u_1&h_2\hat u_2&h_3\hat u_3\\ \partial_1&\partial_2&\partial_3\\ h_1A_1&h_2A_2&h_3A_3\end{vmatrix}\qquad(\text{any orthogonal system})`, true)),

    h('h2', {}, '5. Theorems and identities'),
    h('div', { class: 'formula-box' },
      tex(R`\int_v\nabla\cdot\mathbf A\,dv=\oint_S\mathbf A\cdot d\mathbf s\ \ (\text{divergence}),\qquad \int_S(\nabla\times\mathbf A)\cdot d\mathbf s=\oint_C\mathbf A\cdot d\mathbf l\ \ (\text{Stokes})`, true),
      tex(R`\nabla\times(\nabla V)=0,\qquad \nabla\cdot(\nabla\times\mathbf A)=0,\qquad \nabla\times\nabla\times\mathbf A=\nabla(\nabla\cdot\mathbf A)-\nabla^2\mathbf A`, true)),
    h('p', { class: 'prose' }, 'ds points outward from a closed surface; for an open surface bounded by C, the right-hand rule links the direction of ds to the sense in which C is traversed.'),

    h('h2', {}, '6. Sign conventions'),
    T(['Quantity', 'Convention', 'Consequence'], [
      ['Time dependence', R`$e^{j\omega t}`, R`$\partial/\partial t\to j\omega`],
      ['Propagation constant', R`$\gamma=\alpha+j\beta,\ \ \alpha,\beta\ge0`, R`$\tilde E\propto e^{-\gamma z}\ \text{travels and decays in }+z`],
      ['Boundary normal', R`$\hat n_2\ \text{points from medium 2 into medium 1}`, R`$\hat n_2\cdot(\mathbf D_1-\mathbf D_2)=\rho_s`],
      ['Source vector', R`$\mathbf R\ \text{from source to field point}`, R`$d\mathbf H\propto d\mathbf l\times\hat{\mathbf R}`],
      ['Reflection coefficient', R`$\Gamma=\frac{\eta_2-\eta_1}{\eta_2+\eta_1}\ \text{(E-field ratio)}`, 'Γ = −1 for a perfect conductor'],
      ['Line position', R`$d\ \text{measured from the load toward the generator}`, R`$\Gamma(d)=\Gamma_Le^{-j2\beta d}`],
      ['Power flow', R`$\mathbf S=\mathbf E\times\mathbf H`, 'points in the direction of propagation'],
      ['Faraday', R`$V_{emf}=-N\,d\Phi/dt`, 'minus sign: the induced current opposes the change (Lenz)']]),

    h('h2', {}, '7. Quantities and SI units'),
    T(['Symbol', 'Quantity', 'Unit'], [
      ['E', 'electric field intensity', 'V/m'], ['D', 'electric flux density', 'C/m²'], ['H', 'magnetic field intensity', 'A/m'], ['B', 'magnetic flux density', 'T = Wb/m²'],
      ['J, Jₛ', 'volume / surface current density', 'A/m², A/m'], ['ρᵥ, ρₛ, ρₗ', 'volume / surface / line charge density', 'C/m³, C/m², C/m'],
      ['ε, μ, σ', 'permittivity, permeability, conductivity', 'F/m, H/m, S/m'], ['V, Φ', 'potential, magnetic flux', 'V, Wb'],
      ['η, Z₀', 'intrinsic / characteristic impedance', 'Ω'], ['α, β', 'attenuation, phase constant', 'Np/m, rad/m'], ['S', 'power density (Poynting)', 'W/m²'],
      ['C, L', 'capacitance, inductance', 'F, H'], ['dB', 'power ratio', '10 log₁₀(P₂/P₁) = 20 log₁₀(V₂/V₁);  1 Np = 8.686 dB']]),

    h('h2', {}, '8. Physical constants (CODATA 2022)'), consts,

    h('h2', {}, '9. Site conventions'),
    T(['Item', 'Convention'], [['Field colours', 'E red, H blue, S (power) green, accent blue for geometry'], ['Angles', 'θ from +z, φ from +x toward +y, angles of incidence from the normal'],
      ['Checks', 'each result lists independent checks with relative error and tolerance'], ['Units in inputs', 'SI prefixes accepted: 2.45G, 10M, 0.5m, 3µ']]),

    h('h2', {}, '10. Typical exam pitfalls'),
    h('ul', { class: 'prose' }, [
      'Using R in place of R² (point charge) or r in place of r² (line charge vs point charge).',
      'Forgetting 4π in Coulomb/Biot–Savart, or 2π in line-charge and infinite-wire results.',
      'Taking ε₀ when the medium has εr (and μ₀ when μr ≠ 1).',
      'Adding cylindrical/spherical components that belong to different points.',
      'Degrees vs radians inside sin, cos, tan; and tan⁻¹ quadrant errors.',
      'Mixing peak and rms values in power: S_av = |E₀|²/(2η) uses the peak amplitude.',
      'Treating the image charge as real in the region where the conductor is.',
      'Distance d measured from the generator instead of from the load on a transmission line.',
    ].map((x) => h('li', {}, x))));
  api('constants', {}, 'rulesK').then((k) => consts.replaceChildren(T(['Symbol', 'Value', 'Unit', 'Name'], k.map((c) => [`$${c.tex}`, sci(c.value, 10), c.unit, c.name])))).catch(() => {});
}
