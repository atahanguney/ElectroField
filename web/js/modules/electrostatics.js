// Chapter 2 — electrostatics (Ulaby ch. 4, Cheng ch. 3–4).
import { h, tex, control, segmented, stepsTable, checksTable, kv, si, sci, layout, plotCfg, C } from '../ui.js';
import { api, post, debounce } from '../api.js';

const R = String.raw;
const nC = 1e-9;
const PRESETS = {
  'Single charge': { q: [[1, 0, 0]], ground: false, probe: [0.5, 0.3] },
  'Dipole': { q: [[1, -0.25, 0], [-1, 0.25, 0]], ground: false, probe: [0, 0.4] },
  'Equal charges': { q: [[1, -0.3, 0], [1, 0.3, 0]], ground: false, probe: [0, 0.3] },
  '+2 and −1': { q: [[2, -0.3, 0], [-1, 0.3, 0]], ground: false, probe: [0.6, 0.3] },
  'Quadrupole': { q: [[1, -0.25, -0.25], [-1, 0.25, -0.25], [1, 0.25, 0.25], [-1, -0.25, 0.25]], ground: false, probe: [0.5, 0] },
  'Charge above ground': { q: [[1, 0, 0.4]], ground: true, probe: [0.3, 0.2] },
  'Dipole above ground': { q: [[1, -0.2, 0.4], [-1, 0.2, 0.4]], ground: true, probe: [0, 0.2] },
};

export function render(view, ch, init = {}) {
  const body = h('div');
  const tabs = { charges: chargesSection, gauss: gaussSection, capacitor: capSection };
  let cleanup = null;
  const show = (k) => { cleanup && cleanup(); body.replaceChildren(); cleanup = tabs[k](body, init[k]); };
  view.append(
    h('div', { class: 'eyebrow' }, `CHAPTER ${ch.n}`), h('h1', {}, ch.title),
    h('p', { class: 'lede' }, 'Static charges produce a field that is conservative (∮E·dl = 0) and whose flux through any closed surface equals the enclosed charge over ε. Three ways in: build a charge configuration and read its field, use symmetry and Gauss\'s law, or apply both to capacitors.'),
    segmented([['charges', 'Point charges & images'], ['gauss', "Gauss's law"], ['capacitor', 'Capacitors']], init.tab || 'charges', show),
    body, fundamentals());
  show(init.tab || 'charges');
  return () => cleanup && cleanup();
}

