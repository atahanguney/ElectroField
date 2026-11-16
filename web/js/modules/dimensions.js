// Chapter 0 — 1-D, 2-D and 3-D waves side by side (same medium, same frequency, different geometry).
import { h, tex, control, stepsTable, checksTable, kv, si, layout, plotCfg, C } from '../ui.js';
import { api, debounce } from '../api.js';

const R = String.raw;
const D3 = ['1D', '2D', '3D'];
const INFO = {
  '1D': { name: '1-D · plane wave / transmission line', coord: 'one coordinate: z', law: 'no spreading: |E| = const × e^{−αz}', ex: 'coax and two-wire lines, a plane wave far from its source, a vibrating string' },
  '2D': { name: '2-D · cylindrical wave', coord: 'two coordinates: (x, y) or (ρ, φ)', law: '|E| ∝ e^{−αρ}/√ρ', ex: 'long line sources, surface waves on microstrip/ground, ripples on water' },
  '3D': { name: '3-D · spherical wave', coord: 'three coordinates: (R, θ, φ)', law: '|E| ∝ e^{−αR}/R', ex: 'radiation from an antenna or any small source, sound from a point' },
};

export function render(view, ch, init = {}) {
  const S = { f: 1e9, eps_r: 1, mu_r: 1, sigma: 0, r_max_lambda: 6, ...init };
  let last = null, phase = 0, playing = false, timer = 0;
  const err = h('div', { class: 'error' }), res = h('div'), sens = h('div'), steps = h('div'), checks = h('div');
  const maps = Object.fromEntries(D3.map((d) => [d, h('div', { class: 'plot', style: 'height:300px' })]));
  const fAmp = h('div', { class: 'plot', style: 'height:340px' }), fLine = h('div', { class: 'plot', style: 'height:300px' }), fF = h('div', { class: 'plot', style: 'height:320px' });
  const c = (o) => control({ ...o, onchange: (v) => { S[o.key] = v; run(); } });
  const cs = { f: c({ key: 'f', texLabel: 'f', unit: 'Hz', value: S.f, min: 1e6, max: 1e11, log: true }), eps_r: c({ key: 'eps_r', texLabel: '\\varepsilon_r', value: S.eps_r, min: 1, max: 81, log: true }),
    sigma: c({ key: 'sigma', texLabel: '\\sigma', label: 'loss', unit: 'S/m', value: S.sigma, min: 1e-6, max: 10, log: true }),
    r: c({ key: 'r_max_lambda', texLabel: 'r_{max}/\\lambda', label: 'view range', value: S.r_max_lambda, min: 1, max: 20 }) };
  const phc = control({ texLabel: '\\omega t', unit: '°', value: 0, min: 0, max: 360, step: 1, onchange: (v) => { phase = v; anim(); } });
  const play = h('button', { class: 'btn', onclick: () => { playing = !playing; play.textContent = playing ? 'Pause' : 'Play'; if (playing) tick(); } }, 'Play');
  const pre = [['Air, lossless', { eps_r: 1, sigma: 0 }], ['Glass', { eps_r: 4, sigma: 0 }], ['Wet soil', { eps_r: 20, sigma: 0.05 }], ['Sea water', { eps_r: 81, sigma: 4 }]];

  view.append(h('div', { class: 'eyebrow' }, `CHAPTER ${ch.n}`), h('h1', {}, ch.title),
    h('p', { class: 'lede' }, 'The same wave equation, the same medium and the same frequency give three very different pictures depending on how many coordinates the field depends on. Geometry alone decides how fast the amplitude falls: not at all on a line, as 1/√ρ from a line source, as 1/R from a point source. Material loss then adds e^{−αr} on top of all three.'),
    h('div', { class: 'work' },
      h('div', { class: 'panel' }, h('h3', {}, 'Medium and view'), h('div', { class: 'presets' }, pre.map(([n, v]) => h('button', { class: 'btn', onclick: () => Object.entries(v).forEach(([k, x]) => cs[k].set(x)) }, n))),
        cs.f.el, cs.eps_r.el, cs.sigma.el, cs.r.el, h('div', { style: 'display:grid;grid-template-columns:70px 1fr;gap:10px;align-items:center' }, play, phc.el),
        h('p', { class: 'hint' }, 'σ = 0 is allowed (type 0). Snapshots show Re{ψ e^{jωt}}; press Play to watch the wavefronts move outward.'), err),
      h('div', { class: 'figs' }, res,
        h('div', { class: 'grid3' }, D3.map((d) => h('div', { class: 'fig' }, maps[d], h('p', { class: 'cap' }, h('b', {}, INFO[d].name + '. '), INFO[d].coord + '.')))),
        h('div', { class: 'fig' }, fAmp, h('p', { class: 'cap' }, h('b', {}, 'Amplitude versus distance (log–log). '),
          'Normalised to 1 at r = λ/2. Straight lines with slopes 0, −½ and −1 are the three spreading laws; loss bends all curves down at the same rate.')))),
    h('div', { class: 'grid2', style: 'margin-top:16px' },
      h('div', { class: 'fig' }, fLine, h('p', { class: 'cap' }, h('b', {}, 'Instantaneous field along a radial line. '), 'Same wavelength in all three — only the envelope differs.')),
      h('div', { class: 'fig' }, fF, h('p', { class: 'cap' }, h('b', {}, 'Level at r_max versus frequency (fixed distance in metres). '),
        'Without loss, 2-D and 3-D lose more at low frequency only because the same distance is fewer wavelengths; with loss, high frequencies are absorbed.'))),
    h('h2', {}, 'What happens if you increase…'), h('p', { class: 'prose' }, 'Each row is recomputed by the engine from the current settings: change in wavelength and in the field level at r_max (dB) for each geometry.'), sens,
    h('h2', {}, 'Comparison'), table(),
    h('h2', {}, 'Derivation'), steps, h('h2', {}, 'Verification'),
    h('p', { class: 'prose' }, 'Each field is checked against its own Helmholtz equation by finite differences; for lossless media the Poynting flux through the wavefront (a plane, a cylinder, a sphere) is shown to be the same at every radius, and the log–log slopes are fitted.'), checks);

  const run = debounce(async () => { try { last = await api('dim/compare', S, 'dim'); err.textContent = ''; draw(); } catch (e) { if (!e.stale) err.textContent = e.message; } });
  const inst = (F, p) => F.re.map((r, i) => r * Math.cos(p) - F.im[i] * Math.sin(p));
  const instM = (F, p) => F.re.map((row, i) => row.map((r, j) => r * Math.cos(p) - F.im[i][j] * Math.sin(p)));
  function draw() {
    const v = last.values, M = last.maps, rl = last.r.map((x) => x / v.wavelength);
    res.replaceChildren(kv([['λ', si(v.wavelength, 'm')], ['β', `${v.beta.toPrecision(4)} rad/m`], ['α', `${v.alpha.toPrecision(4)} Np/m`],
      ['level at r_max: 1-D', `${v.level_1D.toFixed(2)} dB`], ['2-D', `${v.level_2D.toFixed(2)} dB`], ['3-D', `${v.level_3D.toFixed(2)} dB`]]));
    D3.forEach((d) => Plotly.react(maps[d], [{ type: 'heatmap', x: M.x, y: M.x, z: instM(M[d], 0), zmin: -1.5, zmax: 1.5, zsmooth: 'best', showscale: false, hoverinfo: 'skip',
      colorscale: [[0, C.H], [0.5, 'rgba(0,0,0,0)'], [1, C.E]] }], layout({ margin: { l: 36, r: 6, t: 6, b: 30 }, hovermode: false,
      shapes: d === '1D' ? [{ type: 'line', x0: M.x[0], x1: M.x[0], y0: M.x[0], y1: M.x[M.x.length - 1], line: { color: C.ink, width: 3 } }] : [],
      annotations: [{ x: d === '1D' ? M.x[0] : 0, y: 0, text: d === '1D' ? 'source plane' : d === '2D' ? 'line ⊥ page' : 'point', showarrow: false, xanchor: d === '1D' ? 'left' : 'center', yshift: -14, font: { size: 11 } }],
      xaxis: { constrain: 'domain', title: { text: 'x (m)' }, exponentformat: 'SI' }, yaxis: { scaleanchor: 'x', exponentformat: 'SI' } }), plotCfg));
    const P = last.profiles, col = { '1D': C.accent, '2D': C.S, '3D': C.E };
    Plotly.react(fAmp, [...D3.map((d) => ({ x: rl, y: P[d].mag, name: d, line: { color: col[d], width: 2.4 } })),
      ...[[0, '1D'], [-0.5, '2D'], [-1, '3D']].map(([s, d]) => ({ x: [0.5, rl[rl.length - 1]], y: [1, Math.pow(rl[rl.length - 1] / 0.5, s)], mode: 'lines', line: { color: col[d], dash: 'dot', width: 1 }, showlegend: false, hoverinfo: 'skip' }))],
      layout({ xaxis: { type: 'log', title: { text: 'r / λ' } }, yaxis: { type: 'log', title: { text: '|ψ| (normalised)' }, exponentformat: 'power' },
        annotations: [{ x: Math.log10(rl[rl.length - 1]), y: Math.log10(Math.max(P['3D'].mag[P['3D'].mag.length - 1], 1e-9)), text: 'slope −1', showarrow: false, xanchor: 'right', yshift: -10, font: { size: 11, color: C.E } },
          { x: Math.log10(rl[rl.length - 1]), y: Math.log10(Math.max(P['2D'].mag[P['2D'].mag.length - 1], 1e-9)), text: 'slope −½', showarrow: false, xanchor: 'right', yshift: 10, font: { size: 11, color: C.S } }] }), plotCfg);
    const fs = last.fsweep;
    Plotly.react(fF, D3.map((d) => ({ x: fs.f, y: fs[d], name: d, line: { color: col[d], width: 2.2 } })).concat([{ x: [S.f, S.f], y: [Math.min(...fs['3D'], -40), 2], mode: 'lines', line: { color: C.ink3, dash: 'dash', width: 1 }, showlegend: false }]),
      layout({ xaxis: { type: 'log', title: { text: 'f (Hz)' }, exponentformat: 'SI' }, yaxis: { title: { text: 'level at r_max (dB re λ/2)' } } }), plotCfg);
    sens.replaceChildren(h('div', { class: 'tablewrap' }, h('table', { class: 't' }, h('thead', {}, h('tr', {}, ['Change', 'New λ', 'Δ level 1-D', 'Δ level 2-D', 'Δ level 3-D'].map((x) => h('th', {}, x)))),
      h('tbody', {}, last.sensitivity.map((s) => h('tr', {}, h('td', {}, s.change), h('td', { class: 'num' }, si(s.lambda, 'm')),
        ...D3.map((d) => h('td', { class: 'num' }, `${s[d] >= 0 ? '+' : ''}${s[d].toFixed(2)} dB`))))))));
    steps.replaceChildren(stepsTable(last.steps)); checks.replaceChildren(checksTable(last.checks));
    anim();
  }
  function anim() {
    if (!last) return;
    const p = (phase * Math.PI) / 180;
    D3.forEach((d) => maps[d].data && Plotly.restyle(maps[d], { z: [instM(last.maps[d], p)] }));
    const rl = last.r.map((x) => x / last.values.wavelength), col = { '1D': C.accent, '2D': C.S, '3D': C.E };
    Plotly.react(fLine, D3.map((d) => ({ x: rl, y: inst(last.profiles[d], p).map((y) => Math.max(Math.min(y, 3), -3)), name: d, line: { color: col[d], width: 1.8 } })),
      layout({ xaxis: { title: { text: 'r / λ' } }, yaxis: { title: { text: 'Re{ψ e^{jωt}}' }, range: [-3, 3] } }), plotCfg);
  }
  function tick() { if (!playing) return; phase = (phase + 6) % 360; phc.set(phase); timer = setTimeout(tick, 70); }
  run();
  return () => { playing = false; clearTimeout(timer); [...Object.values(maps), fAmp, fLine, fF].forEach((f) => Plotly.purge(f)); };
}

