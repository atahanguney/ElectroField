// Verification report — reference problem, theoretical (closed form), numerical (engine) and error per module.
import { h, tex, kv, sci, layout, plotCfg, C } from '../ui.js';
import { api } from '../api.js';

export function render(view, ch) {
  const out = h('div', {}, h('p', { class: 'hint' }, 'Running all reference cases with the engine…'));
  view.append(h('div', { class: 'eyebrow' }, 'VERIFICATION'), h('h1', {}, ch.title),
    h('p', { class: 'lede' }, 'Every module is run on reference problems whose answer is known in closed form. The theoretical value is evaluated directly from the textbook formula (plain arithmetic, no engine code); the numerical value is what the website computes. The table is regenerated each time this page opens.'),
    out);
  const fig = h('div', { class: 'plot', style: 'height:340px', role: 'img', 'aria-label': 'Relative error of each reference case on a logarithmic axis' });
  (async () => {
    let r;
    try { r = await api('report/run', {}, 'report'); } catch (e) { if (!e.stale) out.replaceChildren(h('p', { class: 'error' }, e.message)); return; }
    const rows = r.rows, nOk = rows.filter((x) => x.passed && x.engine_checks_passed).length;
    const maxErr = Math.max(...rows.map((x) => x.error_pct ?? 0));
    const csv = () => {
      const head = ['module', 'problem', 'theory', 'numeric', 'unit', 'error_pct', 'tolerance_pct', 'passed', 'reference'];
      const q = (s) => `"${String(s ?? '').replace(/"/g, '""')}"`;
      const body = rows.map((x) => [x.module, x.problem, x.theory, x.numeric, x.unit, x.error_pct ?? 0, x.tol_pct ?? '', x.passed, x.ref].map(q).join(','));
      const a = h('a', { href: URL.createObjectURL(new Blob([[head.join(','), ...body].join('\n')], { type: 'text/csv' })), download: 'electrofield-verification.csv' });
      document.body.append(a); a.click(); a.remove();
    };
    out.replaceChildren(
      h('div', { style: 'margin-bottom:8px' }, h('span', { class: 'badge' }, r.all_passed ? 'all reference cases pass' : 'some cases fail')),
      kv([['reference cases', `${rows.length}`], ['passed', `${nOk} / ${rows.length}`], ['modules', `${r.modules.length}`], ['largest error', `${sci(maxErr, 2)} %`]]),
      h('h2', {}, 'Summary by module'),
      h('div', { class: 'tablewrap' }, h('table', { class: 't' }, h('thead', {}, h('tr', {}, ['Module', 'Cases', 'Passed', 'Largest error'].map((x) => h('th', { scope: 'col' }, x)))),
        h('tbody', {}, r.modules.map((m) => h('tr', {}, h('td', {}, m.module), h('td', { class: 'num' }, m.cases), h('td', { class: m.passed === m.cases ? 'pass' : 'fail' }, `${m.passed} / ${m.cases}`),
          h('td', { class: 'num' }, `${sci(m.max_error_pct, 2)} %`)))))),
      h('div', { class: 'fig', style: 'margin-top:16px' }, fig, h('p', { class: 'cap' }, h('b', {}, 'Relative error per case. '),
        'Most cases agree to 10⁻¹⁴ %, i.e. floating-point round-off. The larger values are expected: the 2-D case compares with an asymptotic law, the generator with a sampled waveform, the dipole with a numerical integral. Dashes mark each case’s tolerance.')),
      h('h2', {}, 'All reference problems'),
      h('div', { style: 'margin:0 0 10px' }, h('button', { class: 'btn', onclick: csv }, 'Download CSV')),
      h('div', { class: 'tablewrap' }, h('table', { class: 't' },
        h('thead', {}, h('tr', {}, ['Module', 'Reference problem', 'Theory', 'Theoretical', 'Numerical', 'Error', 'Status', 'Source'].map((x) => h('th', { scope: 'col' }, x)))),
        h('tbody', {}, rows.map((x) => h('tr', {},
          h('td', { class: 'note' }, x.module), h('td', {}, x.problem), h('td', {}, tex(x.formula)),
          h('td', { class: 'num' }, `${sci(x.theory, 7)} ${x.unit}`), h('td', { class: 'num' }, `${sci(x.numeric, 7)} ${x.unit}`),
          h('td', { class: 'num' }, x.error_pct == null ? `|Δ| = ${sci(x.abs_error, 2)}` : `${sci(x.error_pct, 2)} %`),
          h('td', { class: x.passed && x.engine_checks_passed ? 'pass' : 'fail' }, x.passed && x.engine_checks_passed ? 'pass' : 'FAIL'),
          h('td', { class: 'note' }, x.ref)))))),
      h('p', { class: 'prose', style: 'margin-top:12px' }, 'Status “pass” requires both: the error is within the stated tolerance, and the engine’s own independent checks for that computation passed.'));
    const floor = 1e-15, mods = [...new Set(rows.map((x) => x.module))], cols = [C.accent, C.E, C.H, C.S, C.ink3];
    Plotly.react(fig, [
      ...mods.map((m, k) => {
        const sub = rows.map((x, i) => ({ x, i })).filter((o) => o.x.module === m);
        return { x: sub.map((o) => o.i + 1), y: sub.map((o) => Math.max(o.x.error_pct ?? floor, floor)), mode: 'markers', name: m,
          marker: { size: 9, color: cols[k % cols.length], symbol: k >= 5 ? 'diamond' : 'circle' }, text: sub.map((o) => o.x.problem), hovertemplate: '%{text}<br>%{y:.2e} %<extra></extra>' };
      }),
      { x: rows.map((_, i) => i + 1), y: rows.map((x) => x.tol_pct ?? null), mode: 'markers', name: 'tolerance', marker: { symbol: 'line-ew-open', size: 14, color: C.ink3 }, hoverinfo: 'skip' },
    ], layout({ hovermode: 'closest', xaxis: { title: { text: 'case' }, dtick: 1 }, yaxis: { type: 'log', title: { text: 'error (%)' }, exponentformat: 'power', range: [-15.5, 1] } }), plotCfg);
  })();
  return () => Plotly.purge(fig);
}
