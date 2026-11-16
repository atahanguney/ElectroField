// Built-in EM tutor: no API key, no language model, always available.
// It reads the question (English or Turkish), extracts quantities with units, chooses engine routes,
// and writes the answer from templates filled ONLY with engine results — so it cannot invent a number.
import { sci, si } from './ui.js';

const R = String.raw;
const PFX = { p: 1e-12, n: 1e-9, 'µ': 1e-6, 'μ': 1e-6, u: 1e-6, m: 1e-3, c: 1e-2, k: 1e3, K: 1e3, M: 1e6, G: 1e9, T: 1e12 };
const UNITS = { hz: 'Hz', m: 'm', f: 'F', h: 'H', c: 'C', v: 'V', a: 'A', 'ω': 'Ω', ohm: 'Ω', 's/m': 'S/m', t: 'T', '°': '°', deg: '°', derece: '°', 'λ': 'λ', lambda: 'λ', db: 'dB' };

// ---------------------------------------------------------------- quantities
export function quantities(text) {
  const out = [];
  const re = /(-?\d+(?:[.,]\d+)?(?:e[-+]?\d+)?)(?:\s*(?:×|x|\*)\s*10\s*\^\s*\(?(-?\d+)\)?)?\s*([a-zA-Zµμ°ΩλΩ/]+)?/g;
  for (const m of text.matchAll(re)) {
    let v = parseFloat(m[1].replace(',', '.'));
    if (m[2]) v *= 10 ** parseInt(m[2]);
    const u = (m[3] || '').replace(/[.,;:)]$/, '');
    const lu = u.toLowerCase();
    let unit = null, mult = 1;
    if (UNITS[lu] && !(u.length === 1 && /[TMGKk]/.test(u) && !['T'].includes(u))) unit = UNITS[lu];
    else if (u.length > 1 && PFX[u[0]] && UNITS[u.slice(1).toLowerCase()]) { mult = PFX[u[0]]; unit = UNITS[u.slice(1).toLowerCase()]; }
    if (unit === 'T' && u === 'T' && /[a-z]/i.test(text[m.index + m[0].length] || '')) unit = null;
    out.push({ v: v * mult, unit, raw: m[0].trim(), index: m.index });
  }
  return out;
}
const byUnit = (qs, u) => qs.filter((q) => q.unit === u).map((q) => q.v);
function named(text, names) {   // e.g. "εr = 4", "a = 2 mm", "N=100"
  for (const n of names) {
    const m = text.match(new RegExp(`(?:^|[\\s,(])${n}\\s*[=:]\\s*(-?[\\d.,]+(?:e[-+]?\\d+)?\\s*[a-zA-Zµμ°Ω/]*)`, 'i'));
    if (m) { const q = quantities(m[1])[0]; if (q) return q.v; }
  }
  return undefined;
}

const MATERIALS = [
  [/copper|bakır/, { eps_r: 1, mu_r: 1, sigma: 5.8e7, name: 'copper' }],
  [/alumin/, { eps_r: 1, mu_r: 1, sigma: 3.5e7, name: 'aluminium' }],
  [/silver|gümüş/, { eps_r: 1, mu_r: 1, sigma: 6.2e7, name: 'silver' }],
  [/gold|altın/, { eps_r: 1, mu_r: 1, sigma: 4.1e7, name: 'gold' }],
  [/iron|demir/, { eps_r: 1, mu_r: 4000, sigma: 1e7, name: 'iron (low field)' }],
  [/sea ?water|deniz suyu|deniz/, { eps_r: 81, mu_r: 1, sigma: 4, name: 'sea water' }],
  [/fresh water|tatlı su|\bwater\b|\bsu\b|\bsuda\b|\bsuya\b/, { eps_r: 80, mu_r: 1, sigma: 1e-3, name: 'fresh water' }],
  [/glass|\bcam\b|cama|camda/, { eps_r: 2.25, mu_r: 1, sigma: 0, name: 'glass (n = 1.5)' }],
  [/teflon|ptfe/, { eps_r: 2.1, mu_r: 1, sigma: 0, name: 'PTFE' }],
  [/fr-?4/, { eps_r: 4.4, mu_r: 1, sigma: 0, name: 'FR-4' }],
  [/muscle|\bkas\b/, { eps_r: 52.7, mu_r: 1, sigma: 1.74, name: 'muscle tissue (2.45 GHz)' }],
  [/soil|toprak/, { eps_r: 3, mu_r: 1, sigma: 1e-4, name: 'dry soil' }],
  [/\bair\b|\bhava\b|vacuum|vakum|free space|boşluk/, { eps_r: 1, mu_r: 1, sigma: 0, name: 'free space' }],
];
const materials = (t) => MATERIALS.filter(([re]) => re.test(t)).map(([, m]) => m);

