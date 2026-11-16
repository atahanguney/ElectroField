// Chapter 8 — rectangular waveguides, dipole antennas, linear arrays (Ulaby ch. 8–10, Cheng ch. 10–11).
import { h, tex, control, segmented, stepsTable, checksTable, kv, si, sci, layout, plotCfg, C } from '../ui.js';
import { api, debounce } from '../api.js';

const R = String.raw;

export function render(view, ch, init = {}) {
  const body = h('div');
  const tabs = { waveguide: wgSection, dipole: dipoleSection, array: arraySection };
  let cleanup = null;
  const show = (k) => { cleanup && cleanup(); body.replaceChildren(); cleanup = tabs[k](body, init[k]); };
  view.append(h('div', { class: 'eyebrow' }, `CHAPTER ${ch.n}`), h('h1', {}, ch.title),
    h('p', { class: 'lede' }, 'Guided and radiated waves. Inside a metal pipe only field patterns that fit between the walls can travel — each mode has a cut-off frequency. An antenna does the opposite: its current distribution launches energy into free space with a direction-dependent pattern, and arrays shape that pattern by phasing many elements.'),
    segmented([['waveguide', 'Rectangular waveguide'], ['dipole', 'Dipole antenna'], ['array', 'Linear array']], init.tab || 'waveguide', show), body, theory());
  show(init.tab || 'waveguide');
  return () => cleanup && cleanup();
}
const tables = (steps, checks, r) => { steps.replaceChildren(stepsTable(r.steps)); checks.replaceChildren(checksTable(r.checks)); };
const tail = (root, steps, checks) => root.append(h('h2', {}, 'Derivation'), steps, h('h2', {}, 'Verification'), checks);
const polar = (el, th, F, name, col) => Plotly.react(el, [{ type: 'scatterpolar', r: [...F, ...F.slice().reverse()], theta: [...th, ...th.slice().reverse().map((t) => 360 - t)],
  mode: 'lines', line: { color: col, width: 2.2 }, fill: 'toself', fillcolor: 'rgba(31,78,121,0.12)', name }],
  layout({ showlegend: false, margin: { l: 30, r: 30, t: 20, b: 20 }, polar: { bgcolor: 'rgba(0,0,0,0)', radialaxis: { range: [0, 1.02], gridcolor: C.rule, tickfont: { size: 10 } },
    angularaxis: { rotation: 90, direction: 'clockwise', gridcolor: C.rule, tickfont: { size: 10 } } } }), plotCfg);