function table() {
  const rows = [
    ['Field depends on', 'z only', 'ρ (and φ for a directive source)', 'R, θ, φ'],
    ['Wave equation', R`\psi''+k^2\psi=0`, R`\tfrac1\rho(\rho\psi')'+k^2\psi=0`, R`\tfrac1{R^2}(R^2\psi')'+k^2\psi=0`],
    ['Outgoing solution', R`e^{-jkz}`, R`H_0^{(2)}(k\rho)`, R`e^{-jkR}/R`],
    ['Wavefront', 'plane', 'cylinder', 'sphere'],
    ['Amplitude law', R`1`, R`1/\sqrt\rho`, R`1/R`],
    ['Power density law', R`1`, R`1/\rho`, R`1/R^2`],
    ['Doubling the distance', '0 dB', '−3 dB', '−6 dB'],
    ['Typical systems', INFO['1D'].ex, INFO['2D'].ex, INFO['3D'].ex],
    ['Book', 'Ulaby ch. 2 & 7', 'Ulaby §9 (line sources), Cheng ch. 10', 'Ulaby ch. 9, Cheng ch. 11'],
  ];
  return h('div', { class: 'tablewrap' }, h('table', { class: 't' }, h('thead', {}, h('tr', {}, ['Property', '1-D', '2-D', '3-D'].map((x) => h('th', { scope: 'col' }, x)))),
    h('tbody', {}, rows.map((r) => h('tr', {}, h('td', {}, h('b', {}, r[0])), ...r.slice(1).map((x) => h('td', {}, /[\\^{]/.test(x) ? tex(x) : x)))))));
}
