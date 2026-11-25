// Chapter 7 — lossless transmission lines, Smith chart and matching (Ulaby ch. 2, Cheng ch. 9).
import { h, tex, control, stepsTable, checksTable, kv, si, sci, layout, plotCfg, C } from '../ui.js';
import { api, debounce } from '../api.js';

const R = String.raw;
const PRE = [['Matched 50 Ω', { Z0: 50, RL: 50, XL: 0 }], ['100 + j50 Ω', { Z0: 50, RL: 100, XL: 50 }], ['Short', { Z0: 50, RL: 0, XL: 0 }],
  ['Capacitive 25 − j30', { Z0: 50, RL: 25, XL: -30 }], ['Dipole 73 + j42.5 on 50 Ω', { Z0: 50, RL: 73, XL: 42.5 }], ['300 Ω on 75 Ω coax', { Z0: 75, RL: 300, XL: 0 }]];

export function render(view, ch, init = {}) {
  const S = { Z0: 50, RL: 100, XL: 50, f: 1e9, length: 0.3, vf: 1, Vg: 10, Zg: 50, ...init };
  const err = h('div', { class: 'error' }), res = h('div'), matchBox = h('div'), steps = h('div'), checks = h('div');
  const fS = h('div', { class: 'plot', style: 'height:470px' }), fV = h('div', { class: 'plot', style: 'height:320px' });
  const c = (o) => control({ ...o, onchange: (v) => { S[o.key] = v; run(); } });
  const cs = { Z0: c({ key: 'Z0', texLabel: 'Z_0', unit: 'Ω', value: S.Z0, min: 10, max: 600, log: true }),
    RL: c({ key: 'RL', texLabel: 'R_L', unit: 'Ω', value: S.RL, min: 0, max: 1000 }), XL: c({ key: 'XL', texLabel: 'X_L', unit: 'Ω', value: S.XL, min: -500, max: 500 }),
    f: c({ key: 'f', texLabel: 'f', unit: 'Hz', value: S.f, min: 1e6, max: 1e11, log: true }), length: c({ key: 'length', texLabel: 'l', label: 'line length', unit: 'm', value: S.length, min: 1e-3, max: 10, log: true }),
    vf: c({ key: 'vf', texLabel: 'u_p/c', label: 'velocity factor', value: S.vf, min: 0.3, max: 1 }) };
  view.append(h('div', { class: 'eyebrow' }, `CHAPTER ${ch.n}`), h('h1', {}, ch.title),
    h('p', { class: 'lede' }, 'A line of characteristic impedance Z₀ terminated in a load impedance carries an incident and a reflected wave. Their interference fixes the standing-wave pattern and transforms the load into a different impedance at every distance — which the Smith chart shows as a rotation of Γ at constant |Γ|.'),
    h('div', { class: 'work' },
      h('div', { class: 'panel' }, h('h3', {}, 'Line and load'), h('div', { class: 'presets' }, PRE.map(([n, v]) => h('button', { class: 'btn', onclick: () => Object.entries(v).forEach(([k, x]) => cs[k].set(x)) }, n))),
        cs.Z0.el, cs.RL.el, cs.XL.el, cs.f.el, cs.length.el, cs.vf.el, h('p', { class: 'hint' }, 'Generator: 10 V with 50 Ω source impedance.'), err),
      h('div', { class: 'figs' }, res,
        h('div', { class: 'grid2' }, h('div', { class: 'fig' }, fS, h('p', { class: 'cap' }, h('b', {}, 'Smith chart. '),
          'Red dot: the normalised load. Moving toward the generator, Γ rotates clockwise on the dashed |Γ| circle; the green arc ends at the input impedance. One full turn = λ/2.')),
          h('div', { class: 'fig' }, fV, h('p', { class: 'cap' }, h('b', {}, 'Standing-wave pattern. '), '|V| and |I| along the line, d measured from the load. Voltage maxima coincide with current minima.'))),
        matchBox)),
    h('h2', {}, 'Derivation'), steps, h('h2', {}, 'Verification'), checks, theory());

  const run = debounce(async () => { try { draw(await api('tl/line', S, 'tl')); err.textContent = ''; } catch (e) { if (!e.stale) err.textContent = e.message; } });
  function draw(r) {
    const v = r.values, Zin = v.Zin;
    res.replaceChildren(kv([['Γ_L', `${sci(v.Gamma_mag)} ∠ ${v.Gamma_deg.toFixed(2)}°`], ['VSWR', v.S == null ? '∞' : sci(v.S)], ['return loss', v.return_loss_dB == null ? '∞ dB' : `${sci(v.return_loss_dB)} dB`],
      ['Z_in', `${sci(Zin.re)} ${Zin.im < 0 ? '−' : '+'} j${sci(Math.abs(Zin.im))} Ω`], ['l / λ', sci(v.l_over_lambda)], ['d_max / d_min', `${si(v.d_max, 'm', 3)} / ${si(v.d_min, 'm', 3)}`],
      ['P delivered', si(v.P_L, 'W')]]));
    smith(fS, r, S);
    Plotly.react(fV, [{ x: r.profile.d, y: r.profile.V, name: '|V| (V)', line: { color: C.E, width: 2.2 } }, { x: r.profile.d, y: r.profile.I, name: '|I| (A)', yaxis: 'y2', line: { color: C.H, width: 2.2 } }],
      layout({ xaxis: { title: { text: 'distance from load d (m)' }, autorange: 'reversed' }, yaxis: { title: { text: '|V| (V)' }, rangemode: 'tozero' },
        yaxis2: { overlaying: 'y', side: 'right', title: { text: '|I| (A)' }, showgrid: false, rangemode: 'tozero' }, margin: { r: 60 } }), plotCfg);
    const m = r.match;
    matchBox.replaceChildren(m.quarter_wave ? h('div', { class: 'panel' }, h('h3', {}, 'Matching networks (engine-verified)'),
      kv([['λ/4 transformer at d_min', `${si(m.quarter_wave.d, 'm', 4)}, Z_T = ${sci(m.quarter_wave.Z_T, 4)} Ω`],
        ...m.stub.map((s, i) => [`short stub, solution ${i + 1}`, `d = ${si(s.d, 'm', 4)}, l_stub = ${si(s.l_stub, 'm', 4)}`])])) : h('p', { class: 'hint' }, 'Load is matched or purely reactive — no matching network applies.'));
    steps.replaceChildren(stepsTable(r.steps)); checks.replaceChildren(checksTable(r.checks));
  }
  run();
  return () => [fS, fV].forEach((f) => Plotly.purge(f));
}

