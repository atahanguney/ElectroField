// Chapter 1 — coordinate systems and differential elements (Ulaby §3-2, Cheng §2-4).
import { h, tex, control, segmented, stepsTable, checksTable, kv, si, sci, layout, plotCfg, C } from '../ui.js';
import { api, debounce } from '../api.js';

const DEF = {
  cartesian:   { u: [1, 1, 1], d: [0.4, 0.4, 0.4],
    uc: [['x', 'm', -2, 2], ['y', 'm', -2, 2], ['z', 'm', -2, 2]], dc: [['dx', 'm', .01, 1], ['dy', 'm', .01, 1], ['dz', 'm', .01, 1]],
    edge: ['dx', 'dy', 'dz'], hat: ['x̂', 'ŷ', 'ẑ'] },
  cylindrical: { u: [1.5, 30, 0.3], d: [0.4, 25, 0.5],
    uc: [['r', 'm', 0, 3], ['\\phi', '°', 0, 360], ['z', 'm', -2, 2]], dc: [['dr', 'm', .01, 1], ['d\\phi', '°', 1, 90], ['dz', 'm', .01, 1]],
    edge: ['dr', 'r dφ', 'dz'], hat: ['r̂', 'φ̂', 'ẑ'] },
  spherical:   { u: [1.5, 50, 30], d: [0.4, 20, 25],
    uc: [['R', 'm', 0, 3], ['\\theta', '°', 0, 180], ['\\phi', '°', 0, 360]], dc: [['dR', 'm', .01, 1], ['d\\theta', '°', 1, 60], ['d\\phi', '°', 1, 90]],
    edge: ['dR', 'R dθ', 'R sinθ dφ'], hat: ['R̂', 'θ̂', 'φ̂'] },
};
const AXC = () => [C.accent, C.S, C.E];

