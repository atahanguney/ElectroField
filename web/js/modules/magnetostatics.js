// Chapter 3 — magnetostatics (Ulaby ch. 5, Cheng ch. 6).
import { h, tex, control, segmented, stepsTable, checksTable, kv, si, sci, layout, plotCfg, onPlotClick, C } from '../ui.js';
import { api, post, debounce } from '../api.js';

const R = String.raw;

export function render(view, ch, init = {}) {
  const body = h('div');
  const tabs = { wires: wiresSection, loops: loopsSection, ampere: ampereSection, inductance: indSection };
  let cleanup = null;
  const show = (k) => { cleanup && cleanup(); body.replaceChildren(); cleanup = tabs[k](body, init[k]); };
  view.append(h('div', { class: 'eyebrow' }, `CHAPTER ${ch.n}`), h('h1', {}, ch.title),
    h('p', { class: 'lede' }, 'Steady currents produce a magnetic field that has no sources (∇·B = 0) and circulates around the current (∮H·dl = I). Field lines therefore always close, and the field of any current distribution is the sum of Biot–Savart contributions.'),
    segmented([['wires', 'Wires & forces'], ['loops', 'Loops & coils'], ['ampere', "Ampère's law"], ['inductance', 'Inductance']], init.tab || 'wires', show),
    body, fundamentals());
  show(init.tab || 'wires');
  return () => cleanup && cleanup();
}

const tables = (steps, checks, r) => { steps.replaceChildren(stepsTable(r.steps)); checks.replaceChildren(checksTable(r.checks)); };
const tail = (root, steps, checks) => root.append(h('h2', {}, 'Derivation'), steps, h('h2', {}, 'Verification'), checks);

