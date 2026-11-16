// Biot–Savart law — the field of a current computed element by element (Ulaby & Ravaioli Sec. 5-2, Cheng Sec. 6-6).
import { h, tex, control, segmented, stepsTable, checksTable, kv, si, sci, layout, plotCfg, simple, C } from '../ui.js';
import { api, debounce } from '../api.js';

const R = String.raw;

export function render(view, ch) {
  const S = { I: 2, z1: -0.5, z2: 0.5, r: 0.2, N: 24 };
  const L = { I: 1, a: 0.1, z: 0.05 };
  const err = h('div', { class: 'error' }), res = h('div'), steps = h('div'), checks = h('div'), resL = h('div'), stepsL = h('div'), checksL = h('div'), resSq = h('div');
  const fGeo = h('div', { class: 'plot', style: 'height:420px' }), fDH = h('div', { class: 'plot', style: 'height:300px' }), fConv = h('div', { class: 'plot', style: 'height:300px' }), fAx = h('div', { class: 'plot', style: 'height:300px' });
  const c = (st, o, fn) => control({ ...o, onchange: (v) => { st[o.key] = v; fn(); } }).el;

  view.append(h('div', { class: 'eyebrow' }, `CHAPTER ${ch.n}`), h('h1', {}, ch.title),
    h('p', { class: 'lede' }, 'Every short piece of a current-carrying wire contributes a little magnetic field, perpendicular both to the current and to the line joining the piece to the observation point, and falling off as 1/R². Adding up all the pieces gives the field of any wire shape. Below the sum is done explicitly with N pieces and compared with the closed-form integral.'),
    h('div', { class: 'formula-box' },
      tex(R`d\mathbf H=\frac{I\,d\mathbf l\times\hat{\mathbf R}}{4\pi R^2}\quad[\mathrm{A/m}],\qquad \mathbf H=\frac{I}{4\pi}\int_\ell\frac{d\mathbf l\times\hat{\mathbf R}}{R^2},\qquad \mathbf B=\mu\mathbf H`, true),
      h('p', { class: 'hint', style: 'margin:4px 0 0' }, 'dl: vector length element along the current · R = vector from the element to the field point, R = |R|, R̂ = R/R · μ = μrμ0.')),
    simple({
      idea: 'Think of the wire as a chain of tiny arrows, each carrying the current. Each arrow makes a small circular "swirl" of magnetic field around itself. Close arrows matter a lot (1/R²); arrows pointing straight at you contribute nothing (sin 0 = 0). The total field is just the sum of all the swirls.',
      remember: [['The direction comes from the cross product: point your right thumb along the current, your fingers curl in the direction of H.'],
        ['Magnitude of one element: ', tex(R`dH=\frac{I\,dl\,\sin\theta}{4\pi R^2}`), ' where θ is the angle between dl and R̂.'],
        ['Long straight wire: ', tex(R`H=\frac{I}{2\pi r}`), '. Centre of a loop: ', tex(R`H=\frac{I}{2a}`), '.']],
      mistakes: ['Taking R from the field point to the element (it is from the element to the field point).', 'Forgetting the cross product and adding magnitudes of vectors that point in different directions.',
        'Using 1/R instead of 1/R² for a current element (1/R is for an infinite line).'],
    }),
    h('h2', {}, 'Finite straight wire'),
    h('div', { class: 'work' },
      h('div', { class: 'panel' }, h('h3', {}, 'Wire on the z-axis, point P at distance r'),
        c(S, { key: 'I', texLabel: 'I', unit: 'A', value: S.I, min: 0.1, max: 100, log: true }, () => runSeg()),
        c(S, { key: 'z1', texLabel: 'z_1', label: 'lower end', unit: 'm', value: S.z1, min: -2, max: 0 }, () => runSeg()),
        c(S, { key: 'z2', texLabel: 'z_2', label: 'upper end', unit: 'm', value: S.z2, min: 0.01, max: 2 }, () => runSeg()),
        c(S, { key: 'r', texLabel: 'r', label: 'distance of P', unit: 'm', value: S.r, min: 0.02, max: 1 }, () => runSeg()),
        c(S, { key: 'N', texLabel: 'N', label: 'number of elements', value: S.N, min: 2, max: 200, step: 1 }, () => runSeg()), err),
      h('div', { class: 'figs' }, res,
        h('div', { class: 'fig' }, fGeo, h('p', { class: 'cap' }, h('b', {}, 'Geometry. '), 'The wire is cut into N elements dl (blue). For a few of them the vector R to P is drawn; each element’s dH at P points out of the page (⊙, +φ̂) and its size is shown by the bar chart below.')))),
    h('div', { class: 'grid2', style: 'margin-top:16px' },
      h('div', { class: 'fig' }, fDH, h('p', { class: 'cap' }, h('b', {}, 'Contribution of each element. '), 'Elements nearest to P dominate; the sum of the bars is H.')),
      h('div', { class: 'fig' }, fConv, h('p', { class: 'cap' }, h('b', {}, 'Sum → integral. '), 'Relative error of the N-element sum against the closed form falls as 1/N² (slope −2): the sum converges to the integral.'))),
    h('h3', {}, 'Proof of the closed form'),
    h('div', { class: 'prose' },
      h('p', {}, 'With the wire on the z-axis and P at (r, 0, 0): dl = ẑ dz, R = r̂ r − ẑ z, so dl × R = φ̂ r dz and R = √(r² + z²). Every element gives dH along φ̂, so the magnitudes add:'),
      tex(R`H_\phi=\frac{I r}{4\pi}\int_{z_1}^{z_2}\frac{dz}{(r^2+z^2)^{3/2}}=\frac{I}{4\pi r}\left[\frac{z}{\sqrt{r^2+z^2}}\right]_{z_1}^{z_2}=\frac{I}{4\pi r}\left(\cos\theta_1-\cos\theta_2\right)`, true),
      h('p', {}, 'where θ is the angle between the +z direction (the current) and the line from the wire end to P (θ₁ at the lower end, θ₂ at the upper end; cos θ = −z/√(r²+z²) at that end). For an infinitely long wire θ₁ → 0 and θ₂ → π:'),
      tex(R`H_\phi=\frac{I}{2\pi r}\qquad\text{(the same result Ampère’s law gives in one line).}`, true)),
    h('h3', {}, 'Derivation with these numbers'), steps, h('h3', {}, 'Verification'), checks,
    h('h2', {}, 'Circular loop: field on the axis'),
    h('div', { class: 'work' },
      h('div', { class: 'panel' }, h('h3', {}, 'Loop of radius a in the xy-plane'),
        c(L, { key: 'I', texLabel: 'I', unit: 'A', value: L.I, min: 0.1, max: 100, log: true }, () => runL()),
        c(L, { key: 'a', texLabel: 'a', unit: 'm', value: L.a, min: 0.01, max: 1, log: true }, () => runL()),
        c(L, { key: 'z', texLabel: 'z', label: 'height on the axis', unit: 'm', value: L.z, min: -1, max: 1 }, () => runL())),
      h('div', { class: 'figs' }, resL, h('div', { class: 'fig' }, fAx, h('p', { class: 'cap' }, h('b', {}, 'H on the axis. '), 'The radial parts of the element fields cancel in pairs; the z-parts add. Marker: the selected height.')))),
    h('div', { class: 'formula-box' }, tex(R`dH_z=\frac{I\,dl}{4\pi R^2}\cdot\frac{a}{R},\quad R=\sqrt{a^2+z^2}\ \Rightarrow\ H_z=\frac{I a}{4\pi R^3}\oint dl=\frac{I a^2}{2\,(a^2+z^2)^{3/2}}`, true)),
    h('h3', {}, 'Derivation'), stepsL, h('h3', {}, 'Verification'), checksL,
    h('h2', {}, 'Square loop: four finite wires'),
    h('p', { class: 'prose' }, 'Each side of a square of side a is a finite wire seen from the centre at r = a/2 with θ₁ = 45°, θ₂ = 135°. The four equal contributions add:'),
    h('div', { class: 'formula-box' }, tex(R`H=4\cdot\frac{I}{4\pi(a/2)}\left(\cos45^\circ-\cos135^\circ\right)=\frac{2\sqrt2\,I}{\pi a}`, true)), resSq);

  const runSeg = debounce(async () => {
    try {
      const r = await api('bs/segment', { ...S, N: Math.round(S.N) }, 'bss'); err.textContent = '';
      const v = r.values;
      res.replaceChildren(kv([['H (sum of N elements)', `${sci(v.H)} A/m`], ['H (closed form)', `${sci(v.H_closed)} A/m`], ['B = μ₀H', si(v.B, 'T')], ['infinite wire I/2πr', `${sci(v.H_infinite)} A/m`], ['finite / infinite', sci(v.ratio_to_infinite, 4)]]));
      geometry(r); bars(r); conv(r);
      steps.replaceChildren(stepsTable(r.steps)); checks.replaceChildren(checksTable(r.checks));
    } catch (e) { if (!e.stale) err.textContent = e.message; }
  });
  function geometry(r) {
    const g = r.geometry, z = r.elements.z, dz = (g.z2 - g.z1) / z.length, tr = [], ann = [];
    tr.push({ x: [0, 0], y: [g.z1, g.z2], mode: 'lines', line: { color: C.H, width: 6 }, hoverinfo: 'skip', showlegend: false });
    tr.push({ x: z.map(() => 0), y: z, mode: 'markers', marker: { color: C.panel, size: 6, line: { color: C.H, width: 1.5 } }, hoverinfo: 'skip', showlegend: false });
    ann.push({ x: 0, y: g.z2 + 0.12 * (g.z2 - g.z1), ax: 0, ay: g.z2, axref: 'x', ayref: 'y', showarrow: true, arrowhead: 2, arrowwidth: 2, arrowcolor: C.H, text: '' });
    ann.push({ x: 0, y: g.z2 + 0.12 * (g.z2 - g.z1), text: `I = ${S.I} A`, showarrow: false, xanchor: 'left', xshift: 8, font: { color: C.H, size: 13 } });
    const pick = [0, Math.floor(z.length / 2), z.length - 1];
    pick.forEach((k) => ann.push({ x: g.r, y: 0, ax: 0, ay: z[k], axref: 'x', ayref: 'y', showarrow: true, arrowhead: 2, arrowwidth: 1.3, arrowcolor: C.ink3, text: '' }));
    ann.push({ x: g.r / 2, y: z[0] / 2, text: 'R', showarrow: false, font: { size: 14, color: C.ink3 } });
    tr.push({ x: [g.r], y: [0], mode: 'markers+text', text: ['⊙'], textfont: { size: 20, color: C.S }, marker: { size: 1 }, hoverinfo: 'skip', showlegend: false });
    ann.push({ x: g.r, y: 0, text: 'P  (dH out of page)', showarrow: false, xanchor: 'left', xshift: 14, font: { size: 13, color: C.S } });
    ann.push({ x: 0, y: z[Math.floor(z.length / 2)], text: 'dl', showarrow: false, xanchor: 'right', xshift: -10, font: { size: 13, color: C.H } });
    ann.push({ x: g.r / 2, y: 0, text: 'r', showarrow: false, yanchor: 'top', yshift: -4, font: { size: 13 } });
    tr.push({ x: [0, g.r], y: [0, 0], mode: 'lines', line: { color: C.ink3, dash: 'dot', width: 1 }, hoverinfo: 'skip', showlegend: false });
    const span = Math.max(g.z2 - g.z1, g.r) * 0.7;
    Plotly.react(fGeo, tr, layout({ annotations: ann, hovermode: false, xaxis: { range: [-span * 0.4, g.r + span * 0.8], title: { text: 'x (m)' }, zeroline: false },
      yaxis: { range: [g.z1 - 0.15 * (g.z2 - g.z1), g.z2 + 0.25 * (g.z2 - g.z1)], title: { text: 'z (m)' }, zeroline: false } }), plotCfg);
    void dz;
  }
  function bars(r) {
    Plotly.react(fDH, [{ type: 'bar', x: r.elements.z, y: r.elements.dH, marker: { color: C.S }, hovertemplate: 'z = %{x:.3f} m<br>dH = %{y:.3e} A/m<extra></extra>' }],
      layout({ xaxis: { title: { text: 'element position z (m)' } }, yaxis: { title: { text: 'dH at P (A/m)' }, exponentformat: 'power' }, showlegend: false }), plotCfg);
  }
  function conv(r) {
    const cv = r.convergence;
    Plotly.react(fConv, [{ x: cv.map((c) => c.N), y: cv.map((c) => c.rel_error), mode: 'lines+markers', name: 'sum vs integral', line: { color: C.accent, width: 2 } },
      { x: cv.map((c) => c.N), y: cv.map((c) => cv[3].rel_error * (cv[3].N / c.N) ** 2), mode: 'lines', name: 'slope −2', line: { color: C.ink3, dash: 'dash', width: 1 } }],
      layout({ xaxis: { type: 'log', title: { text: 'number of elements N' } }, yaxis: { type: 'log', title: { text: 'relative error' }, exponentformat: 'power' } }), plotCfg);
  }

  const runL = debounce(async () => {
    try {
      const r = await api('bs/loop', L, 'bsl');
      const v = r.values;
      resL.replaceChildren(kv([['H_z (sum)', `${sci(v.H)} A/m`], ['H_z (closed form)', `${sci(v.H_closed)} A/m`], ['B_z', si(v.B, 'T')], ['centre I/2a', `${sci(L.I / (2 * L.a))} A/m`]]));
      Plotly.react(fAx, [{ x: r.axis.z, y: r.axis.H, line: { color: C.H, width: 2.2 }, name: 'H_z(z)' }, { x: [L.z], y: [v.H], mode: 'markers', marker: { color: C.S, size: 10 }, showlegend: false }],
        layout({ xaxis: { title: { text: 'z on the axis (m)' } }, yaxis: { title: { text: 'H_z (A/m)' } }, showlegend: false }), plotCfg);
      stepsL.replaceChildren(stepsTable(r.steps)); checksL.replaceChildren(checksTable(r.checks));
    } catch (e) { if (!e.stale) err.textContent = e.message; }
  });

  (async () => {
    try {
      const r = await api('bs/square', { I: 1, a: 0.2, N: 200 }, 'bsq');
      resSq.replaceChildren(kv([['I = 1 A, a = 0.2 m: H (sum of 4 × 200 elements)', `${sci(r.values.H, 6)} A/m`], ['closed form', `${sci(r.values.H_closed, 6)} A/m`]]), checksTable(r.checks));
    } catch (e) { if (!e.stale) err.textContent = e.message; }
  })();
  runSeg(); runL();
  return () => [fGeo, fDH, fConv, fAx].forEach((f) => Plotly.purge(f));
}
