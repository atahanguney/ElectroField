// Explained solution view: renders the `explain` object built by engine/explain.py.
// Everything shown here (text, numbers, plot data, figure angles) comes from the engine; no physics in JS.
import { h, tex, layout, C } from './ui.js';
import { figure } from './figures.js';

const label = (t) => h('div', { class: 'ex-label' }, t);

// Prose with subscripted symbols written plainly (E_n, J_c, V_emf, τ_r) → inline KaTeX for those tokens.
const SUB = /([A-Za-zτρεμσθΦΔ])_([A-Za-z0-9]+)/g;
function P(text, attrs = {}) {
  const parts = [];
  let last = 0;
  for (const m of text.matchAll(SUB)) {
    parts.push(text.slice(last, m.index), tex(`${m[1]}_{${m[2].length > 1 ? String.raw`\text{${m[2]}}` : m[2]}}`));
    last = m.index + m[0].length;
  }
  parts.push(text.slice(last));
  return h('p', attrs, ...parts.filter((x) => x !== ''));
}

function plot(p) {
  const box = h('div', { class: 'ex-plot', role: 'img', 'aria-label': `${p.ylabel} against ${p.xlabel}` });
  const colors = [C.accent, C.ink3];
  const draw = () => {
    if (!box.isConnected || !window.Plotly) return requestAnimationFrame(draw);
    window.Plotly.newPlot(box, p.ys.map((s, i) => ({ x: p.x, y: s.y, name: s.name, mode: p.x.length > 12 ? 'lines' : 'lines+markers',
      line: { color: colors[i % 2], width: 2, dash: i ? 'dash' : 'solid' }, marker: { size: 6 } })),
    layout({ height: 250, showlegend: p.ys.length > 1, margin: { t: p.ys.length > 1 ? 34 : 10 },
      xaxis: { title: { text: p.xlabel }, type: p.logx ? 'log' : 'linear', exponentformat: 'power', showexponent: 'all',
        ...(p.x.length <= 12 ? { tickvals: p.x } : {}) },
      yaxis: { title: { text: p.ylabel }, type: p.logy ? 'log' : 'linear', exponentformat: 'power', showexponent: 'all' } }),
    { displayModeBar: false, responsive: true });
  };
  requestAnimationFrame(draw);
  return box;
}

/**
 * explainView(ex, { stepwise }) → { el, next }.
 * Order: what is asked · idea · steps · answer · evidence · common mistake · "if the question had asked…".
 * With stepwise, steps appear one per next() call; next() returns false once everything is shown.
 */
export function explainView(ex, { stepwise = false, title = '' } = {}) {
  const steps = h('ol', { class: 'ex-steps' });
  const tail = h('div');
  const head = h('div', { class: 'ex-head' },
    h('div', {}, label('What is asked'), P(ex.asked)),
    h('div', {}, label('Idea'), P(ex.idea)));
  const body = h('div', { class: ex.fig ? 'ex-body with-fig' : 'ex-body' }, h('div', {}, label('Solution'), steps),
    ex.fig ? h('figure', { class: 'ex-fig' }, figure(ex.fig, `${title} — solution`), h('figcaption', {}, 'Solution sketch, angles from the engine (not to scale).')) : null);
  const el = h('section', { class: 'ex', 'aria-label': 'Explained solution' }, head, body, tail);

  const stepEl = (s, i) => h('li', {}, h('span', { class: 'ex-n' }, `${i + 1}`), h('div', {}, P(s.say), s.tex ? tex(s.tex, true) : null));
  const finish = () => tail.replaceChildren(...[      // replaceChildren would print null as text
    ex.answer ? h('div', { class: 'ex-answer' }, label('Answer'), P(ex.answer),
      h('span', { class: ex.verified ? 'pass' : 'fail' }, ex.verified ? 'verified by the engine' : 'a verification check failed')) : null,
    ex.answer_text ? h('div', { class: 'ex-answer' }, label('Model answer'), P(ex.answer_text),
      h('span', { class: ex.verified ? 'pass' : 'fail' }, ex.verified ? 'supporting numbers verified by the engine' : 'a verification check failed')) : null,
    ex.evidence_say || ex.plot ? h('div', { class: 'ex-block' }, label('Evidence'), ex.evidence_say ? P(ex.evidence_say) : null, ex.plot ? plot(ex.plot) : null) : null,
    ex.mistake ? h('div', { class: 'ex-block ex-mistake' }, label('Common mistake'), P(ex.mistake)) : null,
    ex.whatif.length ? h('div', { class: 'ex-block' }, label('If the question had asked…'),
      h('ul', { class: 'ex-whatif' }, ex.whatif.map((w) => h('li', {}, P(w.q, { class: 'ex-q' }), P(w.say), w.tex ? tex(w.tex, true) : null)))) : null].filter(Boolean));

  let shown = 0;
  const next = () => {
    if (shown < ex.steps.length) steps.append(stepEl(ex.steps[shown], shown++));
    if (shown >= ex.steps.length && !tail.firstChild) finish();
    return shown < ex.steps.length;
  };
  if (!stepwise) while (next());
  else if (!ex.steps.length) finish();
  return { el, next };
}