// ------------------------------------------------------------------ parallel wires
const WP = {
  'Single wire': [[10, 0, 0]], 'Parallel (attract)': [[10, -0.25, 0], [10, 0.25, 0]], 'Antiparallel (repel)': [[10, -0.25, 0], [-10, 0.25, 0]],
  'Two-wire line + 3rd': [[10, -0.3, 0], [-10, 0.3, 0], [5, 0, 0.5]], 'Four (quadrupole)': [[10, -0.3, -0.3], [-10, 0.3, -0.3], [10, 0.3, 0.3], [-10, -0.3, 0.3]],
};
function wiresSection(root, init) {
  const S = { W: structuredClone(init?.W || WP['Parallel (attract)']), probe: init?.probe || [0, 0.5] };
  const fig = h('div', { class: 'plot', style: 'height:560px' }), list = h('div'), err = h('div', { class: 'error' }), res = h('div'), steps = h('div'), checks = h('div');
  root.append(h('div', { class: 'work' },
    h('div', { class: 'panel' }, h('h3', {}, 'Configurations'), h('div', { class: 'presets' }, Object.keys(WP).map((k) => h('button', { class: 'btn', onclick: () => { S.W = structuredClone(WP[k]); rows(); run(); } }, k))),
      h('h3', {}, 'Wires ⊥ page (I > 0 out of page ⊙)'), list,
      h('button', { class: 'btn', onclick: () => { if (S.W.length < 8) { S.W.push([5, 0, -0.4]); rows(); run(); } } }, 'Add wire'),
      h('p', { class: 'hint' }, 'Click the plot to move the probe. Field lines are contours of A_z at equal steps, so their spacing shows |B| directly: twice as dense, twice as strong.'), err),
    h('div', { class: 'figs' }, h('div', { class: 'fig' }, fig, h('p', { class: 'cap' }, h('b', {}, 'B field lines and forces. '),
      'Closed curves are B lines (right-hand rule around each current). Green arrows: force per unit length on each wire; the probe arrow shows B.')), res)));
  tail(root, steps, checks);
  function rows() {
    list.replaceChildren(h('div', { class: 'qrow head' }, h('span', {}, 'I (A)'), h('span', {}, 'x (m)'), h('span', {}, 'y (m)'), h('span')),
      ...S.W.map((w, i) => h('div', { class: 'qrow' }, ...[0, 1, 2].map((j) => h('input', { type: 'number', step: 'any', value: w[j], onchange: (e) => { w[j] = +e.target.value; run(); } })),
        h('button', { class: 'btn', onclick: () => { if (S.W.length > 1) { S.W.splice(i, 1); rows(); run(); } } }, '×'))));
  }
  const run = debounce(async () => {
    try { draw(await post('ms/wires', { currents: S.W.map(([I, x, y]) => ({ I, x, y })), probe: S.probe }, 'wires')); err.textContent = ''; } catch (e) { if (!e.stale) err.textContent = e.message; }
  });
  function draw(r) {
    const g = r.grid, tr = [], ann = [], v = r.values;
    tr.push({ type: 'heatmap', x: g.x, y: g.y, z: g.Bmag, colorscale: [[0, 'rgba(0,0,0,0)'], [1, C.H]], opacity: 0.35, zsmooth: 'best', hoverinfo: 'skip',
      colorbar: { title: { text: 'log₁₀|B|', side: 'right' }, thickness: 10, len: 0.6, tickfont: { size: 10 } } });
    r.field_lines.forEach((l) => tr.push({ x: l.x, y: l.y, mode: 'lines', line: { color: C.ink, width: 1.1 }, hoverinfo: 'skip', showlegend: false }));
    r.wires.forEach((w) => tr.push({ x: [w.x], y: [w.y], mode: 'markers+text', text: [w.I > 0 ? '•' : '×'], textfont: { size: 16, color: '#fff' },
      marker: { size: 20, color: w.I > 0 ? C.E : C.H }, hovertext: `I = ${w.I} A ${w.I > 0 ? 'out of page' : 'into page'}`, hoverinfo: 'text', showlegend: false }));
    const Fm = Math.max(...r.forces.map((f) => Math.hypot(...f)), 1e-30);
    r.forces.forEach((f, i) => { const m = Math.hypot(...f); if (m > 1e-30 * 10) { const w = r.wires[i], L = 0.22 * m / Fm;
      ann.push({ x: w.x + L * f[0] / m, y: w.y + L * f[1] / m, ax: w.x, ay: w.y, axref: 'x', ayref: 'y', showarrow: true, arrowhead: 3, arrowwidth: 2.5, arrowcolor: C.S,
        text: `${si(m, 'N/m', 3)}`, font: { size: 11, color: C.S } }); } });
    const [px, py] = S.probe, Bm = v.B_mag;
    tr.push({ x: [px], y: [py], mode: 'markers', marker: { symbol: 'circle-cross-open', size: 14, color: C.accent, line: { width: 2 } }, hoverinfo: 'skip', showlegend: false });
    if (Bm > 0) ann.push({ x: px + 0.18 * v.B[0] / Bm, y: py + 0.18 * v.B[1] / Bm, ax: px, ay: py, axref: 'x', ayref: 'y', showarrow: true, arrowhead: 3, arrowwidth: 2.5, arrowcolor: C.accent,
      text: `B = ${si(Bm, 'T', 3)}`, font: { color: C.accent, size: 12 }, xanchor: 'left' });
    Plotly.react(fig, tr, layout({ annotations: ann, hovermode: 'closest', uirevision: 'w', xaxis: { range: [-1, 1], title: { text: 'x (m)' }, zeroline: false, constrain: 'domain' },
      yaxis: { range: [-1, 1], title: { text: 'y (m)' }, scaleanchor: 'x', zeroline: false } }), plotCfg);
    res.replaceChildren(kv([['probe', `(${px.toFixed(3)}, ${py.toFixed(3)}) m`], ['Bₓ', `${sci(v.B[0])} T`], ['B_y', `${sci(v.B[1])} T`], ['|B|', si(Bm, 'T')], ['|H|', si(Bm / 1.25663706e-6, 'A/m')],
      ...r.forces.map((f, i) => [`F′ on wire ${i + 1}`, `${sci(Math.hypot(...f), 3)} N/m`])]));
    tables(steps, checks, r);
  }
  onPlotClick(fig, (x, y) => { S.probe = [+x.toFixed(4), +y.toFixed(4)]; run(); });
  rows(); run();
  return () => Plotly.purge(fig);
}