// Smith chart grid: constant-r circles and constant-x arcs (pure geometry of Γ = (z−1)/(z+1))
function smith(el, r, S) {
  const tr = [], grid = { color: C.rule, width: 1 }, N = 240;
  const circle = (cx, cy, rad) => { const x = [], y = []; for (let i = 0; i <= N; i++) { const t = (2 * Math.PI * i) / N, px = cx + rad * Math.cos(t), py = cy + rad * Math.sin(t);
    if (px * px + py * py <= 1.0001) { x.push(px); y.push(py); } else { x.push(null); y.push(null); } } return { x, y }; };
  tr.push({ ...circle(0, 0, 1), mode: 'lines', line: { color: C.ink3, width: 1.5 } });
  [0.2, 0.5, 1, 2, 5].forEach((rr) => tr.push({ ...circle(rr / (1 + rr), 0, 1 / (1 + rr)), mode: 'lines', line: grid }));
  [0.2, 0.5, 1, 2, 5].forEach((x) => [x, -x].forEach((xx) => tr.push({ ...circle(1, 1 / xx, 1 / Math.abs(xx)), mode: 'lines', line: grid })));
  tr.push({ x: [-1, 1], y: [0, 0], mode: 'lines', line: grid });
  const ann = [0.2, 0.5, 1, 2, 5].map((rr) => ({ x: (rr - 1) / (rr + 1), y: 0, text: `${rr}`, showarrow: false, yshift: 8, font: { size: 10, color: C.ink3 } }));
  [0.5, 1, 2].forEach((x) => [x, -x].forEach((xx) => { const d = 1 + xx * xx;   // Γ for z = jx on the rim
    ann.push({ x: (xx * xx - 1) / d * 1.07, y: (2 * xx) / d * 1.07, text: `${xx > 0 ? '+' : '−'}j${Math.abs(xx)}`, showarrow: false, font: { size: 10, color: C.ink3 } }); }));
  const v = r.values, g = Math.max(v.Gamma_mag, 1e-9);
  tr.push({ ...circle(0, 0, Math.min(g, 1)), mode: 'lines', line: { color: C.accent, dash: 'dash', width: 1.2 } });
  tr.push({ x: r.smith.re, y: r.smith.im, mode: 'lines', line: { color: C.S, width: 3 } });
  const GL = { re: v.Gamma_mag * Math.cos(v.Gamma_deg * Math.PI / 180), im: v.Gamma_mag * Math.sin(v.Gamma_deg * Math.PI / 180) };
  tr.push({ x: [GL.re], y: [GL.im], mode: 'markers', marker: { size: 11, color: C.E }, hovertext: `z_L = ${(S.RL / S.Z0).toFixed(3)} ${S.XL < 0 ? '−' : '+'} j${Math.abs(S.XL / S.Z0).toFixed(3)}`, hoverinfo: 'text' });
  const end = r.smith.re.length - 1;
  tr.push({ x: [r.smith.re[end]], y: [r.smith.im[end]], mode: 'markers', marker: { size: 11, color: C.S, symbol: 'diamond' }, hovertext: 'Z<sub>in</sub>', hoverinfo: 'text' });
  ann.push({ x: GL.re, y: GL.im, text: 'z<sub>L</sub>', showarrow: false, yshift: 12, font: { color: C.E, size: 12 } }, { x: r.smith.re[end], y: r.smith.im[end], text: 'z<sub>in</sub>', showarrow: false, yshift: -12, font: { color: C.S, size: 12 } });
  Plotly.react(el, tr.map((t) => ({ hoverinfo: 'skip', showlegend: false, ...t })), layout({ annotations: ann, hovermode: 'closest', margin: { l: 10, r: 10, t: 10, b: 10 },
    xaxis: { range: [-1.12, 1.12], visible: false, constrain: 'domain' }, yaxis: { range: [-1.12, 1.12], visible: false, scaleanchor: 'x' } }), plotCfg);
}

