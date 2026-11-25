// Worked problems — original exam-level problems with figures, full and simple solutions, engine-verified answers.
import { h, tex, stepsTable, checksTable, sci, segmented } from '../ui.js';
import { api } from '../api.js';
import { openChapter } from '../app.js';
import { figure } from '../figures.js';
import { explainView } from '../explain.js';
import { chapterFor } from './tutor.js';

export function render(view, ch, init = {}) {
  const list = h('div', { class: 'wk-list' }), err = h('div', { class: 'error' });
  const tabsBox = h('div');
  view.append(h('div', { class: 'eyebrow' }, 'PRACTICE'), h('h1', {}, ch.title),
    h('p', { class: 'lede' }, 'Problems at the level of university midterm and final exams, written for this site. Each one names the textbook section where the topic is taught. Try it first, then reveal the solution one step at a time: every formula, substitution and final answer comes from the engine, which also re-checks the result by an independent method.'),
    h('p', { class: 'hint' }, 'The problems are original. They practise the same concepts as the cited sections of Ulaby & Ravaioli and Cheng, but they are not copies of textbook or exam questions.'),
    tabsBox, err, list);
  api('wk/catalog', {}, 'wkc').then((cat) => {
    const keys = Object.keys(cat.topics), start = init.topic && cat.topics[init.topic] ? init.topic : keys[0];
    tabsBox.append(segmented(keys.map((k) => [k, `${cat.topics[k]} (${cat.problems.filter((p) => p.topic === k).length})`]), start, (k) => show(k)));
    const show = (k) => list.replaceChildren(...cat.problems.filter((p) => p.topic === k).map((p, i) => card(p, i + 1)));
    show(start);
  }).catch((e) => { err.textContent = e.message; });
}

const engineDetails = (r) => h('details', { class: 'ex-engine' }, h('summary', {}, `Engine derivation and independent checks (${r.checks.length})`),
  stepsTable(r.steps), checksTable(r.checks));

function openBtn(r) {
  const act = chapterFor(r.route, r.params);
  return act ? h('button', { class: 'btn', type: 'button', style: 'margin-top:8px', onclick: () => openChapter(act.chapter, act.params) }, 'Open the chapter with these values →') : null;
}

function card(p, n) {
  const sol = h('div'), stepBox = h('div'), simpleBox = h('div');
  let solved = null, shown = 0, ev = null;
  const load = async () => { if (!solved) solved = await api('wk/solve', { id: p.id }, `wk${p.id}`); return solved; };
  const answerLine = (r) => h('div', { class: 'wk-answer' }, h('span', { class: r.all_passed ? 'pass' : 'fail' }, r.all_passed ? '✓ verified' : '✗ check failed'),
    ...r.answers.map((a) => h('span', { class: 'wk-ans' }, `${a.label} = `, h('b', {}, `${sci(a.value, 4)} ${a.unit}`))));
  const done = () => { nextBtn.disabled = true; nextBtn.textContent = 'All steps shown'; };

  const nextStep = async () => {
    const r = await load();
    if (r.explain) {                      // written explanation, revealed one step at a time
      if (!ev) { ev = explainView(r.explain, { stepwise: true, title: p.title }); sol.replaceChildren(); stepBox.replaceChildren(ev.el); }
      if (!ev.next()) { done(); stepBox.append(engineDetails(r), openBtn(r) || ''); }
      return;
    }
    const steps = r.steps;
    if (shown === 0) stepBox.append(h('p', { class: 'prose' }, h('b', {}, 'Approach. '), p.approach));
    if (shown < steps.length) {
      const s = steps[shown];
      stepBox.append(h('div', { class: 'wk-step' }, h('div', { class: 'wk-step-n' }, `Step ${shown + 1}`), h('div', {}, h('div', { class: 'note' }, s.label), tex(s.tex, true),
        s.value != null && !Array.isArray(s.value) ? h('div', { class: 'num' }, `= ${sci(s.value)} ${s.unit}`) : null, s.note ? h('div', { class: 'note' }, s.note) : null)));
      shown++;
    }
    if (shown >= steps.length) { done(); stepBox.append(answerLine(r)); }
  };
  const nextBtn = h('button', { class: 'btn', type: 'button', onclick: () => nextStep().catch((e) => sol.replaceChildren(h('p', { class: 'error' }, e.message))) }, 'Next step');
  const full = async () => {
    const r = await load();
    stepBox.replaceChildren(); done();
    if (r.explain) sol.replaceChildren(explainView(r.explain, { title: p.title }).el, engineDetails(r), openBtn(r) || '');
    else sol.replaceChildren(h('p', { class: 'prose' }, h('b', {}, 'Approach. '), p.approach), stepsTable(r.steps), answerLine(r),
      h('details', {}, h('summary', {}, `Independent checks (${r.checks.length})`), checksTable(r.checks)), openBtn(r) || '');
  };
  const concept = p.kind === 'concept';
  return h('article', { class: 'wk-card', id: `wk-${p.id}` },
    h('div', { class: 'wk-head' }, h('span', { class: 'wk-n' }, `Problem ${n}`),
      p.has_explain ? h('span', { class: 'badge soft' }, concept ? 'conceptual' : 'numerical') : null,
      h('span', { class: `badge ${p.level === 'exam' ? '' : 'soft'}` }, p.level === 'exam' ? 'exam level' : 'basic'), h('span', { class: 'note' }, `Topic: ${p.ref}`)),
    h('h2', { class: 'wk-title' }, p.title),
    h('div', { class: 'wk-body' }, h('p', { class: 'wk-text' }, p.text), h('div', { class: 'wk-fig' }, figure(p.fig, p.title))),
    h('div', { class: 'wk-actions' }, nextBtn,
      h('button', { class: 'btn', type: 'button', onclick: () => full().catch((e) => sol.replaceChildren(h('p', { class: 'error' }, e.message))) }, concept ? 'Model answer' : 'Full solution'),
      p.simple ? h('button', { class: 'btn', type: 'button', onclick: () => simpleBox.replaceChildren(h('aside', { class: 'simple' }, h('div', { class: 'simple-h' }, 'Simple explanation'), h('p', {}, p.simple))) }, 'Simple explanation') : null,
      h('span', { class: 'hint', style: 'margin:0' }, p.answer_labels.length ? `Find: ${p.answer_labels.join(', ')}` : 'Answer in words')),
    simpleBox, stepBox, sol);
}