// ------------------------------------------------------------------ loops & coils
function loopsSection(root, init) {
  const S = { kind: 'helmholtz', I: 1, a: 0.1, N: 12, length: 0.4, pr: 0.05, pz: 0.03, ...(init || {}) };
  const fig = h('div', { class: 'plot', style: 'height:540px' }), fAx = h('div', { class: 'plot', style: 'height:280px' });
  const ctl = h('div'), err = h('div', { class: 'error' }), res = h('div'), steps = h('div'), checks = h('div');
  root.append(h('div', { class: 'work' },
    h('div', { class: 'panel' }, h('h3', {}, 'Coil'), segmented([['loop', 'Single loop'], ['helmholtz', 'Helmholtz pair'], ['solenoid', 'Solenoid']], S.kind, (k) => { S.kind = k; build(); }), ctl, err),
    h('div', { class: 'figs' }, h('div', { class: 'fig' }, fig, h('p', { class: 'cap' }, h('b', {}, 'Field lines in a plane through the axis. '),
      '⊗ / ⊙ mark the loop wires going into / out of the page. Each line is a contour of the flux function ρA_φ, so neighbouring lines enclose equal magnetic flux. Click to move the probe.')),
      h('div', { class: 'fig' }, fAx, h('p', { class: 'cap' }, h('b', {}, 'B_z on the axis. '), 'For the Helmholtz pair (spacing = a) the curve is flat at the centre — the reason it is used for uniform test fields.')), res)));
  tail(root, steps, checks);
  function build() {
    const c = (o) => control({ ...o, onchange: (v) => { S[o.key] = v; run(); } }).el;
    ctl.replaceChildren(c({ key: 'I', texLabel: 'I', label: 'current per turn', unit: 'A', value: S.I, min: 0.01, max: 1000, log: true }),
      c({ key: 'a', texLabel: 'a', label: 'radius', unit: 'm', value: S.a, min: 0.01, max: 1, log: true }),
      S.kind === 'solenoid' ? c({ key: 'N', texLabel: 'N', label: 'turns', value: S.N, min: 2, max: 60, step: 1 }) : null,
      S.kind === 'solenoid' ? c({ key: 'length', texLabel: '\\ell', label: 'length', unit: 'm', value: S.length, min: 0.02, max: 2, log: true }) : null);
    run();
  }
  const run = debounce(async () => {
    try { draw(await api('ms/loops', { ...S, N: Math.round(S.N) }, 'loops')); err.textContent = ''; } catch (e) { if (!e.stale) err.textContent = e.message; }
  });
  function draw(r) {
    const tr = [], v = r.values, g = r.grid;
    const full = (arr) => [...arr.slice().reverse().map((x) => -x), ...arr];
    tr.push({ type: 'heatmap', x: full(g.r), y: g.z, z: g.Bmag.map((row) => [...row.slice().reverse(), ...row]), colorscale: [[0, 'rgba(0,0,0,0)'], [1, C.H]], opacity: 0.35,
      zsmooth: 'best', hoverinfo: 'skip', zmin: Math.log10(Math.abs(v.B_center)) - 2.5, zmax: Math.log10(Math.abs(v.B_center)) + 0.5,
      colorbar: { title: { text: 'log₁₀|B|', side: 'right' }, thickness: 10, len: 0.6, tickfont: { size: 10 } } });
    r.field_lines.forEach((l) => { [1, -1].forEach((s) => tr.push({ x: l.x.map((x) => s * x), y: l.y, mode: 'lines', line: { color: C.ink, width: 1.1 }, hoverinfo: 'skip', showlegend: false })); });
    const pos = S.I > 0;
    tr.push({ x: r.loops.map((l) => l.a), y: r.loops.map((l) => l.z), mode: 'markers', marker: { symbol: pos ? 'x-thin-open' : 'circle-dot', size: 11, color: C.E, line: { width: 2, color: C.E } }, hoverinfo: 'skip', showlegend: false });
    tr.push({ x: r.loops.map((l) => -l.a), y: r.loops.map((l) => l.z), mode: 'markers', marker: { symbol: pos ? 'circle-dot' : 'x-thin-open', size: 11, color: C.E, line: { width: 2, color: C.E } }, hoverinfo: 'skip', showlegend: false });
    tr.push({ x: [S.pr], y: [S.pz], mode: 'markers', marker: { symbol: 'circle-cross-open', size: 14, color: C.accent, line: { width: 2 } }, hoverinfo: 'skip', showlegend: false });
    const ext = g.r[g.r.length - 1];
    Plotly.react(fig, tr, layout({ hovermode: 'closest', uirevision: S.kind, shapes: [{ type: 'line', x0: 0, x1: 0, yref: 'paper', y0: 0, y1: 1, line: { color: C.ink3, dash: 'dot', width: 1 } }],
      xaxis: { range: [-ext, ext], title: { text: 'ρ (m) — mirrored for the full cross-section' }, zeroline: false, constrain: 'domain' },
      yaxis: { title: { text: 'z (m)' }, scaleanchor: 'x', zeroline: false } }), plotCfg);
    Plotly.react(fAx, [{ x: r.axis.z, y: r.axis.Bz, line: { color: C.H, width: 2.2 } }], layout({ xaxis: { title: { text: 'z (m)' } }, yaxis: { title: { text: 'B_z (T)' }, exponentformat: 'power' }, showlegend: false }), plotCfg);
    res.replaceChildren(kv([['B at centre', si(v.B_center, 'T')], ['B_ρ at probe', `${sci(v.B[0])} T`], ['B_z at probe', `${sci(v.B[1])} T`], ['|B| at probe', si(v.B_mag, 'T')], ['dipole moment m', `${sci(v.m)} A·m²`]]));
    tables(steps, checks, r);
  }
  onPlotClick(fig, (x, y) => { S.pr = +Math.abs(x).toFixed(4); S.pz = +y.toFixed(4); run(); });
  build();
  return () => [fig, fAx].forEach((f) => Plotly.purge(f));
}