function wgSection(root, init) {
  const S = { a: 22.86e-3, b: 10.16e-3, eps_r: 1, f: 10e9, mode: 'TE', m: 1, n: 0, ...(init || {}) };
  const err = h('div', { class: 'error' }), res = h('div'), modes = h('div'), steps = h('div'), checks = h('div');
  const fF = h('div', { class: 'plot', style: 'height:300px' }), fD = h('div', { class: 'plot', style: 'height:320px' });
  const c = (o) => control({ ...o, onchange: (v) => { S[o.key] = v; run(); } }).el;
  const msel = h('div', { style: 'display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px' },
    h('select', { onchange: (e) => { S.mode = e.target.value; run(); } }, ['TE', 'TM'].map((x) => h('option', { selected: x === S.mode }, x))),
    h('input', { type: 'number', min: 0, max: 5, value: S.m, onchange: (e) => { S.m = +e.target.value; run(); } }),
    h('input', { type: 'number', min: 0, max: 5, value: S.n, onchange: (e) => { S.n = +e.target.value; run(); } }));
  root.append(h('div', { class: 'work' },
    h('div', { class: 'panel' }, h('h3', {}, 'Guide (WR-90 default)'), c({ key: 'a', texLabel: 'a', label: 'broad wall', unit: 'm', value: S.a, min: 1e-3, max: 0.3, log: true }),
      c({ key: 'b', texLabel: 'b', label: 'narrow wall', unit: 'm', value: S.b, min: 1e-3, max: 0.3, log: true }), c({ key: 'eps_r', texLabel: '\\varepsilon_r', label: 'filling', value: S.eps_r, min: 1, max: 10 }),
      c({ key: 'f', texLabel: 'f', unit: 'Hz', value: S.f, min: 1e8, max: 1e11, log: true }), h('h3', {}, 'Mode  (type, m, n)'), msel, err),
    h('div', { class: 'figs' }, res, h('div', { class: 'fig' }, fF, h('p', { class: 'cap' }, h('b', {}, 'Transverse E in the cross-section. '), 'Shading |E_t|, arrows direction. E_t vanishes along every wall it is tangent to.')),
      h('div', { class: 'fig' }, fD, h('p', { class: 'cap' }, h('b', {}, 'Dispersion β(f) of the lowest modes. '), 'Each mode starts at its cut-off and approaches the light line β = ω/u.')), modes)));
  tail(root, steps, checks);
  const run = debounce(async () => { try { draw(await api('ra/waveguide', S, 'wg')); err.textContent = ''; } catch (e) { if (!e.stale) err.textContent = e.message; } });
  function draw(r) {
    const v = r.values, F = r.field;
    res.replaceChildren(h('div', { style: 'margin-bottom:8px' }, h('span', { class: 'badge' }, v.propagating ? `${S.mode}${S.m}${S.n} propagates` : `${S.mode}${S.m}${S.n} is cut off`)),
      kv([['f_c', si(v.fc, 'Hz')], ...(v.propagating ? [['β', `${sci(v.beta)} rad/m`], ['λ_g', si(v.lambda_g, 'm')], ['u_p', si(v.up, 'm/s')], ['u_g', si(v.ug, 'm/s')], ['Z', si(v.Z, 'Ω')]]
        : [['α (evanescent)', `${sci(v.alpha)} Np/m`]]), ['modes above cut-off', `${v.n_modes}`]]));
    const ann = F.qx.map((x, i) => { const m = Math.hypot(F.qu[i], F.qv[i]), mx = Math.max(...F.qu.map((u, j) => Math.hypot(u, F.qv[j]))) || 1, L = 0.06 * S.a * m / mx;
      return m / mx < 0.05 ? null : { x: x + L * F.qu[i] / m, y: F.qy[i] + L * F.qv[i] / m, ax: x, ay: F.qy[i], axref: 'x', ayref: 'y', showarrow: true, arrowhead: 2, arrowwidth: 1.3, arrowcolor: C.E, text: '' }; }).filter(Boolean);
    Plotly.react(fF, [{ type: 'heatmap', x: F.x, y: F.y, z: F.mag, colorscale: [[0, 'rgba(0,0,0,0)'], [1, C.E]], opacity: 0.45, showscale: false, zsmooth: 'best', hoverinfo: 'skip' }],
      layout({ annotations: ann, hovermode: false, shapes: [{ type: 'rect', x0: 0, x1: S.a, y0: 0, y1: S.b, line: { color: C.ink, width: 2 } }],
        xaxis: { title: { text: 'x (m)' }, constrain: 'domain', exponentformat: 'SI' }, yaxis: { title: { text: 'y (m)' }, scaleanchor: 'x', exponentformat: 'SI' } }), plotCfg);
    const cols = [C.E, C.H, C.S, C.accent, C.ink3];
    Plotly.react(fD, Object.entries(r.dispersion.beta).map(([k, b], i) => ({ x: r.dispersion.f, y: b, name: k, line: { color: cols[i % 5], width: 2 } }))
      .concat([{ x: [S.f, S.f], y: [0, Math.max(...Object.values(r.dispersion.beta).flat().filter((x) => x != null))], mode: 'lines', line: { color: C.ink3, dash: 'dash', width: 1 }, name: 'f' }]),
      layout({ xaxis: { title: { text: 'f (Hz)' }, exponentformat: 'SI' }, yaxis: { title: { text: 'β (rad/m)' } } }), plotCfg);
    modes.replaceChildren(h('table', { class: 't' }, h('thead', {}, h('tr', {}, ['Mode', 'Cut-off', 'At f'].map((x) => h('th', {}, x)))),
      h('tbody', {}, r.modes.map((m) => h('tr', {}, h('td', {}, m.mode), h('td', { class: 'num' }, si(m.fc, 'Hz')), h('td', { class: m.fc < S.f ? 'pass' : 'note' }, m.fc < S.f ? 'propagates' : 'cut off'))))));
    tables(steps, checks, r);
  }
  run();
  return () => [fF, fD].forEach((f) => Plotly.purge(f));
}

