// Landing page: what the workbench is, a live engine-verified example, and the proof methods used.
import { h, tex, kv, si, sci, stepsTable, checksTable } from './ui.js';
import { api, backend, engineReady } from './api.js';

const R = String.raw;

// key relation and what is independently checked, per chapter
const KEY = {
  dimensions: [R`|\psi|\propto 1,\ \rho^{-1/2},\ R^{-1}`, 'Helmholtz residuals; Poynting flux constant through every wavefront'],
  coordinates: [R`dv=R^2\sin\theta\,dR\,d\theta\,d\phi`, 'Jacobian by finite differences; ∫dv over a sphere = 4πa³/3'],
  electrostatics: [R`\oint_S\mathbf D\cdot d\mathbf s=Q_{enc}`, 'flux integrals = q/ε₀; E = −∇V; induced charge on a grounded plane = −q'],
  images: [R`V=\frac{Q}{4\pi\varepsilon}\Big(\frac1{R_+}-\frac1{R_-}\Big)`, 'V = 0 on the plane; ∫ρs ds = −Q; fields of (a) and (b) identical'],
  biot: [R`d\mathbf H=\frac{I\,d\mathbf l\times\hat{\mathbf R}}{4\pi R^2}`, 'N-element sum → closed form with error ∝ 1/N²'],
  magnetostatics: [R`\oint_C\mathbf H\cdot d\mathbf l=I_{enc}`, 'elliptic-integral field vs direct Biot–Savart; Newton’s third law'],
  maxwell: [R`\nabla\times\mathbf E=-\frac{\partial\mathbf B}{\partial t}`, 'loop and pill-box integrals at interfaces; u×B line integral = −dΦ/dt'],
  waves: [R`\gamma=\alpha+j\beta=j\omega\sqrt{\mu\varepsilon_c}`, 'closed form vs complex root; fields substituted back into both curl equations'],
  reflection: [R`\Gamma=\frac{\eta_2-\eta_1}{\eta_2+\eta_1}`, 'tangential E and H continuity; R + T = 1; Γ∥(θB) = 0'],
  tlines: [R`Z_{in}=Z_0\frac{Z_L+jZ_0\tan\beta l}{Z_0+jZ_L\tan\beta l}`, 'formula vs ABCD cascade; matching networks give Z_in = Z₀'],
  radiation: [R`f_{mn}=\frac{u}{2}\sqrt{(m/a)^2+(n/b)^2}`, 'transverse Helmholtz residual; E_tan = 0 on walls; R_rad = 30 Cin(2π)'],
  questions: [R`|x-x_{engine}|\le\varepsilon`, 'answers accepted only when the solver’s own checks pass'],
};

const METHODS = [
  ['Two independent formulas', 'α, β from the closed form are compared with Re/Im of a complex square root; Z_in with the ABCD matrix; loop field with direct Biot–Savart.', 'Ch. 5, 7, 3'],
  ['Back-substitution into Maxwell', 'The computed field is differentiated numerically and inserted into ∇×E = −jωμH and ∇×H = (σ + jωε)E; the residual must be at truncation-error level.', 'Ch. 5, 0, 8'],
  ['Integral laws evaluated numerically', 'Gauss flux over spheres, Ampère circulation, Stokes loops and pill-boxes at interfaces, field energy ∫½εE² dv = ½CV².', 'Ch. 2, 3, 4'],
  ['Limits and known values', 'Low-loss and good-conductor limits, dipole far field, Helmholtz-pair flatness, half-wave dipole R_rad = 73.1 Ω, WR-90 cut-off 6.557 GHz.', 'all'],
  ['Conservation', 'Power through every wavefront, R + T = 1, P_in = P_L on lossless lines, Newton’s third law between wires.', 'Ch. 0, 3, 6, 7'],
  ['Convergence', 'Differential elements approach the exact finite volume with first-order error as increments are halved.', 'Ch. 1'],
];