// ------------------------------------------------------------------ Ampère
const AK = { wire: 'Solid wire', tube: 'Hollow conductor', coax: 'Coaxial cable', toroid: 'Toroid', solenoid: 'Ideal solenoid' };
function ampereSection(root, init) {
  const S = { kind: 'coax', I: 5, a: 0.01, b: 0.02, c: 0.025, N: 100, n_per_m: 1000, mu_r: 1, r: 0.015, ...(init || {}) };
  const ctl = h('div'), err = h('div', { class: 'error' }), res = h('div'), steps = h('div'), checks = h('div');
  const fB = h('div', { class: 'plot', style: 'height:320px' }), fX = h('div', { class: 'plot', style: 'height:300px' });
  const sel = h('select', { onchange: () => { S.kind = sel.value; build(); } }, Object.entries(AK).map(([k, v]) => h('option', { value: k, selected: k === S.kind }, v)));
  root.append(h('div', { class: 'work' },
    h('div', { class: 'panel' }, h('h3', {}, 'Distribution'), sel, h('div', { style: 'height:10px' }), ctl, err),
    h('div', { class: 'figs' }, h('div', { class: 'grid2' }, h('div', { class: 'fig' }, fX, h('p', { class: 'cap' }, h('b', {}, 'Cross-section. '), 'Current-carrying regions shaded; dashed circle = Amperian path.')), res),
      h('div', { class: 'fig' }, fB, h('p', { class: 'cap' }, h('b', {}, 'B versus radius. '), 'Inside a uniform conductor B grows linearly (enclosed current ∝ r²); outside it falls as 1/r. A coax confines the field to r < c.')))));
  tail(root, steps, checks);
  function build() {
    const c = (o) => control({ ...o, onchange: (v) => { S[o.key] = v; run(); } }).el, k = S.kind;
    ctl.replaceChildren(c({ key: 'I', texLabel: 'I', label: 'current', unit: 'A', value: S.I, min: 0.01, max: 1e4, log: true }),
      c({ key: 'a', texLabel: 'a', unit: 'm', value: S.a, min: 1e-3, max: 0.1, log: true }),
      ['tube', 'coax', 'toroid'].includes(k) ? c({ key: 'b', texLabel: 'b', unit: 'm', value: S.b, min: 1e-3, max: 0.2, log: true }) : null,
      k === 'coax' ? c({ key: 'c', texLabel: 'c', label: 'outer shell edge', unit: 'm', value: S.c, min: 1e-3, max: 0.3, log: true }) : null,
      k === 'toroid' ? c({ key: 'N', texLabel: 'N', label: 'turns', value: S.N, min: 1, max: 5000, step: 1 }) : null,
      k === 'solenoid' ? c({ key: 'n_per_m', texLabel: 'n', label: 'turns per metre', unit: '1/m', value: S.n_per_m, min: 10, max: 1e5, log: true }) : null,
      c({ key: 'mu_r', texLabel: '\\mu_r', value: S.mu_r, min: 1, max: 1e4, log: true }),
      c({ key: 'r', texLabel: 'r', label: 'field point', unit: 'm', value: S.r, min: 1e-4, max: 0.3, log: true }));
    run();
  }
  const run = debounce(async () => {
    try { draw(await api('ms/ampere', { ...S, N: Math.round(S.N) }, 'amp')); err.textContent = ''; } catch (e) { if (!e.stale) err.textContent = e.message; }
  });
  function draw(r) {
    const p = r.profile, k = S.kind, bands = { wire: [[0, S.a]], tube: [[S.a, S.b]], coax: [[0, S.a], [S.b, S.c]], toroid: [[S.a, S.b]], solenoid: [[0, S.a]] }[k];
    const shapes = [...bands.map(([x0, x1]) => ({ type: 'rect', x0, x1, yref: 'paper', y0: 0, y1: 1, fillcolor: 'rgba(29,95,160,0.09)', line: { width: 0 }, layer: 'below' })),
      { type: 'line', x0: S.r, x1: S.r, yref: 'paper', y0: 0, y1: 1, line: { color: C.S, dash: 'dash', width: 1 } }];
    Plotly.react(fB, [{ x: p.r, y: p.B, line: { color: C.H, width: 2.2 } }, { x: [S.r], y: [r.values.B], mode: 'markers', marker: { color: C.S, size: 10 } }],
      layout({ shapes, showlegend: false, xaxis: { title: { text: 'r (m)' } }, yaxis: { title: { text: 'B (T)' }, exponentformat: 'power' } }), plotCfg);
    const circ = (rr) => { const x = [], y = []; for (let i = 0; i <= 90; i++) { const t = (2 * Math.PI * i) / 90; x.push(rr * Math.cos(t)); y.push(rr * Math.sin(t)); } return { x, y }; };
    const tr = [];
    const ring = (r0, r1) => { const A = circ(r1), B = circ(r0); tr.push({ x: [...A.x, ...B.x.reverse()], y: [...A.y, ...B.y.reverse()], fill: 'toself', fillcolor: 'rgba(29,95,160,0.25)', line: { color: C.H, width: 1 }, mode: 'lines' }); };
    bands.forEach(([x0, x1]) => ring(x0, x1));
    tr.push({ ...circ(S.r), mode: 'lines', line: { color: C.S, dash: 'dash', width: 1.5 } });
    const L = Math.max(S.r, ...bands.flat()) * 1.2;
    Plotly.react(fX, tr.map((t) => ({ ...t, hoverinfo: 'skip', showlegend: false })), layout({ hovermode: false, margin: { l: 40, r: 10, t: 8, b: 36 },
      xaxis: { range: [-L, L], zeroline: false, constrain: 'domain' }, yaxis: { range: [-L, L], scaleanchor: 'x', zeroline: false } }), plotCfg);
    res.replaceChildren(h('div', {}, h('div', { class: 'eyebrow', style: 'margin-bottom:6px' }, r.title.toUpperCase()), kv([['B', si(r.values.B, 'T')], ['H', si(r.values.H, 'A/m')]])));
    tables(steps, checks, r);
  }
  build();
  return () => [fB, fX].forEach((f) => Plotly.purge(f));
}

