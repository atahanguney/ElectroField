// Chapter 5 — uniform plane waves in lossy media (Ulaby §7-4…7-5, Cheng §8-3).
import { h, tex, control, stepsTable, checksTable, kv, si, sci, layout, plotCfg, C } from '../ui.js';
import { api, debounce } from '../api.js';

// typical values; biological tissue from Gabriel et al. (1996) at 2.45 GHz
const PRESETS = [
  ['Free space', { eps_r: 1, mu_r: 1, sigma: 0 }],
  ['PTFE', { eps_r: 2.1, mu_r: 1, sigma: 0 }],
  ['Dry soil', { eps_r: 3, mu_r: 1, sigma: 1e-4 }],
  ['Fresh water', { eps_r: 80, mu_r: 1, sigma: 1e-3 }],
  ['Sea water', { eps_r: 81, mu_r: 1, sigma: 4 }],
  ['Muscle (2.45 GHz)', { eps_r: 52.7, mu_r: 1, sigma: 1.74, f: 2.45e9 }],
  ['Copper', { eps_r: 1, mu_r: 1, sigma: 5.8e7 }],
  ['Iron (low field)', { eps_r: 1, mu_r: 4000, sigma: 1e7 }],
];
const SWEEP = { f: ['frequency f', 'Hz', 1e3, 1e12], sigma: ['conductivity σ', 'S/m', 1e-6, 1e8],
  eps_r: ['relative permittivity εr', '', 1, 100], mu_r: ['relative permeability μr', '', 1, 1e4] };

