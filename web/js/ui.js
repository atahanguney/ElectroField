// Small DOM/format helpers shared by all modules. No physics here.

export function h(tag, attrs = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k === 'class') el.className = v;
    else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
    else if (k === 'html') el.innerHTML = v;
    else el.setAttribute(k, v === true ? '' : v);
  }
  for (const c of kids.flat()) if (c != null && c !== false) el.append(c instanceof Node ? c : document.createTextNode(c));
  return el;
}

// KaTeX loads with `defer`; render now if ready, else when it arrives.
const pending = [];
export function tex(src, display = false) {
  const el = h('span', { class: display ? 'tex display' : 'tex' });
  const draw = () => window.katex.render(src, el, { throwOnError: false, displayMode: display });
  window.katex ? draw() : (el.textContent = src, pending.push(draw));
  return el;
}
window.addEventListener('load', () => { while (pending.length) pending.shift()(); });

// ---------- numbers ----------
const PREFIX = { p: -12, n: -9, u: -6, 'µ': -6, m: -3, k: 3, M: 6, G: 9, T: 12 };
export function parseSI(s) {
  s = String(s).trim().replace(',', '.');
  const m = s.match(/^([-+]?\d*\.?\d+(?:e[-+]?\d+)?)\s*([pnuµmkMGT]?)$/i);
  if (!m) return NaN;
  const p = m[2] ? PREFIX[m[2]] ?? PREFIX[m[2].toLowerCase()] : 0;
  return parseFloat(m[1]) * 10 ** p;
}
export function sci(x, sig = 4) {
  if (x == null) return '∞';
  if (typeof x === 'object') return `${sci(x.re, sig)} ${x.im < 0 ? '−' : '+'} j${sci(Math.abs(x.im), sig)}`;
  if (x === 0) return '0';
  const e = Math.floor(Math.log10(Math.abs(x)));
  if (e >= -2 && e <= 4) return (+x.toPrecision(sig)).toString();
  const m = x / 10 ** e;
  return `${m.toFixed(sig - 1)}×10${sup(e)}`;
}
const SUP = { '-': '⁻', 0: '⁰', 1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹' };
const sup = (e) => String(e).split('').map((c) => SUP[c]).join('');
export function si(x, unit = '', sig = 4) {
  if (x == null || !isFinite(x)) return `∞ ${unit}`;
  if (x === 0) return `0 ${unit}`;
  const steps = [[1e12, 'T'], [1e9, 'G'], [1e6, 'M'], [1e3, 'k'], [1, ''], [1e-3, 'm'], [1e-6, 'µ'], [1e-9, 'n'], [1e-12, 'p']];
  for (const [f, p] of steps) if (Math.abs(x) >= f) return `${(+(x / f).toPrecision(sig))} ${p}${unit}`;
  return `${sci(x, sig)} ${unit}`;
}

// ---------- controls ----------
/** Slider + text field. log=true uses a log10 slider; text accepts SI prefixes (2.45G). */
export function control({ label, texLabel, unit = '', value, min, max, log = false, step, onchange }) {
  const toS = (v) => (log ? Math.log10(v) : v), fromS = (s) => (log ? 10 ** s : s);
  const range = h('input', { type: 'range', min: toS(min), max: toS(max), step: step ?? (log ? 0.01 : (max - min) / 400), value: toS(value) });
  const text = h('input', { type: 'text', value: fmtIn(value) });
  const wrap = h('div', { class: 'ctl' },
    h('label', {}, h('span', {}, texLabel ? tex(texLabel) : label, texLabel && label ? ` ${label}` : ''), h('span', { class: 'unit' }, unit)),
    h('div', { class: 'row' }, range, text));
  let v = value;
  const set = (nv, from) => {
    v = nv;
    if (from !== 'range') range.value = toS(Math.min(Math.max(nv, min), max));
    if (from !== 'text') text.value = fmtIn(nv);
    text.classList.remove('invalid');
    onchange && onchange(v);
  };
  range.addEventListener('input', () => set(fromS(+range.value), 'range'));
  text.addEventListener('change', () => {
    const p = parseSI(text.value);
    isFinite(p) ? set(p, 'text') : text.classList.add('invalid');
  });
  return { el: wrap, get: () => v, set: (nv) => set(nv) };
}
function fmtIn(v) {
  if (v === 0) return '0';
  const a = Math.abs(v);
  return a >= 1e4 || a < 1e-3 ? v.toExponential(3).replace(/\.?0+e/, 'e') : String(+v.toPrecision(5));
}

export function segmented(options, value, onchange) {
  const el = h('div', { class: 'seg' });
  const btns = options.map(([key, text]) => h('button', {
    class: key === value ? 'on' : '', onclick: () => { btns.forEach((b) => b.classList.remove('on')); btn(key).classList.add('on'); onchange(key); },
  }, text));
  const btn = (k) => btns[options.findIndex((o) => o[0] === k)];
  el.append(...btns);
  return el;
}

// ---------- derivation & verification tables ----------
export function stepsTable(steps) {
  return h('div', { class: 'tablewrap' }, h('table', { class: 't' },
    h('thead', {}, h('tr', {}, h('th', {}, 'Step'), h('th', {}, 'Relation and substitution'), h('th', {}, 'Result'))),
    h('tbody', {}, steps.map((s) => h('tr', {},
      h('td', {}, s.label, s.note ? h('div', { class: 'note' }, s.note) : null),
      h('td', {}, tex(s.tex)),
      h('td', { class: 'num' }, s.value == null || Array.isArray(s.value) && s.value.length > 3 ? '' :
        Array.isArray(s.value) ? s.value.map((x) => sci(x)).join(', ') : `${sci(s.value)} ${s.unit}`))))));
}

export function checksTable(checks) {
  const ok = checks.every((c) => c.passed);
  return h('div', { class: 'tablewrap' },
    h('table', { class: 't' },
      h('thead', {}, h('tr', {}, ['Identity / limit', 'Method', 'Reference', 'Computed', 'Rel. error', ''].map((x) => h('th', {}, x)))),
      h('tbody', {}, checks.map((c) => h('tr', {},
        h('td', {}, tex(c.label)), h('td', { class: 'note' }, c.method),
        h('td', { class: 'num' }, sci(c.reference, 6)), h('td', { class: 'num' }, sci(c.computed, 6)),
        h('td', { class: 'num' }, `${sci(c.rel_error, 2)} ≤ ${sci(c.tol, 1)}`),
        h('td', { class: c.passed ? 'pass' : 'fail' }, c.passed ? 'pass' : 'FAIL'))))),
    h('p', { class: 'verdict' }, ok ? `All ${checks.length} independent checks agree within tolerance.`
      : 'At least one check failed — treat these numbers with caution.'));
}

export function kv(pairs) {
  return h('div', { class: 'kv' }, pairs.map(([k, v]) => h('div', {}, h('div', { class: 'k' }, k), h('div', { class: 'v' }, v))));
}

// ---------- plotting ----------
const css = (n) => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
export const C = { get E() { return css('--E'); }, get H() { return css('--H'); }, get S() { return css('--S'); },
  get ink() { return css('--ink'); }, get ink3() { return css('--ink-3'); }, get rule() { return css('--rule'); },
  get accent() { return css('--accent'); }, get panel() { return css('--panel'); } };

export function layout(extra = {}) {
  const ax = { gridcolor: C.rule, zerolinecolor: C.rule, linecolor: C.ink3, ticks: 'outside', tickcolor: C.ink3,
    tickfont: { family: 'ui-monospace, Consolas, monospace', size: 11 }, titlefont: { size: 12.5 }, automargin: true };
  const base = { paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', font: { family: 'system-ui, Segoe UI, sans-serif', size: 12.5, color: C.ink },
    margin: { l: 60, r: 20, t: 10, b: 46 }, xaxis: { ...ax }, yaxis: { ...ax }, legend: { orientation: 'h', y: 1.08, x: 0, font: { size: 12 } },
    hovermode: 'x unified' };
  for (const [k, v] of Object.entries(extra)) base[k] = (typeof v === 'object' && !Array.isArray(v) && base[k]) ? { ...base[k], ...v } : v;
  return base;
}
/** Click anywhere inside a 2-D Plotly plot area → cb(x, y) in data coordinates. */
export function onPlotClick(fig, cb) {
  fig.addEventListener('click', (ev) => {
    const fl = fig._fullLayout, bb = fig.querySelector('.nsewdrag')?.getBoundingClientRect();
    if (!fl || !bb || ev.clientX < bb.left || ev.clientX > bb.right || ev.clientY < bb.top || ev.clientY > bb.bottom) return;
    cb(fl.xaxis.p2l(ev.clientX - bb.left), fl.yaxis.p2l(ev.clientY - bb.top));
  });
}
export const plotCfg = { displaylogo: false, responsive: true, scrollZoom: false, modeBarButtonsToRemove: ['lasso2d', 'select2d'] };