// ---------------------------------------------------------------- planning
export function plan(question) {
  const t = question.toLowerCase();
  const qs = quantities(question);
  const tr = /[çğıöşü]|nedir|nasıl|açıkla|hesapla|grafi|neden|kaç/.test(t);
  const f = byUnit(qs, 'Hz'), len = byUnit(qs, 'm'), ang = byUnit(qs, '°'), cur = byUnit(qs, 'A'), chg = byUnit(qs, 'C'), lam = byUnit(qs, 'λ');
  const mats = materials(t);
  const turns = (() => { const m = t.match(/(\d+)\s*(?:turns?|sarım|sarim|tur\b|windings?)/); return m ? +m[1] : named(question, ['n']); })();
  const epsN = named(question, ['εr', 'ε_r', 'eps_?r', 'epsilon_?r', 'er']), muN = named(question, ['μr', 'μ_r', 'mu_?r', 'ur']);
  const sigN = named(question, ['σ', 'sigma', 'iletkenlik']) ?? byUnit(qs, 'S/m')[0];
  const med = { eps_r: epsN ?? mats[0]?.eps_r ?? 1, mu_r: muN ?? mats[0]?.mu_r ?? 1, sigma: sigN ?? mats[0]?.sigma ?? 0 };
  const assumed = [];
  const need = (v, d, what) => (v === undefined || Number.isNaN(v) ? (assumed.push(what), d) : v);
  const calls = [];
  const z = question.match(/(\d+(?:[.,]\d+)?)\s*([+-−])\s*j\s*(\d+(?:[.,]\d+)?)/i);
  const has = (re) => re.test(t);
  const conceptual = has(/\b(what is|explain|why|derive|meaning|define|nedir|açıkla|neden|niçin|türet|anlat|ne demek)\b/) && qs.filter((q) => q.unit).length === 0;

  if (has(/brewster/)) calls.push({ route: 'rf/oblique', params: { eps1: 1, eps2: need(epsN ?? mats.find((m) => m.eps_r > 1)?.eps_r, 2.25, 'εr₂ = 2.25 (glass)'), theta_deg: 30 }, key: 'theta_B' });
  else if (has(/critical angle|kritik açı|total internal|tam iç yansıma/)) calls.push({ route: 'rf/oblique', params: { eps1: need(epsN ?? mats.find((m) => m.eps_r > 1)?.eps_r, 2.25, 'εr₁ = 2.25 (glass)'), eps2: 1, theta_deg: 30 }, key: 'theta_c' });
  else if (z || has(/vswr|\bswr\b|smith|return loss|duran dalga|quarter-?wave|çeyrek dalga|\bstub\b|matching|uydurma|transmission line|iletim hatt|z_?0|characteristic impedance|karakteristik empedans/)) {
    const rest = z ? question.replace(z[0], ' ') : question;           // remove the complex load before reading Z0
    const ohms = byUnit(quantities(rest), 'Ω');
    const Z0 = named(question, ['z0', 'z_0', 'zo']) ?? (z ? ohms[0] : ohms.length > 1 ? ohms[ohms.length - 1] : undefined);
    const RL = z ? parseFloat(z[1].replace(',', '.')) : named(question, ['rl', 'r_l', 'zl', 'z_l']) ?? byUnit(qs, 'Ω')[0];
    const XL = z ? (z[2] === '+' ? 1 : -1) * parseFloat(z[3].replace(',', '.')) : named(question, ['xl', 'x_l']) ?? 0;
    calls.push({ route: 'tl/line', params: { Z0: need(Z0, 50, 'Z₀ = 50 Ω'), RL: need(RL, 100, 'R_L = 100 Ω'), XL, f: f[0] ?? 1e9, length: len[0] ?? 0.3, vf: 1 }, key: 'S' });
  } else if (has(/reflect|yansı|transmi|geçen güç|normal incidence|dik geliş/)) {
    const m2 = mats.find((m) => m.name !== 'free space') || { eps_r: epsN ?? 2.25, sigma: sigN ?? 0, mu_r: 1 };
    calls.push({ route: 'rf/normal', params: { f: f[0] ?? need(undefined, 1e9, 'f = 1 GHz'), eps2: m2.eps_r, s2: m2.sigma, mu2: m2.mu_r }, key: 'R' });
  } else if (has(/waveguide|dalga kılavuz|wr-?\d+|\bte\d\d|\btm\d\d|cut-?off|kesim frekans/)) {
    const mode = (t.match(/\b(te|tm)(\d)(\d)/) || [null, 'te', '1', '0']);
    const isWR90 = has(/wr-?90/) || !len.length;
    if (isWR90 && !has(/wr-?90/)) assumed.push('WR-90: a = 22.86 mm, b = 10.16 mm');
    calls.push({ route: 'ra/waveguide', params: { a: len[0] ?? 22.86e-3, b: len[1] ?? (len[0] ? len[0] / 2 : 10.16e-3), eps_r: med.eps_r, f: f[0] ?? need(undefined, 10e9, 'f = 10 GHz'), mode: mode[1].toUpperCase(), m: +mode[2], n: +mode[3] }, key: 'fc' });
  } else if (has(/dipole antenna|dipol anten|half-?wave|yarım dalga|radiation resistance|ışıma direnci|\bantenna\b|\banten\b/) && !has(/array|dizi/)) {
    calls.push({ route: 'ra/dipole', params: { length_lambda: lam[0] ?? (has(/short|kısa|hertz/) ? 0.05 : 0.5), I0: cur[0] ?? 1, f: f[0] ?? 100e6 }, key: 'R_rad' });
  } else if (has(/array|dizi/)) {
    const N = named(question, ['n']) ?? (qs.find((q) => !q.unit && Number.isInteger(q.v) && q.v > 1)?.v);
    calls.push({ route: 'ra/array', params: { N: need(N, 8, 'N = 8 elements'), d_lambda: lam[0] ?? need(undefined, 0.5, 'd = λ/2'), delta_deg: ang[0] ?? 0 }, key: 'theta0' });
  } else if (has(/image|görüntü|grounded plane|topraklı|ground plane/)) {
    calls.push({ route: 'img/plane', params: { Q: chg[0] ?? need(undefined, 1e-9, 'Q = 1 nC'), d: len[0] ?? need(undefined, 0.4, 'd = 0.4 m'), eps_r: med.eps_r }, key: 'F' });
  } else if (has(/biot|savart|finite wire|sonlu tel|wire segment|tel parça/)) {
    const L = len.length > 1 ? len[0] : 1, r = len.length > 1 ? len[1] : len[0];
    calls.push({ route: 'bs/segment', params: { I: cur[0] ?? need(undefined, 1, 'I = 1 A'), z1: -L / 2, z2: L / 2, r: need(r, 0.2, 'r = 0.2 m'), N: 200 }, key: 'H' });
  } else if (has(/helmholtz|solenoid|selenoid|current loop|akım halka|halkanın|\bloop\b|halka/)) {
    const kind = has(/helmholtz/) ? 'helmholtz' : has(/solenoid|selenoid/) ? 'solenoid' : 'loop';
    calls.push({ route: 'ms/loops', params: { kind, I: cur[0] ?? 1, a: len[0] ?? need(undefined, 0.1, 'a = 0.1 m'), N: turns ?? 10, length: len[1] ?? 0.3 }, key: 'B_center' });
  } else if (has(/inductance|endüktans|indüktans/)) {
    const kind = has(/coax|koaks/) ? 'coax' : has(/toroid/) ? 'toroid' : has(/two-?wire|iki telli|çift tel/) ? 'twowire' : 'solenoid';
    calls.push({ route: 'ms/inductance', params: { kind, N: turns ?? 100, a: len[0] ?? 1e-3, b: len[1] ?? 3e-3, d: len[1] ?? 0.05, length: len[2] ?? 1, mu_r: med.mu_r }, key: 'L' });
  } else if (has(/capacit|kapasit|kondansat|sığa/)) {
    const kind = has(/coax|koaks/) ? 'coax' : has(/spher|küresel/) ? 'spherical' : 'parallel';
    const p = kind === 'parallel' ? { A: byUnit(qs, 'm²')[0] ?? named(question, ['a']) ?? need(undefined, 1e-4, 'A = 1 cm²'), d: len[0] ?? need(undefined, 1e-3, 'd = 1 mm') }
      : { a: len[0] ?? need(undefined, 0.45e-3, 'a = 0.45 mm'), b: len[1] ?? need(undefined, 1.47e-3, 'b = 1.47 mm'), length: 1 };
    calls.push({ route: 'es/capacitor', params: { kind, ...p, eps_r: med.eps_r, V0: byUnit(qs, 'V')[0] ?? 1 }, key: 'C' });
  } else if (has(/force|kuvvet|parallel wires|paralel tel/) && cur.length) {
    const d = len[0] ?? need(undefined, 0.1, 'd = 0.1 m');
    calls.push({ route: 'ms/wires', params: { currents: [{ I: cur[0], x: -d / 2, y: 0 }, { I: cur[1] ?? cur[0], x: d / 2, y: 0 }], probe: [0, d] }, key: 'force' });
  } else if (has(/gauss|sphere|küre|line charge|çizgi yük|sheet|levha|slab/)) {
    const kind = has(/shell|kabuk/) ? 'shell' : has(/line|çizgi/) ? 'line' : has(/sheet|levha/) ? 'sheet' : has(/coax|koaks/) ? 'coax' : has(/cylind|silindir/) ? 'cylinder' : 'sphere';
    const rho = chg[0] ?? 1e-6;
    calls.push({ route: 'es/gauss', params: { kind, rho, a: len[0] ?? 0.1, r: len[1] ?? 0.05, b: len[2] ?? 0.3, eps_r: med.eps_r }, key: 'E' });
  } else if (chg.length || has(/point charge|nokta yük|coulomb|electric dipole|elektrik dipol/)) {
    const q = chg.length ? chg : [1e-9, -1e-9];
    const d = len[0] ?? 0.2;
    const charges = q.length === 1 ? [{ q: q[0], x: 0, y: 0 }] : q.slice(0, 2).map((v, i) => ({ q: v, x: i ? d / 2 : -d / 2, y: 0 }));
    calls.push({ route: 'es/charges', params: { charges, probe: [0.3 * d + 0.1, len[1] ?? 0.4 * d + 0.1] }, key: 'E_mag' });
  } else if (has(/faraday|emf|generator|jenerat|indüklen/)) {
    calls.push({ route: 'mx/faraday', params: { mode: has(/transformer|transformatör|fixed loop|sabit/) ? 'transformer' : 'motional', B0: byUnit(qs, 'T')[0] ?? 0.2, f: f[0] ?? 50, w: len[0] ?? 0.1, l: len[1] ?? 0.2, N: turns ?? 1, R: byUnit(qs, 'Ω')[0] ?? 1 }, key: 'V_peak' });
  } else if (has(/boundary|sınır koşul|refraction of (the )?field|alan çizgilerinin kırılması/)) {
    const e = qs.filter((q) => !q.unit && q.v >= 1).map((q) => q.v);
    calls.push({ route: 'mx/boundary', params: { kind: has(/magnetic|manyetik|\bh\b/) ? 'H' : 'E', eps1: e[0] ?? 1, eps2: e[1] ?? 4, F1: byUnit(qs, 'V')[0] ?? 10, theta1_deg: ang[0] ?? 40 }, key: 'theta2_deg' });
  } else if (has(/displacement|deplasman|conduction current|iletim akım|relaxation|durulma/)) {
    calls.push({ route: 'mx/currents', params: { eps_r: med.eps_r === 1 && mats.length === 0 ? 81 : med.eps_r, sigma: med.sigma || 4, f: f[0] ?? 1e6 }, key: 'fc' });
  } else if (has(/1-?d|2-?d|3-?d|spreading|yayılım|boyut|cylindrical wave|spherical wave|silindirik dalga|küresel dalga/)) {
    calls.push({ route: 'dim/compare', params: { f: f[0] ?? 1e9, eps_r: med.eps_r, sigma: med.sigma }, key: 'level_3D' });
  } else if (has(/skin|deri kalınlı|nüfuz|penetrat|attenuat|zayıfla|plane wave|düzlem dalga|wavelength|dalga boyu|intrinsic|phase velocity|faz hızı|propagation|yayılma/) || mats.length) {
    if (f.length >= 2 || has(/sweep|from .* to|arasında|vs\.? frequency|frekansa göre/)) {
      calls.push({ route: 'waves/sweep', params: { param: 'f', lo: Math.min(...(f.length >= 2 ? f : [1e3])), hi: Math.max(...(f.length >= 2 ? f : [1e10])), ...med }, key: null });
    }
    calls.push({ route: 'waves/solve', params: { f: f[0] ?? need(undefined, 1e6, 'f = 1 MHz'), ...med }, key: has(/skin|deri|nüfuz|penetrat/) ? 'skin_depth' : has(/wavelength|dalga boyu/) ? 'wavelength' : 'alpha' });
  } else if (has(/coordinate|koordinat|volume element|hacim eleman|\bdv\b|scale factor|ölçek çarpan/)) {
    const sys = has(/cylind|silindir/) ? 'cylindrical' : has(/cartes|kartezyen/) ? 'cartesian' : 'spherical';
    calls.push({ route: 'coords/element', params: { system: sys, u1: len[0] ?? 1.5, u2: ang[0] ?? (sys === 'cylindrical' ? 30 : 50), u3: sys === 'spherical' ? ang[1] ?? 30 : len[1] ?? 0.3, d1: 0.1, d2: 10, d3: sys === 'spherical' ? 10 : 0.1 }, key: 'dv' });
  }
  const concept = KB.find((k) => k.re.test(t));
  return { calls: conceptual && concept ? [] : calls.slice(0, 2), concept, tr, assumed, conceptual };
}