export function render(view, ch, init = {}) {
  let sys = DEF[init.system] ? init.system : 'spherical';
  const st = Object.fromEntries(Object.entries(DEF).map(([k, v]) => [k, { u: [...v.u], d: [...v.d] }]));
  if (init.u?.length === 3) st[sys].u = init.u.map(Number);
  if (init.d?.length === 3) st[sys].d = init.d.map(Number);

  const ctlBox = h('div');
  const err = h('div', { class: 'error' });
  const fig3d = h('div', { class: 'plot tall' });
  const figConv = h('div', { class: 'plot', style: 'height:260px' });
  const viewA = h('div', { class: 'plot', style: 'height:340px' }), viewB = h('div', { class: 'plot', style: 'height:340px' });
  const capA = h('p', { class: 'cap' }), capB = h('p', { class: 'cap' });
  const viewsBox = h('div', { class: 'grid2' }, h('div', { class: 'fig' }, viewA, capA), h('div', { class: 'fig' }, viewB, capB));
  const formulas = h('div'), results = h('div'), steps = h('div'), checks = h('div'), convTable = h('div');

  view.append(
    h('div', { class: 'eyebrow' }, `CHAPTER ${ch.n}`),
    h('h1', {}, ch.title),
    h('p', { class: 'lede' }, 'A point is fixed by three coordinates; a small step in each traces three edges of a curved box. Their lengths are the scale factors times the increments, and everything else — surface and volume elements, the divergence, the curl — is built from them.'),
    h('div', { class: 'work' },
      h('div', { class: 'panel' },
        h('h3', {}, 'System'),
        segmented([['cartesian', 'Cartesian'], ['cylindrical', 'Cylindrical'], ['spherical', 'Spherical']], sys, (k) => { sys = k; build(); }),
        ctlBox, err),
      h('div', { class: 'figs' },
        h('div', { class: 'fig' }, fig3d, h('p', { class: 'cap' }, h('b', {}, 'Differential volume element. '),
          'The three coloured edges are the components of dl leaving the point; the arrows are the local unit vectors. Dashed lines locate the point from the origin. Drag to rotate.')),
        viewsBox, formulas, results)),
    h('h2', {}, 'Derivation'), steps,
    h('h2', {}, 'Verification'), checks,
    h('h2', {}, 'Why "differential": convergence to the exact volume'),
    h('p', { class: 'prose' }, 'The product h₁h₂h₃ du₁du₂du₃ is exact only in the limit. Below, the finite box [u, u+d] is integrated exactly and compared with the differential formula while every increment is halved. The error halves too — first-order convergence, so the formula is the correct limit.'),
    h('div', { class: 'grid2' }, h('div', { class: 'fig' }, figConv), convTable),
    converter(),
    theory());

  function build() {
    const D = DEF[sys], s = st[sys];
    const mk = (spec, arr, i, isD) => control({
      texLabel: spec[0], unit: spec[1], min: spec[2], max: spec[3], value: arr[i],
      onchange: (v) => { arr[i] = v; update(); },
    }).el;
    ctlBox.replaceChildren(h('h3', {}, 'Point'), ...D.uc.map((sp, i) => mk(sp, s.u, i)),
      h('h3', {}, 'Increments'), ...D.dc.map((sp, i) => mk(sp, s.d, i)),
      h('p', { class: 'hint' }, 'Text fields accept SI prefixes, e.g. 250m = 0.25.'));
    update();
  }

  const update = debounce(async () => {
    const s = st[sys];
    try {
      const r = await api('coords/element', { system: sys, u1: s.u[0], u2: s.u[1], u3: s.u[2], d1: s.d[0], d2: s.d[1], d3: s.d[2] }, 'coords');
      err.textContent = '';
      draw(r);
    } catch (e) { if (!e.stale) err.textContent = e.message; }
  });

  function draw(r) {
    const D = DEF[sys], col = AXC(), v = r.values;
    const tr = [];
    // faint reference: axes and the coordinate surface through the point
    const L = 2.6;
    [[L, 0, 0, 'x'], [0, L, 0, 'y'], [0, 0, L, 'z']].forEach(([x, y, z, n]) => tr.push({
      type: 'scatter3d', mode: 'lines+text', x: [0, x], y: [0, y], z: [0, z], text: ['', n], textfont: { color: C.ink3 },
      line: { color: C.ink3, width: 2 }, hoverinfo: 'skip', showlegend: false }));
    tr.push(...referenceSurface(sys, st[sys].u, st[sys].d));
    r.faces.forEach((f) => tr.push({ type: 'surface', x: f.x, y: f.y, z: f.z, showscale: false, opacity: 0.38,
      colorscale: [[0, C.accent], [1, C.accent]], hoverinfo: 'skip', lighting: { ambient: 0.9, diffuse: 0.3 } }));
    r.edges.forEach((e, i) => tr.push({ type: 'scatter3d', mode: 'lines', x: e.x, y: e.y, z: e.z, name: `${D.edge[i]} = ${si(v.dl[i], 'm', 3)}`,
      line: { color: col[i], width: 9 }, hoverinfo: 'name' }));
    const p = r.point, k = 0.7;
    r.unit_vectors.forEach((u, i) => {
      tr.push({ type: 'scatter3d', mode: 'lines', x: [p[0], p[0] + k * u[0]], y: [p[1], p[1] + k * u[1]], z: [p[2], p[2] + k * u[2]],
        line: { color: col[i], width: 4, dash: 'dot' }, showlegend: false, hoverinfo: 'skip' });
      tr.push({ type: 'cone', x: [p[0] + k * u[0]], y: [p[1] + k * u[1]], z: [p[2] + k * u[2]], u: [u[0]], v: [u[1]], w: [u[2]],
        sizemode: 'absolute', sizeref: 0.14, anchor: 'tip', showscale: false, colorscale: [[0, col[i]], [1, col[i]]], hoverinfo: 'skip', name: D.hat[i] });
      tr.push({ type: 'scatter3d', mode: 'text', x: [p[0] + 1.05 * k * u[0]], y: [p[1] + 1.05 * k * u[1]], z: [p[2] + 1.05 * k * u[2]],
        text: [D.hat[i]], textfont: { color: col[i], size: 14 }, showlegend: false, hoverinfo: 'skip' });
    });
    // construction lines + value labels at the middle of each edge
    r.guides.lines.forEach((g) => tr.push({ type: 'scatter3d', mode: 'lines', x: g.x, y: g.y, z: g.z, showlegend: false, hoverinfo: 'skip',
      line: { color: g.kind === 'angle' ? C.ink : C.ink3, width: g.kind === 'angle' ? 3 : 2, dash: g.kind === 'angle' ? 'solid' : 'dash' } }));
    tr.push({ type: 'scatter3d', mode: 'text', x: r.guides.labels.map((l) => l.x), y: r.guides.labels.map((l) => l.y), z: r.guides.labels.map((l) => l.z),
      text: r.guides.labels.map((l) => l.text), textfont: { size: 15, color: C.ink }, showlegend: false, hoverinfo: 'skip' });
    r.edges.forEach((e, i) => { const m = e.x.length >> 1; tr.push({ type: 'scatter3d', mode: 'text', x: [e.x[m]], y: [e.y[m]], z: [e.z[m]],
      text: [`${D.edge[i]}`], textposition: 'top center', textfont: { size: 13, color: col[i] }, showlegend: false, hoverinfo: 'skip' }); });
    const sc = { showbackground: false, gridcolor: C.rule, zerolinecolor: C.rule, color: C.ink3, title: '' };
    drawViews(r.views, col);
    Plotly.react(fig3d, tr, layout({ margin: { l: 0, r: 0, t: 0, b: 0 }, hovermode: 'closest', uirevision: sys,
      scene: { aspectmode: 'data', xaxis: sc, yaxis: sc, zaxis: sc, camera: { eye: { x: 1.5, y: 1.2, z: 0.9 } } } }), plotCfg);

    const T = r.steps;
    formulas.replaceChildren(h('div', { class: 'panel' },
      tex(T[1].tex, true), tex(T.slice(5, 8).map((s) => s.tex.split('=').slice(0, 2).join('=')).join(',\\quad '), true),
      tex(T[8].tex.split('=').slice(0, 2).join('='), true)));
    results.replaceChildren(kv([
      ...D.edge.map((n, i) => [`dl along ${D.hat[i]}  (${n})`, si(v.dl[i], 'm')]),
      ...['1', '2', '3'].map((_, i) => [`ds ⊥ ${D.hat[i]}`, `${sci(v.ds[i])} m²`]),
      ['dv', `${sci(v.dv)} m³`], ['exact box volume', `${sci(v.exact_finite_volume)} m³`]]));
    steps.replaceChildren(stepsTable(T));
    checks.replaceChildren(checksTable(r.checks));

    const cv = r.convergence;
    Plotly.react(figConv, [
      { x: cv.map((c) => c.scale), y: cv.map((c) => c.rel_error), mode: 'lines+markers', name: 'relative error', line: { color: C.accent } },
      { x: cv.map((c) => c.scale), y: cv.map((c) => cv[0].rel_error * c.scale), mode: 'lines', name: 'slope 1 reference', line: { color: C.ink3, dash: 'dash', width: 1 } },
    ], layout({ xaxis: { type: 'log', title: { text: 'increment scale (×d)' } }, yaxis: { type: 'log', title: { text: '|dv − V_exact| / V_exact' } } }), plotCfg);
    convTable.replaceChildren(h('table', { class: 't' },
      h('thead', {}, h('tr', {}, ['scale', 'exact V', 'h₁h₂h₃ d³u', 'rel. error'].map((x) => h('th', {}, x)))),
      h('tbody', {}, cv.map((c) => h('tr', {}, [c.scale, c.exact, c.approx, c.rel_error].map((x) => h('td', { class: 'num' }, sci(x, 4))))))));
  }

  // 2-D dimensioned sections (equal aspect so angles and lengths read true)
  function drawViews(vs, col) {
    const style = { element: { color: C.accent, width: 1.2 }, edge0: { color: col[0], width: 4 }, edge1: { color: col[1], width: 4 },
      edge2: { color: col[2], width: 4 }, guide: { color: C.ink3, width: 1.2, dash: 'dash' }, guide2: { color: C.ink, width: 1.2, dash: 'dot' },
      faint: { color: C.rule, width: 1 }, axis: { color: C.ink3, width: 1 }, angle: { color: C.ink, width: 1.5 } };
    const tcol = { edge0: col[0], edge1: col[1], edge2: col[2], angle: C.ink, guide: C.ink3, guide2: C.ink };
    [[viewA, capA], [viewB, capB]].forEach(([el, cap], k) => {
      const v = vs[k];
      const traces = v.paths.map((p) => ({ x: p.x, y: p.y, mode: 'lines', line: style[p.kind], hoverinfo: 'skip', showlegend: false,
        fill: p.kind === 'element' ? 'toself' : 'none', fillcolor: p.kind === 'element' ? 'rgba(31,78,121,0.16)' : undefined }));
      const ann = v.labels.map((l) => ({ x: l.x, y: l.y, text: l.text, showarrow: false, font: { size: 12, color: tcol[l.kind] || C.ink, family: 'ui-monospace, Consolas, monospace' },
        bgcolor: C.panel, borderpad: 2, opacity: 0.95 }));
      Plotly.react(el, traces, layout({ annotations: ann, hovermode: false, margin: { l: 50, r: 12, t: 8, b: 42 },
        xaxis: { title: { text: v.xlabel }, zeroline: false, constrain: 'domain' }, yaxis: { title: { text: v.ylabel }, scaleanchor: 'x', scaleratio: 1, zeroline: false } }), plotCfg);
      cap.replaceChildren(h('b', {}, v.title + '. '), 'Coloured segments are the same dl edges as in the 3-D view, drawn to scale.');
    });
  }

  build();
  return () => { [fig3d, figConv, viewA, viewB].forEach((f) => Plotly.purge(f)); };
}

