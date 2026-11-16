// EM tutor — a free LLM plans and explains; the ElectroField engine does every computation.
//   1. plan:    the model returns JSON {calls:[{route, params}]} chosen from the engine's routes
//   2. compute: each call runs in the engine (local server or in-browser Pyodide) with its own checks
//   3. explain: the model writes the answer from the engine results only
//   4. audit:   every number in the answer is matched against the engine output; unmatched ones are flagged
import { h, tex, kv, si, sci, stepsTable, checksTable, layout, plotCfg, C } from '../ui.js';
import { api, post, backend } from '../api.js';
import { openChapter } from '../app.js';
import * as B from '../tutor-builtin.js';

// ---------------------------------------------------------------- providers (all have a free option)
const oai = (base, keyUrl, name, needsKey, pick) => ({
  name, keyUrl, needsKey, pick,
  async models(key) {
    const r = await fetch(`${base}/models`, { headers: key ? { Authorization: `Bearer ${key}` } : {} });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(j.error?.message || `HTTP ${r.status}`);
    return (j.data || j).map((m) => m.id || m.name).filter(Boolean);
  },
  async chat(key, model, system, msgs) {
    const r = await fetch(`${base}/chat/completions`, {
      method: 'POST', headers: { 'Content-Type': 'application/json', ...(key ? { Authorization: `Bearer ${key}` } : {}) },
      body: JSON.stringify({ model, temperature: 0.2, messages: [{ role: 'system', content: system }, ...msgs] }),
    });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(j.error?.message || j.message || `HTTP ${r.status}`);
    return j.choices?.[0]?.message?.content || '';
  },
});
const PROVIDERS = {
  builtin: { name: 'Built-in tutor — no key, always available (engine + formula templates)', needsKey: false, builtin: true,
    async models() { return ['engine templates']; }, pick: (ms) => ms[0] },
  gemini: {
    name: 'Google Gemini — free API key (recommended)', keyUrl: 'https://aistudio.google.com/apikey', needsKey: true,
    // text models only: stable "gemini-X.Y-flash" first (newest), then flash-lite; never tts/image/audio/live/embedding/gemma
    rank: (ms) => {
      const ok = ms.filter((m) => /^gemini-[\d.]+-flash(-lite)?(-\d+)?$/.test(m));
      const ver = (m) => parseFloat(m.match(/gemini-([\d.]+)/)[1]);
      return ok.sort((a, b) => (/lite/.test(a) - /lite/.test(b)) || ver(b) - ver(a));
    },
    pick(ms) { return this.rank(ms)[0] || ms.find((m) => /flash/.test(m) && !/tts|image|audio|live|embed|gemma/.test(m)); },
    async models(key) {
      const r = await fetch('https://generativelanguage.googleapis.com/v1beta/models?pageSize=200', { headers: { 'x-goog-api-key': key } });
      const j = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(j.error?.message || `HTTP ${r.status}`);
      return j.models.filter((m) => (m.supportedGenerationMethods || []).includes('generateContent')).map((m) => m.name.replace(/^models\//, ''));
    },
    async chat(key, model, system, msgs) {
      const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(model)}:generateContent`, {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'x-goog-api-key': key },
        body: JSON.stringify({ systemInstruction: { parts: [{ text: system }] }, generationConfig: { temperature: 0.2 },
          contents: msgs.map((m) => ({ role: m.role === 'assistant' ? 'model' : 'user', parts: [{ text: m.content }] })) }),
      });
      const j = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(j.error?.message || `HTTP ${r.status}`);
      return (j.candidates?.[0]?.content?.parts || []).map((p) => p.text || '').join('');
    },
  },
  groq: oai('https://api.groq.com/openai/v1', 'https://console.groq.com/keys', 'Groq — free API key', true,
    (ms) => ms.find((m) => /gpt-oss-120b/.test(m)) || ms.find((m) => /70b|qwen|gpt-oss/.test(m) && !/guard|whisper|tts/.test(m)) || ms[0]),
  openrouter: oai('https://openrouter.ai/api/v1', 'https://openrouter.ai/keys', 'OpenRouter — free models, free API key', true,
    (ms) => { const f = ms.filter((m) => m.endsWith(':free')); return f.find((m) => /deepseek|qwen|gpt-oss|llama-3\.3/.test(m)) || f[0]; }),
};
// (keyless services such as Pollinations now require a Cloudflare Turnstile token, so they cannot be called from a site)

// ---------------------------------------------------------------- engine routes the model may call
const ROUTES = {
  'waves/solve': 'uniform plane wave in a medium. params: f [Hz], eps_r, mu_r, sigma [S/m], E0 [V/m]. Gives alpha, beta, |eta|, skin depth, wavelength, phase velocity, power density and E/H along z.',
  'waves/sweep': 'how alpha, beta, |eta_c|, skin depth change with one parameter. params: param ("f"|"sigma"|"eps_r"|"mu_r"), lo, hi, and fixed f, eps_r, mu_r, sigma.',
  'dim/compare': '1-D (plane/transmission line) vs 2-D (cylindrical, line source) vs 3-D (spherical, point source) waves: spreading laws and what doubling f, eps_r, sigma or distance does. params: f, eps_r, mu_r, sigma, r_max_lambda.',
  'coords/element': 'differential length/area/volume elements. params: system ("cartesian"|"cylindrical"|"spherical"), u1,u2,u3 (point; angles in degrees), d1,d2,d3 (increments).',
  'coords/convert': 'convert a point (and vector A1..A3) between systems. params: src, dst, u1,u2,u3 (angles in degrees), A1,A2,A3 optional.',
  'es/charges': 'point charges in the plane z=0, field lines, equipotentials, E and V at a probe. params: charges [{q [C], x, y [m]}] (up to 8), ground (bool, grounded plane at y=0, all y>0), probe [x,y].',
  'es/gauss': 'Gauss law for symmetric charge. params: kind ("sphere" rho_v | "shell" rho_s | "line" rho_l | "cylinder" rho_v | "coax" rho_l | "sheet" rho_s | "slab" rho_v), rho, a, b, eps_r, r (field point).',
  'es/capacitor': 'capacitor C, Q, energy, max field, breakdown voltage. params: kind ("parallel": A, d | "coax": a, b, length | "spherical": a, b), V0, eps_r, E_bd [V/m].',
  'ms/wires': 'infinite wires perpendicular to the page (I>0 out of page): B lines, B at probe, force per metre. params: currents [{I [A], x, y}], probe [x,y].',
  'ms/loops': 'coaxial current loops (exact field): kind ("loop"|"helmholtz"|"solenoid"), I, a, N, length, pr, pz (probe rho,z).',
  'ms/ampere': 'Ampere law B(r): kind ("wire"|"tube"|"coax"|"toroid"|"solenoid"), I, a, b, c, N, n_per_m, mu_r, r.',
  'ms/inductance': 'inductance and stored energy: kind ("solenoid": N,a,length | "coax": a,b,length | "toroid": N,a,b,h | "twowire": a,d,length), I, mu_r.',
  'mx/boundary': 'boundary conditions at a planar interface. params: kind ("E"|"H"), eps1, eps2, mu1, mu2, F1 (|E1| or |H1|), theta1_deg (from normal), source (rho_s or Js_z), pec (bool).',
  'mx/faraday': 'induced EMF: mode ("motional" rotating loop | "transformer" fixed loop), B0 [T], f [Hz], w, l [m], N, R [ohm], alpha_deg.',
  'mx/currents': 'conduction vs displacement current, crossover frequency, charge relaxation time. params: eps_r, sigma, f.',
  'rf/normal': 'normal incidence on a planar interface (lossy allowed): Gamma, tau, SWR, R, T, standing wave. params: f, eps1, mu1, s1, eps2, mu2, s2.',
  'rf/oblique': 'oblique incidence (lossless): Snell, Fresnel TE/TM, Brewster, critical angle, R and T vs angle. params: eps1, mu1, eps2, mu2, theta_deg.',
  'tl/line': 'lossless transmission line: Gamma, VSWR, return loss, Z_in, standing wave, Smith chart, quarter-wave and stub matching. params: Z0, RL, XL, f, length [m], vf.',
  'ra/waveguide': 'rectangular waveguide: cut-off, beta, guide wavelength, velocities, impedance, mode list. params: a, b [m], eps_r, f, mode ("TE"|"TM"), m, n.',
  'ra/dipole': 'centre-fed dipole: pattern, radiation resistance, directivity, beamwidth. params: length_lambda (total length in wavelengths), I0, f.',
  'ra/array': 'uniform linear array: array factor, beam direction, directivity, grating lobes. params: N, d_lambda, delta_deg.',
};
const POST_ROUTES = new Set(['es/charges', 'ms/wires']);

const PLAN = `You are the planning step of ElectroField, an electromagnetics workbench for electrical-engineering students (Ulaby & Ravaioli, Cheng).
Decide which engine computations answer the user's latest request. Reply with ONE JSON object and nothing else (no prose, no code fences):
{"calls":[{"route":"<route>","params":{...}}],"topic":"<3-6 word title>"}
Rules:
- Use SI units in params: convert GHz→Hz, MHz→Hz, mm→m, cm→m, nC→C, µC/m³→C/m³. Angles in degrees.
- At most 3 calls. Choose the call that directly produces what was asked (a graph request needs a route that returns that curve).
- Use "calls": [] only when the request is purely conceptual (definitions, derivations, intuition) and needs no numbers.
- Only these routes exist:
${Object.entries(ROUTES).map(([k, v]) => `  ${k}: ${v}`).join('\n')}`;

const EXPLAIN = `You are ElectroField's electromagnetics tutor for electrical-engineering students. Answer in the same language as the user's question.
Everything you say must be consistent with Maxwell's equations, the constitutive relations and standard electromagnetic field theory (Ulaby & Ravaioli, Cheng); if the request contradicts physics, say so and explain why.
Hard rules:
- Use ONLY numerical values that appear in ENGINE RESULTS (you may round to 3–4 significant figures or change SI prefixes). Never invent, estimate or recall a numerical result. If a needed number was not computed, say which part of the site computes it.
- Write the governing formula in LaTeX ($...$ inline, $$...$$ on its own line), substitute the values, then give the result with units.
- Say how many independent checks the engine ran and whether they all passed.
- Explain the physics: what the result means, which regime applies, what would change if a key parameter increased.
- For a purely conceptual question: give the definition, the key equations in LaTeX and the intuition; do not state specific numerical results.
- Plain text with short paragraphs or "- " bullets, **bold** allowed, no HTML, at most about 250 words.`;

// ---------------------------------------------------------------- settings (per browser)
const store = {
  get(k, d) { try { const v = localStorage.getItem(`ef.tutor.${k}`); return v == null ? d : v; } catch { return d; } },
  set(k, v) { try { v == null ? localStorage.removeItem(`ef.tutor.${k}`) : localStorage.setItem(`ef.tutor.${k}`, v); } catch { /* storage blocked */ } },
};

export function render(view, ch) {
  const S = { provider: store.get('provider', 'builtin'), key: store.get('key', ''), model: store.get('model', ''), remember: store.get('key', '') !== '' };
  const history = [];
  const log = h('div', { class: 'tutor-log', 'aria-live': 'polite' });
  const status = h('p', { class: 'hint', role: 'status' });
  const provSel = h('select', { id: 'tutor-provider', onchange: () => { S.provider = provSel.value; store.set('provider', S.provider); S.model = ''; syncKey(); } });
  const keyIn = h('input', { id: 'tutor-key', type: 'password', autocomplete: 'off', placeholder: 'paste your free API key', value: S.key, onchange: () => { S.key = keyIn.value.trim(); if (S.remember) store.set('key', S.key); loadModels(); } });
  const rem = h('input', { id: 'tutor-remember', type: 'checkbox', checked: S.remember, onchange: () => { S.remember = rem.checked; store.set('key', S.remember ? S.key : null); } });
  const modelSel = h('select', { id: 'tutor-model', onchange: () => { S.model = modelSel.value; store.set('model', S.model); } });
  const keyLink = h('a', { target: '_blank', rel: 'noopener' });
  const keyRow = h('div');
  const q = h('textarea', { id: 'tutor-q', rows: 3, placeholder: 'e.g. "Plot how the skin depth of copper changes from 1 kHz to 10 GHz" or "Explain Gauss’s law with a coaxial cable"' });
  const ask = h('button', { class: 'btn primary', onclick: () => run() }, 'Ask');
  q.addEventListener('keydown', (e) => { if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) run(); });

  view.append(h('div', { class: 'eyebrow' }, 'AI'), h('h1', {}, ch.title),
    h('p', { class: 'lede' }, 'Ask for a graph, a formula or an explanation, in English or Turkish. The built-in tutor needs no key and always works: it reads the quantities in your question, runs the ElectroField engine with its independent checks and writes the answer from formula templates filled only with engine results. If you add your own free key, a language model can phrase the answer more freely — under the same rule: the engine computes, every number in the answer is matched against the engine output, and anything that does not match is flagged.'),
    h('div', { class: 'work' },
      h('div', { class: 'panel' },
        h('h2', { class: 'h3' }, 'Connection'),
        h('label', { for: 'tutor-provider', class: 'lbl' }, 'AI provider'), provSel,
        keyRow,
        h('label', { for: 'tutor-model', class: 'lbl' }, 'Model'), modelSel,
        status,
        h('p', { class: 'hint' }, 'Your key is sent only to the provider you choose, directly from this browser. It is stored only if you tick “remember”, and only in this browser.')),
      h('div', { class: 'figs' },
        h('div', { class: 'panel' }, h('label', { for: 'tutor-q', class: 'lbl' }, 'Your question'), q,
          h('div', { style: 'display:flex;gap:8px;flex-wrap:wrap;margin-top:8px' }, ask,
            ...['Plot α and β of sea water from 1 kHz to 10 GHz', 'Compare 1-D, 2-D and 3-D wave spreading at 2.4 GHz', 'Field of a dipole of ±2 nC charges 10 cm apart', 'Explain the Brewster angle and compute it for glass'].map((t) =>
              h('button', { class: 'btn', onclick: () => { q.value = t; run(); } }, t)))),
        log)));

  (async () => {
    const opts = Object.entries(PROVIDERS).map(([k, p]) => [k, p.name]);
    if ((await backend()) === 'server') opts.push(['claude', 'Claude via the local server (ANTHROPIC_API_KEY)']);
    provSel.replaceChildren(...opts.map(([k, n]) => h('option', { value: k, selected: k === S.provider }, n)));
    if (!opts.some(([k]) => k === S.provider)) S.provider = 'builtin';
    provSel.value = S.provider;
    syncKey();
  })();

  function syncKey() {
    const p = PROVIDERS[S.provider];
    keyRow.replaceChildren();
    if (p?.needsKey) {
      keyLink.href = p.keyUrl; keyLink.textContent = 'Get a free key';
      keyRow.append(h('label', { for: 'tutor-key', class: 'lbl' }, 'API key  ', keyLink), keyIn,
        h('label', { for: 'tutor-remember', style: 'display:flex;gap:6px;align-items:center;font-size:13px;margin-top:4px' }, rem, 'Remember key in this browser'));
    }
    loadModels();
  }
  async function loadModels() {
    const p = PROVIDERS[S.provider];
    if (!p) { modelSel.replaceChildren(h('option', {}, 'claude-opus-5-5 (server)')); status.textContent = ''; return; }
    if (p.needsKey && !S.key) { modelSel.replaceChildren(h('option', {}, '— enter a key first —')); status.textContent = ''; return; }
    status.textContent = 'Loading the provider’s current model list…';
    try {
      const ms = (await p.models(S.key)).sort();
      const usable = p.rank ? p.rank(ms) : ms;
      const best = S.model && usable.includes(S.model) ? S.model : p.pick(ms);   // ignore a remembered model that is not a text model
      modelSel.replaceChildren(...ms.map((m) => h('option', { value: m, selected: m === best }, m)));
      S.model = best || ms[0] || ''; status.textContent = ms.length ? `${ms.length} models available.` : 'No models returned.';
    } catch (e) {
      status.textContent = explainError(e);
    }
  }

  // on a free-tier quota error or an unsupported model, fall back to the next suitable model automatically
  async function llm(system, msgs) {
    const p = PROVIDERS[S.provider];
    const all = [...modelSel.options].map((o) => o.value);
    const order = [S.model, ...(p.rank ? p.rank(all) : []).filter((m) => m !== S.model)].filter(Boolean).slice(0, 4);
    let last;
    for (const m of order) {
      try {
        const out = await p.chat(S.key, m, system, msgs);
        if (m !== S.model) { S.model = m; modelSel.value = m; store.set('model', m); status.textContent = `Switched to ${m} (the previous model was unavailable on the free tier).`; }
        return out;
      } catch (e) {
        last = e;
        if (!/429|quota|rate|not enabled|not supported|not found|limit: 0/i.test(String(e.message))) throw e;
      }
    }
    throw last;
  }

  async function run() {
    const text = q.value.trim();
    if (!text || ask.disabled) return;
    const p = PROVIDERS[S.provider];
    if (p?.needsKey && !S.key) { status.textContent = 'Enter a free API key first — “Get a free key” above takes about a minute with a Google account.'; return; }
    ask.disabled = true; q.value = '';
    const turn = h('div', { class: 'tutor-turn' }, h('div', { class: 'ai-msg user' }, text));
    const body = h('div', { class: 'ai-msg bot' }, h('p', { class: 'hint' }, 'Planning…'));
    turn.append(body); log.prepend(turn);
    try {
      if (S.provider === 'claude') return await viaClaude(text, body);
      if (S.provider === 'builtin') return await viaBuiltin(text, body);
      // 1 · plan
      const recent = history.slice(-4);
      const raw = await llm(PLAN, [...recent, { role: 'user', content: text }]);
      const plan = parsePlan(raw);
      const calls = (plan.calls || []).filter((c) => ROUTES[c.route]).slice(0, 3);
      // 2 · compute
      body.replaceChildren(h('p', { class: 'hint' }, calls.length ? `Running ${calls.length} engine computation(s)…` : 'Conceptual question — no computation needed. Writing the explanation…'));
      const results = [];
      for (const c of calls) {
        try { results.push({ ...c, result: POST_ROUTES.has(c.route) ? await post(c.route, c.params || {}, `tutor${results.length}`) : await api(c.route, c.params || {}, `tutor${results.length}`) }); }
        catch (e) { results.push({ ...c, error: e.message }); }
      }
      // 3 · explain
      body.replaceChildren(h('p', { class: 'hint' }, 'Writing the answer from the engine results…'));
      const consts = await api('constants', {}, 'tutorK').catch(() => []);
      const ctx = results.length ? JSON.stringify(results.map(summary)) : 'none (conceptual question)';
      const answer = await llm(EXPLAIN, [...recent, { role: 'user', content: `QUESTION:\n${text}\n\nENGINE RESULTS:\n${ctx}\n\nPHYSICAL CONSTANTS:\n${JSON.stringify(consts.map((k) => [k.key, k.value, k.unit]))}` }]);
      history.push({ role: 'user', content: text }, { role: 'assistant', content: answer.slice(0, 2000) });
      // 4 · show + audit
      const pool = numbersOf(results, consts);
      body.replaceChildren(...md(answer), audit(answer, pool, results.length > 0),
        ...results.map((r) => engineCard(r)));
      typeset(body);
    } catch (e) {
      body.replaceChildren(h('p', { class: 'error' }, explainError(e)));
    } finally {
      ask.disabled = false;
    }
  }

  async function viaBuiltin(text, body) {
    const p = B.plan(text);
    body.replaceChildren(h('p', { class: 'hint' }, p.calls.length ? `Running ${p.calls.length} engine computation(s)…` : 'Looking up the explanation…'));
    const results = [];
    for (const c of p.calls) {
      try { results.push({ ...c, result: POST_ROUTES.has(c.route) ? await post(c.route, c.params, `tb${results.length}`) : await api(c.route, c.params, `tb${results.length}`) }); }
      catch (e) { results.push({ ...c, error: e.message }); }
    }
    const answer = B.answer(text, p, results);
    const consts = await api('constants', {}, 'tutorK').catch(() => []);
    const note = results.length ? audit(answer, numbersOf(results, consts), true)
      : h('p', { class: 'audit' }, p.concept ? 'Explanation from the built-in formula sheet; no numerical result was computed. Add values with units to get an engine-verified calculation.' : 'No computation was run.');
    body.replaceChildren(...md(answer), note, ...results.map((r) => engineCard(r)));
  }

  async function viaClaude(text, body) {
    history.push({ role: 'user', content: text });
    const r = await post('assistant', { messages: history }, 'tutorClaude');
    history.push({ role: 'assistant', content: r.reply });
    body.replaceChildren(...md(r.reply), ...(r.actions || []).map((a) => h('button', { class: 'btn', style: 'margin:6px 6px 0 0', onclick: () => openChapter(a.chapter, a.params) },
      `Open ${a.chapter} ${a.all_passed ? '✓ verified' : '✗ check failed'}`)));
    typeset(body);
  }
  return () => {};
}

// ---------------------------------------------------------------- helpers
function explainError(e) {
  const m = String(e?.message || e);
  if (e instanceof TypeError || /Failed to fetch|NetworkError/i.test(m)) return 'The provider could not be reached from this browser (network or CORS). Try another provider.';
  if (/429|quota|rate/i.test(m)) return `Rate limit reached on the free tier — wait a minute or switch provider. (${m})`;
  if (/401|403|API key|invalid/i.test(m)) return `The provider rejected the key. Check it, or create a new free key. (${m})`;
  return m;
}

function parsePlan(raw) {
  const s = String(raw).replace(/```(?:json)?/gi, '');
  const a = s.indexOf('{'), b = s.lastIndexOf('}');
  if (a < 0 || b < a) return { calls: [] };
  try { return JSON.parse(s.slice(a, b + 1)); } catch { return { calls: [] }; }
}

function summary(r) {
  if (r.error) return { route: r.route, params: r.params, error: r.error };
  const v = r.result.values ? Object.fromEntries(Object.entries(r.result.values).filter(([, x]) => !(Array.isArray(x) && x.length > 6))) : undefined;
  const extra = {};
  if (r.result.sensitivity) extra.sensitivity = r.result.sensitivity;
  if (r.result.match) extra.matching = r.result.match;
  if (r.result.modes) extra.modes = r.result.modes.slice(0, 6);
  if (r.result.forces) extra.forces_N_per_m = r.result.forces;
  if (r.result.boundaries) extra.regime_boundaries = r.result.boundaries;
  return { route: r.route, params: r.params, values: v, ...extra,
    steps: (r.result.steps || []).map((s) => ({ step: s.label, value: Array.isArray(s.value) && s.value.length > 4 ? undefined : s.value, unit: s.unit, note: s.note || undefined })),
    checks: (r.result.checks || []).map((c) => ({ check: c.label, passed: c.passed })), all_checks_passed: r.result.all_passed };
}

// every finite number the engine produced (scalars, small arrays), for the audit
function numbersOf(results, consts) {
  const out = [];
  const walk = (o, depth = 0) => {
    if (o == null || depth > 6) return;
    if (typeof o === 'number') { if (isFinite(o) && o !== 0) out.push(Math.abs(o)); return; }
    if (Array.isArray(o)) { if (o.length <= 12) o.forEach((x) => walk(x, depth + 1)); return; }
    if (typeof o === 'object') Object.entries(o).forEach(([k, v]) => { if (!['field', 'profile', 'grid', 'faces', 'edges', 'views', 'maps', 'pattern', 'sweep', 'dispersion', 'fsweep', 'r', 'profiles', 'equipotentials', 'field_lines', 'smith', 'axis', 't', 'Phi', 'emf', 'I'].includes(k)) walk(v, depth + 1); });
  };
  results.forEach((r) => {
    walk(r.result); walk(r.params);
    // numbers the engine itself wrote into its derivation formulas (e.g. η₂ = 251.2 inside a step)
    (r.result?.steps || []).forEach((s) => {
      for (const m of String(s.tex || '').matchAll(/(\d+(?:\.\d+)?)(?:\\times10\^\{(-?\d+)\})?/g)) {
        const v = parseFloat(m[1]) * 10 ** (m[2] ? parseInt(m[2]) : 0);
        if (v) out.push(v);
      }
    });
  });
  consts.forEach((k) => out.push(Math.abs(k.value)));
  return out;
}

const NUM = /(?<![\w.^_])(\d+(?:[.,]\d+)?)(?:\s*(?:×|x|\\times|\\cdot)\s*10\s*\^?\s*\{?\s*([−-]?\s*\d+)\s*\}?|[eE]([−-]?\d+))?/g;
function audit(answer, pool, computed) {
  const found = [], bad = [];
  const SUP = { '⁻': '-', '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9' };
  const plain = answer.replace(/10([⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+)/g, (_, s) => `10^{${[...s].map((c) => SUP[c]).join('')}}`)
    .replace(/\\frac|\\sqrt|_\{[^}]*\}|\^\{?2\}?(?!\d)|\^\{?3\}?(?!\d)/g, ' ');
  for (const m of plain.matchAll(NUM)) {
    const base = parseFloat(m[1].replace(',', '.')), exp = m[2] ?? m[3];
    const val = exp != null ? base * 10 ** parseInt(exp.replace(/[−\s]/g, (c) => (c === '−' ? '-' : ''))) : base;
    const digits = m[1].replace(/[^\d]/g, '').replace(/^0+/, '').length;
    if (!isFinite(val) || val === 0 || (exp == null && !/[.,]/.test(m[1]) && val <= 100) || digits < 2) continue;   // skip small integers, years-free text
    found.push(m[0]);
    const ok = pool.some((p) => [...Array(9).keys()].some((k) => { const s = 10 ** (3 * (k - 4)); return Math.abs(val * s - p) <= 0.006 * p; })
      || Math.abs(val / 100 - p) <= 0.006 * p || Math.abs(val * 100 - p) <= 0.006 * p);
    if (!ok) bad.push(m[0]);
  }
  if (!computed && !found.length) return h('p', { class: 'audit' }, 'Conceptual answer: no numerical claims. Open the matching chapter to compute and verify specific values.');
  if (!found.length) return h('p', { class: 'audit' }, 'Number check: the answer quotes no numerical results.');
  return bad.length
    ? h('p', { class: 'audit warn' }, `Number check: ${found.length - bad.length} of ${found.length} numbers match the engine output. Not produced by the engine — treat with caution: ${[...new Set(bad)].join(', ')}`)
    : h('p', { class: 'audit ok' }, `Number check: all ${found.length} numbers in this answer match the engine output.`);
}

// minimal, safe markdown: paragraphs, "- " lists, **bold**, $…$ and $$…$$ (text nodes only, no HTML)
function md(text) {
  const blocks = String(text).replace(/\r/g, '').split(/\n{2,}/);
  const out = [];
  for (const b of blocks) {
    if (/^\s*\$\$[\s\S]*\$\$\s*$/.test(b)) { out.push(h('div', { class: 'md-display' }, tex(b.trim().slice(2, -2), true))); continue; }
    const lines = b.split('\n');
    if (lines.every((l) => /^\s*[-*•]\s+/.test(l) || !l.trim())) {
      out.push(h('ul', {}, lines.filter((l) => l.trim()).map((l) => h('li', {}, ...inline(l.replace(/^\s*[-*•]\s+/, ''))))));
    } else out.push(h('p', {}, ...inline(lines.join(' ').replace(/^#+\s*/, ''))));
  }
  return out;
}
function inline(s) {
  const parts = [];
  const re = /\$\$([^$]+)\$\$|\$([^$\n]+)\$|\*\*([^*]+)\*\*/g;
  let last = 0, m;
  while ((m = re.exec(s))) {
    if (m.index > last) parts.push(s.slice(last, m.index));
    if (m[1] != null) parts.push(tex(m[1], true)); else if (m[2] != null) parts.push(tex(m[2])); else parts.push(h('b', {}, m[3]));
    last = re.lastIndex;
  }
  if (last < s.length) parts.push(s.slice(last));
  return parts;
}
function typeset() { /* tex() renders immediately once KaTeX is loaded */ }

// ---------------------------------------------------------------- engine result card: values, plot, derivation, checks, open chapter
const NAMES = { 'waves/solve': 'Plane wave', 'waves/sweep': 'Parameter sweep', 'dim/compare': '1-D / 2-D / 3-D comparison', 'coords/element': 'Differential element',
  'coords/convert': 'Coordinate conversion', 'es/charges': 'Point charges', 'es/gauss': "Gauss's law", 'es/capacitor': 'Capacitor', 'ms/wires': 'Parallel wires',
  'ms/loops': 'Current loops', 'ms/ampere': "Ampère's law", 'ms/inductance': 'Inductance', 'mx/boundary': 'Boundary conditions', 'mx/faraday': "Faraday's law",
  'mx/currents': 'Conduction vs displacement current', 'rf/normal': 'Normal incidence', 'rf/oblique': 'Oblique incidence', 'tl/line': 'Transmission line',
  'ra/waveguide': 'Rectangular waveguide', 'ra/dipole': 'Dipole antenna', 'ra/array': 'Linear array' };

function engineCard(c) {
  if (c.error) return h('div', { class: 'tutor-card' }, h('p', { class: 'error' }, `${NAMES[c.route] || c.route}: ${c.error}`));
  const r = c.result, v = r.values || {};
  const scal = Object.entries(v).filter(([, x]) => typeof x === 'number' || (x && typeof x === 'object' && 're' in x)).slice(0, 8)
    .map(([k, x]) => [k, typeof x === 'number' ? sci(x, 4) : sci(x, 4)]);
  const plot = quickPlot(c.route, r);
  const act = chapterFor(c.route, c.params || {});
  return h('div', { class: 'tutor-card' },
    h('div', { style: 'display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;align-items:center' },
      h('b', {}, NAMES[c.route] || c.route), !r.checks ? h('span', { class: 'note' }, 'sweep of the verified closed forms (open the chapter for the checks at a point)')
        : h('span', { class: r.all_passed ? 'pass' : 'fail' }, r.all_passed ? `✓ ${r.checks.length} independent checks passed` : '✗ a check failed')),
    h('p', { class: 'hint', style: 'margin:2px 0 8px' }, `engine route ${c.route} · ${Object.entries(c.params || {}).map(([k, x]) => `${k}=${typeof x === 'object' ? JSON.stringify(x) : x}`).join(', ')}`),
    scal.length ? kv(scal) : null, plot,
    r.steps ? h('details', {}, h('summary', {}, 'Derivation and checks'), stepsTable(r.steps), checksTable(r.checks || [])) : null,
    act ? h('button', { class: 'btn', style: 'margin-top:8px', onclick: () => openChapter(act.chapter, act.params) }, 'Open the full chapter with these values →') : null);
}

function quickPlot(route, r) {
  const el = h('div', { class: 'plot', style: 'height:300px', role: 'img', 'aria-label': `${NAMES[route] || route} graph` });
  const L = (x, y, name, color, extra = {}) => ({ x, y, name, mode: 'lines', line: { color, width: 2.2 }, ...extra });
  const env = (F) => F.re.map((a, i) => Math.hypot(a, F.im[i]));
  let tr = null, lay = {};
  switch (route) {
    case 'waves/solve': tr = [L(r.field.z, env(r.field.E), '|E| envelope', C.E), L(r.field.z, r.field.E.re, 'E_x(z, 0)', C.E, { line: { color: C.E, width: 1, dash: 'dot' } })];
      lay = { xaxis: { title: { text: 'z (m)' } }, yaxis: { title: { text: 'E (V/m)' } } }; break;
    case 'waves/sweep': tr = [L(r.x, r.alpha, 'α (Np/m)', C.E), L(r.x, r.beta, 'β (rad/m)', C.accent), L(r.x, r.skin_depth, 'δs (m)', C.H, { yaxis: 'y2' })];
      lay = { xaxis: { type: 'log', title: { text: r.param } }, yaxis: { type: 'log', title: { text: 'Np/m, rad/m' } }, yaxis2: { type: 'log', overlaying: 'y', side: 'right', title: { text: 'δs (m)' }, showgrid: false } }; break;
    case 'dim/compare': { const rl = r.r.map((x) => x / r.values.wavelength);
      tr = [L(rl, r.profiles['1D'].mag, '1-D', C.accent), L(rl, r.profiles['2D'].mag, '2-D', C.S), L(rl, r.profiles['3D'].mag, '3-D', C.E)];
      lay = { xaxis: { type: 'log', title: { text: 'r / λ' } }, yaxis: { type: 'log', title: { text: '|ψ| (normalised)' } } }; break; }
    case 'es/gauss': tr = [L(r.profile.r, r.profile.E, 'E', C.E), L(r.profile.r, r.profile.V, 'V', C.accent, { yaxis: 'y2' })];
      lay = { xaxis: { title: { text: 'distance (m)' } }, yaxis: { title: { text: 'E (V/m)' } }, yaxis2: { overlaying: 'y', side: 'right', title: { text: 'V (V)' }, showgrid: false } }; break;
    case 'es/capacitor': tr = [L(r.profile.s, r.profile.E, 'E', C.E)]; lay = { xaxis: { title: { text: 'position (m)' } }, yaxis: { title: { text: 'E (V/m)' } } }; break;
    case 'es/charges': case 'ms/wires': {
      const lines = r.field_lines || [];
      tr = [...lines.map((l) => ({ x: l.x, y: l.y, mode: 'lines', line: { color: C.ink, width: 1 }, hoverinfo: 'skip', showlegend: false })),
        ...(r.equipotentials || []).map((e) => ({ x: e.x, y: e.y, mode: 'lines', line: { color: e.V > 0 ? C.E : e.V < 0 ? C.H : C.ink3, width: 0.8 }, hoverinfo: 'skip', showlegend: false })),
        { x: (r.charges || r.wires).map((q) => q.x), y: (r.charges || r.wires).map((q) => q.y), mode: 'markers', marker: { size: 12, color: (r.charges || r.wires).map((q) => ((q.q ?? q.I) > 0 ? C.E : C.H)) }, showlegend: false }];
      lay = { hovermode: false, xaxis: { range: [-1, 1], constrain: 'domain', title: { text: 'x (m)' } }, yaxis: { scaleanchor: 'x', title: { text: 'y (m)' } } }; el.style.height = '380px'; break; }
    case 'ms/loops': tr = [L(r.axis.z, r.axis.Bz, 'B_z on axis', C.H)]; lay = { xaxis: { title: { text: 'z (m)' } }, yaxis: { title: { text: 'B_z (T)' } } }; break;
    case 'ms/ampere': tr = [L(r.profile.r, r.profile.B, 'B', C.H)]; lay = { xaxis: { title: { text: 'r (m)' } }, yaxis: { title: { text: 'B (T)' } } }; break;
    case 'mx/faraday': tr = [L(r.t, r.Phi, 'NΦ (Wb)', C.H), L(r.t, r.emf, 'emf (V)', C.E, { yaxis: 'y2' })];
      lay = { xaxis: { title: { text: 't (s)' } }, yaxis: { title: { text: 'NΦ (Wb)' } }, yaxis2: { overlaying: 'y', side: 'right', title: { text: 'V' }, showgrid: false } }; break;
    case 'mx/currents': tr = [L(r.sweep.f, r.sweep.ratio, '|Jc|/|Jd|', C.accent)]; lay = { xaxis: { type: 'log', title: { text: 'f (Hz)' } }, yaxis: { type: 'log', title: { text: 'σ/ωε' } } }; break;
    case 'rf/normal': tr = [L(r.field.z1, env(r.field.E1), '|E₁|', C.E), L(r.field.z2, env(r.field.E2), '|E₂|', C.H)]; lay = { xaxis: { title: { text: 'z (m)' } }, yaxis: { title: { text: '|E| (V/m)' } } }; break;
    case 'rf/oblique': tr = [L(r.sweep.theta, r.sweep.R_perp, 'R⊥', C.E), L(r.sweep.theta, r.sweep.R_par, 'R∥', C.H)]; lay = { xaxis: { title: { text: 'θi (°)' } }, yaxis: { title: { text: 'R' }, range: [0, 1.02] } }; break;
    case 'tl/line': tr = [L(r.profile.d, r.profile.V, '|V|', C.E), L(r.profile.d, r.profile.I, '|I|', C.H, { yaxis: 'y2' })];
      lay = { xaxis: { title: { text: 'distance from load (m)' }, autorange: 'reversed' }, yaxis: { title: { text: '|V| (V)' } }, yaxis2: { overlaying: 'y', side: 'right', title: { text: '|I| (A)' }, showgrid: false } }; break;
    case 'ra/waveguide': tr = Object.entries(r.dispersion.beta).map(([k, b], i) => L(r.dispersion.f, b, k, [C.E, C.H, C.S, C.accent, C.ink3][i % 5])); lay = { xaxis: { title: { text: 'f (Hz)' } }, yaxis: { title: { text: 'β (rad/m)' } } }; break;
    case 'ra/dipole': case 'ra/array': {
      const th = r.pattern.theta_deg, F = r.pattern.F || r.pattern.AF;
      tr = [{ type: 'scatterpolar', r: [...F, ...F.slice().reverse()], theta: [...th, ...th.slice().reverse().map((t) => 360 - t)], mode: 'lines', line: { color: C.accent, width: 2 }, fill: 'toself', fillcolor: 'rgba(31,78,121,0.12)' }];
      lay = { showlegend: false, polar: { bgcolor: 'rgba(0,0,0,0)', radialaxis: { range: [0, 1.02] }, angularaxis: { rotation: 90, direction: 'clockwise' } } }; el.style.height = '340px'; break; }
    default: return null;
  }
  setTimeout(() => Plotly.react(el, tr, layout(lay), plotCfg), 0);   // after the card is in the DOM (rAF stalls in background tabs)
  return el;
}

export function chapterFor(route, p) {
  const tab = (chapter, t, key = t) => ({ chapter, params: { tab: t, [key]: p } });
  switch (route) {
    case 'waves/solve': return { chapter: 'waves', params: p };
    case 'waves/sweep': { const { param, lo, hi, n, ...rest } = p; return { chapter: 'waves', params: rest }; }
    case 'dim/compare': return { chapter: 'dimensions', params: p };
    case 'coords/element': return { chapter: 'coordinates', params: { system: p.system, u: [p.u1, p.u2, p.u3], d: [p.d1, p.d2, p.d3] } };
    case 'coords/convert': return { chapter: 'coordinates', params: {} };
    case 'es/charges': return { chapter: 'electrostatics', params: { tab: 'charges', charges: { q: (p.charges || []).map((c) => [c.q / 1e-9, c.x, c.y]), ground: !!p.ground, probe: p.probe || [0, 0] } } };
    case 'es/gauss': return tab('electrostatics', 'gauss');
    case 'es/capacitor': return tab('electrostatics', 'capacitor');
    case 'ms/wires': return { chapter: 'magnetostatics', params: { tab: 'wires', wires: { W: (p.currents || []).map((w) => [w.I, w.x, w.y]), probe: p.probe || [0, 0.5] } } };
    case 'ms/loops': return tab('magnetostatics', 'loops');
    case 'ms/ampere': return tab('magnetostatics', 'ampere');
    case 'ms/inductance': return tab('magnetostatics', 'inductance');
    case 'mx/boundary': return tab('maxwell', 'boundary');
    case 'mx/faraday': return tab('maxwell', 'faraday');
    case 'mx/currents': return tab('maxwell', 'currents');
    case 'rf/normal': return tab('reflection', 'normal');
    case 'rf/oblique': return tab('reflection', 'oblique');
    case 'tl/line': return { chapter: 'tlines', params: p };
    case 'ra/waveguide': return tab('radiation', 'waveguide');
    case 'ra/dipole': return tab('radiation', 'dipole');
    case 'ra/array': return tab('radiation', 'array');
    case 'img/plane': return { chapter: 'images', params: { Q: (p.Q ?? 1e-9) / 1e-9, d: p.d ?? 0.4, eps_r: p.eps_r ?? 1 } };
    case 'img/corner': return { chapter: 'images', params: {} };
    case 'bs/segment': case 'bs/loop': case 'bs/square': return { chapter: 'biot', params: {} };
    default: return null;
  }
}