// ------------------------------------------------------------------ inductance
function indSection(root, init) {
  const S = { kind: 'coax', I: 1, N: 100, a: 0.45e-3, b: 1.47e-3, length: 1, h: 0.01, d: 0.01, mu_r: 1, ...(init || {}) };
  const ctl = h('div'), err = h('div', { class: 'error' }), res = h('div'), steps = h('div'), checks = h('div');
  root.append(h('div', { class: 'work' },
    h('div', { class: 'panel' }, h('h3', {}, 'Geometry'), segmented([['solenoid', 'Solenoid'], ['coax', 'Coax'], ['toroid', 'Toroid'], ['twowire', 'Two-wire']], S.kind, (k) => { S.kind = k; build(); }), ctl, err),
    h('div', { class: 'figs' }, res, h('div', { class: 'panel prose' }, h('p', {}, 'Inductance is flux linkage per ampere. It depends only on geometry and μ — just as capacitance depends only on geometry and ε. For a coax, L′C′ = με exactly, which is why the wave speed on the line is 1/√(με).')))));
  tail(root, steps, checks);
  function build() {
    const c = (o) => control({ ...o, onchange: (v) => { S[o.key] = v; run(); } }).el, k = S.kind;
    ctl.replaceChildren(
      ['solenoid', 'toroid'].includes(k) ? c({ key: 'N', texLabel: 'N', label: 'turns', value: S.N, min: 1, max: 1e4, log: true }) : null,
      c({ key: 'a', texLabel: 'a', label: k === 'solenoid' ? 'radius' : k === 'twowire' ? 'wire radius' : 'inner radius', unit: 'm', value: S.a, min: 1e-5, max: 0.1, log: true }),
      ['coax', 'toroid'].includes(k) ? c({ key: 'b', texLabel: 'b', label: 'outer radius', unit: 'm', value: S.b, min: 1e-5, max: 0.3, log: true }) : null,
      k === 'toroid' ? c({ key: 'h', texLabel: 'h', label: 'core height', unit: 'm', value: S.h, min: 1e-4, max: 0.1, log: true }) : null,
      k === 'twowire' ? c({ key: 'd', texLabel: 'd', label: 'centre spacing', unit: 'm', value: S.d, min: 1e-4, max: 1, log: true }) : null,
      k !== 'toroid' ? c({ key: 'length', texLabel: '\\ell', label: 'length', unit: 'm', value: S.length, min: 1e-3, max: 100, log: true }) : null,
      c({ key: 'mu_r', texLabel: '\\mu_r', value: S.mu_r, min: 1, max: 1e4, log: true }),
      c({ key: 'I', texLabel: 'I', label: 'current', unit: 'A', value: S.I, min: 1e-3, max: 1e3, log: true }));
    run();
  }
  const run = debounce(async () => {
    try {
      const r = await api('ms/inductance', { ...S, N: Math.round(S.N) }, 'ind'); err.textContent = '';
      res.replaceChildren(kv([['L', si(r.values.L, 'H')], ['per metre', r.values.L_per_m ? si(r.values.L_per_m, 'H/m') : '—'], ['W = ½LI²', si(r.values.W, 'J')]]));
      tables(steps, checks, r);
    } catch (e) { if (!e.stale) err.textContent = e.message; }
  });
  build();
  return () => {};
}

