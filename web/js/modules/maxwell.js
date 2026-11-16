// Chapter 4 — Maxwell's equations, boundary conditions, Faraday's law, displacement current.
import { h, tex, control, segmented, stepsTable, checksTable, kv, si, sci, layout, plotCfg, C } from '../ui.js';
import { api, debounce } from '../api.js';

const R = String.raw;

export function render(view, ch, init = {}) {
  const body = h('div');
  const tabs = { equations: equations, boundary: boundarySection, faraday: faradaySection, currents: currentsSection };
  let cleanup = null;
  const show = (k) => { cleanup && cleanup(); body.replaceChildren(); cleanup = tabs[k](body, init[k]); };
  view.append(h('div', { class: 'eyebrow' }, `CHAPTER ${ch.n}`), h('h1', {}, ch.title),
    h('p', { class: 'lede' }, 'Four equations tie E, D, H and B to their sources. When fields change in time, a changing B induces E (Faraday) and a changing D acts as a current (Maxwell). Across any interface the same equations, applied to vanishing loops and pill-boxes, fix how the fields jump.'),
    segmented([['equations', 'The equations'], ['boundary', 'Boundary conditions'], ['faraday', "Faraday's law"], ['currents', 'Displacement current']], init.tab || 'equations', show),
    body);
  show(init.tab || 'equations');
  return () => cleanup && cleanup();
}

// ------------------------------------------------------------------ reference
function equations(root) {
  const rows = [
    ["Gauss's law", R`\nabla\cdot\mathbf D=\rho_v`, R`\oint_S\mathbf D\cdot d\mathbf s=Q`, 'Electric flux leaving a closed surface equals the free charge inside. Charges are sources and sinks of D.'],
    ["Faraday's law", R`\nabla\times\mathbf E=-\frac{\partial\mathbf B}{\partial t}`, R`\oint_C\mathbf E\cdot d\mathbf l=-\frac{d}{dt}\int_S\mathbf B\cdot d\mathbf s`, 'A changing magnetic flux induces a circulating E — the EMF of transformers and generators.'],
    ['No magnetic charge', R`\nabla\cdot\mathbf B=0`, R`\oint_S\mathbf B\cdot d\mathbf s=0`, 'Field lines of B always close on themselves; there are no isolated poles.'],
    ['Ampère–Maxwell', R`\nabla\times\mathbf H=\mathbf J+\frac{\partial\mathbf D}{\partial t}`, R`\oint_C\mathbf H\cdot d\mathbf l=I+\frac{d}{dt}\int_S\mathbf D\cdot d\mathbf s`, 'Currents and changing electric flux both produce circulating H. The second term makes waves possible.'],
  ];
  const cons = [
    ['Constitutive', R`\mathbf D=\varepsilon\mathbf E,\quad\mathbf B=\mu\mathbf H,\quad\mathbf J=\sigma\mathbf E`],
    ['Continuity', R`\nabla\cdot\mathbf J=-\frac{\partial\rho_v}{\partial t}`],
    ['Lorentz force', R`\mathbf F=q(\mathbf E+\mathbf u\times\mathbf B)`],
    ['Phasor form', R`\nabla\times\tilde{\mathbf E}=-j\omega\mu\tilde{\mathbf H},\quad\nabla\times\tilde{\mathbf H}=(\sigma+j\omega\varepsilon)\tilde{\mathbf E}`],
    ['Wave equation', R`\nabla^2\tilde{\mathbf E}-\gamma^2\tilde{\mathbf E}=0,\ \ \gamma^2=j\omega\mu(\sigma+j\omega\varepsilon)\quad\text{(Chapter 5)}`],
  ];
  root.append(h('h2', {}, "Maxwell's equations"),
    h('div', { class: 'tablewrap' }, h('table', { class: 't' }, h('thead', {}, h('tr', {}, ['Law', 'Differential form', 'Integral form', 'Meaning'].map((x) => h('th', {}, x)))),
      h('tbody', {}, rows.map((r) => h('tr', {}, h('td', {}, r[0]), h('td', {}, tex(r[1])), h('td', {}, tex(r[2])), h('td', { class: 'note' }, r[3])))))),
    h('p', { class: 'prose', style: 'margin-top:12px' }, 'The differential and integral forms are equivalent through the divergence theorem ∫∇·A dv = ∮A·ds and Stokes\' theorem ∫(∇×A)·ds = ∮A·dl. In statics (∂/∂t = 0) the set splits into electrostatics (Chapter 2) and magnetostatics (Chapter 3); time variation couples them.'),
    h('h2', {}, 'Companion relations'),
    h('table', { class: 't' }, h('tbody', {}, cons.map((r) => h('tr', {}, h('td', { style: 'width:180px' }, r[0]), h('td', {}, tex(r[1])))))),
    h('h2', {}, 'Boundary conditions (n̂₂ points from medium 2 into medium 1)'),
    h('table', { class: 't' }, h('thead', {}, h('tr', {}, ['Field', 'General interface', 'Dielectric–dielectric (no sources)', 'Medium 2 a perfect conductor'].map((x) => h('th', {}, x)))),
      h('tbody', {}, [
        ['Tangential E', R`\hat n_2\times(\mathbf E_1-\mathbf E_2)=0`, R`E_{1t}=E_{2t}`, R`E_{1t}=0`],
        ['Normal D', R`\hat n_2\cdot(\mathbf D_1-\mathbf D_2)=\rho_s`, R`\varepsilon_1E_{1n}=\varepsilon_2E_{2n}`, R`D_{1n}=\rho_s`],
        ['Tangential H', R`\hat n_2\times(\mathbf H_1-\mathbf H_2)=\mathbf J_s`, R`H_{1t}=H_{2t}`, R`\hat n_2\times\mathbf H_1=\mathbf J_s`],
        ['Normal B', R`\hat n_2\cdot(\mathbf B_1-\mathbf B_2)=0`, R`\mu_1H_{1n}=\mu_2H_{2n}`, R`B_{1n}=0`],
      ].map((r) => h('tr', {}, h('td', {}, r[0]), ...r.slice(1).map((x) => h('td', {}, tex(x))))))));
}

