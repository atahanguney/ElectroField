// Chapter 6 — reflection and transmission of plane waves (Ulaby ch. 8, Cheng ch. 8).
import { h, tex, control, segmented, stepsTable, checksTable, kv, si, sci, layout, plotCfg, C } from '../ui.js';
import { api, debounce } from '../api.js';

const R = String.raw;

export function render(view, ch, init = {}) {
  const body = h('div');
  const tabs = { normal: normalSection, oblique: obliqueSection };
  let cleanup = null;
  const show = (k) => { cleanup && cleanup(); body.replaceChildren(); cleanup = tabs[k](body, init[k]); };
  view.append(h('div', { class: 'eyebrow' }, `CHAPTER ${ch.n}`), h('h1', {}, ch.title),
    h('p', { class: 'lede' }, 'At an interface the tangential E and H must be continuous. That single requirement fixes how much of a wave is reflected and how much passes, and — at oblique incidence — the direction of the transmitted wave, the angle of zero reflection (Brewster) and the angle beyond which nothing is transmitted (critical angle).'),
    segmented([['normal', 'Normal incidence'], ['oblique', 'Oblique incidence']], init.tab || 'normal', show), body, theory());
  show(init.tab || 'normal');
  return () => cleanup && cleanup();
}

const PRE = [['Air → glass', { eps1: 1, s1: 0, eps2: 2.25, s2: 0 }], ['Air → water', { eps1: 1, s1: 0, eps2: 80, s2: 1e-3 }],
  ['Air → sea water', { eps1: 1, s1: 0, eps2: 81, s2: 4 }], ['Air → copper', { eps1: 1, s1: 0, eps2: 1, s2: 5.8e7 }], ['Glass → air', { eps1: 2.25, s1: 0, eps2: 1, s2: 0 }]];

function normalSection(root, init) {
  const S = { f: 1e8, eps1: 1, mu1: 1, s1: 0, eps2: 2.25, mu2: 1, s2: 0, E0: 1, ...(init || {}) };
  const err = h('div', { class: 'error' }), res = h('div'), steps = h('div'), checks = h('div');
  const fig = h('div', { class: 'plot', style: 'height:400px' });
  let last = null, phase = 0, playing = false, timer = 0;
  const c = (o) => control({ ...o, onchange: (v) => { S[o.key] = v; run(); } });
  const cs = { f: c({ key: 'f', texLabel: 'f', unit: 'Hz', value: S.f, min: 1e3, max: 1e12, log: true }),
    eps1: c({ key: 'eps1', texLabel: '\\varepsilon_{r1}', value: S.eps1, min: 1, max: 100, log: true }), s1: c({ key: 's1', texLabel: '\\sigma_1', unit: 'S/m', value: S.s1, min: 1e-8, max: 1e8, log: true }),
    eps2: c({ key: 'eps2', texLabel: '\\varepsilon_{r2}', value: S.eps2, min: 1, max: 100, log: true }), s2: c({ key: 's2', texLabel: '\\sigma_2', unit: 'S/m', value: S.s2, min: 1e-8, max: 1e8, log: true }),
    mu2: c({ key: 'mu2', texLabel: '\\mu_{r2}', value: S.mu2, min: 1, max: 1e4, log: true }) };
  const ph = control({ texLabel: '\\omega t', unit: '°', value: 0, min: 0, max: 360, step: 1, onchange: (v) => { phase = v; draw(); } });
  const play = h('button', { class: 'btn', onclick: () => { playing = !playing; play.textContent = playing ? 'Pause' : 'Play'; if (playing) tick(); } }, 'Play');
  root.append(h('div', { class: 'work' },
    h('div', { class: 'panel' }, h('h3', {}, 'Media'), h('div', { class: 'presets' }, PRE.map(([n, v]) => h('button', { class: 'btn', onclick: () => Object.entries(v).forEach(([k, x]) => cs[k].set(x)) }, n))),
      cs.f.el, h('h3', {}, 'Medium 1 (z < 0)'), cs.eps1.el, cs.s1.el, h('h3', {}, 'Medium 2 (z > 0)'), cs.eps2.el, cs.mu2.el, cs.s2.el,
      h('p', { class: 'hint' }, 'σ fields accept 0. A lossy medium 1 has no single standing-wave ratio, so S is shown only when σ₁ = 0.'), err),
    h('div', { class: 'figs' }, res, h('div', { class: 'fig' }, fig, h('div', { style: 'display:grid;grid-template-columns:80px 1fr;gap:12px;align-items:center' }, play, ph.el),
      h('p', { class: 'cap' }, h('b', {}, 'Total field on both sides of the interface. '), 'Dotted: |E(z)| envelope — the standing-wave pattern in medium 1 (maxima λ₁/2 apart) and the decaying transmitted wave in medium 2. Solid: instantaneous E_x.')))));
  root.append(h('h2', {}, 'Derivation'), steps, h('h2', {}, 'Verification'), checks);
  const run = debounce(async () => { try { last = await api('rf/normal', S, 'rfn'); err.textContent = ''; show(); } catch (e) { if (!e.stale) err.textContent = e.message; } });
  function show() {
    const v = last.values;
    res.replaceChildren(kv([['Γ', `${sci(v.Gamma_mag)} ∠ ${v.Gamma_deg.toFixed(2)}°`], ['τ', sci(v.tau)], ['S (SWR)', v.S == null ? '∞' : sci(v.S)],
      ['R reflected power', `${(100 * v.R).toPrecision(4)} %`], ['T transmitted power', `${(100 * v.T).toPrecision(4)} %`], ['λ₁', si(v.lambda1, 'm')], ['λ₂', si(v.lambda2, 'm')]]));
    steps.replaceChildren(stepsTable(last.steps)); checks.replaceChildren(checksTable(last.checks)); draw();
  }
  const inst = (F, p) => F.re.map((r, i) => r * Math.cos(p) - F.im[i] * Math.sin(p));
  const env = (F) => F.re.map((r, i) => Math.hypot(r, F.im[i]));
  function draw() {
    if (!last) return;
    const F = last.field, p = (phase * Math.PI) / 180;
    Plotly.react(fig, [
      { x: F.z1, y: env(F.E1), mode: 'lines', line: { color: C.E, dash: 'dot', width: 1.2 }, name: '|E| envelope' },
      { x: F.z2, y: env(F.E2), mode: 'lines', line: { color: C.E, dash: 'dot', width: 1.2 }, showlegend: false },
      { x: F.z1, y: inst(F.E1, p), mode: 'lines', line: { color: C.E, width: 2 }, name: 'E_x(z, t)' },
      { x: F.z2, y: inst(F.E2, p), mode: 'lines', line: { color: C.E, width: 2 }, showlegend: false },
    ], layout({ shapes: [{ type: 'rect', x0: 0, x1: F.z2[F.z2.length - 1], yref: 'paper', y0: 0, y1: 1, fillcolor: C.accent, opacity: 0.08, line: { width: 0 }, layer: 'below' },
      { type: 'line', x0: 0, x1: 0, yref: 'paper', y0: 0, y1: 1, line: { color: C.ink, width: 1.5 } }],
      xaxis: { title: { text: 'z (m)' }, exponentformat: 'SI' }, yaxis: { title: { text: 'E (V/m)' } } }), plotCfg);
  }
  function tick() { if (!playing) return; phase = (phase + 5) % 360; ph.set(phase); timer = setTimeout(tick, 50); }
  run();
  return () => { playing = false; clearTimeout(timer); Plotly.purge(fig); };
}