export function render(view, ch, init = {}) {
  const p = { f: 1e6, eps_r: 81, mu_r: 1, sigma: 4, E0: 1, ...init };
  let sweepParam = 'f', phase = 0, playing = false, raf = 0, last = null;

  const ctl = {
    f: control({ texLabel: 'f', label: 'frequency', unit: 'Hz', value: p.f, min: 1, max: 1e12, log: true, onchange: (v) => set('f', v) }),
    eps_r: control({ texLabel: '\\varepsilon_r', unit: '', value: p.eps_r, min: 1, max: 100, onchange: (v) => set('eps_r', v) }),
    mu_r: control({ texLabel: '\\mu_r', unit: '', value: p.mu_r, min: 1, max: 1e4, log: true, onchange: (v) => set('mu_r', v) }),
    sigma: control({ texLabel: '\\sigma', unit: 'S/m', value: p.sigma, min: 1e-8, max: 1e8, log: true, onchange: (v) => set('sigma', v) }),
    E0: control({ texLabel: 'E_0', label: 'amplitude', unit: 'V/m', value: p.E0, min: 0.01, max: 1e4, log: true, onchange: (v) => set('E0', v) }),
  };
  const err = h('div', { class: 'error' }), summary = h('div'), steps = h('div'), checks = h('div');
  const figZ = h('div', { class: 'plot' }), fig3 = h('div', { class: 'plot' }), figA = h('div', { class: 'plot' }), figB = h('div', { class: 'plot' });
  const phaseCtl = control({ texLabel: '\\omega t', unit: '°', value: 0, min: 0, max: 360, step: 1, onchange: (v) => { phase = v; drawTime(); } });
  const playBtn = h('button', { class: 'btn', onclick: () => { playing = !playing; playBtn.textContent = playing ? 'Pause' : 'Play'; if (playing) tick(); } }, 'Play');
  const sweepSel = h('select', { onchange: () => { sweepParam = sweepSel.value; doSweep(); } },
    Object.entries(SWEEP).map(([k, v]) => h('option', { value: k }, v[0])));

  view.append(
    h('div', { class: 'eyebrow' }, `CHAPTER ${ch.n}`), h('h1', {}, ch.title),
    h('p', { class: 'lede' }, 'In a medium with permittivity ε, permeability μ and conductivity σ, Maxwell\'s equations allow a wave whose amplitude decays as e^{−αz} while its phase advances as βz. Everything about the wave — how fast it dies, how fast it travels, how E and H are related — follows from the single complex number γ = α + jβ.'),
    h('div', { class: 'work' },
      h('div', { class: 'panel' },
        h('h3', {}, 'Medium'), h('div', { class: 'presets' }, PRESETS.map(([n, v]) => h('button', { class: 'btn', onclick: () => preset(v) }, n))),
        ctl.f.el, ctl.eps_r.el, ctl.mu_r.el, ctl.sigma.el, ctl.E0.el,
        h('p', { class: 'hint' }, 'Type values like 2.45G, 58M or 0 (σ). Values are typical, not certified material data.'), err),
      h('div', { class: 'figs' }, summary,
        h('div', { class: 'fig' }, figZ, h('div', { style: 'display:grid;grid-template-columns:80px 1fr;gap:12px;align-items:center' }, playBtn, phaseCtl.el),
          h('p', { class: 'cap' }, h('b', {}, 'Instantaneous fields along z. '), 'E_x(z,t) = Re{E₀e^{−γz}e^{jωt}} with envelope ±E₀e^{−αz}; H_y lags E by θ_η (right axis). Dashed lines mark δs and λ.')),
        h('div', { class: 'fig' }, fig3, h('p', { class: 'cap' }, h('b', {}, 'Field vectors in space. '), 'E along x̂, H along ŷ (drawn ×|ηc| so both share a scale), propagation along ẑ: E × H points in +ẑ.')))),
    h('h2', {}, 'How the wave depends on the medium'),
    h('div', { class: 'panel', style: 'display:flex;gap:12px;align-items:center;margin-bottom:12px' }, h('span', {}, 'Sweep'), h('div', { style: 'width:260px' }, sweepSel),
      h('span', { class: 'hint', style: 'margin:0' }, 'other parameters held at the values above; bands show the loss regime')),
    h('div', { class: 'grid2' },
      h('div', { class: 'fig' }, figA, h('p', { class: 'cap' }, h('b', {}, 'α and β. '), 'In a good conductor α = β ∝ √(fμσ); in a low-loss dielectric α ≈ (σ/2)√(μ/ε), independent of f.')),
      h('div', { class: 'fig' }, figB, h('p', { class: 'cap' }, h('b', {}, '|ηc| and skin depth δs = 1/α. '), 'The marker is the current operating point.'))),
    h('h2', {}, 'Derivation'), steps,
    h('h2', {}, 'Verification'),
    h('p', { class: 'prose' }, 'The closed forms for α and β are compared with a direct complex square root; the impedance with Faraday\'s law; and the computed field is differentiated numerically along z and substituted back into both curl equations. The residual must be at the level of the finite-difference truncation error.'),
    checks, theory());

  function set(k, v) { p[k] = v; refresh(); }
  function preset(v) { for (const [k, x] of Object.entries(v)) { p[k] = x; ctl[k].set(x); } }
  const refresh = debounce(() => { solve(); doSweep(); });

  async function solve() {
    try {
      last = await api('waves/solve', p, 'solve');
      err.textContent = '';
      const v = last.values;
      summary.replaceChildren(h('div', { style: 'margin-bottom:8px' }, h('span', { class: 'badge' }, v.regime), ' ',
        h('span', { class: 'hint' }, `ε''/ε' = ${sci(v.loss_tangent)}`)), kv([
        ['α attenuation', `${sci(v.alpha)} Np/m`], ['α in dB', `${sci(v.alpha_dB)} dB/m`], ['β phase', `${sci(v.beta)} rad/m`],
        ['|ηc|', si(v.eta_mag, 'Ω')], ['θη', `${v.eta_phase_deg.toFixed(3)}°`], ['up phase velocity', si(v.vp, 'm/s')],
        ['λ wavelength', si(v.wavelength, 'm')], ['δs skin depth', si(v.skin_depth, 'm')], ['S_av(0)', `${sci(v.S_av0)} W/m²`]]));
      steps.replaceChildren(stepsTable(last.steps));
      checks.replaceChildren(checksTable(last.checks));
      drawTime(); draw3d(); mark();
    } catch (e) { if (!e.stale) err.textContent = e.message; }
  }

  function inst(F, ph) { const c = Math.cos(ph), s = Math.sin(ph); return F.re.map((r, i) => r * c - F.im[i] * s); }
  function drawTime() {
    if (!last) return;
    const { z, E, H } = last.field, v = last.values, ph = (phase * Math.PI) / 180;
    const env = E.re.map((r, i) => Math.hypot(r, E.im[i]));
    const zmax = z[z.length - 1], shapes = [];
    [[v.skin_depth, 'δs'], [v.wavelength, 'λ']].forEach(([x, n]) => x && x < zmax && shapes.push(
      { type: 'line', x0: x, x1: x, yref: 'paper', y0: 0, y1: 1, line: { color: C.ink3, dash: 'dash', width: 1 }, label: { text: n, textposition: 'end', font: { size: 11, color: C.ink3 } } }));
    Plotly.react(figZ, [
      { x: z, y: env, mode: 'lines', line: { color: C.E, width: 1, dash: 'dot' }, name: 'envelope', hoverinfo: 'skip' },
      { x: z, y: env.map((e) => -e), mode: 'lines', line: { color: C.E, width: 1, dash: 'dot' }, showlegend: false, hoverinfo: 'skip' },
      { x: z, y: inst(E, ph), mode: 'lines', line: { color: C.E, width: 2 }, name: 'E_x (V/m)' },
      { x: z, y: inst(H, ph), mode: 'lines', line: { color: C.H, width: 2 }, name: 'H_y (A/m)', yaxis: 'y2' },
    ], layout({ shapes, xaxis: { title: { text: 'z (m)' }, exponentformat: 'SI' }, yaxis: { title: { text: 'E_x (V/m)' }, exponentformat: 'power' },
      yaxis2: { overlaying: 'y', side: 'right', title: { text: 'H_y (A/m)' }, showgrid: false, exponentformat: 'power', tickfont: { size: 11 } },
      margin: { r: 64 } }), plotCfg);
  }

  function draw3d() {
    const { z, E, H } = last.field, eta = last.values.eta_mag, ph = (phase * Math.PI) / 180;
    const e = inst(E, ph), hh = inst(H, ph).map((x) => x * eta), stem = (vals, axis) => {
      const X = [], Y = [], Z = [];
      for (let i = 0; i < z.length; i += 8) { X.push(z[i], z[i], null); if (axis === 'E') { Y.push(0, 0, null); Z.push(0, vals[i], null); } else { Y.push(0, vals[i], null); Z.push(0, 0, null); } }
      return { X, Y, Z };
    };
    const sE = stem(e, 'E'), sH = stem(hh, 'H'), sc = { showbackground: false, gridcolor: C.rule, color: C.ink3 };
    Plotly.react(fig3, [
      { type: 'scatter3d', mode: 'lines', x: z, y: z.map(() => 0), z: e, line: { color: C.E, width: 5 }, name: 'E_x' },
      { type: 'scatter3d', mode: 'lines', x: sE.X, y: sE.Y, z: sE.Z, line: { color: C.E, width: 2 }, showlegend: false, hoverinfo: 'skip' },
      { type: 'scatter3d', mode: 'lines', x: z, y: hh, z: z.map(() => 0), line: { color: C.H, width: 5 }, name: 'H_y·|ηc|' },
      { type: 'scatter3d', mode: 'lines', x: sH.X, y: sH.Y, z: sH.Z, line: { color: C.H, width: 2 }, showlegend: false, hoverinfo: 'skip' },
      { type: 'scatter3d', mode: 'lines', x: [0, z[z.length - 1]], y: [0, 0], z: [0, 0], line: { color: C.ink3, width: 2 }, showlegend: false, hoverinfo: 'skip' },
    ], layout({ margin: { l: 0, r: 0, t: 0, b: 0 }, hovermode: 'closest', uirevision: 'k',
      scene: { xaxis: { ...sc, title: 'z (m)' }, yaxis: { ...sc, title: 'y: H' }, zaxis: { ...sc, title: 'x: E' }, aspectmode: 'manual', aspectratio: { x: 2.4, y: 1, z: 1 },
        camera: { eye: { x: 0.6, y: -2.0, z: 0.9 } } } }), plotCfg);
  }

  function tick() {
    if (!playing) return;
    phase = (phase + 4) % 360; phaseCtl.set(phase);
    raf = setTimeout(() => requestAnimationFrame(tick), 50);
  }

  let sw = null;
  async function doSweep() {
    const [, unit, lo, hi] = SWEEP[sweepParam];
    try { sw = await api('waves/sweep', { param: sweepParam, lo, hi, ...p, E0: undefined }, 'sweep'); } catch (e) { if (!e.stale) err.textContent = e.message; return; }
    const x = sw.x, xt = `${SWEEP[sweepParam][0]}${unit ? ` (${unit})` : ''}`;
    const bands = regimeBands(x, sw.loss_tangent);
    const lx = { type: 'log', title: { text: xt }, exponentformat: 'power' };
    Plotly.react(figA, [
      { x, y: sw.alpha.map((a) => a || null), name: 'α (Np/m)', line: { color: C.E, width: 2 } },
      { x, y: sw.beta, name: 'β (rad/m)', line: { color: C.accent, width: 2 } },
    ], layout({ shapes: bands, xaxis: lx, yaxis: { type: 'log', title: { text: 'Np/m, rad/m' }, exponentformat: 'power' } }), plotCfg);
    Plotly.react(figB, [
      { x, y: sw.eta_mag, name: '|ηc| (Ω)', line: { color: C.S, width: 2 } },
      { x, y: sw.skin_depth, name: 'δs (m)', line: { color: C.H, width: 2 }, yaxis: 'y2' },
    ], layout({ shapes: bands, xaxis: lx, yaxis: { type: 'log', title: { text: '|ηc| (Ω)' }, exponentformat: 'power' },
      yaxis2: { type: 'log', overlaying: 'y', side: 'right', title: { text: 'δs (m)' }, showgrid: false, exponentformat: 'power' }, margin: { r: 64 } }), plotCfg);
    mark();
  }

  // operating point marker on both sweep plots
  function mark() {
    if (!last || !sw || !figA.data) return;
    const x0 = p[sweepParam], v = last.values;
    const pts = [[figA, [v.alpha || null, v.beta], [C.E, C.accent], ['y', 'y']], [figB, [v.eta_mag, v.skin_depth], [C.S, C.H], ['y', 'y2']]];
    for (const [fig, ys, cs, ax] of pts) {
      const n = fig.data.length;
      if (n > 2) Plotly.deleteTraces(fig, [...Array(n - 2).keys()].map((i) => i + 2));
      Plotly.addTraces(fig, ys.map((y, i) => ({ x: [x0], y: [y], mode: 'markers', marker: { color: cs[i], size: 9, line: { color: C.panel, width: 2 } }, showlegend: false, yaxis: ax[i], hoverinfo: 'skip' })));
    }
  }

  solve(); doSweep();
  return () => { playing = false; clearTimeout(raf); [figZ, fig3, figA, figB].forEach((f) => Plotly.purge(f)); };
}