// ------------------------------------------------------------------ boundary conditions
function boundarySection(root, init) {
  const S = { kind: 'E', eps1: 1, eps2: 4, mu1: 1, mu2: 100, F1: 10, theta1_deg: 40, source: 0, pec: false, ...(init || {}) };
  const ctl = h('div'), err = h('div', { class: 'error' }), res = h('div'), steps = h('div'), checks = h('div');
  const fig = h('div', { class: 'plot', style: 'height:480px' });
  root.append(h('div', { class: 'work' },
    h('div', { class: 'panel' }, h('h3', {}, 'Field'), segmented([['E', 'E and D'], ['H', 'H and B']], S.kind, (k) => { S.kind = k; S.source = 0; build(); }), ctl, err),
    h('div', { class: 'figs' }, h('div', { class: 'fig' }, fig, h('p', { class: 'cap' }, h('b', {}, 'One field line crossing the interface. '),
      'Arrow length is proportional to field magnitude. Dashed segments are the tangential and normal components; the arcs are the angles from the normal.')), res)),
  h('h2', {}, 'Derivation'), steps, h('h2', {}, 'Verification'),
  h('p', { class: 'prose' }, 'The two conditions come from shrinking a rectangular loop (Faraday / Ampère) and a pill-box (Gauss) onto the interface. The checks below evaluate those integrals with the computed fields.'), checks);
  function build() {
    const E = S.kind === 'E', c = (o) => control({ ...o, onchange: (v) => { S[o.key] = v; run(); } }).el;
    const pec = h('input', { type: 'checkbox', checked: S.pec, onchange: () => { S.pec = pec.checked; build(); } });
    ctl.replaceChildren(
      c({ key: E ? 'eps1' : 'mu1', texLabel: E ? '\\varepsilon_{r1}' : '\\mu_{r1}', label: 'medium 1 (top)', value: S[E ? 'eps1' : 'mu1'], min: 1, max: E ? 100 : 1e4, log: true }),
      S.pec ? null : c({ key: E ? 'eps2' : 'mu2', texLabel: E ? '\\varepsilon_{r2}' : '\\mu_{r2}', label: 'medium 2 (bottom)', value: S[E ? 'eps2' : 'mu2'], min: 1, max: E ? 100 : 1e4, log: true }),
      c({ key: 'F1', texLabel: E ? '|E_1|' : '|H_1|', unit: E ? 'V/m' : 'A/m', value: S.F1, min: 0.01, max: 1e6, log: true }),
      c({ key: 'theta1_deg', texLabel: '\\theta_1', label: 'from normal', unit: '°', value: S.theta1_deg, min: 0, max: 89.9, step: 0.1 }),
      S.pec ? null : c({ key: 'source', texLabel: E ? '\\rho_s' : 'J_{sz}', label: 'surface source', unit: E ? 'C/m²' : 'A/m', value: S.source, min: E ? -1e-9 : -10, max: E ? 1e-9 : 10 }),
      h('label', { style: 'display:flex;gap:6px;align-items:center;font-size:13px' }, pec, 'Medium 2 is a perfect conductor'),
      h('p', { class: 'hint' }, E ? 'With ρs = 0, field lines bend toward the normal when they enter the medium of higher ε: tanθ₁/tanθ₂ = ε₁/ε₂.'
        : 'Entering a high-μ material, H lines turn almost parallel to the surface — the principle of magnetic shielding.'));
    run();
  }
  const run = debounce(async () => {
    try { draw(await api('mx/boundary', S, 'bc')); err.textContent = ''; } catch (e) { if (!e.stale) err.textContent = e.message; }
  });
  function draw(r) {
    const v = r.values, E = S.kind === 'E', col = E ? C.E : C.H, [t1, n1] = v.F1, [t2, n2] = v.F2;
    const m = Math.max(Math.hypot(t1, n1), Math.hypot(t2, n2), 1e-30), L = 1;
    const a1 = [t1 / m * L, n1 / m * L], a2 = [t2 / m * L, n2 / m * L];
    const tr = [], ann = [];
    const arrow = (x0, y0, x1, y1, text, c, w = 3) => ann.push({ x: x1, y: y1, ax: x0, ay: y0, axref: 'x', ayref: 'y', showarrow: true, arrowhead: 2, arrowwidth: w, arrowcolor: c,
      text: '', }) && text && ann.push({ x: x1, y: y1, text, showarrow: false, xanchor: 'left', yanchor: 'bottom', font: { color: c, size: 13 } });
    // medium 2 → origin → medium 1 (field line passes through origin)
    if (Math.hypot(...a2) > 1e-9) arrow(-a2[0], -a2[1], 0, 0, '', col);
    arrow(0, 0, a1[0], a1[1], `${S.kind}₁`, col);
    if (Math.hypot(...a2) > 1e-9) ann.push({ x: -a2[0], y: -a2[1], text: `${S.kind}₂`, showarrow: false, xanchor: 'right', font: { color: col, size: 13 } });
    const dash = (x, y, c = C.ink3) => tr.push({ x, y, mode: 'lines', line: { color: c, dash: 'dash', width: 1.2 }, hoverinfo: 'skip', showlegend: false });
    dash([0, a1[0], a1[0]], [a1[1], a1[1], 0]); dash([0, -a2[0], -a2[0]], [-a2[1], -a2[1], 0]);
    dash([0, 0], [-1.25, 1.25], C.ink);
    ann.push({ x: a1[0] / 2, y: a1[1], text: `${S.kind}₁ₜ = ${sci(t1, 3)}`, showarrow: false, yanchor: 'bottom', font: { size: 11.5, color: C.ink3 } });
    ann.push({ x: a1[0], y: a1[1] / 2, text: `${S.kind}₁ₙ = ${sci(n1, 3)}`, showarrow: false, xanchor: 'left', font: { size: 11.5, color: C.ink3 } });
    if (Math.hypot(...a2) > 1e-9) {
      ann.push({ x: -a2[0] / 2, y: -a2[1], text: `${S.kind}₂ₜ = ${sci(t2, 3)}`, showarrow: false, yanchor: 'top', font: { size: 11.5, color: C.ink3 } });
      ann.push({ x: -a2[0], y: -a2[1] / 2, text: `${S.kind}₂ₙ = ${sci(n2, 3)}`, showarrow: false, xanchor: 'right', font: { size: 11.5, color: C.ink3 } });
    }
    const arc = (r0, th, up) => { const x = [], y = []; for (let i = 0; i <= 30; i++) { const t = (th * i) / 30; x.push((up ? 1 : -1) * r0 * Math.sin(t)); y.push((up ? 1 : -1) * r0 * Math.cos(t)); } return { x, y }; };
    const th1 = (S.theta1_deg * Math.PI) / 180, th2 = (v.theta2_deg * Math.PI) / 180;
    const A1 = arc(0.28, th1, true), A2 = arc(0.22, th2, false);
    tr.push({ ...A1, mode: 'lines', line: { color: C.ink, width: 1.3 }, hoverinfo: 'skip', showlegend: false });
    if (!S.pec) tr.push({ ...A2, mode: 'lines', line: { color: C.ink, width: 1.3 }, hoverinfo: 'skip', showlegend: false });
    ann.push({ x: 0.36 * Math.sin(th1 / 2), y: 0.36 * Math.cos(th1 / 2), text: `θ₁ = ${S.theta1_deg.toFixed(1)}°`, showarrow: false, xanchor: 'left', font: { size: 12 } });
    if (!S.pec) ann.push({ x: -0.3 * Math.sin(th2 / 2), y: -0.3 * Math.cos(th2 / 2), text: `θ₂ = ${v.theta2_deg.toFixed(2)}°`, showarrow: false, xanchor: 'right', font: { size: 12 } });
    const p1 = E ? S.eps1 : S.mu1, p2 = E ? S.eps2 : S.mu2, sh = (p) => Math.min(0.06 + 0.1 * Math.log10(p), 0.45);
    const shapes = [{ type: 'rect', x0: -1.4, x1: 1.4, y0: 0, y1: 1.3, fillcolor: C.accent, opacity: sh(p1), line: { width: 0 }, layer: 'below' },
      { type: 'rect', x0: -1.4, x1: 1.4, y0: -1.3, y1: 0, fillcolor: S.pec ? C.ink3 : C.accent, opacity: S.pec ? 0.5 : sh(p2), line: { width: 0 }, layer: 'below' },
      { type: 'line', x0: -1.4, x1: 1.4, y0: 0, y1: 0, line: { color: C.ink, width: 2 } }];
    const sym = E ? 'ε' : 'μ';
    ann.push({ x: -1.35, y: 1.22, text: `medium 1: ${sym}ᵣ = ${p1}`, showarrow: false, xanchor: 'left', font: { size: 12.5 } });
    ann.push({ x: -1.35, y: -1.22, text: S.pec ? 'medium 2: perfect conductor' : `medium 2: ${sym}ᵣ = ${p2}`, showarrow: false, xanchor: 'left', font: { size: 12.5 } });
    ann.push({ x: 0.02, y: 1.2, text: 'n̂₂', showarrow: false, xanchor: 'left', font: { size: 13 } });
    if (v.source) ann.push({ x: 1.35, y: 0.04, text: `${E ? 'ρs' : 'Js'} = ${sci(v.source, 3)} ${E ? 'C/m²' : 'A/m'}`, showarrow: false, xanchor: 'right', yanchor: 'bottom', font: { size: 12, color: C.S } });
    Plotly.react(fig, tr, layout({ shapes, annotations: ann, hovermode: false, margin: { l: 10, r: 10, t: 10, b: 10 },
      xaxis: { range: [-1.4, 1.4], visible: false, constrain: 'domain' }, yaxis: { range: [-1.3, 1.3], visible: false, scaleanchor: 'x' } }), plotCfg);
    const u = E ? ['V/m', 'C/m²'] : ['A/m', 'T'];
    res.replaceChildren(kv([[`|${S.kind}₂|`, `${sci(v.F2_mag)} ${u[0]}`], ['θ₂', `${v.theta2_deg.toFixed(3)}°`], [`${E ? 'D' : 'B'}₁ₙ`, `${sci(v.flux[0])} ${u[1]}`],
      [`${E ? 'D' : 'B'}₂ₙ`, `${sci(v.flux[1])} ${u[1]}`], ['w₁', `${sci(v.w[0])} J/m³`], ['w₂', `${sci(v.w[1])} J/m³`]]));
    steps.replaceChildren(stepsTable(r.steps)); checks.replaceChildren(checksTable(r.checks));
  }
  build();
  return () => Plotly.purge(fig);
}