function obliqueSection(root, init) {
  const S = { eps1: 1, mu1: 1, eps2: 2.25, mu2: 1, theta_deg: 40, ...(init || {}) };
  const err = h('div', { class: 'error' }), res = h('div'), steps = h('div'), checks = h('div');
  const fRay = h('div', { class: 'plot', style: 'height:420px' }), fR = h('div', { class: 'plot', style: 'height:340px' });
  const c = (o) => control({ ...o, onchange: (v) => { S[o.key] = v; run(); } });
  const cs = { eps1: c({ key: 'eps1', texLabel: '\\varepsilon_{r1}', value: S.eps1, min: 1, max: 20, log: true }), eps2: c({ key: 'eps2', texLabel: '\\varepsilon_{r2}', value: S.eps2, min: 1, max: 20, log: true }),
    mu2: c({ key: 'mu2', texLabel: '\\mu_{r2}', value: S.mu2, min: 1, max: 100, log: true }),
    th: c({ key: 'theta_deg', texLabel: '\\theta_i', label: 'incidence', unit: '°', value: S.theta_deg, min: 0, max: 89.5, step: 0.1 }) };
  const pre = [['Air → glass', 1, 2.25], ['Glass → air', 2.25, 1], ['Air → water (optical)', 1, 1.77], ['Water → air', 1.77, 1]];
  root.append(h('div', { class: 'work' },
    h('div', { class: 'panel' }, h('h3', {}, 'Media (lossless)'), h('div', { class: 'presets' }, pre.map(([n, a, b]) => h('button', { class: 'btn', onclick: () => { cs.eps1.set(a); cs.eps2.set(b); } }, n))),
      cs.eps1.el, cs.eps2.el, cs.mu2.el, cs.th.el, err),
    h('div', { class: 'figs' }, h('div', { class: 'fig' }, fRay, h('p', { class: 'cap' }, h('b', {}, 'Rays at the interface. '),
      'Line width ∝ power fraction (TE solid, TM dashed for the reflected ray). Beyond the critical angle the transmitted wave becomes evanescent and is not drawn.')), res)),
  h('div', { class: 'fig', style: 'margin-top:16px' }, fR, h('p', { class: 'cap' }, h('b', {}, 'Reflectivity versus angle. '), 'R∥ drops to zero at the Brewster angle, so reflected light there is purely TE-polarised. Above θc both reach 1.')),
  h('h2', {}, 'Derivation'), steps, h('h2', {}, 'Verification'), checks);
  const run = debounce(async () => { try { draw(await api('rf/oblique', S, 'rfo')); err.textContent = ''; } catch (e) { if (!e.stale) err.textContent = e.message; } });
  function draw(r) {
    const v = r.values, th = (S.theta_deg * Math.PI) / 180, tt = (v.theta_t * Math.PI) / 180, L = 1;
    const tr = [], ann = [];
    const ray = (x0, y0, x1, y1, w, col, dash, label) => { tr.push({ x: [x0, x1], y: [y0, y1], mode: 'lines', line: { color: col, width: Math.max(w, 0.6), dash }, hoverinfo: 'skip', showlegend: false });
      ann.push({ x: x1, y: y1, ax: x0 + 0.8 * (x1 - x0), ay: y0 + 0.8 * (y1 - y0), axref: 'x', ayref: 'y', showarrow: true, arrowhead: 2, arrowwidth: 1.5, arrowcolor: col, text: '' });
      if (label) ann.push({ x: x1, y: y1, text: label, showarrow: false, xanchor: x1 < 0 ? 'right' : 'left', font: { size: 12, color: col } }); };
    ray(-L * Math.sin(th), L * Math.cos(th), 0, 0, 5, C.E, 'solid', '');
    ann.push({ x: -L * Math.sin(th), y: L * Math.cos(th), text: 'incident', showarrow: false, xanchor: 'right', font: { size: 12, color: C.E } });
    ray(0, 0, L * Math.sin(th), L * Math.cos(th), 5 * v.R_perp, C.E, 'solid', `R⊥ ${(100 * v.R_perp).toFixed(1)}%  R∥ ${(100 * v.R_par).toFixed(1)}%`);
    if (v.R_par > 0.002) tr.push({ x: [0, L * Math.sin(th)], y: [0, L * Math.cos(th)], mode: 'lines', line: { color: C.H, width: 5 * v.R_par, dash: 'dash' }, hoverinfo: 'skip', showlegend: false });
    if (!v.tir) ray(0, 0, L * Math.sin(tt), -L * Math.cos(tt), 5 * v.T_perp, C.S, 'solid', `θt = ${v.theta_t.toFixed(2)}°  T⊥ ${(100 * v.T_perp).toFixed(1)}%`);
    else ann.push({ x: 0.5, y: -0.25, text: 'total internal reflection — evanescent field only', showarrow: false, font: { size: 12, color: C.ink3 } });
    tr.push({ x: [0, 0], y: [-1.1, 1.1], mode: 'lines', line: { color: C.ink3, dash: 'dot', width: 1 }, hoverinfo: 'skip', showlegend: false });
    const arc = (r0, a0, a1, down) => { const x = [], y = []; for (let i = 0; i <= 30; i++) { const a = a0 + ((a1 - a0) * i) / 30; x.push(r0 * Math.sin(a)); y.push((down ? -1 : 1) * r0 * Math.cos(a)); } return { x, y }; };
    tr.push({ ...arc(0.3, -th, 0), mode: 'lines', line: { color: C.ink, width: 1.2 }, hoverinfo: 'skip', showlegend: false });
    ann.push({ x: -0.36 * Math.sin(th / 2), y: 0.36 * Math.cos(th / 2), text: `θi = ${S.theta_deg.toFixed(1)}°`, showarrow: false, xanchor: 'right', font: { size: 12 } });
    const op = (e) => Math.min(0.05 + 0.12 * Math.log10(e) * 3, 0.45);
    Plotly.react(fRay, tr, layout({ hovermode: false, annotations: ann, margin: { l: 10, r: 10, t: 10, b: 10 },
      shapes: [{ type: 'rect', x0: -1.3, x1: 1.3, y0: 0, y1: 1.15, fillcolor: C.accent, opacity: op(S.eps1 * S.mu1), line: { width: 0 }, layer: 'below' },
        { type: 'rect', x0: -1.3, x1: 1.3, y0: -1.15, y1: 0, fillcolor: C.accent, opacity: op(S.eps2 * S.mu2), line: { width: 0 }, layer: 'below' },
        { type: 'line', x0: -1.3, x1: 1.3, y0: 0, y1: 0, line: { color: C.ink, width: 2 } }],
      xaxis: { range: [-1.3, 1.3], visible: false, constrain: 'domain' }, yaxis: { range: [-1.15, 1.15], visible: false, scaleanchor: 'x' } }), plotCfg);
    const sw = r.sweep, marks = [];
    if (v.theta_B != null) marks.push({ type: 'line', x0: v.theta_B, x1: v.theta_B, yref: 'paper', y0: 0, y1: 1, line: { color: C.H, dash: 'dash', width: 1 }, label: { text: `θB ${v.theta_B.toFixed(1)}°`, textposition: 'end', font: { size: 11 } } });
    if (v.theta_c != null) marks.push({ type: 'line', x0: v.theta_c, x1: v.theta_c, yref: 'paper', y0: 0, y1: 1, line: { color: C.E, dash: 'dash', width: 1 }, label: { text: `θc ${v.theta_c.toFixed(1)}°`, textposition: 'end', font: { size: 11 } } });
    marks.push({ type: 'line', x0: S.theta_deg, x1: S.theta_deg, yref: 'paper', y0: 0, y1: 1, line: { color: C.S, width: 1 } });
    Plotly.react(fR, [{ x: sw.theta, y: sw.R_perp, name: 'R⊥ (TE)', line: { color: C.E, width: 2.2 } }, { x: sw.theta, y: sw.R_par, name: 'R∥ (TM)', line: { color: C.H, width: 2.2 } },
      { x: sw.theta, y: sw.T_perp, name: 'T⊥', line: { color: C.E, width: 1, dash: 'dot' } }, { x: sw.theta, y: sw.T_par, name: 'T∥', line: { color: C.H, width: 1, dash: 'dot' } }],
      layout({ shapes: marks, xaxis: { title: { text: 'θi (degrees)' }, range: [0, 90] }, yaxis: { title: { text: 'power fraction' }, range: [0, 1.02] } }), plotCfg);
    res.replaceChildren(kv([['θt', v.tir ? 'evanescent' : `${v.theta_t.toFixed(3)}°`], ['Brewster θB', v.theta_B == null ? '—' : `${v.theta_B.toFixed(3)}°`], ['critical θc', v.theta_c == null ? '—' : `${v.theta_c.toFixed(3)}°`],
      ['R⊥ / T⊥', `${sci(v.R_perp, 4)} / ${sci(v.T_perp, 4)}`], ['R∥ / T∥', `${sci(v.R_par, 4)} / ${sci(v.T_par, 4)}`]]));
    steps.replaceChildren(stepsTable(r.steps)); checks.replaceChildren(checksTable(r.checks));
  }
  run();
  return () => [fRay, fR].forEach((f) => Plotly.purge(f));
}

