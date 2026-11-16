// Method of images — Q above a grounded plane ≡ Q and −Q with the plane removed (cf. Ulaby & Ravaioli Sec. 4-11, Fig. 4-26).
import { h, tex, control, stepsTable, checksTable, kv, si, sci, layout, plotCfg, simple, C } from '../ui.js';
import { api, post, debounce } from '../api.js';

const R = String.raw;

export function render(view, ch, init = {}) {
  const S = { Q: 1, d: 0.4, eps_r: 1, ...init };   // Q in nC
  const err = h('div', { class: 'error' }), res = h('div'), steps = h('div'), checks = h('div');
  const fA = h('div', { class: 'plot', style: 'height:430px' }), fB = h('div', { class: 'plot', style: 'height:430px' });
  const fRho = h('div', { class: 'plot', style: 'height:300px' }), fCorner = h('div', { class: 'plot', style: 'height:420px' });
  const c = (o) => control({ ...o, onchange: (v) => { S[o.key] = v; run(); } }).el;
  view.append(h('div', { class: 'eyebrow' }, `CHAPTER ${ch.n}`), h('h1', {}, ch.title),
    h('p', { class: 'lede' }, 'A point charge Q at height d above a grounded, perfectly conducting plane induces negative charge on the plane. Above the plane the field is exactly the field of Q together with an image charge −Q at depth d below it — with the plane removed. The two pictures below are computed independently by the engine and agree everywhere in z > 0.'),
    h('div', { class: 'formula-box' }, tex(R`V(x,z)=\frac{Q}{4\pi\varepsilon}\left[\frac{1}{\sqrt{x^2+(z-d)^2}}-\frac{1}{\sqrt{x^2+(z+d)^2}}\right],\qquad z\ge0`, true)),
    h('div', { class: 'work' },
      h('div', { class: 'panel' }, h('h3', {}, 'Configuration'),
        c({ key: 'Q', texLabel: 'Q', label: 'charge', unit: 'nC', value: S.Q, min: -10, max: 10, step: 0.1 }),
        c({ key: 'd', texLabel: 'd', label: 'height above plane', unit: 'm', value: S.d, min: 0.1, max: 0.8 }),
        c({ key: 'eps_r', texLabel: '\\varepsilon_r', label: 'medium above plane', value: S.eps_r, min: 1, max: 10 }),
        h('p', { class: 'hint' }, 'Field lines start on +Q and end on negative charge; equipotentials are red for V > 0 and blue for V < 0.'), err),
      h('div', { class: 'figs' }, h('div', { class: 'grid2' },
        h('div', { class: 'fig' }, fA, h('p', { class: 'cap' }, h('b', {}, '(a) Charge Q above a grounded plane. '), 'σ = ∞, V = 0 on the plane; n̂ is the outward normal. Lines meet the conductor at right angles.')),
        h('div', { class: 'fig' }, fB, h('p', { class: 'cap' }, h('b', {}, '(b) Equivalent configuration. '), 'Q and its image −Q, plane removed. The dashed line z = 0 is still at V = 0, and the upper half is identical to (a).'))),
        res)),
    h('div', { class: 'fig', style: 'margin-top:16px' }, fRho, h('p', { class: 'cap' }, h('b', {}, 'Induced surface charge on the plane. '), 'ρs = εE_z at z = 0⁺ from the field (markers) and the closed form (line). Its integral over the plane is exactly −Q.')),
    simple({
      idea: 'The metal plane is "at zero volts". Instead of solving for how charge spreads on the metal, imagine a mirror: put an opposite charge −Q at the same distance below the surface. A + and − pair at equal distance makes every point of the middle line exactly 0 V — so the mirror pair reproduces the grounded plane above it.',
      remember: ['Image = opposite sign, same distance, mirror position.', 'Only valid in the region of the real charge (z > 0). Below the plane the real field is zero.',
        'The force on Q is the Coulomb force from its image at distance 2d: F = Q²/(4πε(2d)²), always attractive.'],
      mistakes: ['Using distance d instead of 2d in the force.', 'Expecting a field inside the conductor (z < 0): it is zero there; the image is only a calculation tool.', 'Forgetting that the induced charge totals −Q.'],
    }),
    h('h2', {}, 'Derivation'), steps, h('h2', {}, 'Verification'), checks,
    h('h2', {}, 'Why it works: the uniqueness theorem'),
    h('div', { class: 'prose' },
      h('p', {}, 'In the region z > 0 the potential must satisfy Poisson’s equation with the single point charge as source, V = 0 on the plane and V → 0 far away. A solution of Poisson’s (or Laplace’s) equation is unique once its boundary values are fixed. The image pair satisfies the same equation in z > 0 (the image is outside that region) and the same boundary values, so it is the solution.'),
      tex(R`\nabla^2 V=-\frac{Q}{\varepsilon}\delta(\mathbf R-\mathbf R_Q)\ \ (z>0),\qquad V\big|_{z=0}=0,\qquad V\big|_{R\to\infty}=0`, true)),
    h('h2', {}, 'Extension: charge in a 90° corner'),
    h('p', { class: 'prose' }, 'Two grounded planes meeting at a right angle need three images: −Q mirrored in each wall and +Q mirrored in both. The engine checks that V = 0 on both walls.'),
    h('div', { class: 'fig' }, fCorner, h('p', { class: 'cap' }, h('b', {}, 'Corner reflector. '), 'Only the first quadrant is physical; the faint charges are images.')));

  const run = debounce(async () => {
    try {
      const r = await api('img/plane', { Q: S.Q * 1e-9, d: S.d, eps_r: S.eps_r }, 'img');
      err.textContent = ''; draw(r);
    } catch (e) { if (!e.stale) err.textContent = e.message; }
  });

  function panel(el, r, grounded) {
    const tr = [], ann = [], d = S.d, L = Math.max(1, 2.5 * d);
    for (const e of r.equipotentials) tr.push({ x: e.x, y: e.y, mode: 'lines', line: { color: e.V > 0 ? C.E : e.V < 0 ? C.H : C.ink, width: 0.9, dash: e.V === 0 ? 'dash' : 'solid' }, opacity: 0.55, hoverinfo: 'skip', showlegend: false });
    for (const l of r.field_lines) {
      const xs = grounded ? l.x : l.x, ys = l.y;
      tr.push({ x: xs, y: ys, mode: 'lines', line: { color: C.ink, width: 1.3 }, hoverinfo: 'skip', showlegend: false });
      const m = Math.floor(l.x.length * 0.35);
      if (l.x.length > 6) ann.push({ x: l.x[m + 1], y: l.y[m + 1], ax: l.x[m - 1], ay: l.y[m - 1], axref: 'x', ayref: 'y', showarrow: true, arrowhead: 2, arrowsize: 1, arrowwidth: 1.2, arrowcolor: C.ink, text: '' });
    }
    const pos = S.Q >= 0;
    const charge = (y, sgn, label) => {
      tr.push({ x: [0], y: [y], mode: 'markers+text', text: [sgn > 0 ? '+' : '−'], textfont: { color: '#fff', size: 15 }, marker: { size: 22, color: sgn > 0 ? C.E : C.H }, hoverinfo: 'skip', showlegend: false });
      ann.push({ x: 0, y, text: label, showarrow: false, xanchor: 'left', xshift: 16, font: { size: 15, color: C.ink } });
    };
    charge(d, pos ? 1 : -1, 'Q');
    const shapes = [{ type: 'line', x0: 0, x1: 0, y0: grounded ? 0 : -L * 0.9, y1: L * 0.95, line: { color: C.ink3, width: 1, dash: 'dot' } }];
    ann.push({ x: 0, y: L * 0.97, text: 'z', showarrow: false, yanchor: 'bottom', font: { size: 14 } });
    // dimension d on the right of the axis
    ann.push({ x: -0.08 * L, y: d, ax: -0.08 * L, ay: 0, axref: 'x', ayref: 'y', showarrow: true, arrowhead: 2, arrowside: 'end+start', arrowwidth: 1, arrowcolor: C.ink3, text: '' });
    ann.push({ x: -0.08 * L, y: d / 2, text: 'd', showarrow: false, xanchor: 'right', xshift: -4, font: { size: 14 } });
    ann.push({ x: 0.75 * L, y: 0.8 * L, text: 'ε', showarrow: false, font: { size: 16 } });
    if (grounded) {
      shapes.push({ type: 'rect', x0: -L, x1: L, y0: -0.35 * L, y1: 0, fillcolor: C.ink3, opacity: 0.3, line: { width: 0 } });
      shapes.push({ type: 'line', x0: -L, x1: L, y0: 0, y1: 0, line: { color: C.ink, width: 3 } });
      ann.push({ x: 0, y: -0.2 * L, text: 'σ = ∞', showarrow: false, font: { size: 14 } });
      ann.push({ x: -0.85 * L, y: 0, text: 'V = 0', showarrow: false, yanchor: 'bottom', font: { size: 13 } });
      ann.push({ x: 0.55 * L, y: 0.22 * L, ax: 0.55 * L, ay: 0, axref: 'x', ayref: 'y', showarrow: true, arrowhead: 2, arrowwidth: 1.8, arrowcolor: C.accent, text: '' });
      ann.push({ x: 0.55 * L, y: 0.22 * L, text: 'n̂', showarrow: false, xanchor: 'left', xshift: 4, font: { size: 15, color: C.accent } });
      // ground symbol at the left edge
      [0, 1, 2].forEach((k) => shapes.push({ type: 'line', x0: -0.95 * L + 0.02 * L * k, x1: -0.85 * L - 0.02 * L * k, y0: -0.3 * L - 0.03 * L * k, y1: -0.3 * L - 0.03 * L * k, line: { color: C.ink, width: 1.5 } }));
    } else {
      charge(-d, pos ? -1 : 1, '−Q');
      shapes.push({ type: 'line', x0: -L, x1: L, y0: 0, y1: 0, line: { color: C.ink, width: 1.5, dash: 'dash' } });
      ann.push({ x: 0.85 * L, y: 0, text: 'V = 0', showarrow: false, yanchor: 'bottom', font: { size: 13 } });
      ann.push({ x: 0.75 * L, y: -0.8 * L, text: 'ε', showarrow: false, font: { size: 16 } });
      ann.push({ x: -0.08 * L, y: -d, ax: -0.08 * L, ay: 0, axref: 'x', ayref: 'y', showarrow: true, arrowhead: 2, arrowside: 'end+start', arrowwidth: 1, arrowcolor: C.ink3, text: '' });
      ann.push({ x: -0.08 * L, y: -d / 2, text: 'd', showarrow: false, xanchor: 'right', xshift: -4, font: { size: 14 } });
    }
    Plotly.react(el, tr, layout({ annotations: ann, shapes, hovermode: false, margin: { l: 44, r: 10, t: 10, b: 40 },
      xaxis: { range: [-L, L], title: { text: 'x (m)' }, zeroline: false, constrain: 'domain' },
      yaxis: { range: grounded ? [-0.35 * L, L] : [-L, L], title: { text: 'z (m)' }, zeroline: false, scaleanchor: 'x' } }), plotCfg);
  }

  function draw(r) {
    const v = r.values;
    panel(fA, r.a, true); panel(fB, r.b, false);
    res.replaceChildren(kv([['ρs at x = 0', `${sci(v.rho_s0)} C/m²`], ['force on Q (toward plane)', si(v.F, 'N')], ['energy', `${sci(v.W)} J`], ['induced charge', `−Q = ${sci(-S.Q)} nC`]]));
    const rs = r.rho_s, every = Math.max(1, Math.floor(rs.x.length / 40));
    Plotly.react(fRho, [{ x: rs.x, y: rs.closed, name: 'closed form', line: { color: C.H, width: 2.2 } },
      { x: rs.x.filter((_, i) => i % every === 0), y: rs.num.filter((_, i) => i % every === 0), name: 'from the engine field', mode: 'markers', marker: { color: C.E, size: 6 } }],
      layout({ xaxis: { title: { text: 'x along the plane (m)' } }, yaxis: { title: { text: 'ρs (C/m²)' }, exponentformat: 'power' } }), plotCfg);
    steps.replaceChildren(stepsTable(r.steps)); checks.replaceChildren(checksTable(r.checks));
    corner();
  }

  async function corner() {
    const x0 = 0.3, y0 = 0.5, q = S.Q || 1;
    try {
      const [cr, fl] = await Promise.all([api('img/corner', { Q: q * 1e-9, x0, y0 }, 'imgc'),
        post('es/charges', { charges: [[q, x0, y0], [-q, -x0, y0], [-q, x0, -y0], [q, -x0, -y0]].map(([qq, x, y]) => ({ q: qq * 1e-9, x, y })), probe: [0.6, 0.6] }, 'imgcf')]);
      const tr = fl.field_lines.map((l) => ({ x: l.x, y: l.y, mode: 'lines', line: { color: C.ink, width: 1.1 }, hoverinfo: 'skip', showlegend: false }));
      fl.charges.forEach((p, i) => tr.push({ x: [p.x], y: [p.y], mode: 'markers+text', text: [p.q > 0 ? '+' : '−'], textfont: { color: '#fff', size: 13 },
        marker: { size: 18, color: p.q > 0 ? C.E : C.H, opacity: i === 0 ? 1 : 0.35 }, hoverinfo: 'skip', showlegend: false }));
      Plotly.react(fCorner, tr, layout({ hovermode: false, annotations: [{ x: 0.5, y: 0.95, xref: 'paper', yref: 'paper', text: cr.all_passed ? `V = 0 on both walls ✓ (${cr.checks.length} checks)` : 'check failed', showarrow: false, font: { size: 12, color: cr.all_passed ? C.S : C.E } }],
        shapes: [{ type: 'rect', x0: -1, x1: 0, y0: -1, y1: 1, fillcolor: C.ink3, opacity: 0.18, line: { width: 0 } }, { type: 'rect', x0: 0, x1: 1, y0: -1, y1: 0, fillcolor: C.ink3, opacity: 0.18, line: { width: 0 } },
          { type: 'line', x0: 0, x1: 0, y0: 0, y1: 1, line: { color: C.ink, width: 3 } }, { type: 'line', x0: 0, x1: 1, y0: 0, y1: 0, line: { color: C.ink, width: 3 } }],
        xaxis: { range: [-1, 1], title: { text: 'x (m)' }, zeroline: false, constrain: 'domain' }, yaxis: { range: [-1, 1], title: { text: 'y (m)' }, scaleanchor: 'x', zeroline: false } }), plotCfg);
    } catch (e) { if (!e.stale) err.textContent = e.message; }
  }
  run();
  return () => [fA, fB, fRho, fCorner].forEach((f) => Plotly.purge(f));
}