// ------------------------------------------------------------------ point charges
function chargesSection(root, init) {
  const P = structuredClone(init || PRESETS['Dipole']);
  const fig = h('div', { class: 'plot', style: 'height:560px' });
  const list = h('div'), err = h('div', { class: 'error' }), res = h('div'), contrib = h('div'), steps = h('div'), checks = h('div');
  const gnd = h('input', { type: 'checkbox', checked: P.ground, onchange: () => { P.ground = gnd.checked; run(); } });
  const showE = h('input', { type: 'checkbox', checked: true, onchange: () => last && draw(last) });
  let last = null;

  root.append(h('div', { class: 'work' },
    h('div', { class: 'panel' },
      h('h3', {}, 'Configurations'), h('div', { class: 'presets' }, Object.keys(PRESETS).map((k) => h('button', { class: 'btn', onclick: () => { Object.assign(P, structuredClone(PRESETS[k])); gnd.checked = P.ground; rows(); run(); } }, k))),
      h('h3', {}, 'Charges (plane z = 0)'), list,
      h('button', { class: 'btn', onclick: () => { if (P.q.length < 8) { P.q.push([1, 0, 0.2]); rows(); run(); } } }, 'Add charge'),
      h('label', { style: 'display:flex;gap:6px;align-items:center;margin-top:12px;font-size:13px' }, gnd, 'Grounded conducting plane at y = 0'),
      h('label', { style: 'display:flex;gap:6px;align-items:center;margin-top:6px;font-size:13px' }, showE, 'Shade |E| (log scale)'),
      h('p', { class: 'hint' }, 'Click anywhere on the plot to move the probe ⊕. Field-line count per charge is proportional to |q|.'), err),
    h('div', { class: 'figs' },
      h('div', { class: 'fig' }, fig, h('p', { class: 'cap' }, h('b', {}, 'Field lines and equipotentials. '),
        'Solid curves: E field lines (arrows give direction). Thin curves: equipotentials, red for V > 0, blue for V < 0, dashed for V = 0. They always cross at right angles because E = −∇V.')),
      res)),
  h('h2', {}, 'Superposition at the probe'), contrib,
  h('h2', {}, 'Derivation'), steps, h('h2', {}, 'Verification'), checks);

  function rows() {
    list.replaceChildren(h('div', { class: 'qrow head' }, h('span', {}, 'q (nC)'), h('span', {}, 'x (m)'), h('span', {}, 'y (m)'), h('span')),
      ...P.q.map((c, i) => h('div', { class: 'qrow' },
        ...[0, 1, 2].map((j) => h('input', { type: 'number', step: 'any', value: c[j], onchange: (e) => { c[j] = +e.target.value; run(); } })),
        h('button', { class: 'btn', title: 'remove', onclick: () => { if (P.q.length > 1) { P.q.splice(i, 1); rows(); run(); } } }, '×'))));
  }

  const run = debounce(async () => {
    try {
      last = await post('es/charges', { charges: P.q.map(([q, x, y]) => ({ q: q * nC, x, y })), ground: P.ground, probe: P.probe }, 'charges');
      err.textContent = ''; draw(last);
    } catch (e) { if (!e.stale) err.textContent = e.message; }
  });

  function draw(r) {
    const tr = [], ann = [], g = r.grid;
    if (showE.checked) tr.push({ type: 'heatmap', x: g.x, y: g.y, z: g.Emag, colorscale: [[0, 'rgba(0,0,0,0)'], [1, C.accent]], opacity: 0.35,
      showscale: true, colorbar: { title: { text: 'log₁₀|E|', side: 'right' }, thickness: 10, len: 0.6, tickfont: { size: 10 } }, hoverinfo: 'skip', zsmooth: 'best' });
    for (const e of r.equipotentials) tr.push({ x: e.x, y: e.y, mode: 'lines', hoverinfo: 'text', text: `V = ${sci(e.V, 3)} V`, showlegend: false,
      line: { color: e.V > 0 ? C.E : e.V < 0 ? C.H : C.ink, width: 1, dash: e.V === 0 ? 'dash' : 'solid' }, opacity: 0.8 });
    for (const l of r.field_lines) {
      tr.push({ x: l.x, y: l.y, mode: 'lines', line: { color: C.ink, width: 1.3 }, hoverinfo: 'skip', showlegend: false });
      const n = l.x.length, m = Math.floor(n * 0.45);
      if (n > 6) ann.push({ x: l.x[m + 1], y: l.y[m + 1], ax: l.x[m - 1], ay: l.y[m - 1], axref: 'x', ayref: 'y', showarrow: true, arrowhead: 2, arrowsize: 1.1, arrowwidth: 1.3, arrowcolor: C.ink, text: '' });
    }
    for (const q of r.charges) {
      const pos = q.q > 0;
      tr.push({ x: [q.x], y: [q.y], mode: 'markers+text', text: [`${pos ? '+' : '−'}`], textfont: { color: '#fff', size: 14 },
        marker: { size: 20, color: q.image ? 'rgba(0,0,0,0)' : pos ? C.E : C.H, line: { color: pos ? C.E : C.H, width: 2, dash: 'dot' } },
        hovertext: `${q.image ? 'image ' : ''}q = ${sci(q.q / nC, 3)} nC at (${q.x}, ${q.y})`, hoverinfo: 'text', showlegend: false });
    }
    const [px, py] = P.probe, E = r.values.E, Em = r.values.E_mag, L = 0.18;
    tr.push({ x: [px], y: [py], mode: 'markers', marker: { symbol: 'circle-cross-open', size: 14, color: C.S, line: { width: 2 } }, hoverinfo: 'skip', showlegend: false });
    if (Em > 0) ann.push({ x: px + L * E[0] / Em, y: py + L * E[1] / Em, ax: px, ay: py, axref: 'x', ayref: 'y', showarrow: true, arrowhead: 3, arrowwidth: 2.5, arrowcolor: C.S,
      text: `E = ${si(Em, 'V/m', 3)}`, font: { color: C.S, size: 12 }, xanchor: 'left' });
    const shapes = P.ground ? [{ type: 'rect', xref: 'paper', x0: 0, x1: 1, y0: -0.12, y1: 0, fillcolor: C.ink3, opacity: 0.35, line: { width: 0 } },
      { type: 'line', xref: 'paper', x0: 0, x1: 1, y0: 0, y1: 0, line: { color: C.ink, width: 2 } }] : [];
    const yr = P.ground ? [-0.12, 2] : [-1, 1];
    Plotly.react(fig, tr, layout({ annotations: ann, shapes, hovermode: 'closest', uirevision: P.ground ? 'g' : 'n',
      xaxis: { range: [-1, 1], title: { text: 'x (m)' }, zeroline: false, constrain: 'domain' },
      yaxis: { range: yr, title: { text: 'y (m)' }, scaleanchor: 'x', zeroline: false } }), plotCfg);
    attachClick();
    const v = r.values;
    res.replaceChildren(kv([['probe', `(${px.toFixed(3)}, ${py.toFixed(3)}) m`], ['Eₓ', `${sci(v.E[0])} V/m`], ['E_y', `${sci(v.E[1])} V/m`],
      ['|E|', si(v.E_mag, 'V/m')], ['V', si(v.V, 'V')], ['direction', `${(Math.atan2(v.E[1], v.E[0]) * 180 / Math.PI).toFixed(2)}°`]]));
    contrib.replaceChildren(h('div', { class: 'tablewrap' }, h('table', { class: 't' },
      h('thead', {}, h('tr', {}, ['source', 'q (nC)', '|R − Rᵢ| (m)', 'Eₓ (V/m)', 'E_y (V/m)', 'V (V)'].map((x) => h('th', {}, x)))),
      h('tbody', {}, r.contributions.map((c, i) => h('tr', {}, h('td', {}, c.image ? `image of q${i - P.q.length + 1}` : `q${i + 1}`),
        ...[c.q / nC, c.R, c.E[0], c.E[1], c.V].map((x) => h('td', { class: 'num' }, sci(x, 5))))),
        h('tr', {}, h('td', {}, h('b', {}, 'sum')), h('td'), h('td'), ...[v.E[0], v.E[1], v.V].map((x) => h('td', { class: 'num' }, h('b', {}, sci(x, 5)))))))));
    steps.replaceChildren(stepsTable(r.steps)); checks.replaceChildren(checksTable(r.checks));
  }

  // click → data coordinates (works on any part of the plot area)
  function attachClick() {
    if (fig._clickBound) return;
    fig._clickBound = true;
    fig.addEventListener('click', (ev) => {
      const fl = fig._fullLayout; if (!fl) return;
      const bb = fig.querySelector('.nsewdrag')?.getBoundingClientRect(); if (!bb) return;
      const x = fl.xaxis.p2l(ev.clientX - bb.left), y = fl.yaxis.p2l(ev.clientY - bb.top);
      if (ev.clientX < bb.left || ev.clientX > bb.right || ev.clientY < bb.top || ev.clientY > bb.bottom) return;
      P.probe = [+x.toFixed(4), +y.toFixed(4)]; run();
    });
  }

  rows(); run();
  return () => Plotly.purge(fig);
}

