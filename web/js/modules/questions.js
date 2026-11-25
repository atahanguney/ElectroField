// Question bank — randomised textbook-style problems; the engine solves and verifies every answer.
import { h, stepsTable, checksTable, sci } from '../ui.js';
import { api } from '../api.js';
import { openChapter, chapterTitle } from '../app.js';
import { figure } from '../figures.js';
import { explainView } from '../explain.js';

const CH = ['all', 'dimensions', 'coordinates', 'electrostatics', 'magnetostatics', 'maxwell', 'waves', 'reflection', 'tlines', 'radiation'];
const score = { tried: 0, right: 0 };   // per page visit

export function render(view, ch, init = {}) {
  const chSel = h('select', {}, CH.map((c) => h('option', { value: c, selected: c === (init.chapter || 'all') }, c === 'all' ? 'All chapters' : chapterTitle(c))));
  const lvSel = h('select', {}, [['', 'Any level'], ['1', 'Level 1 — direct'], ['2', 'Level 2 — multi-step'], ['3', 'Level 3 — advanced']].map(([v, t]) => h('option', { value: v }, t)));
  const card = h('div'), tally = h('span', { class: 'hint', style: 'margin:0' });
  view.append(h('div', { class: 'eyebrow' }, 'PRACTICE'), h('h1', {}, ch.title),
    h('p', { class: 'lede' }, 'Original problems written in the style of Ulaby and Cheng end-of-chapter exercises, with fresh numbers every time. Your answer is compared with the engine\'s solution, and that solution is accepted only if all of its independent checks pass. After answering you get a written explanation, variations of the question, and the full derivation.'),
    h('div', { class: 'panel', style: 'display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:16px 0' },
      h('div', { style: 'width:220px' }, chSel), h('div', { style: 'width:200px' }, lvSel),
      h('button', { class: 'btn primary', onclick: () => next() }, 'New question'), tally),
    card);
  const upd = () => { tally.textContent = score.tried ? `Score: ${score.right} / ${score.tried}` : ''; };

  async function next() {
    card.replaceChildren(h('p', { class: 'hint' }, 'Generating…'));
    try {
      const q = await api('qb/new', { chapter: chSel.value, level: lvSel.value || undefined }, 'qbn');
      show(q);
    } catch (e) { if (!e.stale) card.replaceChildren(h('p', { class: 'error' }, e.message)); }
  }

  function show(q) {
    const inp = h('input', { type: 'text', placeholder: 'your answer', style: 'max-width:180px' });
    const out = h('div');
    let done = false;
    const go = async (withAnswer) => {
      if (done) return;
      const a = inp.value.trim().replace(',', '.');
      if (withAnswer && (a === '' || !isFinite(+a))) { inp.classList.add('invalid'); return; }
      try {
        const r = await api('qb/check', { id: q.id, seed: q.seed, answer: withAnswer ? +a : undefined }, 'qbc');
        done = true; inp.disabled = true;
        if (withAnswer) { score.tried++; if (r.correct) score.right++; upd(); }
        const tol = r.tolerance_kind === 'absolute' ? `± ${r.tolerance} ${r.unit}` : `± ${(100 * r.tolerance).toFixed(0)} %`;
        const derivation = [h('h2', {}, 'Derivation'), stepsTable(r.steps), h('h2', {}, 'Verification'), checksTable(r.checks)];
        out.replaceChildren(
          h('div', { class: 'panel', style: 'margin-top:12px' },
            withAnswer ? h('p', { class: r.correct ? 'pass' : 'fail', style: 'font-size:15px;margin:0 0 6px' }, r.correct ? 'Correct.' : 'Not within tolerance.') : null,
            h('p', { style: 'margin:0' }, 'Engine answer: ', h('b', { class: 'num', style: 'font-family:var(--mono)' }, `${sci(r.answer, 4)} ${r.unit}`), h('span', { class: 'hint' }, `  (accepted ${tol})`)),
            h('p', { class: r.verified ? 'pass' : 'fail', style: 'margin:6px 0 0;font-size:13px' }, r.verified ? `Solution verified by ${r.checks.length} independent checks.` : 'Warning: a verification check failed.'),
            h('button', { class: 'btn', style: 'margin-top:10px', onclick: () => openChapter(r.action.chapter, r.action.params) }, `Open ${chapterTitle(r.action.chapter)} with these values →`)),
          ...(r.explain
            ? [h('h2', {}, 'Solution'), explainView(r.explain, { title: q.id }).el,
              h('details', { class: 'ex-engine' }, h('summary', {}, `Engine derivation and independent checks (${r.checks.length})`), ...derivation)]
            : [h('h2', {}, 'Solution'), stepsTable(r.steps), h('h2', {}, 'Verification'), checksTable(r.checks)]));
      } catch (e) { if (!e.stale) out.replaceChildren(h('p', { class: 'error' }, e.message)); }
    };
    inp.addEventListener('keydown', (e) => { if (e.key === 'Enter') go(true); });
    const text = h('p', { class: 'prose', style: 'font-size:17px;margin:0 0 14px' }, q.text);
    card.replaceChildren(h('div', { class: 'panel' },
      h('div', { class: 'eyebrow', style: 'margin-bottom:8px' }, `${chapterTitle(q.chapter).toUpperCase()} · LEVEL ${q.level} · CF. ${q.ref.toUpperCase()}`),
      q.fig ? h('div', { class: 'qb-body' }, text, h('div', { class: 'wk-fig' }, figure(q.fig, 'Question figure'))) : text,
      h('div', { style: 'display:flex;gap:8px;align-items:center;flex-wrap:wrap' }, inp, h('span', { class: 'unit', style: 'font-family:var(--mono)' }, q.unit || '(dimensionless)'),
        h('button', { class: 'btn primary', onclick: () => go(true) }, 'Check'), h('button', { class: 'btn', onclick: () => go(false) }, 'Show solution'),
        h('span', { class: 'hint', style: 'margin:0' }, `#${q.id}/${q.seed}`))), out);
    inp.focus();
  }
  upd(); next();
}
