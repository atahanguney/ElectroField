// Landing page: what the workbench is, an engine-computed example shown at once, and the verification methods.
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
  const example = h('section', { class: 'example panel', 'aria-labelledby': 'ex-title' });
  const stats = h('div');
  view.append(
    h('div', { class: 'eyebrow' }, 'OVERVIEW'),
    h('h1', {}, 'Electromagnetics you can check'),
    h('p', { class: 'lede' }, 'Interactive chapters following Ulaby & Ravaioli and Cheng. A Python engine (NumPy/SciPy) computes every number, shows the derivation, and checks the result by a second, independent method.'),
    example,
    stats,
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

  exampleCard(example, stats);

}

// ---------- landing example: 1 MHz plane wave in sea water (Chapter 5) ----------
// Shown at once from web/data/home.json, which the engine wrote ahead of time
// (scripts/build_home_example.py; tests/test_home_example.py keeps it equal to the engine's output).
// "Run it live" recomputes the same case with the engine — in the browser (Pyodide) or on the local server.
const EX_PARAMS = { f: 1e6, eps_r: 81, mu_r: 1, sigma: 4, E0: 1 };

async function exampleCard(box, statsBox) {
  let snap;
  try {
    snap = await (await fetch(new URL('../data/home.json', import.meta.url))).json();
  } catch {
    box.replaceChildren(h('p', { class: 'error' }, 'The example could not be loaded. Open Chapter 5 to run it.'));
    return;
  }
  const c = snap.counts;
  statsBox.replaceWith(kv([['chapters', '9 + practice'], ['worked problems', String(c.worked)],
    ['question templates', `${c.templates}, randomised`], ['verification cases', String(c.report_cases)]]));

  const plot = h('div', { class: 'ex-plot' });
  const results = h('div');
  const source = h('p', { class: 'hint ex-source' });
  const actions = h('div', { class: 'ex-actions' });
  box.append(
    h('div', { class: 'ex-head' }, h('span', { class: 'eyebrow' }, 'EXAMPLE · CHAPTER 5'), h('span', { class: 'badge' }, 'computed by the engine')),
    h('h2', { id: 'ex-title', class: 'ex-title' }, 'How far does a 1 MHz radio wave get in sea water?'),
    h('p', { class: 'ex-q' }, 'Sea water: εr = 81, μr = 1, σ = 4 S/m. A plane wave of 1 V/m enters at z = 0.'),
    h('div', { class: 'ex-body' },
      h('figure', { class: 'ex-fig' }, plot,
        h('figcaption', { class: 'cap' }, h('span', { class: 'key-e' }, 'E', h('sub', {}, 'x'), '(z, t)'), ' travelling into the water; dashed: envelope ±E₀e', h('sup', {}, '−αz'), '. In a good conductor α ≈ β, so the wave dies out before completing one wavelength.')),
      results),
    actions, source);

  const show = (r, how) => {
    const v = r.values;
    results.replaceChildren(
      h('p', { class: 'ex-answer' }, 'It fades to 1/e every ', h('b', {}, si(v.skin_depth, 'm')), ' (skin depth) and loses ', h('b', {}, `${v.alpha_dB.toFixed(1)} dB`), ' per metre.'),
      kv([['regime', v.regime], ['α', `${sci(v.alpha)} Np/m`], ['β', `${sci(v.beta)} rad/m`],
        ['|ηc|', si(v.eta_mag, 'Ω')], ['skin depth δs', si(v.skin_depth, 'm')], ['wavelength λ', si(v.wavelength, 'm')]]),
      h('p', { class: r.all_passed ? 'ex-verdict pass' : 'ex-verdict fail' },
        r.all_passed ? `✓ ${r.checks.length} of ${r.checks.length} independent checks pass` : '✗ a check failed'),
      h('details', { class: 'ex-more' }, h('summary', {}, 'Derivation and checks'),
        h('h3', {}, 'Derivation'), stepsTable(r.steps), h('h3', {}, 'Independent checks'), checksTable(r.checks)));
    source.textContent = how;
    wave(plot, r.field, v);
  };
  show(snap, 'Precomputed by this site’s Python engine. “Run it live” recomputes it with the same engine.');

  const open = h('a', { class: 'btn primary', href: '#/waves' }, 'Change the medium in Chapter 5 →');
  const runBtn = h('button', { class: 'btn', type: 'button' }, 'Run it live');
  const runLive = async () => {
    runBtn.disabled = true;
    source.textContent = 'Starting the engine…';
    try {
      const mode = await backend();
      const r = await api('waves/solve', EX_PARAMS, 'home');
      r.field = { z: r.field.z, E: r.field.E };
      show(r, mode === 'pyodide' ? 'Computed just now in your browser by the Python engine (Pyodide).' : 'Computed just now by the local Python server.');
      runBtn.remove();
    } catch (e) {
      if (!e.stale) { source.textContent = `Could not run the engine: ${e.message}`; runBtn.disabled = false; }
    }
  };
  runBtn.addEventListener('click', runLive);
  actions.append(open, runBtn);
  backend().then((m) => {
    if (m === 'server' || engineReady()) return runLive();   // instant: no download needed
    runBtn.textContent = 'Run it live in your browser';
    actions.append(h('span', { class: 'hint' }, 'first run downloads the engine, about 30 MB'));
  });
}

