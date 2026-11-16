// Router + table of contents. Chapters register here; `load` is a lazy import.
import { h, a11y } from './ui.js';
import { backend } from './api.js';

const CHAPTERS = [
  { group: 'Foundations' },
  { id: 'dimensions', n: '0', title: '1-D, 2-D and 3-D waves', blurb: 'Lines, cylinders, spheres: how geometry sets the spreading law and what each parameter changes.', load: () => import('./modules/dimensions.js') },
  { id: 'coordinates', n: '1', title: 'Vectors & coordinate systems', blurb: 'Cartesian, cylindrical, spherical; dl, ds, dv and how they scale.', load: () => import('./modules/coordinates.js') },
  { id: 'electrostatics', n: '2', title: 'Electrostatics', blurb: 'Coulomb, Gauss, potential, conductors, dielectrics, capacitance, images.', load: () => import('./modules/electrostatics.js') },
  { id: 'magnetostatics', n: '3', title: 'Magnetostatics', blurb: 'Biot–Savart, Ampère, vector potential, inductance, magnetic forces.', load: () => import('./modules/magnetostatics.js') },
  { group: 'Time-varying fields' },
  { id: 'maxwell', n: '4', title: "Maxwell's equations", blurb: 'Faraday, displacement current, boundary conditions, continuity.', load: () => import('./modules/maxwell.js') },
  { id: 'waves', n: '5', title: 'Plane waves in media', blurb: 'α, β, ηc, skin depth and power vs ε, μ, σ and f.', load: () => import('./modules/waves.js') },
  { id: 'reflection', n: '6', title: 'Reflection & transmission', blurb: 'Normal and oblique incidence, Fresnel, Brewster, total internal reflection.', load: () => import('./modules/reflection.js') },
  { id: 'tlines', n: '7', title: 'Transmission lines', blurb: 'Telegrapher, standing waves, Smith chart, matching.', load: () => import('./modules/tlines.js') },
  { id: 'radiation', n: '8', title: 'Waveguides & antennas', blurb: 'TE/TM modes, cut-off, dipole radiation, arrays.', load: () => import('./modules/radiation.js') },
  { group: 'Practice' },
  { id: 'questions', n: 'Q', title: 'Question bank', blurb: 'Randomised problems in textbook style; answers solved and verified by the engine.', load: () => import('./modules/questions.js') },
  { id: 'tutor', n: 'AI', title: 'EM tutor (AI)', blurb: 'Ask for a graph, a formula or an explanation; the AI plans, the engine computes and verifies.', load: () => import('./modules/tutor.js') },
  { id: 'report', n: 'V', title: 'Verification report', blurb: 'Reference problem, theoretical result, numerical result and error for every module.', load: () => import('./modules/report.js') },
];
const live = (c) => c.load;

function toc(active) {
  const nav = document.getElementById('toc');
  nav.replaceChildren(...CHAPTERS.map((c) => c.group ? h('div', { class: 'grp' }, c.group)
    : live(c) ? h('a', { href: `#/${c.id}`, class: c.id === active ? 'active' : '', 'aria-current': c.id === active ? 'page' : null }, h('span', { class: 'num', 'aria-hidden': 'true' }, c.n), c.title)
      : h('span', {}, h('span', { class: 'num' }, c.n), h('span', {}, c.title, h('span', { class: 'soon' }, 'in progress')))));
}

let cleanup = null, pendingInit = null;

/** Open a chapter with initial parameters (used by the assistant). */
export function openChapter(id, init = {}) {
  pendingInit = init;
  if (location.hash === `#/${id}`) route(); else location.hash = `#/${id}`;
}
export const chapterTitle = (id) => CHAPTERS.find((c) => c.id === id)?.title || id;

// Plotly (3.5 MB) is loaded only when a page with plots opens: from the local server if present, else the pinned CDN build
let plotlyP = null;
const plotly = () => window.Plotly ? Promise.resolve() : (plotlyP ||= backend().then((m) => new Promise((ok) => {
  const s = document.createElement('script');
  s.src = m === 'server' ? 'vendor/plotly.min.js' : 'https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2/plotly.min.js';
  s.onload = ok; s.onerror = ok; document.head.append(s);
})));

async function route() {
  const raw = location.hash;
  if (raw && !raw.startsWith('#/')) {   // in-page anchor such as the skip link: move focus, keep the page
    document.getElementById(raw.slice(1))?.focus();
    return;
  }
  const id = raw.replace(/^#\/?/, '').split('/')[0];
  const view = document.getElementById('view');
  cleanup && cleanup(); cleanup = null;
  toc(id);
  const ch = CHAPTERS.find((c) => c.id === id && live(c));
  if (!ch) {
    view.replaceChildren();
    document.title = 'ElectroField — applied electromagnetics, computed and verified';
    (await import('./home.js')).home(view, CHAPTERS); window.scrollTo(0, 0); return;
  }
  await plotly();
  view.replaceChildren();
  document.title = `${ch.title} · ElectroField`;
  const mod = await ch.load();
  const init = pendingInit || {}; pendingInit = null;
  cleanup = mod.render(view, ch, init) || null;
  window.scrollTo(0, 0);
}
window.addEventListener('hashchange', route);
route();
// name every control, label icon buttons, give plots an image role — for content rendered now and later
{
  let t = 0;
  const run = () => { clearTimeout(t); t = setTimeout(() => a11y(document.body), 60); };
  new MutationObserver(run).observe(document.body, { childList: true, subtree: true });
  run();
}
import('./assistant.js').then((m) => m.mount());