function theory() {
  const rows = [
    ['Normal incidence', R`\Gamma=\frac{\eta_2-\eta_1}{\eta_2+\eta_1},\quad\tau=1+\Gamma`, 'From E and H tangential continuity at z = 0.'],
    ['Standing waves', R`|E_1(z)|=E_0\left|1+\Gamma e^{j2k_1z}\right|,\quad S=\frac{1+|\Gamma|}{1-|\Gamma|}`, 'Maxima λ/2 apart; S = 1 means no reflection.'],
    ['Snell', R`k_1\sin\theta_i=k_2\sin\theta_t\ \ (n_1\sin\theta_i=n_2\sin\theta_t)`, 'Phase matching along the interface.'],
    ['TE (⊥)', R`\Gamma_\perp=\frac{\eta_2\cos\theta_i-\eta_1\cos\theta_t}{\eta_2\cos\theta_i+\eta_1\cos\theta_t}`, 'E parallel to the interface.'],
    ['TM (∥)', R`\Gamma_\parallel=\frac{\eta_2\cos\theta_t-\eta_1\cos\theta_i}{\eta_2\cos\theta_t+\eta_1\cos\theta_i}`, 'E in the plane of incidence.'],
    ['Brewster', R`\tan\theta_B=n_2/n_1\ \ (\mu_1=\mu_2)`, 'Γ∥ = 0: polarisation by reflection.'],
    ['Critical angle', R`\sin\theta_c=n_2/n_1\ \ (n_1>n_2)`, 'Above θc: |Γ| = 1, optical fibres.'],
    ['Power', R`R=|\Gamma|^2,\quad T=|\tau|^2\frac{\eta_1\cos\theta_t}{\eta_2\cos\theta_i},\quad R+T=1`, 'Lossless media.'],
  ];
  return h('div', {}, h('h2', {}, 'Summary'), h('div', { class: 'tablewrap' }, h('table', { class: 't' }, h('thead', {}, h('tr', {}, ['Case', 'Relation', 'Meaning'].map((x) => h('th', {}, x)))),
    h('tbody', {}, rows.map((r) => h('tr', {}, h('td', {}, r[0]), h('td', {}, tex(r[1])), h('td', { class: 'note' }, r[2])))))));
}