// ---------------------------------------------------------------- answer
const WHATIF = {
  'waves/solve': ['Raising f: in a good conductor α and β grow as √f and δs shrinks as 1/√f; in a low-loss dielectric α hardly changes and λ shrinks as 1/f.', 'f artarsa: iyi iletkende α ve β √f ile artar, δs 1/√f ile küçülür; az kayıplı dielektrikte α pek değişmez, λ 1/f ile kısalır.'],
  'waves/sweep': ['The curves show the regime change: σ/ωε > 100 is the good-conductor band, < 0.01 the low-loss band.', 'Eğriler rejim değişimini gösterir: σ/ωε > 100 iyi iletken, < 0.01 az kayıplı bölge.'],
  'rf/oblique': ['A larger index contrast moves θB toward 90° and lowers θc.', 'Kırılma indisi farkı büyüdükçe θB 90°’ye yaklaşır, θc küçülür.'],
  'rf/normal': ['The larger the impedance mismatch η₂/η₁, the more power is reflected; a metal reflects almost everything.', 'η₂/η₁ uyumsuzluğu büyüdükçe yansıyan güç artar; metal neredeyse tamamını yansıtır.'],
  'tl/line': ['As Z_L approaches Z₀, |Γ| → 0 and VSWR → 1; moving along the line only rotates Γ on the Smith chart.', 'Z_L, Z₀’a yaklaştıkça |Γ| → 0 ve VSWR → 1; hat boyunca ilerlemek Γ’yı Smith abağında sadece döndürür.'],
  'ra/waveguide': ['A wider guide (larger a) lowers the cut-off; filling with εr divides it by √εr.', 'Kılavuz genişledikçe (a büyüdükçe) kesim frekansı düşer; εr ile doldurmak onu √εr’ye böler.'],
  'ra/dipole': ['Longer dipoles (up to ~1.25λ) become more directive; R_rad changes strongly with length.', 'Dipol uzadıkça (~1.25λ’ya kadar) yönlülük artar; R_rad uzunlukla güçlü değişir.'],
  'ra/array': ['More elements narrow the beam; a progressive phase δ steers it (cos θ₀ = −δ/kd).', 'Eleman sayısı arttıkça hüzme daralır; ilerleyen faz δ hüzmeyi yönlendirir (cos θ₀ = −δ/kd).'],
  'img/plane': ['Halving d quadruples the force (1/d²) and concentrates the induced charge under Q.', 'd yarıya inerse kuvvet 4 katına çıkar (1/d²) ve indüklenen yük Q’nun altında toplanır.'],
  'bs/segment': ['A longer wire approaches the infinite-wire value I/2πr; doubling r halves H for a long wire.', 'Tel uzadıkça H sonsuz tel değeri I/2πr’ye yaklaşır; uzun telde r iki katına çıkarsa H yarıya iner.'],
  'ms/loops': ['B at the centre is proportional to I/a; a Helmholtz pair makes the axial field flat near the centre.', 'Merkezdeki B, I/a ile orantılıdır; Helmholtz çifti merkez civarında alanı düzleştirir.'],
  'ms/inductance': ['L grows as N² for coils and with ln(b/a) for coaxial geometry; μr multiplies it.', 'L bobinlerde N² ile, koakside ln(b/a) ile artar; μr ile çarpılır.'],
  'es/capacitor': ['C is proportional to εr; a thinner gap raises C but also raises E_max and lowers the breakdown voltage.', 'C, εr ile orantılıdır; aralık incelirse C artar ama E_max da artar ve delinme gerilimi düşer.'],
  'ms/wires': ['Force per metre ∝ I₁I₂/d: parallel currents attract, antiparallel repel.', 'Birim boy başına kuvvet ∝ I₁I₂/d: aynı yönlü akımlar çeker, zıt yönlüler iter.'],
  'es/gauss': ['Inside a uniform charge E grows linearly; outside it falls like a point charge (1/R²).', 'Düzgün yükün içinde E doğrusal artar; dışında nokta yük gibi 1/R² ile azalır.'],
  'es/charges': ['E falls as 1/R² from each charge; superposition adds the vectors.', 'E her yükten 1/R² ile azalır; süperpozisyonla vektörler toplanır.'],
  'mx/faraday': ['The peak EMF is proportional to N, B, area and frequency.', 'Tepe EMK; N, B, alan ve frekansla orantılıdır.'],
  'mx/boundary': ['With no surface charge, field lines bend toward the normal on entering a higher-ε medium.', 'Yüzey yükü yoksa alan çizgileri ε’u büyük ortama girerken normale doğru kırılır.'],
  'mx/currents': ['Above f_c = σ/2πε displacement current dominates and the medium acts as a dielectric.', 'f_c = σ/2πε üstünde deplasman akımı baskın olur ve ortam dielektrik gibi davranır.'],
  'dim/compare': ['Doubling the distance: 0 dB (1-D), −3 dB (2-D), −6 dB (3-D) without loss.', 'Mesafe iki katına çıkınca kayıpsız ortamda: 0 dB (1-D), −3 dB (2-D), −6 dB (3-D).'],
  'coords/element': ['dv grows as R² sin θ: elements near the poles (θ → 0) collapse.', 'dv, R² sin θ ile büyür: kutuplara yakın (θ → 0) elemanlar küçülür.'],
};