function dipoleSection(root, init) {
  const S = { length_lambda: 0.5, I0: 1, f: 100e6, ...(init || {}) };
  const err = h('div', { class: 'error' }), res = h('div'), steps = h('div'), checks = h('div'), fP = h('div', { class: 'plot', style: 'height:420px' });
  const c = (o) => control({ ...o, onchange: (v) => { S[o.key] = v; run(); } });
  const L = c({ key: 'length_lambda', texLabel: 'l/\\lambda', label: 'total length', value: S.length_lambda, min: 0.01, max: 3, step: 0.01 });
  root.append(h('div', { class: 'work' },
    h('div', { class: 'panel' }, h('h3', {}, 'Dipole'), h('div', { class: 'presets' }, [['Short', 0.05], ['λ/2', 0.5], ['λ', 1], ['1.25λ', 1.25], ['1.5λ', 1.5]].map(([n, x]) => h('button', { class: 'btn', onclick: () => L.set(x) }, n))),
      L.el, c({ key: 'I0', texLabel: 'I_0', label: 'peak current', unit: 'A', value: S.I0, min: 0.001, max: 100, log: true }).el,
      c({ key: 'f', texLabel: 'f', unit: 'Hz', value: S.f, min: 1e5, max: 1e11, log: true }).el, err),
    h('div', { class: 'figs' }, res, h('div', { class: 'fig' }, fP, h('p', { class: 'cap' }, h('b', {}, 'Normalised power pattern (E-plane). '), 'Dipole along the vertical axis (θ = 0 up). Beyond l ≈ 1.25λ the main lobe splits into side lobes.')))));
  tail(root, steps, checks);
  const run = debounce(async () => { try { draw(await api('ra/dipole', S, 'dip')); err.textContent = ''; } catch (e) { if (!e.stale) err.textContent = e.message; } });
  function draw(r) {
    const v = r.values;
    res.replaceChildren(kv([['R_rad', si(v.R_rad, 'Ω')], ['directivity', `${sci(v.D)} (${v.D_dBi.toFixed(2)} dBi)`], ['HPBW', v.hpbw_deg == null ? '—' : `${v.hpbw_deg.toFixed(1)}°`],
      ['P_rad', si(v.P_rad, 'W')], ['λ', si(v.wavelength, 'm')], ['physical length', si(v.length, 'm')]]));
    polar(fP, r.pattern.theta_deg, r.pattern.F, 'F', C.accent); tables(steps, checks, r);
  }
  run();
  return () => Plotly.purge(fP);
}