// faint surface u1 = const through the point (sphere / cylinder) — drawing aid only
function referenceSurface(sys, u, d) {
  if (sys === 'cartesian') return [];
  const n = 40, a = [], b = [], c = [], z0 = Math.min(0, u[2]) - 0.2, z1 = Math.max(0, u[2] + d[2]) + 0.2;
  for (let i = 0; i <= n; i++) {
    const ra = [], rb = [], rc = [];
    for (let j = 0; j <= n; j++) {
      const p = (2 * Math.PI * j) / n;
      if (sys === 'spherical') { const t = (Math.PI * i) / n; ra.push(u[0] * Math.sin(t) * Math.cos(p)); rb.push(u[0] * Math.sin(t) * Math.sin(p)); rc.push(u[0] * Math.cos(t)); }
      else { const z = z0 + ((z1 - z0) * i) / n; ra.push(u[0] * Math.cos(p)); rb.push(u[0] * Math.sin(p)); rc.push(z); }
    }
    a.push(ra); b.push(rb); c.push(rc);
  }
  return [{ type: 'surface', x: a, y: b, z: c, opacity: 0.07, showscale: false, colorscale: [[0, C.ink3], [1, C.ink3]], hoverinfo: 'skip' }];
}

function converter() {
  const box = h('div');
  const S = { cartesian: ['x', 'y', 'z'], cylindrical: ['r', 'φ (°)', 'z'], spherical: ['R', 'θ (°)', 'φ (°)'] };
  const src = h('select', {}, Object.keys(S).map((k) => h('option', { value: k }, k)));
  const dst = h('select', {}, Object.keys(S).map((k) => h('option', { value: k, selected: k === 'spherical' }, k)));
  const pin = [2, 3, -1].map((v) => h('input', { type: 'number', value: v, step: 'any' }));
  const vin = [1, 0, 0].map((v) => h('input', { type: 'number', value: v, step: 'any' }));
  const plab = h('div', { class: 'hint' }), out = h('div');
  const go = async () => {
    plab.textContent = `Point (${S[src.value].join(', ')}) · vector components along (${S[src.value].map((x) => x.split(' ')[0] + '̂').join(', ')})`;
    try {
      const r = await api('coords/convert', { src: src.value, dst: dst.value, u1: pin[0].value, u2: pin[1].value, u3: pin[2].value,
        A1: vin[0].value, A2: vin[1].value, A3: vin[2].value }, 'conv');
      const v = r.values, L = S[dst.value];
      out.replaceChildren(kv([...L.map((n, i) => [n, sci(v.point[i], 6)]), ...L.map((n, i) => [`A along ${n.split(' ')[0]}̂`, sci(v.vector[i], 6)])]),
        h('h3', {}, 'Transformation matrix (rows: target unit vectors · source unit vectors)'),
        h('table', { class: 't' }, h('thead', {}, h('tr', {}, h('th', { scope: 'col' }, 'target \\ source'), ...S[src.value].map((n) => h('th', { scope: 'col' }, `${n.split(' ')[0]}̂`)))),
          h('tbody', {}, v.matrix.map((row, i) => h('tr', {}, h('th', { scope: 'row' }, `${L[i].split(' ')[0]}̂`), ...row.map((x) => h('td', { class: 'num' }, sci(x, 5))))))),
        h('h3', {}, 'Checks'), checksTable(r.checks));
    } catch (e) { if (!e.stale) out.replaceChildren(h('p', { class: 'error' }, e.message)); }
  };
  [src, dst, ...pin, ...vin].forEach((el) => el.addEventListener('change', go));
  go();
  return h('div', {}, h('h2', {}, 'Point and vector conversion'),
    h('p', { class: 'prose' }, 'Unit vectors in cylindrical and spherical systems depend on position, so converting a vector needs the point as well. The matrix entries are the dot products of the two sets of unit vectors (Ulaby Table 3-2); its rows are orthonormal, so |A| is unchanged.'),
    h('div', { class: 'grid2' },
      h('div', { class: 'panel' }, h('div', { class: 'grid2' }, h('label', {}, 'From', src), h('label', {}, 'To', dst)),
        h('h3', {}, 'Point'), h('div', { class: 'grid2', style: 'grid-template-columns:1fr 1fr 1fr' }, pin),
        h('h3', {}, 'Vector A'), h('div', { class: 'grid2', style: 'grid-template-columns:1fr 1fr 1fr' }, vin), plab),
      out));
}