function keyValue(c, r) {
  const v = r.values || {};
  if (c.key === 'force') return ['force per metre', `${sci(Math.hypot(...r.forces[0]))} N/m`];
  if (!c.key || v[c.key] == null) return null;
  const units = { theta_B: '°', theta_c: '°', S: '', R: '', fc: 'Hz', R_rad: 'Ω', theta0: '°', F: 'N', H: 'A/m', B_center: 'T', L: 'H', C: 'F', E: 'V/m', E_mag: 'V/m', V_peak: 'V', theta2_deg: '°', level_3D: 'dB', skin_depth: 'm', wavelength: 'm', alpha: 'Np/m', dv: 'm³' };
  const x = v[c.key], u = units[c.key] ?? '';
  return [c.key.replace('_', ' '), u === 'Hz' || u === 'm' || u === 'Ω' || u === 'N' || u === 'T' || u === 'H' || u === 'F' || u === 'V' ? si(x, u) : `${sci(x)} ${u}`];
}

export function answer(question, p, results) {
  const L = (en, trs) => (p.tr ? trs : en);
  const parts = [];
  if (p.concept && (p.conceptual || !results.length)) {
    const k = p.concept;
    parts.push(`**${k.title}**`, `$$${k.formula}$$`, k.pro, `**${L('In simple words', 'Basitçe')}:** ${p.tr ? k.tr : k.simple}`, `${L('See', 'Bakınız')}: ${k.ref}.`);
  }
  if (!results.length && !p.concept) {
    parts.push(L('I could not match this question to a topic I can compute or explain. Try naming the quantity and the values with units, e.g. "skin depth of copper at 10 MHz", "VSWR of 100+j50 Ω on 50 Ω", "Brewster angle for glass", or ask "what is Gauss’s law?".',
      'Bu soruyu hesaplayabileceğim ya da açıklayabileceğim bir konuyla eşleştiremedim. Büyüklüğü ve değerleri birimleriyle yazmayı deneyin: örneğin "bakırın 10 MHz’deki deri kalınlığı", "50 Ω hatta 100+j50 Ω yükün VSWR’si", "cam için Brewster açısı" ya da "Gauss yasası nedir?".'));
  }
  for (const c of results) {
    if (c.error) { parts.push(`${L('Engine error', 'Motor hatası')}: ${c.error}`); continue; }
    const r = c.result, kvp = keyValue(c, r);
    if (kvp) parts.push(`**${L('Result', 'Sonuç')}: ${kvp[0]} = ${kvp[1]}**`);
    const st = (r.steps || []).filter((s) => s.tex && /=/.test(s.tex)).slice(0, 5);
    if (st.length) parts.push(`**${L('Derivation', 'Türetme')}**`, ...st.map((s) => `$$${s.tex}$$`));
    if (r.values?.regime) parts.push(`${L('Regime', 'Rejim')}: ${r.values.regime}.`);
    const w = WHATIF[c.route];
    if (w) parts.push(`**${L('What changes', 'Ne değişir')}:** ${p.tr ? w[1] : w[0]}`);
    if (r.checks) parts.push(r.all_passed ? L(`The engine verified this with ${r.checks.length} independent checks — all passed.`, `Motor bu sonucu ${r.checks.length} bağımsız kontrolle doğruladı — hepsi geçti.`)
      : L('Warning: at least one engine check failed.', 'Uyarı: en az bir motor kontrolü başarısız.'));
  }
  if (p.assumed.length) parts.push(`${L('Values not given in the question were assumed', 'Soruda verilmeyen değerler varsayıldı')}: ${p.assumed.join(', ')}.`);
  return parts.join('\n\n');
}