function arraySection(root, init) {
  const S = { N: 8, d_lambda: 0.5, delta_deg: 0, ...(init || {}) };
  const err = h('div', { class: 'error' }), res = h('div'), steps = h('div'), checks = h('div'), fP = h('div', { class: 'plot', style: 'height:420px' }), fC = h('div', { class: 'plot', style: 'height:280px' });
  const c = (o) => control({ ...o, onchange: (v) => { S[o.key] = v; run(); } });
  const cs = { N: c({ key: 'N', texLabel: 'N', label: 'elements', value: S.N, min: 1, max: 32, step: 1 }), d: c({ key: 'd_lambda', texLabel: 'd/\\lambda', label: 'spacing', value: S.d_lambda, min: 0.05, max: 2, step: 0.01 }),
    dl: c({ key: 'delta_deg', texLabel: '\\delta', label: 'progressive phase', unit: '°', value: S.delta_deg, min: -360, max: 360, step: 1 }) };
  root.append(h('div', { class: 'work' },
    h('div', { class: 'panel' }, h('h3', {}, 'Array along the vertical axis'), h('div', { class: 'presets' }, [['Broadside', 0.5, 0], ['End-fire', 0.25, -90], ['Steered 60°', 0.5, -90], ['Grating lobes', 1.2, 0]].map(([n, d, p]) => h('button', { class: 'btn', onclick: () => { cs.d.set(d); cs.dl.set(p); } }, n))),
      cs.N.el, cs.d.el, cs.dl.el, err),
    h('div', { class: 'figs' }, res, h('div', { class: 'grid2' }, h('div', { class: 'fig' }, fP, h('p', { class: 'cap' }, h('b', {}, 'Polar |AF|. '), 'θ from the array axis. Changing δ steers the beam without moving anything.')),
      h('div', { class: 'fig' }, fC, h('p', { class: 'cap' }, h('b', {}, '|AF| in dB. '), 'First side lobe of a uniform array ≈ −13.3 dB.'))))));
  tail(root, steps, checks);
  const run = debounce(async () => { try { draw(await api('ra/array', { ...S, N: Math.round(S.N) }, 'arr')); err.textContent = ''; } catch (e) { if (!e.stale) err.textContent = e.message; } });
  function draw(r) {
    const v = r.values, p = r.pattern;
    res.replaceChildren(kv([['main beam θ₀', v.theta0 == null ? '—' : `${v.theta0.toFixed(2)}°`], ['directivity', `${sci(v.D)} (${v.D_dBi.toFixed(2)} dBi)`], ['grating lobes', v.grating ? 'yes' : 'no']]));
    polar(fP, p.theta_deg, p.AF, 'AF', C.accent);
    Plotly.react(fC, [{ x: p.theta_deg, y: p.AF.map((a) => Math.max(20 * Math.log10(Math.max(a, 1e-6)), -50)), line: { color: C.accent, width: 2 } }],
      layout({ showlegend: false, xaxis: { title: { text: 'θ (degrees)' }, range: [0, 180] }, yaxis: { title: { text: '|AF| (dB)' }, range: [-50, 1] } }), plotCfg);
    tables(steps, checks, r);
  }
  run();
  return () => [fP, fC].forEach((f) => Plotly.purge(f));
}

function theory() {
  const rows = [
    ['Cut-off', R`f_{mn}=\frac{u}{2}\sqrt{(m/a)^2+(n/b)^2}`, 'Below f_c the mode is evanescent.'],
    ['Propagation', R`\beta=k\sqrt{1-(f_c/f)^2},\ \ \lambda_g=\frac{\lambda}{\sqrt{1-(f_c/f)^2}}`, 'Dispersive: u_p u_g = u².'],
    ['Wave impedance', R`Z_{TE}=\frac{\eta}{\sqrt{1-(f_c/f)^2}},\ Z_{TM}=\eta\sqrt{1-(f_c/f)^2}`, 'Ratio of transverse E to transverse H.'],
    ['Short dipole', R`F=\sin^2\theta,\ D=1.5`, 'Doughnut pattern, no radiation along the axis.'],
    ['Half-wave dipole', R`R_{rad}\approx73\,\Omega,\ D\approx1.64\ (2.15\,\text{dBi})`, 'The reference antenna of practice.'],
    ['Directivity', R`D=\frac{4\pi F_{max}}{\iint F\,d\Omega}`, 'How much the antenna concentrates power.'],
    ['Array factor', R`AF=\frac{\sin(N\psi/2)}{N\sin(\psi/2)},\ \psi=kd\cos\theta+\delta`, 'Pattern multiplication: total = element × AF.'],
    ['Beam steering', R`\cos\theta_0=-\delta/kd`, 'Phased arrays steer electronically.'],
  ];
  return h('div', {}, h('h2', {}, 'Summary'), h('div', { class: 'tablewrap' }, h('table', { class: 't' }, h('thead', {}, h('tr', {}, ['Topic', 'Relation', 'Meaning'].map((x) => h('th', {}, x)))),
    h('tbody', {}, rows.map((r) => h('tr', {}, h('td', {}, r[0]), h('td', {}, tex(r[1])), h('td', { class: 'note' }, r[2])))))));
}