// ------------------------------------------------------------------ Gauss's law
const GK = {
  sphere: ['Uniform sphere', 'ρ_v', 'C/m³', 'spherical', 'a'], shell: ['Spherical shell', 'ρ_s', 'C/m²', 'spherical', 'a'],
  line: ['Line charge', 'ρ_l', 'C/m', 'cylindrical', 'b'], cylinder: ['Uniform cylinder', 'ρ_v', 'C/m³', 'cylindrical', 'ab'],
  coax: ['Coaxial line', 'ρ_l', 'C/m', 'cylindrical', 'ab'], sheet: ['Infinite sheet', 'ρ_s', 'C/m²', 'planar', ''],
  slab: ['Uniform slab', 'ρ_v', 'C/m³', 'planar', 'a'],
};
function gaussSection(root, init) {
  const S = { kind: 'sphere', rho: 1e-6, a: 0.1, b: 0.3, eps_r: 1, r: 0.05, ...(init || {}) };
  const ctl = h('div'), err = h('div', { class: 'error' }), res = h('div'), steps = h('div'), checks = h('div');
  const fE = h('div', { class: 'plot', style: 'height:300px' }), fV = h('div', { class: 'plot', style: 'height:260px' }), fS = h('div', { class: 'plot', style: 'height:300px' });
  const sel = h('select', { onchange: () => { S.kind = sel.value; build(); } }, Object.entries(GK).map(([k, v]) => h('option', { value: k, selected: k === S.kind }, v[0])));
  root.append(h('div', { class: 'work' },
    h('div', { class: 'panel' }, h('h3', {}, 'Distribution'), sel, h('div', { style: 'height:10px' }), ctl, err),
    h('div', { class: 'figs' },
      h('div', { class: 'grid2' }, h('div', { class: 'fig' }, fS, h('p', { class: 'cap' }, h('b', {}, 'Cross-section. '), 'Charge is shaded; the dashed curve is the Gaussian surface through the field point.')), res),
      h('div', { class: 'fig' }, fE, h('p', { class: 'cap' }, h('b', {}, 'E versus distance. '), 'The marker is the Gaussian surface. Kinks occur exactly where the enclosed charge stops growing.')),
      h('div', { class: 'fig' }, fV, h('p', { class: 'cap' }, h('b', {}, 'Potential. '), 'V is continuous everywhere — it is the integral of E.')))),
  h('h2', {}, 'Derivation'), steps, h('h2', {}, 'Verification'), checks);

  function build() {
    const g = GK[S.kind];
    const c = (o) => control({ ...o, onchange: (v) => { S[o.key] = v; run(); } }).el;
    ctl.replaceChildren(
      c({ key: 'rho', texLabel: g[1], unit: g[2], value: S.rho, min: 1e-12, max: 1e-3, log: true }),
      g[4].includes('a') ? c({ key: 'a', texLabel: 'a', label: 'radius / half-thickness', unit: 'm', value: S.a, min: 0.01, max: 0.5 }) : null,
      g[4].includes('b') ? c({ key: 'b', texLabel: 'b', label: S.kind === 'coax' ? 'outer radius' : 'zero-V reference', unit: 'm', value: S.b, min: 0.05, max: 2 }) : null,
      c({ key: 'eps_r', texLabel: '\\varepsilon_r', unit: '', value: S.eps_r, min: 1, max: 20 }),
      c({ key: 'r', texLabel: g[3] === 'spherical' ? 'R' : g[3] === 'planar' ? 'x' : 'r', label: 'field point', unit: 'm', value: S.r, min: 0.005, max: 1 }),
      h('p', { class: 'hint' }, 'Inside a uniform sphere E grows linearly with R; outside it falls as 1/R², exactly like a point charge Q at the centre.'));
    run();
  }
  const run = debounce(async () => {
    try {
      const r = await api('es/gauss', S, 'gauss'); err.textContent = ''; draw(r);
    } catch (e) { if (!e.stale) err.textContent = e.message; }
  });
  function draw(r) {
    const p = r.profile, v = r.values, geo = r.geometry, xl = geo === 'spherical' ? 'R (m)' : geo === 'planar' ? 'x (m)' : 'r (m)';
    const bands = [];
    if (['sphere', 'cylinder'].includes(S.kind)) bands.push([0, S.a]);
    if (S.kind === 'slab') bands.push([-S.a, S.a]);
    const marks = ['shell'].includes(S.kind) ? [S.a] : S.kind === 'coax' ? [S.a, S.b] : S.kind === 'sheet' ? [0] : [];
    const shapes = [...bands.map(([x0, x1]) => ({ type: 'rect', x0, x1, yref: 'paper', y0: 0, y1: 1, fillcolor: 'rgba(176,58,46,0.08)', line: { width: 0 }, layer: 'below' })),
      ...marks.map((x) => ({ type: 'line', x0: x, x1: x, yref: 'paper', y0: 0, y1: 1, line: { color: C.E, width: 2 } })),
      { type: 'line', x0: S.r, x1: S.r, yref: 'paper', y0: 0, y1: 1, line: { color: C.S, width: 1, dash: 'dash' } }];
    Plotly.react(fE, [{ x: p.r, y: p.E, mode: 'lines', line: { color: C.E, width: 2.2 }, name: 'E' },
      { x: [S.r], y: [v.E], mode: 'markers', marker: { color: C.S, size: 10 }, showlegend: false }],
      layout({ shapes, xaxis: { title: { text: xl } }, yaxis: { title: { text: 'E (V/m)' }, exponentformat: 'power' }, showlegend: false }), plotCfg);
    Plotly.react(fV, [{ x: p.r, y: p.V, mode: 'lines', line: { color: C.accent, width: 2.2 } }, { x: [S.r], y: [v.V], mode: 'markers', marker: { color: C.S, size: 10 } }],
      layout({ shapes, xaxis: { title: { text: xl } }, yaxis: { title: { text: 'V (V)' }, exponentformat: 'power' }, showlegend: false }), plotCfg);
    crossSection(fS, S, geo);
    res.replaceChildren(h('div', {}, h('div', { class: 'eyebrow', style: 'margin-bottom:6px' }, r.title.toUpperCase()),
      kv([['Q_enc', `${sci(v.Q_enc)} ${geo === 'spherical' ? 'C' : geo === 'planar' ? 'C/m²' : 'C/m'}`], ['D', `${sci(v.D)} C/m²`], ['E', si(v.E, 'V/m')], ['V', si(v.V, 'V')]])));
    steps.replaceChildren(stepsTable(r.steps)); checks.replaceChildren(checksTable(r.checks));
  }
  build();
  return () => [fE, fV, fS].forEach((f) => Plotly.purge(f));
}