// ------------------------------------------------------------------ Faraday
function faradaySection(root, init) {
  const S = { mode: 'motional', B0: 0.2, f: 60, w: 0.1, l: 0.3, N: 10, R: 2, alpha_deg: 0, ...(init || {}) };
  const ctl = h('div'), err = h('div', { class: 'error' }), res = h('div'), steps = h('div'), checks = h('div');
  const fig = h('div', { class: 'plot' });
  root.append(h('div', { class: 'work' },
    h('div', { class: 'panel' }, h('h3', {}, 'Situation'), segmented([['motional', 'Rotating loop (generator)'], ['transformer', 'Fixed loop, B(t)']], S.mode, (k) => { S.mode = k; build(); }), ctl, err),
    h('div', { class: 'figs' }, res, h('div', { class: 'fig' }, fig, h('p', { class: 'cap' }, h('b', {}, 'Flux linkage and induced EMF over two periods. '),
      'The EMF peaks where the flux crosses zero: it follows the rate of change, not the flux itself (Lenz: the minus sign).')))),
  h('h2', {}, 'Derivation'), steps, h('h2', {}, 'Verification'),
  h('p', { class: 'prose' }, 'For the rotating loop the EMF is computed twice: once from the flux rule −N dΦ/dt and once by integrating the motional field u × B around the moving conductor. Agreement shows the two descriptions are the same physics.'), checks);
  function build() {
    const c = (o) => control({ ...o, onchange: (v) => { S[o.key] = v; run(); } }).el;
    ctl.replaceChildren(c({ key: 'B0', texLabel: 'B_0', unit: 'T', value: S.B0, min: 1e-4, max: 2, log: true }),
      c({ key: 'f', texLabel: 'f', label: S.mode === 'motional' ? 'rotation' : 'field', unit: 'Hz', value: S.f, min: 0.1, max: 1e5, log: true }),
      c({ key: 'w', texLabel: 'w', label: 'loop width', unit: 'm', value: S.w, min: 0.001, max: 1, log: true }),
      c({ key: 'l', texLabel: 'l', label: 'loop length', unit: 'm', value: S.l, min: 0.001, max: 1, log: true }),
      c({ key: 'N', texLabel: 'N', label: 'turns', unit: '', value: S.N, min: 1, max: 1000, step: 1 }),
      c({ key: 'R', texLabel: 'R', label: 'loop resistance', unit: 'Ω', value: S.R, min: 0.01, max: 1e4, log: true }),
      S.mode === 'transformer' ? c({ key: 'alpha_deg', texLabel: '\\alpha', label: 'B to loop normal', unit: '°', value: S.alpha_deg, min: 0, max: 90 }) : null);
    run();
  }
  const run = debounce(async () => {
    try { draw(await api('mx/faraday', { ...S, N: Math.round(S.N) }, 'far')); err.textContent = ''; } catch (e) { if (!e.stale) err.textContent = e.message; }
  });
  function draw(r) {
    const v = r.values;
    res.replaceChildren(kv([['loop area', `${sci(v.A)} m²`], ['peak EMF', si(v.V_peak, 'V')], ['peak current', si(v.I_peak, 'A')], ['average power', si(v.P_av, 'W')]]));
    Plotly.react(fig, [{ x: r.t, y: r.Phi, name: 'NΦ (Wb)', line: { color: C.H, width: 2 } }, { x: r.t, y: r.emf, name: 'V_emf (V)', yaxis: 'y2', line: { color: C.E, width: 2 } }],
      layout({ xaxis: { title: { text: 't (s)' }, exponentformat: 'SI' }, yaxis: { title: { text: 'NΦ (Wb)' }, exponentformat: 'power' },
        yaxis2: { overlaying: 'y', side: 'right', title: { text: 'V_emf (V)' }, showgrid: false, exponentformat: 'power' }, margin: { r: 60 } }), plotCfg);
    steps.replaceChildren(stepsTable(r.steps)); checks.replaceChildren(checksTable(r.checks));
  }
  build();
  return () => Plotly.purge(fig);
}