// E_x(z,t) = Re{E(z) e^{jωt}} from the engine's phasor samples, drawn at the container's real width
// so the text stays readable on a phone. Animation stops when the plot leaves the page.
const NS = 'http://www.w3.org/2000/svg';
const sv = (tag, attrs = {}) => { const el = document.createElementNS(NS, tag); for (const [k, x] of Object.entries(attrs)) el.setAttribute(k, x); return el; };

function wave(box, field, v) {
  const z = field.z, re = field.E.re, im = field.E.im;
  const env = re.map((r, i) => Math.hypot(r, im[i]));
  const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const gen = (box._gen || 0) + 1;
  box._gen = gen;   // a newer call (live result) stops this one's animation
  let W = 0, path = null, X = null, Y = null;

  const draw = () => {
    W = Math.max(280, Math.round(box.clientWidth || 560));
    const H = W < 480 ? 190 : 230, L = 40, R = 12, T = 12, B = 34;
    const zmax = z[z.length - 1], ymax = Math.max(...env) * 1.08;
    X = (x) => L + (x / zmax) * (W - L - R);
    Y = (y) => T + (1 - (y + ymax) / (2 * ymax)) * (H - T - B);
    const line = (ys) => ys.map((y, i) => `${i ? 'L' : 'M'}${X(z[i]).toFixed(1)},${Y(y).toFixed(1)}`).join('');
    const svg = sv('svg', { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: 'img',
      'aria-label': `Electric field decaying into sea water; skin depth ${si(v.skin_depth, 'm')}` });
    // axes and ticks (z in cm)
    svg.append(sv('line', { x1: L, x2: W - R, y1: Y(0), y2: Y(0), class: 'ax0' }), sv('line', { x1: L, x2: L, y1: T, y2: H - B, class: 'ax' }),
      sv('line', { x1: L, x2: W - R, y1: H - B, y2: H - B, class: 'ax' }));
    const step = zmax * 100 > 60 ? 25 : 10;
    for (let cm = 0; cm <= zmax * 100 + 1e-9; cm += step) {
      svg.append(sv('line', { x1: X(cm / 100), x2: X(cm / 100), y1: H - B, y2: H - B + 4, class: 'ax' }));
      const t = sv('text', { x: X(cm / 100), y: H - B + 16, 'text-anchor': 'middle', class: 'tick' }); t.textContent = String(cm); svg.append(t);
    }
    const xl = sv('text', { x: W - R, y: H - 4, 'text-anchor': 'end', class: 'tick' }); xl.textContent = 'z (cm)';
    for (const y of [ymax / 1.08, 0, -ymax / 1.08]) {
      const t = sv('text', { x: L - 6, y: Y(y) + 4, 'text-anchor': 'end', class: 'tick' }); t.textContent = y === 0 ? '0' : (y > 0 ? '+E₀' : '−E₀'); svg.append(t);
    }
    // skin depth marker
    const xd = X(v.skin_depth);
    const dl = sv('text', { x: xd + 5, y: T + 12, class: 'tick' }); dl.textContent = `δs = ${si(v.skin_depth, 'm')}`;
    svg.append(sv('line', { x1: xd, x2: xd, y1: T, y2: H - B, class: 'mark' }), dl, xl,
      sv('path', { d: line(env), class: 'env' }), sv('path', { d: line(env.map((e) => -e)), class: 'env' }));
    path = sv('path', { class: 'e' });
    svg.append(path);
    box.replaceChildren(svg);
  };
  const frame = (t) => {
    if (!box.isConnected || box._gen !== gen) return;
    const ph = still ? 0 : (t / 1000) * Math.PI;    // one period every 2 s: slowed down from 1 MHz so it can be followed
    const c = Math.cos(ph), s = Math.sin(ph);
    path.setAttribute('d', re.map((r, i) => `${i ? 'L' : 'M'}${X(z[i]).toFixed(1)},${Y(r * c - im[i] * s).toFixed(1)}`).join(''));
    if (!still) requestAnimationFrame(frame);
  };
  box._redraw = () => { draw(); if (still) frame(0); };
  draw();
  frame(performance.now());
  if (!box._ro) {
    let last = box.clientWidth;
    box._ro = new ResizeObserver(() => { if (Math.abs(box.clientWidth - last) > 8) { last = box.clientWidth; box._redraw(); } });
    box._ro.observe(box);
  }
}