function circ(r, n = 90) { const x = [], y = []; for (let i = 0; i <= n; i++) { const t = (2 * Math.PI * i) / n; x.push(r * Math.cos(t)); y.push(r * Math.sin(t)); } return [x, y]; }
function crossSection(el, S, geo) {
  const tr = [], L = Math.max(S.r, S.a, S.kind === 'coax' || S.kind === 'line' ? S.b : 0) * 1.25;
  const fill = 'rgba(176,58,46,0.22)';
  if (geo !== 'planar') {
    if (S.kind === 'sphere' || S.kind === 'cylinder') { const [x, y] = circ(S.a); tr.push({ x, y, fill: 'toself', fillcolor: fill, line: { color: C.E, width: 1 }, mode: 'lines' }); }
    if (S.kind === 'shell' || S.kind === 'coax') { const [x, y] = circ(S.a); tr.push({ x, y, line: { color: C.E, width: 3 }, mode: 'lines' }); }
    if (S.kind === 'coax') { const [x, y] = circ(S.b); tr.push({ x, y, line: { color: C.H, width: 3 }, mode: 'lines' }); }
    if (S.kind === 'line') tr.push({ x: [0], y: [0], mode: 'markers', marker: { color: C.E, size: 8 } });
    const [x, y] = circ(S.r); tr.push({ x, y, line: { color: C.S, width: 1.5, dash: 'dash' }, mode: 'lines' });
    tr.push({ x: [0, S.r], y: [0, 0], mode: 'lines+text', text: ['', geo === 'spherical' ? 'R' : 'r'], textposition: 'top left', line: { color: C.S, width: 1 } });
  } else {
    const w = S.kind === 'slab' ? S.a : 0.004 * L;
    tr.push({ x: [-w, w, w, -w, -w], y: [-L, -L, L, L, -L], fill: 'toself', fillcolor: fill, line: { color: C.E, width: 1 }, mode: 'lines' });
    tr.push({ x: [-S.r, S.r, S.r, -S.r, -S.r], y: [-L / 4, -L / 4, L / 4, L / 4, -L / 4], line: { color: C.S, width: 1.5, dash: 'dash' }, mode: 'lines' });
  }
  Plotly.react(el, tr.map((t) => ({ ...t, hoverinfo: 'skip', showlegend: false })), layout({ hovermode: false, margin: { l: 40, r: 10, t: 8, b: 36 },
    xaxis: { range: [-L, L], zeroline: false, constrain: 'domain' }, yaxis: { range: [-L, L], scaleanchor: 'x', zeroline: false } }), plotCfg);
}