function regimeBands(x, lt) {
  const cls = (t) => (t < 0.01 ? 0 : t > 100 ? 2 : 1), fill = ['rgba(46,125,79,0.07)', 'rgba(0,0,0,0)', 'rgba(176,58,46,0.07)'];
  const names = ['low-loss', '', 'good conductor'], out = [];
  let s = 0;
  for (let i = 1; i <= x.length; i++) {
    if (i === x.length || cls(lt[i]) !== cls(lt[s])) {
      const c = cls(lt[s]);
      if (c !== 1) out.push({ type: 'rect', xref: 'x', yref: 'paper', x0: x[s], x1: x[i - 1], y0: 0, y1: 1, fillcolor: fill[c], line: { width: 0 }, layer: 'below',
        label: { text: names[c], textposition: 'top center', font: { size: 11, color: '#888' } } });
      s = i;
    }
  }
  return out;
}

function theory() {
  const R = String.raw;
  const rows = [
    ['Quantity', 'Any medium', R`Low-loss \;(\varepsilon''/\varepsilon'\ll1)`, R`Good conductor \;(\varepsilon''/\varepsilon'\gg1)`],
    ['α', R`\omega\Big[\tfrac{\mu\varepsilon'}{2}\big(\sqrt{1+(\varepsilon''/\varepsilon')^2}-1\big)\Big]^{1/2}`, R`\frac{\sigma}{2}\sqrt{\frac{\mu}{\varepsilon}}`, R`\sqrt{\pi f\mu\sigma}`],
    ['β', R`\omega\Big[\tfrac{\mu\varepsilon'}{2}\big(\sqrt{1+(\varepsilon''/\varepsilon')^2}+1\big)\Big]^{1/2}`, R`\omega\sqrt{\mu\varepsilon}`, R`\sqrt{\pi f\mu\sigma}`],
    ['ηc', R`\sqrt{\mu/\varepsilon'}\,(1-j\varepsilon''/\varepsilon')^{-1/2}`, R`\sqrt{\mu/\varepsilon}`, R`(1+j)\,\alpha/\sigma`],
    ['up', R`\omega/\beta`, R`1/\sqrt{\mu\varepsilon}`, R`\sqrt{4\pi f/\mu\sigma}`],
    ['δs', R`1/\alpha`, R`\frac{2}{\sigma}\sqrt{\frac{\varepsilon}{\mu}}`, R`1/\sqrt{\pi f\mu\sigma}`],
  ];
  return h('div', {}, h('h2', {}, 'Theory'),
    h('div', { class: 'prose' },
      h('p', {}, 'Taking the curl of Faraday\'s law and substituting Ampère–Maxwell for a source-free linear medium gives the homogeneous Helmholtz equation:'),
      tex(R`\nabla^2\mathbf E-\gamma^2\mathbf E=0,\qquad \gamma^2=j\omega\mu(\sigma+j\omega\varepsilon)=-\omega^2\mu\varepsilon_c`, true),
      h('p', {}, 'For a wave travelling in +z with E along x̂, the solution is E = x̂E₀e^{−γz}. Faraday\'s law then fixes H = ŷ(E₀/ηc)e^{−γz} with ηc = jωμ/γ. Splitting γ² into real and imaginary parts, α² − β² = −ω²με and 2αβ = ωμσ, and solving the pair gives the expressions below.')),
    h('table', { class: 't', style: 'margin-top:10px' }, h('thead', {}, h('tr', {}, rows[0].map((x, i) => h('th', {}, i > 1 ? tex(x) : x)))),
      h('tbody', {}, rows.slice(1).map((r) => h('tr', {}, h('td', {}, r[0]), ...r.slice(1).map((x) => h('td', {}, tex(x))))))),
    h('p', { class: 'prose', style: 'margin-top:12px' }, 'Reading the table: in a good conductor every quantity scales with √f, so doubling the frequency shrinks the skin depth by √2. In a low-loss dielectric the attenuation does not depend on frequency at all, only on σ and the ratio μ/ε. The sweeps above show both limits and the transition between them.'));
}
