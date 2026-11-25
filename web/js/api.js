// Client for the Python engine. Two interchangeable backends:
//   server  — local FastAPI (python run.py): fetch('api/...')
//   pyodide — static hosting (GitHub Pages): the same engine/*.py runs in the browser via Pyodide
// Both call engine/routes.py logic; tests/test_routes.py proves they return identical results.
// Latest-call-wins per key, so fast slider drags never render stale data.
const seq = {};
const PYODIDE = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/';
const ENGINE_BASE = new URL('../../engine/', import.meta.url).href;   // web/js/ → repo engine/, wherever the page is served from
const ENGINE_FILES = ['__init__.py', 'constants.py', 'derivation.py', 'coordinates.py', 'waves.py', 'electrostatics.py', 'magnetostatics.py',
  'maxwell.py', 'reflection.py', 'tlines.py', 'radiation.py', 'dimensions.py', 'questions.py', 'report.py', 'biot.py', 'images.py', 'worked.py', 'routes.py'];

let modeP = null;
/** 'server' when the local Python server answers, otherwise 'pyodide'. */
export function backend() {
  if (modeP) return modeP;
  modeP = (async () => {
    const forced = new URLSearchParams(location.search).get('backend');
    if (forced === 'pyodide' || forced === 'server') return forced;
    if (location.protocol === 'file:' || location.hostname.endsWith('github.io')) return 'pyodide';
    try {
      const r = await fetch('api/constants', { cache: 'no-store' });
      if (r.ok && (r.headers.get('content-type') || '').includes('json')) return 'server';
    } catch { /* fall through */ }
    return 'pyodide';
  })();
  return modeP;
}

// ---------- Pyodide backend
let pyP = null, pyDone = false;
/** true once the in-browser engine has finished loading in this tab */
export const engineReady = () => pyDone;
// Status box while the in-browser engine loads: step k of 3 with a bar (the steps are real, not a time estimate).
const STEPS = 3;
const banner = (() => {
  let el = null, text = null, bar = null;
  return (msg, step = 0) => {
    if (!msg) { el && el.remove(); el = null; return; }
    if (!el) {
      el = document.createElement('div'); el.className = 'engine-banner'; el.setAttribute('role', 'status');
      text = document.createElement('div');
      const track = document.createElement('div'); track.className = 'bar'; bar = document.createElement('i'); track.append(bar);
      el.append(text, track); document.body.append(el);
    }
    text.replaceChildren();
    if (step) { const s = document.createElement('span'); s.className = 'step'; s.textContent = `${step}/${STEPS}`; text.append(s); }
    text.append(msg);
    bar.parentElement.hidden = !step;
    bar.style.width = `${Math.round(((step - 1) / STEPS) * 100 + 100 / STEPS / 2)}%`;
  };
})();
function loadScript(src) {
  return new Promise((ok, bad) => { const s = document.createElement('script'); s.src = src; s.onload = ok; s.onerror = () => bad(new Error(`cannot load ${src}`)); document.head.append(s); });
}
function python() {
  if (pyP) return pyP;
  pyP = (async () => {
    try {
      banner('Downloading the Python runtime (first visit only: about 30 MB in total, then cached)…', 1);
      await loadScript(`${PYODIDE}pyodide.js`);
      const py = await window.loadPyodide({ indexURL: PYODIDE });
      banner('Downloading NumPy and SciPy…', 2);
      await py.loadPackage(['numpy', 'scipy', 'contourpy']);
      banner('Loading the ElectroField engine…', 3);
      py.FS.mkdirTree('/home/pyodide/engine');
      await Promise.all(ENGINE_FILES.map(async (f) => {
        const r = await fetch(ENGINE_BASE + f, { cache: 'no-cache' });
        if (!r.ok) throw new Error(`engine file ${f}: HTTP ${r.status}`);
        py.FS.writeFile(`/home/pyodide/engine/${f}`, await r.text());
      }));
      py.runPython('import sys\nif "/home/pyodide" not in sys.path: sys.path.insert(0, "/home/pyodide")');
      const fn = py.pyimport('engine.routes').call_json;
      banner(null);
      pyDone = true;
      return fn;
    } catch (e) {
      banner(`The in-browser engine could not start: ${e.message}. Reload the page, or run the local version (python run.py).`);
      pyP = null;
      throw e;
    }
  })();
  return pyP;
}
async function viaPython(path, params) {
  const fn = await python();
  await new Promise((r) => setTimeout(r, 0));   // let the UI paint before a long computation
  const out = JSON.parse(fn(path, JSON.stringify(params)));
  if ('error' in out) throw new Error(out.error);
  return out.ok;
}

// ---------- public API (same signatures as before)
export async function api(path, params = {}, key = path) {
  const id = (seq[key] = (seq[key] || 0) + 1);
  const clean = Object.fromEntries(Object.entries(params).filter(([, v]) => v != null));
  let body;
  if ((await backend()) === 'pyodide') {
    body = await viaPython(path, clean);
    if (id !== seq[key]) throw { stale: true };
    return body;
  }
  const r = await fetch(`api/${path}?${new URLSearchParams(clean)}`);
  body = await r.json();
  if (id !== seq[key]) throw { stale: true };
  if (!r.ok) throw new Error(body.error || body.detail || r.statusText);
  return body;
}
export async function post(path, body, key = path) {
  const id = (seq[key] = (seq[key] || 0) + 1);
  if ((await backend()) === 'pyodide') {
    if (path === 'assistant') throw new Error('The assistant runs only in the local version (python run.py), because it needs your own Anthropic API key.');
    const out = await viaPython(path, body);
    if (id !== seq[key]) throw { stale: true };
    return out;
  }
  const r = await fetch(`api/${path}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  const out = await r.json();
  if (id !== seq[key]) throw { stale: true };
  if (!r.ok) throw new Error(out.error || (Array.isArray(out.detail) ? out.detail.map((d) => d.msg).join('; ') : out.detail) || r.statusText);
  return out;
}
export function debounce(fn, ms = 120) {
  let t;
  return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); };
}