// ------------------------------------------------------------------ capacitors
function capSection(root, init) {
  const S = { kind: 'coax', V0: 100, eps_r: 2.25, A: 1e-2, d: 1e-3, a: 0.45e-3, b: 1.47e-3, length: 1, E_bd: 3e6, ...(init || {}) };
  const ctl = h('div'), err = h('div', { class: 'error' }), res = h('div'), steps = h('div'), checks = h('div');
  const fE = h('div', { class: 'plot', style: 'height:300px' });
  const seg = segmented([['parallel', 'Parallel plate'], ['coax', 'Coaxial'], ['spherical', 'Spherical']], S.kind, (k) => { S.kind = k; build(); });
  root.append(h('div', { class: 'work' },
    h('div', { class: 'panel' }, h('h3', {}, 'Geometry'), seg, ctl, err),
    h('div', { class: 'figs' }, res, h('div', { class: 'fig' }, fE, h('p', { class: 'cap' }, h('b', {}, 'Field and potential across the dielectric. '),
      'The field is strongest at the inner conductor — that is where breakdown starts.')))),
  h('h2', {}, 'Derivation'), steps, h('h2', {}, 'Verification'), checks);
  function build() {
    const c = (o) => control({ ...o, onchange: (v) => { S[o.key] = v; run(); } }).el;
    const geo = S.kind === 'parallel'
      ? [c({ key: 'A', texLabel: 'A', label: 'plate area', unit: 'm²', value: S.A, min: 1e-6, max: 1, log: true }), c({ key: 'd', texLabel: 'd', label: 'gap', unit: 'm', value: S.d, min: 1e-6, max: 0.1, log: true })]
      : [c({ key: 'a', texLabel: 'a', label: 'inner radius', unit: 'm', value: S.a, min: 1e-5, max: 0.1, log: true }), c({ key: 'b', texLabel: 'b', label: 'outer radius', unit: 'm', value: S.b, min: 1e-5, max: 0.5, log: true }),
        S.kind === 'coax' ? c({ key: 'length', texLabel: '\\ell', label: 'length', unit: 'm', value: S.length, min: 0.01, max: 100, log: true }) : null];
    ctl.replaceChildren(...geo, c({ key: 'eps_r', texLabel: '\\varepsilon_r', unit: '', value: S.eps_r, min: 1, max: 100, log: true }),
      c({ key: 'V0', texLabel: 'V_0', label: 'applied voltage', unit: 'V', value: S.V0, min: 0.01, max: 1e5, log: true }),
      c({ key: 'E_bd', texLabel: 'E_{bd}', label: 'dielectric strength', unit: 'V/m', value: S.E_bd, min: 1e5, max: 1e9, log: true }),
      h('p', { class: 'hint' }, 'Defaults approximate RG-58 coax: a = 0.45 mm, b = 1.47 mm, polyethylene εr = 2.25. Air breaks down near 3 MV/m.'));
    run();
  }
  const run = debounce(async () => {
    try { draw(await api('es/capacitor', S, 'cap')); err.textContent = ''; } catch (e) { if (!e.stale) err.textContent = e.message; }
  });
  function draw(r) {
    const v = r.values, p = r.profile;
    res.replaceChildren(kv([['C', si(v.C, 'F')], ['Q = CV₀', si(v.Q, 'C')], ['W = ½CV₀²', si(v.W, 'J')], ['E_max', si(v.E_max, 'V/m')], ['breakdown V', si(v.V_bd, 'V')],
      ['field / strength', `${(100 * v.E_max / S.E_bd).toPrecision(3)} %`]]));
    Plotly.react(fE, [{ x: p.s, y: p.E, name: 'E (V/m)', line: { color: C.E, width: 2.2 } }, { x: p.sV, y: p.V, name: 'V (V)', yaxis: 'y2', line: { color: C.accent, width: 2.2 } }],
      layout({ xaxis: { title: { text: S.kind === 'parallel' ? 'position across gap (m)' : 'radius (m)' }, exponentformat: 'SI' }, yaxis: { title: { text: 'E (V/m)' }, exponentformat: 'power', rangemode: 'tozero' },
        yaxis2: { overlaying: 'y', side: 'right', title: { text: 'V (V)' }, showgrid: false, rangemode: 'tozero' }, margin: { r: 60 } }), plotCfg);
    steps.replaceChildren(stepsTable(r.steps)); checks.replaceChildren(checksTable(r.checks));
  }
  build();
  return () => Plotly.purge(fE);
}

