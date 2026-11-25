// Assistant drawer. Claude picks engine calls; each call comes back as an action that opens
// the matching chapter with those parameters, so every graph it "draws" is the engine's.
import { h } from './ui.js';
import { post, backend } from './api.js';
import { openChapter, chapterTitle } from './app.js';

const EXAMPLES = [
  'Plot a 2.45 GHz wave in muscle tissue (εr 52.7, σ 1.74 S/m). How deep does it go?',
  'Show the field of a 3 nC charge 20 cm above a grounded plane.',
  'Coax with a = 0.5 mm, b = 2 mm, PTFE: capacitance per metre and breakdown voltage?',
  'E field hits glass (εr 6) at 60° from air. Draw the refraction.',
];

export function mount() {
  const history = [];
  const log = h('div', { class: 'ai-log' });
  const input = h('textarea', { rows: 3, placeholder: 'Ask about a field, a medium or a device — e.g. "skin depth of copper at 10 MHz"' });
  const send = h('button', { class: 'btn primary', onclick: () => ask() }, 'Send');
  const status = h('div', { class: 'hint' });
  const panel = h('aside', { class: 'ai-panel', hidden: true },
    h('div', { class: 'ai-head' }, h('div', {}, h('b', {}, 'Assistant'), h('div', { class: 'hint', style: 'margin:0' }, 'Numbers come from the Python engine, not the model.')),
      h('button', { class: 'btn', onclick: () => toggle(false) }, 'Close')),
    log,
    h('div', { class: 'ai-input' }, input, h('div', { style: 'display:flex;justify-content:space-between;align-items:center' }, status, send)));
  const fab = h('button', { class: 'ai-fab', onclick: () => toggle(true) }, 'Ask the assistant');
  document.body.append(panel, fab);

  const intro = h('div', { class: 'ai-msg sys' }, h('p', {}, 'Describe what you want to see. The assistant chooses the solver and parameters, runs it, opens the chapter with the plots, and explains the result together with the verification status.'),
    h('div', { class: 'presets' }, EXAMPLES.map((e) => h('button', { class: 'btn', onclick: () => { input.value = e; ask(); } }, e))));
  log.append(intro);

  backend().then((m) => {
    if (m === 'server') return;
    // static build (GitHub Pages): no server-side key, so the assistant cannot run here.
    // The corner button opens the EM tutor instead, which runs in the browser without a key.
    fab.replaceWith(h('a', { class: 'ai-fab', href: '#/tutor' }, 'Ask the EM tutor'));
    intro.replaceChildren(h('p', {}, 'The assistant needs the local version of ElectroField, because it uses your own Anthropic API key on your computer. Everything else on this site — every solver, graph, derivation and check — runs here in your browser.'),
      h('p', { class: 'hint' }, 'Local version: download the repository, run Start_ElectroField.bat (or python run.py) and set ANTHROPIC_API_KEY.'));
    input.disabled = true; send.disabled = true;
  });
  input.addEventListener('keydown', (e) => { if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) ask(); });
  function toggle(on) { panel.hidden = !on; fab.hidden = on; if (on) input.focus(); }

  async function ask() {
    const text = input.value.trim();
    if (!text || send.disabled) return;
    input.value = '';
    history.push({ role: 'user', content: text });
    log.append(h('div', { class: 'ai-msg user' }, text));
    send.disabled = true; status.textContent = 'Working…';
    try {
      const r = await post('assistant', { messages: history }, 'ai');
      history.push({ role: 'assistant', content: r.reply });
      const msg = h('div', { class: 'ai-msg bot' }, ...r.reply.split(/\n{2,}/).map((p) => h('p', {}, p)));
      if (r.actions?.length) {
        msg.append(h('div', { class: 'ai-actions' }, r.actions.map((a) => h('button', { class: 'btn', onclick: () => openChapter(a.chapter, a.params) },
          `Open ${chapterTitle(a.chapter)}${a.params.tab ? ` · ${a.params.tab}` : ''}`, h('span', { class: a.all_passed ? 'pass' : 'fail' }, a.all_passed ? ' ✓ verified' : ' ✗ check failed')))));
        const last = r.actions[r.actions.length - 1];
        openChapter(last.chapter, last.params);
      }
      log.append(msg);
      status.textContent = '';
    } catch (e) {
      if (e.stale) return;
      history.pop();
      log.append(h('div', { class: 'ai-msg err' }, e.message));
      status.textContent = '';
    } finally {
      send.disabled = false;
      log.scrollTop = log.scrollHeight;
    }
  }
}