function theory() {
  const rows = [
    ['Cartesian', 'x, y, z', '1, 1, 1', String.raw`dx\,dy\,dz`],
    ['Cylindrical', 'r, φ, z', '1, r, 1', String.raw`r\,dr\,d\phi\,dz`],
    ['Spherical', 'R, θ, φ', String.raw`1,\;R,\;R\sin\theta`, String.raw`R^2\sin\theta\,dR\,d\theta\,d\phi`],
  ];
  return h('div', {}, h('h2', {}, 'Summary'),
    h('table', { class: 't' }, h('thead', {}, h('tr', {}, ['System', 'Coordinates', 'Scale factors h₁, h₂, h₃', 'dv'].map((x) => h('th', {}, x)))),
      h('tbody', {}, rows.map((r) => h('tr', {}, h('td', {}, r[0]), h('td', {}, r[1]), h('td', {}, tex(r[2])), h('td', {}, tex(r[3])))))),
    h('div', { class: 'prose', style: 'margin-top:14px' },
      h('p', {}, 'Why R sinθ in front of dφ? A change dφ moves the point around a circle whose radius is its distance from the z-axis, R sinθ — not R. At the poles (θ = 0, 180°) that circle shrinks to a point, so ds_R and dv vanish there. Set θ near 0 above and watch the element collapse.'),
      h('p', {}, 'The general operators follow from the same h_i:'),
      tex(String.raw`\nabla\cdot\mathbf A=\frac{1}{h_1h_2h_3}\left[\frac{\partial(h_2h_3A_1)}{\partial u_1}+\frac{\partial(h_1h_3A_2)}{\partial u_2}+\frac{\partial(h_1h_2A_3)}{\partial u_3}\right]`, true),
      tex(String.raw`\nabla V=\hat u_1\frac{1}{h_1}\frac{\partial V}{\partial u_1}+\hat u_2\frac{1}{h_2}\frac{\partial V}{\partial u_2}+\hat u_3\frac{1}{h_3}\frac{\partial V}{\partial u_3}`, true)));
}