// ------------------------------------------------------------------ reference
function fundamentals() {
  const rows = [
    ['Coulomb field', R`\mathbf E=\frac{q}{4\pi\varepsilon R^2}\hat{\mathbf R}`, 'Field of a point charge; superpose for many charges.', 'V/m'],
    ['Potential', R`V=-\int_\infty^P\mathbf E\cdot d\mathbf l,\quad \mathbf E=-\nabla V`, 'Work per unit charge; E points downhill in V.', 'V'],
    ['Gauss (integral)', R`\oint_S\mathbf D\cdot d\mathbf s=Q_{enc}`, 'Flux out of a closed surface counts the charge inside.', 'C'],
    ['Gauss (point)', R`\nabla\cdot\mathbf D=\rho_v`, 'Charge is the source of D.', 'C/m³'],
    ['Conservative', R`\oint\mathbf E\cdot d\mathbf l=0,\quad\nabla\times\mathbf E=0`, 'No net work around a loop in electrostatics.', ''],
    ['Poisson / Laplace', R`\nabla^2V=-\rho_v/\varepsilon\quad(\rho_v=0:\ \nabla^2V=0)`, 'Single equation for V; with boundary values it has a unique solution.', ''],
    ['Constitutive', R`\mathbf D=\varepsilon_0\mathbf E+\mathbf P=\varepsilon\mathbf E,\ \varepsilon=\varepsilon_r\varepsilon_0`, 'Polarisation of the dielectric reduces E for the same free charge.', 'C/m²'],
    ['Conductor', R`\mathbf E_{in}=0,\ V=\text{const},\ D_n=\rho_s`, 'Charge sits on the surface; field leaves normal to it.', ''],
    ['Boundary', R`E_{1t}=E_{2t},\quad D_{1n}-D_{2n}=\rho_s`, 'Tangential E continuous; normal D jumps by surface charge (Ch. 4).', ''],
    ['Capacitance', R`C=Q/V`, 'Depends only on geometry and ε.', 'F'],
    ['Energy', R`W_e=\tfrac12\int_v\varepsilon E^2\,dv=\tfrac12CV^2`, 'Energy is stored in the field itself.', 'J'],
  ];
  return h('div', {}, h('h2', {}, 'Fundamentals'),
    h('div', { class: 'tablewrap' }, h('table', { class: 't' }, h('thead', {}, h('tr', {}, ['Law', 'Relation', 'Meaning', 'Unit'].map((x) => h('th', {}, x)))),
      h('tbody', {}, rows.map((r) => h('tr', {}, h('td', {}, r[0]), h('td', {}, tex(r[1])), h('td', { class: 'note' }, r[2]), h('td', { class: 'num' }, r[3])))))));
}