// ---------------------------------------------------------------- knowledge base (original wording)
const KB = [
  { re: /gauss/, title: "Gauss's law", formula: R`\oint_S\mathbf D\cdot d\mathbf s=Q_{enc},\qquad \nabla\cdot\mathbf D=\rho_v`, pro: 'The outward flux of D through any closed surface equals the free charge enclosed. With spherical, cylindrical or planar symmetry D is normal to a well-chosen surface and constant on it, so the integral reduces to |D| × area.', simple: 'Count the field lines leaving a closed bag: their number tells you how much charge is inside.', tr: 'Kapalı bir yüzeyden çıkan D akısı içerideki yüke eşittir; simetri varsa alanı tek satırda verir.', ref: 'Ulaby & Ravaioli Sec. 4-4; Chapter 2 of this site' },
  { re: /faraday|induct.*emf|emk/, title: "Faraday's law", formula: R`\oint_C\mathbf E\cdot d\mathbf l=-\frac{d}{dt}\int_S\mathbf B\cdot d\mathbf s,\qquad \nabla\times\mathbf E=-\frac{\partial\mathbf B}{\partial t}`, pro: 'A time-varying magnetic flux through a loop induces an EMF around it; the minus sign (Lenz) means the induced current opposes the change. Motional EMF (u × B) and transformer EMF are two faces of the same law.', simple: 'Change the magnetic flux through a loop and a voltage appears around the loop, pushing against the change.', tr: 'Bir halkadan geçen manyetik akı değişirse halkada, bu değişime karşı koyan bir gerilim oluşur.', ref: 'Ulaby & Ravaioli Sec. 6-2; Chapter 4' },
  { re: /amp[eè]re/, title: "Ampère's law", formula: R`\oint_C\mathbf H\cdot d\mathbf l=I_{enc}\ \ \left(+\tfrac{d}{dt}\int_S\mathbf D\cdot d\mathbf s\right)`, pro: 'The circulation of H around a closed path equals the current through it (plus displacement current when fields vary). With symmetry H is tangential and constant on a circle, so H·2πr = I_enc.', simple: 'Walk around a current: how much H you "collect" equals the current you encircled.', tr: 'Bir akımın etrafında dolaşınca toplanan H, çevrelenen akıma eşittir.', ref: 'Ulaby & Ravaioli Sec. 5-4; Chapter 3' },
  { re: /biot|savart/, title: 'Biot–Savart law', formula: R`d\mathbf H=\frac{I\,d\mathbf l\times\hat{\mathbf R}}{4\pi R^2}`, pro: 'Each current element contributes a field perpendicular to both dl and R̂, falling as 1/R². Integrating along the conductor gives H for any geometry; for a finite straight wire H = I(cosθ₁ − cosθ₂)/(4πr).', simple: 'Cut the wire into tiny arrows; each makes a small swirl of field; add them up.', tr: 'Teli küçük parçalara böl; her parça küçük bir manyetik girdap üretir; hepsini topla.', ref: 'Ulaby & Ravaioli Sec. 5-2; Chapter 3.1' },
  { re: /image|görüntü/, title: 'Method of images', formula: R`V=\frac{Q}{4\pi\varepsilon}\left(\frac{1}{R_+}-\frac{1}{R_-}\right)`, pro: 'A charge above a grounded conducting plane is replaced by the charge and an opposite image at the mirror point; both satisfy the same equation and boundary values above the plane, so by uniqueness the fields there are identical.', simple: 'Replace the grounded metal by a mirror charge of opposite sign; the middle plane is then automatically at 0 V.', tr: 'Topraklı metali, ters işaretli bir ayna yükle değiştir; ortadaki düzlem kendiliğinden 0 V olur.', ref: 'Ulaby & Ravaioli Sec. 4-11; Chapter 2.1' },
  { re: /boundary|sınır/, title: 'Boundary conditions', formula: R`E_{1t}=E_{2t},\quad D_{1n}-D_{2n}=\rho_s,\quad H_{1t}-H_{2t}=J_s,\quad B_{1n}=B_{2n}`, pro: 'Obtained by shrinking a loop (Faraday, Ampère) and a pill-box (Gauss) onto the interface. The normal n̂₂ points from medium 2 into medium 1.', simple: 'Along the surface E and H carry straight through (unless a sheet current sits there); across it D jumps by the surface charge and B never jumps.', tr: 'Yüzey boyunca E sürekli, D’nin dik bileşeni yüzey yükü kadar sıçrar; B’nin dik bileşeni hiç sıçramaz.', ref: 'Ulaby & Ravaioli Sec. 4-8, 5-7; Chapter 4' },
  { re: /skin|deri kalın|nüfuz/, title: 'Skin depth', formula: R`\delta_s=\frac1\alpha\approx\frac{1}{\sqrt{\pi f\mu\sigma}}\ \ (\sigma\gg\omega\varepsilon)`, pro: 'In a good conductor the field decays as e^{−z/δs}; at one skin depth the amplitude is 1/e (36.8 %) of its surface value. Currents at RF flow in a layer about δs thick.', simple: 'High-frequency current only uses a thin outer skin of the metal; the higher the frequency, the thinner the skin.', tr: 'Yüksek frekanslı akım metalin sadece ince bir dış katmanını kullanır; frekans arttıkça katman incelir.', ref: 'Ulaby & Ravaioli Sec. 7-5; Chapter 5' },
  { re: /brewster/, title: 'Brewster angle', formula: R`\tan\theta_B=\frac{n_2}{n_1}\ \ (\mu_1=\mu_2)`, pro: 'At θB the parallel-polarised (TM) reflection coefficient vanishes, so reflected light is purely TE-polarised.', simple: 'At one special angle, light polarised in the plane of incidence passes through without any reflection.', tr: 'Özel bir açıda, geliş düzleminde polarize ışık hiç yansımadan geçer.', ref: 'Ulaby & Ravaioli Sec. 8-4; Chapter 6' },
  { re: /smith/, title: 'Smith chart', formula: R`\Gamma=\frac{z-1}{z+1},\quad z=Z/Z_0,\quad \Gamma(d)=\Gamma_Le^{-j2\beta d}`, pro: 'A map of the complex Γ plane with circles of constant normalised resistance and arcs of constant reactance. Moving along a lossless line rotates Γ clockwise at constant |Γ|; one turn is λ/2.', simple: 'A round map of all possible loads; walking along the cable just spins your point around the centre.', tr: 'Tüm yüklerin yuvarlak haritası; hat boyunca ilerlemek noktayı merkez etrafında döndürür.', ref: 'Ulaby & Ravaioli Sec. 2-9; Chapter 7' },
  { re: /vswr|swr|duran dalga/, title: 'Standing-wave ratio', formula: R`S=\frac{|V|_{max}}{|V|_{min}}=\frac{1+|\Gamma|}{1-|\Gamma|}`, pro: 'Incident and reflected waves interfere into a standing pattern; S = 1 for a matched load and ∞ for open, short or purely reactive loads.', simple: 'How uneven the voltage along the line is: 1 means perfect match.', tr: 'Hat boyunca gerilimin ne kadar dalgalandığı: 1 tam uyum demektir.', ref: 'Ulaby & Ravaioli Sec. 2-6; Chapter 7' },
  { re: /waveguide|dalga kılavuz|cut-?off|kesim/, title: 'Waveguide cut-off', formula: R`f_{mn}=\frac{u}{2}\sqrt{\left(\frac{m}{a}\right)^2+\left(\frac{n}{b}\right)^2},\quad \beta=k\sqrt{1-(f_c/f)^2}`, pro: 'Each TE/TM mode propagates only above its cut-off; below it the field is evanescent. TE10 is the dominant mode of a rectangular guide.', simple: 'A metal pipe only lets waves through if they are small enough to fit; the cut-off is the lowest frequency that fits.', tr: 'Metal boru sadece içine sığacak kadar küçük dalgaları geçirir; kesim frekansı sığan en düşük frekanstır.', ref: 'Ulaby & Ravaioli Sec. 8-10; Chapter 8' },
  { re: /poynting|power density|güç yoğunluğu/, title: 'Poynting vector', formula: R`\mathbf S=\mathbf E\times\mathbf H,\qquad \mathbf S_{av}=\tfrac12\mathrm{Re}(\tilde{\mathbf E}\times\tilde{\mathbf H}^*)`, pro: 'Power flow density in W/m²; its flux through a closed surface is the power leaving the volume (Poynting theorem).', simple: 'An arrow showing where electromagnetic energy flows and how much.', tr: 'Elektromanyetik enerjinin nereye ve ne kadar aktığını gösteren ok.', ref: 'Ulaby & Ravaioli Sec. 7-7; Chapter 5' },
  { re: /displacement|deplasman/, title: 'Displacement current', formula: R`\mathbf J_d=\frac{\partial\mathbf D}{\partial t}\ \ (\text{phasor: } j\omega\varepsilon\tilde{\mathbf E})`, pro: 'Maxwell’s addition to Ampère’s law; it makes the equations consistent with charge conservation and allows waves.', simple: 'A changing electric field acts like a current, even in empty space — that is what lets light travel.', tr: 'Değişen elektrik alanı boşlukta bile akım gibi davranır; ışığın yayılmasını sağlayan budur.', ref: 'Ulaby & Ravaioli Sec. 6-7; Chapter 4' },
  { re: /maxwell/, title: "Maxwell's equations", formula: R`\nabla\cdot\mathbf D=\rho_v,\ \ \nabla\times\mathbf E=-\partial_t\mathbf B,\ \ \nabla\cdot\mathbf B=0,\ \ \nabla\times\mathbf H=\mathbf J+\partial_t\mathbf D`, pro: 'Four laws for the sources and circulation of the fields; with the constitutive relations D = εE, B = μH, J = σE they determine all classical EM phenomena.', simple: 'Charges make electric fields, currents and changing E make magnetic fields, changing B makes electric fields, and there are no magnetic charges.', tr: 'Yükler elektrik alan, akımlar ve değişen E manyetik alan, değişen B elektrik alan üretir; manyetik yük yoktur.', ref: 'Ulaby & Ravaioli Ch. 6; Chapter 4' },
  { re: /uniqueness|teklik/, title: 'Uniqueness theorem', formula: R`\nabla^2V=-\rho_v/\varepsilon\ \text{in } v,\ \ V \text{ given on } S\ \Rightarrow\ V \text{ unique}`, pro: 'Any function that satisfies Poisson’s equation in a region and the prescribed boundary values is the solution — the basis of the image method.', simple: 'If a guess satisfies the equation and the edges, it is the answer.', tr: 'Denklemi ve sınır değerlerini sağlayan tahmin, cevabın ta kendisidir.', ref: 'Cheng Sec. 4-3' },
  { re: /coordinate|koordinat|scale factor|ölçek/, title: 'Scale factors', formula: R`d\mathbf l=\hat u_1h_1du_1+\hat u_2h_2du_2+\hat u_3h_3du_3,\quad dv=h_1h_2h_3\,du_1du_2du_3`, pro: 'Spherical: h = (1, R, R sin θ); cylindrical: h = (1, r, 1). They turn angle steps into lengths and build every differential operator.', simple: 'Turning by an angle moves you further when you are far from the centre — the scale factor is that distance.', tr: 'Merkezden uzaktayken aynı açı daha uzun yol demektir; ölçek çarpanı bu uzaklıktır.', ref: 'Ulaby & Ravaioli Sec. 3-2; Chapter 1' },
];