function theory() {
  const rows = [
    ['Telegrapher', R`\frac{d^2\tilde V}{dz^2}-\gamma^2\tilde V=0,\ \gamma=\sqrt{(R'+j\omega L')(G'+j\omega C')}`, 'Lossless: γ = jβ, β = ω√(L′C′).'],
    ['Characteristic impedance', R`Z_0=\sqrt{\frac{R'+j\omega L'}{G'+j\omega C'}}\to\sqrt{L'/C'}`, 'Ratio of V⁺ to I⁺ — not a physical resistor.'],
    ['Reflection', R`\Gamma_L=\frac{Z_L-Z_0}{Z_L+Z_0},\quad\Gamma(d)=\Gamma_Le^{-j2\beta d}`, 'Magnitude constant along a lossless line.'],
    ['Input impedance', R`Z_{in}=Z_0\frac{Z_L+jZ_0\tan\beta l}{Z_0+jZ_L\tan\beta l}`, 'λ/2 repeats Z_L; λ/4 inverts it: Z_in = Z₀²/Z_L.'],
    ['VSWR', R`S=\frac{|V|_{max}}{|V|_{min}}=\frac{1+|\Gamma|}{1-|\Gamma|}`, '1 for a matched load, ∞ for open/short/reactive loads.'],
    ['Power', R`P_L=\frac{|V_0^+|^2}{2Z_0}\left(1-|\Gamma|^2\right)`, 'Reflected power fraction |Γ|²; return loss −20 log|Γ| dB.'],
    ['Quarter-wave match', R`Z_T=\sqrt{Z_0R}`, 'Matches a real impedance R (at d_max or d_min).'],
    ['Stub match', R`Y(d)=Y_0+jB,\quad Y_{stub}=-jB`, 'Shunt short-circuited stub cancels the susceptance.'],
  ];
  return h('div', {}, h('h2', {}, 'Summary'), h('div', { class: 'tablewrap' }, h('table', { class: 't' }, h('thead', {}, h('tr', {}, ['Topic', 'Relation', 'Meaning'].map((x) => h('th', {}, x)))),
    h('tbody', {}, rows.map((r) => h('tr', {}, h('td', {}, r[0]), h('td', {}, tex(r[1])), h('td', { class: 'note' }, r[2])))))));
}