// ------------------------------------------------------------------ displacement current
function currentsSection(root, init) {
  const S = { eps_r: 81, sigma: 4, f: 1e6, ...(init || {}) };
  const err = h('div', { class: 'error' }), res = h('div'), steps = h('div'), checks = h('div'), fig = h('div', { class: 'plot' });
  const c = (o) => control({ ...o, onchange: (v) => { S[o.key] = v; run(); } });
  const cs = { eps_r: c({ key: 'eps_r', texLabel: '\\varepsilon_r', value: S.eps_r, min: 1, max: 100 }), sigma: c({ key: 'sigma', texLabel: '\\sigma', unit: 'S/m', value: S.sigma, min: 1e-8, max: 1e8, log: true }),
    f: c({ key: 'f', texLabel: 'f', unit: 'Hz', value: S.f, min: 1, max: 1e12, log: true }) };
  const pre = [['Sea water', 81, 4], ['Fresh water', 80, 1e-3], ['Dry soil', 3, 1e-4], ['Copper', 1, 5.8e7], ['Glass', 6, 1e-12]];
  root.append(h('div', { class: 'work' },
    h('div', { class: 'panel' }, h('h3', {}, 'Medium'), h('div', { class: 'presets' }, pre.map(([n, e, s]) => h('button', { class: 'btn', onclick: () => { cs.eps_r.set(e); cs.sigma.set(s); } }, n))),
      cs.eps_r.el, cs.sigma.el, cs.f.el, err),
    h('div', { class: 'figs' }, res, h('div', { class: 'fig' }, fig, h('p', { class: 'cap' }, h('b', {}, '|Jc| / |Jd| versus frequency. '),
      'Above the line the medium conducts; below it, it behaves as a dielectric. The crossover f_c = σ/2πε is the same boundary used in Chapter 5.')))),
  h('h2', {}, 'Derivation'), steps, h('h2', {}, 'Verification'), checks);
  const run = debounce(async () => {
    try {
      const r = await api('mx/currents', S, 'cur'); err.textContent = '';
      const v = r.values;
      res.replaceChildren(kv([['|Jc| per V/m', `${sci(v.Jc)} A/m²`], ['|Jd| per V/m', `${sci(v.Jd)} A/m²`], ['Jc / Jd', sci(v.ratio)], ['crossover f_c', si(v.fc, 'Hz')], ['relaxation τ', si(v.tau, 's')]]));
      Plotly.react(fig, [{ x: r.sweep.f, y: r.sweep.ratio, line: { color: C.accent, width: 2.2 }, name: 'σ/ωε' },
        { x: [S.f], y: [v.ratio], mode: 'markers', marker: { color: C.S, size: 10 }, showlegend: false }],
        layout({ shapes: [{ type: 'line', xref: 'paper', x0: 0, x1: 1, y0: 1, y1: 1, line: { color: C.ink3, dash: 'dash', width: 1 } }],
          xaxis: { type: 'log', title: { text: 'f (Hz)' }, exponentformat: 'power' }, yaxis: { type: 'log', title: { text: '|Jc| / |Jd|' }, exponentformat: 'power' }, showlegend: false }), plotCfg);
      steps.replaceChildren(stepsTable(r.steps)); checks.replaceChildren(checksTable(r.checks));
    } catch (e) { if (!e.stale) err.textContent = e.message; }
  });
  run();
  return () => Plotly.purge(fig);
}