export function home(view, chapters) {
  const live = h('div', { 'aria-live': 'polite' });
  view.append(
    h('div', { class: 'eyebrow' }, 'OVERVIEW'),
    h('h1', {}, 'Electromagnetics you can check'),
    h('p', { class: 'lede' }, 'Interactive chapters following Ulaby & Ravaioli and Cheng. Change ε, μ, σ, frequency or geometry and a Python engine (NumPy/SciPy) recomputes every quantity, writes out the derivation with the numbers substituted, and verifies the result by a second, independent method. Nothing on a graph is drawn from a formula typed into the page.'),
    kv([['chapters', '9 + question bank'], ['problem templates', '28, randomised'], ['automated tests', '330+'], ['constants', 'CODATA 2022']]),
    h('h2', {}, 'A live example: a 1 MHz wave in sea water'),
    h('p', { class: 'prose' }, 'This is not a screenshot. The engine is running now — the same computation as Chapter 5, with every step and every check shown.'),
    live,
    h('h2', {}, 'Chapters'),
    h('div', { class: 'chapters' }, chapters.filter((c) => !c.group).map((c) => h('a', { class: 'chapter', href: `#/${c.id}` },
      h('div', { class: 'n' }, /^\d+(\.\d+)?$/.test(c.n) ? `Chapter ${c.n}` : c.n === 'Q' || c.n === 'W' ? 'Practice' : 'Tools'), h('div', { class: 'ti' }, c.title),
      KEY[c.id] ? h('div', { class: 'f' }, tex(KEY[c.id][0])) : null,
      h('p', {}, c.blurb), KEY[c.id] ? h('p', { class: 'chk' }, 'Checked: ', KEY[c.id][1]) : null))),
    h('h2', {}, 'How results are verified'),
    h('div', { class: 'tablewrap' }, h('table', { class: 't' }, h('thead', {}, h('tr', {}, ['Method', 'What is compared', 'Where'].map((x) => h('th', {}, x)))),
      h('tbody', {}, METHODS.map((m) => h('tr', {}, h('td', {}, h('b', {}, m[0])), h('td', {}, m[1]), h('td', { class: 'note' }, m[2])))))),
    h('p', { class: 'prose', style: 'margin-top:12px' }, 'A check reports the relative error against a stated tolerance. If any check of a result fails, the page says so next to the numbers instead of hiding it.'),
    h('h2', {}, 'References'),
    h('ul', { class: 'prose' },
      h('li', {}, 'F. T. Ulaby, U. Ravaioli, ', h('i', {}, 'Fundamentals of Applied Electromagnetics'), ', Pearson.'),
      h('li', {}, 'D. K. Cheng, ', h('i', {}, 'Field and Wave Electromagnetics'), ', Addison-Wesley.'),
      h('li', {}, 'D. J. Griffiths, ', h('i', {}, 'Introduction to Electrodynamics'), ', Cambridge University Press.'),
      h('li', {}, 'CODATA 2022 recommended values, via ', h('code', {}, 'scipy.constants'), '.'),
      h('li', {}, 'Problems in the question bank are original, written in the style of these texts; section references are for further reading.')),
    h('p', { class: 'hint', style: 'margin-top:20px' }, 'Source code and tests: ', h('a', { href: 'https://github.com/atahanguney/ElectroField' }, 'github.com/atahanguney/ElectroField'),
      ' · Previous version: ', h('a', { href: new URL('../../legacy/index.html', import.meta.url).href }, 'legacy page')),
    h('p', { class: 'hint' }, 'Built by ', h('a', { href: 'https://atahanguney.github.io/', rel: 'author' }, 'Atahan Güney'), ' — electrical & electronics engineering, Antalya Bilim University.'));

  const runLive = async () => {
    try {
      live.replaceChildren(h('p', { class: 'hint', role: 'status' }, 'Computing with the Python engine…'));
      const mode = await backend();
      const r = await api('waves/solve', { f: 1e6, eps_r: 81, mu_r: 1, sigma: 4, E0: 1 }, 'home');
      const v = r.values;
      live.replaceChildren(
        h('p', { class: 'hint' }, mode === 'pyodide' ? 'Computed in your browser by the Python engine (Pyodide).' : 'Computed by the local Python server.'),
        kv([['regime', v.regime], ['α', `${sci(v.alpha)} Np/m`], ['β', `${sci(v.beta)} rad/m`], ['|ηc|', si(v.eta_mag, 'Ω')], ['skin depth δs', si(v.skin_depth, 'm')], ['wavelength', si(v.wavelength, 'm')]]),
        h('h3', {}, 'Derivation'), stepsTable(r.steps), h('h3', {}, 'Independent checks'), checksTable(r.checks),
        h('p', {}, h('a', { href: '#/waves' }, 'Open Chapter 5 to change the medium and see the plots →')));
    } catch (e) {
      if (!e.stale) live.replaceChildren(h('p', { class: 'error' }, e.message));
    }
  };
  // With a local server the example is instant. In the browser build it first downloads the Python engine,
  // so it starts on request (or immediately if the engine is already running) — the landing page stays light.
  backend().then((m) => {
    if (m === 'server' || engineReady()) return runLive();
    live.replaceChildren(h('div', { class: 'panel' },
      h('p', { style: 'margin:0 0 8px' }, 'The computation runs in your browser. The first run downloads the Python engine (about 30 MB, cached afterwards).'),
      h('button', { class: 'btn primary', type: 'button', onclick: runLive }, 'Run the live example')));
  });
}