function fundamentals() {
  const rows = [
    ['Biot–Savart', R`d\mathbf H=\frac{I\,d\mathbf l\times\hat{\mathbf R}}{4\pi R^2}`, 'Field of a current element; integrate along the conductor.', 'A/m'],
    ['Infinite wire', R`\mathbf B=\hat\phi\frac{\mu I}{2\pi r}`, 'Circles around the wire, right-hand rule.', 'T'],
    ['Loop on axis', R`B_z=\frac{\mu Ia^2}{2(a^2+z^2)^{3/2}}`, 'Far away it is a dipole: μm/(2πz³), m = Iπa².', 'T'],
    ["Ampère (integral)", R`\oint_C\mathbf H\cdot d\mathbf l=I_{enc}`, 'Use with symmetry like Gauss\'s law in electrostatics.', 'A'],
    ['Ampère (point)', R`\nabla\times\mathbf H=\mathbf J`, 'Currents are the vortices of H.', 'A/m²'],
    ['No monopoles', R`\nabla\cdot\mathbf B=0,\ \oint\mathbf B\cdot d\mathbf s=0`, 'B lines close; flux into a volume equals flux out.', ''],
    ['Vector potential', R`\mathbf B=\nabla\times\mathbf A,\ \ \mathbf A=\frac{\mu}{4\pi}\int\frac{\mathbf J}{R}dv`, 'Satisfies ∇·B = 0 automatically.', 'Wb/m'],
    ['Force on current', R`d\mathbf F=I\,d\mathbf l\times\mathbf B,\quad F'=\frac{\mu_0I_1I_2}{2\pi d}`, 'Parallel currents attract.', 'N'],
    ['Constitutive', R`\mathbf B=\mu\mathbf H=\mu_0(\mathbf H+\mathbf M)`, 'Magnetisation of the material adds to the applied field.', ''],
    ['Boundary', R`B_{1n}=B_{2n},\quad \hat n_2\times(\mathbf H_1-\mathbf H_2)=\mathbf J_s`, 'See Chapter 4.', ''],
    ['Inductance & energy', R`L=\Lambda/I,\quad W_m=\tfrac12LI^2=\int\frac{B^2}{2\mu}dv`, 'Energy is stored in the field.', 'H, J'],
  ];
  return h('div', {}, h('h2', {}, 'Fundamentals'),
    h('div', { class: 'tablewrap' }, h('table', { class: 't' }, h('thead', {}, h('tr', {}, ['Law', 'Relation', 'Meaning', 'Unit'].map((x) => h('th', {}, x)))),
      h('tbody', {}, rows.map((r) => h('tr', {}, h('td', {}, r[0]), h('td', {}, tex(r[1])), h('td', { class: 'note' }, r[2]), h('td', { class: 'num' }, r[3])))))));
}
