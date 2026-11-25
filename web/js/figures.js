// Original problem figures drawn as SVG (labelled sketches, not to scale unless stated).
const NS = 'http://www.w3.org/2000/svg';
let uid = 0;

function el(tag, attrs = {}, ...kids) {
  const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) if (v != null) e.setAttribute(k, v);
  kids.flat().forEach((k) => k != null && e.append(typeof k === 'string' ? document.createTextNode(k) : k));
  return e;
}

export function figure(spec, title = '') {
  const id = `ar${++uid}`;
  const s = el('svg', { viewBox: '0 0 340 210', class: 'fig-svg', role: 'img', 'aria-label': title || 'Problem figure' },
    el('defs', {}, ['ink', 'E', 'H', 'S', 'accent'].map((c) => el('marker', { id: `${id}${c}`, viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: 'auto-start-reverse' },
      el('path', { d: 'M0,0 L10,5 L0,10 z', fill: `var(--${c === 'ink' ? 'ink' : c})` })))));
  const col = (c) => `var(--${c})`;
  const L = (x1, y1, x2, y2, o = {}) => s.append(el('line', { x1, y1, x2, y2, stroke: col(o.c || 'ink'), 'stroke-width': o.w || 1.5, 'stroke-dasharray': o.dash, 'marker-end': o.arrow ? `url(#${id}${o.c || 'ink'})` : null, 'marker-start': o.both ? `url(#${id}${o.c || 'ink'})` : null }));
  const Tx = (x, y, t, o = {}) => s.append(el('text', { x, y, fill: col(o.c || 'ink'), 'font-size': o.size || 13, 'text-anchor': o.anchor || 'middle', 'font-style': o.italic ? 'italic' : null, 'font-family': 'Georgia, serif', 'dominant-baseline': 'middle' }, t));
  const Ci = (x, y, r, o = {}) => s.append(el('circle', { cx: x, cy: y, r, fill: o.fill ? col(o.fill) : 'none', stroke: col(o.c || 'ink'), 'stroke-width': o.w || 1.5, 'stroke-dasharray': o.dash, opacity: o.op }));
  const Re = (x, y, w, h, o = {}) => s.append(el('rect', { x, y, width: w, height: h, fill: o.fill ? col(o.fill) : 'none', stroke: o.c === 'none' ? 'none' : col(o.c || 'ink'), 'stroke-width': o.w || 1.5, opacity: o.op, 'stroke-dasharray': o.dash }));
  const Pa = (d, o = {}) => s.append(el('path', { d, fill: o.fill ? col(o.fill) : 'none', stroke: col(o.c || 'ink'), 'stroke-width': o.w || 1.5, 'stroke-dasharray': o.dash, opacity: o.op, 'marker-end': o.arrow ? `url(#${id}${o.c || 'ink'})` : null }));
  const charge = (x, y, q, label) => { Ci(x, y, 11, { fill: q > 0 ? 'E' : 'H', c: q > 0 ? 'E' : 'H' }); Tx(x, y + 1, q > 0 ? '+' : '−', { c: 'paper', size: 15 }); if (label) Tx(x, y - 20, label); };
  const axes = (ox, oy, lx = 'x', ly = 'y') => { L(ox - 10, oy, 320, oy, { arrow: 1, c: 'ink-3', w: 1 }); L(ox, oy + 10, ox, 14, { arrow: 1, c: 'ink-3', w: 1 }); Tx(326, oy, lx, { italic: 1, size: 12 }); Tx(ox, 8, ly, { italic: 1, size: 12 }); };

  switch (spec.type) {
    case 'dims': {
      if (spec.dim === '1D') { Re(20, 90, 300, 30, { fill: 'accent-bg', c: 'ink-3' }); for (let i = 0; i < 6; i++) L(40 + i * 48, 92, 40 + i * 48, 118, { c: 'E', w: 2 }); L(30, 140, 310, 140, { arrow: 1, c: 'S' }); Tx(170, 160, 'z — plane wavefronts, constant amplitude'); }
      else if (spec.dim === '2D') { Ci(170, 105, 4, { fill: 'ink' }); [25, 50, 75, 100].forEach((r, i) => Ci(170, 105, r, { c: 'E', op: 1 - i * 0.2 })); Tx(170, 196, 'line source ⊙ — cylinders, |E| ∝ 1/√ρ'); L(170, 105, 270, 105, { arrow: 1, c: 'S' }); Tx(262, 94, 'ρ', { italic: 1 }); }
      else { Ci(170, 105, 4, { fill: 'ink' }); [25, 50, 75, 100].forEach((r, i) => Ci(170, 105, r, { c: 'E', op: 1 - i * 0.22, dash: i % 2 ? '4 3' : null })); Tx(170, 196, 'point source — spheres, |E| ∝ 1/R'); L(170, 105, 260, 60, { arrow: 1, c: 'S' }); Tx(250, 50, 'R', { italic: 1 }); }
      break;
    }
    case 'coord': {
      const ox = 110, oy = 150;
      L(ox, oy, ox, 20, { arrow: 1, c: 'ink-3', w: 1 }); L(ox, oy, 300, oy, { arrow: 1, c: 'ink-3', w: 1 }); L(ox, oy, 40, 195, { arrow: 1, c: 'ink-3', w: 1 });
      Tx(ox, 12, 'z', { italic: 1 }); Tx(306, oy, 'y', { italic: 1, anchor: 'start' }); Tx(32, 200, 'x', { italic: 1 });
      const px = 230, py = 70;
      if (spec.system === 'spherical') { L(ox, oy, px, py, { c: 'accent', w: 2 }); Tx((ox + px) / 2 - 8, (oy + py) / 2 - 8, 'R', { italic: 1, c: 'accent' }); Pa(`M ${ox} ${oy - 40} A 40 40 0 0 1 ${ox + 26} ${oy - 31}`, { c: 'ink' }); Tx(ox + 14, oy - 54, 'θ', { italic: 1 }); L(px, py, px, oy + 20, { dash: '4 3', c: 'ink-3', w: 1 }); L(ox, oy, px, oy + 20, { dash: '4 3', c: 'ink-3', w: 1 }); Tx(ox + 45, oy + 22, 'φ', { italic: 1 }); }
      else { L(ox, oy, px, oy + 20, { c: 'accent', w: 2 }); Tx((ox + px) / 2, oy + 24, 'r', { italic: 1, c: 'accent' }); L(px, oy + 20, px, py, { c: 'accent', w: 2 }); Tx(px + 10, (py + oy) / 2, 'z', { italic: 1, c: 'accent' }); Tx(ox + 45, oy + 20, 'φ', { italic: 1 }); }
      Ci(px, py, 5, { fill: 'S', c: 'S' }); Tx(px + 10, py - 12, spec.point ? `P(${spec.point.join(', ')})` : 'P', { anchor: 'start', size: 12 });
      break;
    }
    case 'charges': case 'wires': {
      const items = spec.charges || spec.wires; const xs = items.map((c) => c[1]).concat(spec.probe ? [spec.probe[0]] : []); const ys = items.map((c) => c[2]).concat(spec.probe ? [spec.probe[1]] : []);
      const span = Math.max(0.1, ...xs.map(Math.abs), ...ys.map(Math.abs)) * 1.3, sx = (x) => 170 + (x / span) * 140, sy = (y) => 120 - (y / span) * 90;
      axes(170, 120);
      items.forEach(([q, x, y]) => {
        if (spec.type === 'wires') { Ci(sx(x), sy(y), 11, { c: q > 0 ? 'E' : 'H', w: 2 }); Tx(sx(x), sy(y) + 1, q > 0 ? '•' : '×', { c: q > 0 ? 'E' : 'H', size: 16 }); Tx(sx(x), sy(y) + 24, `${Math.abs(q)} A`, { size: 12 }); }
        else charge(sx(x), sy(y), q, `${q} nC`);
      });
      if (spec.probe) { Ci(sx(spec.probe[0]), sy(spec.probe[1]), 5, { fill: 'S', c: 'S' }); Tx(sx(spec.probe[0]) + 10, sy(spec.probe[1]) - 10, 'P', { anchor: 'start', c: 'S', italic: 1 }); }
      if (items.length === 2) { const [a, b] = items; L(sx(a[1]), 190, sx(b[1]), 190, { both: 1, arrow: 1, c: 'ink-3', w: 1 }); Tx((sx(a[1]) + sx(b[1])) / 2, 200, `d = ${Math.abs(b[1] - a[1]).toFixed(2)} m`, { size: 12 }); }
      break;
    }
    case 'sphere': case 'line': {
      if (spec.type === 'sphere') { Ci(170, 105, 70, { fill: 'accent-bg', c: 'E' }); Tx(170, 30, `a = ${spec.a * 100} cm`); Ci(170, 105, 70 * spec.r / spec.a, { c: 'S', dash: '5 4' }); Tx(170, 105 + 70 * spec.r / spec.a + 12, 'Gaussian surface', { c: 'S', size: 12 }); L(170, 105, 170 + 70 * spec.r / spec.a, 105, { c: 'S', arrow: 1 }); Tx(170 + 35 * spec.r / spec.a, 96, 'R', { italic: 1, c: 'S' }); }
      else { L(170, 20, 170, 190, { c: 'E', w: 4 }); Tx(150, 30, 'ρₗ', { c: 'E' }); Re(130, 60, 80, 90, { c: 'S', dash: '5 4' }); L(170, 105, 210, 105, { arrow: 1, c: 'S' }); Tx(192, 95, 'r', { italic: 1, c: 'S' }); Tx(260, 105, 'cylindrical Gaussian surface', { size: 11, c: 'S' }); }
      break;
    }
    case 'coax': case 'toroid': {
      Ci(170, 105, 80, { c: 'H', w: 3 }); Ci(170, 105, 80 * spec.a / spec.b, { fill: spec.type === 'coax' ? 'E' : null, c: 'E', w: 3 });
      if (spec.type === 'toroid') { Re(80, 101, 0, 0); for (let k = 0; k < 16; k++) { const t = (k / 16) * 2 * Math.PI, r1 = 80 * spec.a / spec.b, r2 = 80; L(170 + r1 * Math.cos(t), 105 + r1 * Math.sin(t), 170 + r2 * Math.cos(t), 105 + r2 * Math.sin(t), { c: 'ink-3', w: 1 }); } }
      L(170, 105, 170 + 80 * spec.a / spec.b, 105, { arrow: 1 }); Tx(170 + 40 * spec.a / spec.b, 96, 'a', { italic: 1 }); L(170, 105, 170, 25, { arrow: 1 }); Tx(178, 60, 'b', { italic: 1, anchor: 'start' });
      Tx(290, 190, spec.label || (spec.type === 'coax' ? `a = ${spec.a}, b = ${spec.b} (mm)` : `a = ${spec.a}, b = ${spec.b} (cm)`), { size: 12 });
      break;
    }
    case 'plates': { Re(60, 60, 220, 8, { fill: 'E', c: 'E' }); Re(60, 142, 220, 8, { fill: 'H', c: 'H' }); Re(60, 68, 220, 74, { fill: 'accent-bg', c: 'none' }); for (let i = 0; i < 7; i++) L(80 + i * 30, 72, 80 + i * 30, 138, { arrow: 1, c: 'E', w: 1 }); L(300, 68, 300, 142, { both: 1, arrow: 1, c: 'ink-3', w: 1 }); if (spec.d != null) Tx(312, 105, `d = ${spec.d} mm`, { anchor: 'start', size: 12 }); Tx(40, 64, '+'); Tx(40, 146, '−'); Tx(170, 105, 'ε', { italic: 1, size: 16 }); break; }
    case 'plane': case 'corner': {
      if (spec.type === 'plane') {
        Re(20, 150, 300, 40, { fill: 'ink-3', c: 'none', op: 0.35 }); L(20, 150, 320, 150, { w: 3 }); Tx(170, 172, 'σ = ∞,  V = 0'); charge(170, 150 - 100 * Math.min(spec.d / 0.4, 1.2), 1, 'Q');
        const y = 150 - 100 * Math.min(spec.d / 0.4, 1.2); L(130, y, 130, 150, { both: 1, arrow: 1, c: 'ink-3', w: 1 }); Tx(120, (y + 150) / 2, 'd', { italic: 1, anchor: 'end' }); L(280, 150, 280, 120, { arrow: 1, c: 'accent', w: 2 }); Tx(292, 125, 'n̂', { c: 'accent', anchor: 'start' });
        if (spec.probe) { Ci(170 + 300 * spec.probe[0], 150 - 100 * spec.probe[1] / 0.4, 5, { fill: 'S', c: 'S' }); Tx(178 + 300 * spec.probe[0], 140 - 100 * spec.probe[1] / 0.4, 'P', { c: 'S', anchor: 'start', italic: 1 }); }
      } else { Re(40, 20, 20, 170, { fill: 'ink-3', c: 'none', op: 0.35 }); Re(40, 170, 280, 20, { fill: 'ink-3', c: 'none', op: 0.35 }); L(60, 20, 60, 170, { w: 3 }); L(60, 170, 320, 170, { w: 3 }); charge(60 + 300 * spec.x0, 170 - 220 * spec.y0, 1, 'Q'); Tx(250, 40, 'grounded 90° corner', { size: 12 }); }
      break;
    }
    case 'segment': { L(80, 30, 80, 180, { c: 'H', w: 5 }); L(80, 40, 80, 25, { arrow: 1, c: 'H', w: 2 }); Tx(66, 30, 'I', { c: 'H', italic: 1 }); Ci(250, 105, 5, { fill: 'S', c: 'S' }); Tx(262, 100, 'P', { italic: 1, c: 'S', anchor: 'start' }); L(80, 105, 250, 105, { dash: '4 3', c: 'ink-3', w: 1 }); Tx(165, 96, 'r', { italic: 1 }); L(80, 30, 250, 105, { c: 'ink-3', w: 1 }); L(80, 180, 250, 105, { c: 'ink-3', w: 1 }); Tx(108, 54, 'θ₂', { size: 12 }); Tx(108, 160, 'θ₁', { size: 12 }); L(40, 30, 40, 180, { both: 1, arrow: 1, c: 'ink-3', w: 1 }); Tx(30, 105, `L = ${spec.L} m`, { anchor: 'end', size: 11 }); break; }
    case 'square': { Re(100, 35, 140, 140, { c: 'H', w: 4 }); L(240, 140, 240, 70, { arrow: 1, c: 'H', w: 2 }); Ci(170, 105, 5, { fill: 'S', c: 'S' }); Tx(170, 92, 'P', { italic: 1, c: 'S' }); L(100, 190, 240, 190, { both: 1, arrow: 1, c: 'ink-3', w: 1 }); Tx(170, 202, `a = ${spec.a} m`, { size: 12 }); Tx(256, 105, 'I', { italic: 1, c: 'H' }); break; }
    case 'loop': case 'solenoid': {
      if (spec.type === 'loop') { s.append(el('ellipse', { cx: 170, cy: 150, rx: 90, ry: 22, fill: 'none', stroke: col('H'), 'stroke-width': 4 })); L(170, 190, 170, 20, { c: 'ink-3', w: 1, arrow: 1 }); Tx(178, 22, 'z', { italic: 1, anchor: 'start' }); L(170, 150, 260, 150, { c: 'ink-3', w: 1 }); Tx(215, 162, 'a', { italic: 1 }); if (spec.z) { Ci(170, 60, 5, { fill: 'S', c: 'S' }); Tx(180, 60, 'P on the axis', { anchor: 'start', c: 'S', size: 12 }); } else { Ci(170, 150, 5, { fill: 'S', c: 'S' }); } }
      else { for (let k = 0; k < 9; k++) s.append(el('ellipse', { cx: 70 + k * 25, cy: 105, rx: 8, ry: 40, fill: 'none', stroke: col('H'), 'stroke-width': 2 })); L(50, 105, 300, 105, { c: 'ink-3', w: 1, dash: '4 3' }); Tx(170, 170, `radius ${spec.a} cm, length ${spec.l} cm`, { size: 12 }); }
      break;
    }
    case 'interface': {
      Re(20, 20, 300, 85, { fill: 'accent-bg', c: 'none' }); Re(20, 105, 300, 85, { fill: 'accent', c: 'none', op: 0.18 }); L(20, 105, 320, 105, { w: 2 }); L(170, 20, 170, 190, { dash: '4 3', c: 'ink-3', w: 1 });
      // drawing only: angles are the given θ₁ and, in a solution figure, the engine's θ₂ (spec.theta2)
      const t1 = (spec.theta * Math.PI) / 180, c = spec.H ? 'H' : 'E', f = spec.H ? 'H' : 'E', m = spec.H ? 'μ' : 'ε';
      const arc = (a, r, down) => { const sx = 170, sy = down ? 105 + r : 105 - r, ex = down ? 170 - r * Math.sin(a) : 170 + r * Math.sin(a), ey = down ? 105 + r * Math.cos(a) : 105 - r * Math.cos(a);
        Pa(`M ${sx} ${sy} A ${r} ${r} 0 0 ${down ? 1 : 1} ${ex} ${ey}`, { c: 'ink-2', w: 1.2 }); };
      L(170, 105, 170 + 80 * Math.sin(t1), 105 - 80 * Math.cos(t1), { arrow: 1, c, w: 2.5 }); Tx(178 + 80 * Math.sin(t1), 100 - 80 * Math.cos(t1), `${f}₁`, { c, anchor: 'start' });
      if (spec.theta > 3) { arc(t1, 32, false); Tx(170 + 46 * Math.sin(t1 / 2), 105 - 46 * Math.cos(t1 / 2), 'θ₁', { size: 12 }); }
      if (spec.theta2 != null) {
        const t2 = (spec.theta2 * Math.PI) / 180;
        L(170 - 80 * Math.sin(t2), 105 + 80 * Math.cos(t2), 169, 104.5, { arrow: 1, c, w: 2.5 }); Tx(162 - 80 * Math.sin(t2), 112 + 80 * Math.cos(t2), `${f}₂`, { c, anchor: 'end' });
        if (spec.theta2 > 3) { arc(t2, 32, true); Tx(170 - 48 * Math.sin(t2 / 2), 105 + 48 * Math.cos(t2 / 2), 'θ₂', { size: 12 }); }
        Tx(300, 160, `θ₂ = ${spec.theta2.toFixed(2)}°`, { anchor: 'end', size: 12 });
      }
      Tx(40, 34, `${m}r₁ = ${spec.e1}`, { anchor: 'start', size: 12 }); Tx(300, 180, `${m}r₂ = ${spec.e2}`, { anchor: 'end', size: 12 }); Tx(176, 26, 'n̂₂', { anchor: 'start', c: 'accent' });
      break;
    }
    case 'oblique': case 'normal': {
      Re(20, 105, 300, 85, { fill: 'accent', c: 'none', op: 0.18 }); L(20, 105, 320, 105, { w: 2 }); L(170, 20, 170, 190, { dash: '4 3', c: 'ink-3', w: 1 });
      if (spec.type === 'normal') { L(150, 30, 150, 100, { arrow: 1, c: 'E', w: 2.5 }); L(190, 100, 190, 30, { arrow: 1, c: 'E', w: 1.2 }); L(170, 110, 170, 180, { arrow: 1, c: 'S', w: 2 }); Tx(140, 40, 'incident', { anchor: 'end', size: 12 }); Tx(200, 40, 'reflected', { anchor: 'start', size: 12 }); Tx(180, 170, 'transmitted', { anchor: 'start', size: 12 }); Tx(40, 176, `εr₂ = ${spec.e2}`, { anchor: 'start', size: 12 }); }
      else { const t = (spec.theta * Math.PI) / 180, tt = Math.asin(Math.min(1, Math.sqrt(spec.e1 / spec.e2) * Math.sin(t)));
        L(170 - 85 * Math.sin(t), 105 - 85 * Math.cos(t), 168, 103, { arrow: 1, c: 'E', w: 2.5 }); L(172, 103, 170 + 85 * Math.sin(t), 105 - 85 * Math.cos(t), { arrow: 1, c: 'E', w: 1.2 }); L(170, 107, 170 + 80 * Math.sin(tt), 105 + 80 * Math.cos(tt), { arrow: 1, c: 'S', w: 2 });
        Tx(150, 50, 'θᵢ', { size: 12 }); Tx(184, 160, 'θₜ', { size: 12, anchor: 'start' }); Tx(40, 34, `εr₁ = ${spec.e1}`, { anchor: 'start', size: 12 }); Tx(40, 176, `εr₂ = ${spec.e2}`, { anchor: 'start', size: 12 }); }
      break;
    }
    case 'tline': {
      L(60, 80, 260, 80, { w: 2.5 }); L(60, 130, 260, 130, { w: 2.5 }); Ci(40, 105, 16); Tx(40, 106, '~'); L(40, 80, 60, 80); L(40, 130, 60, 130); L(40, 89, 40, 80); L(40, 121, 40, 130);
      Re(270, 85, 30, 40, { fill: 'accent-bg' }); L(260, 80, 285, 80); L(285, 80, 285, 85); L(260, 130, 285, 130); L(285, 130, 285, 125); Tx(285, 106, 'Z_L', { size: 11 });
      Tx(160, 68, `Z₀ = ${spec.Z0}`, { size: 12 }); Tx(285, 150, `Z_L = ${spec.ZL}`, { size: 12 }); if (spec.l) Tx(160, 145, `l = ${spec.l}`, { size: 12 });
      L(255, 195, 175, 195, { arrow: 1, c: 'ink-3', w: 1 }); Tx(215, 205, 'd from the load', { size: 11 });
      if (spec.stub) { L(140, 130, 140, 175, { c: 'S', w: 2 }); L(160, 130, 160, 175, { c: 'S', w: 2 }); L(140, 175, 160, 175, { c: 'S', w: 3 }); Tx(134, 160, 'shorted stub', { anchor: 'end', c: 'S', size: 11 }); }
      break;
    }
    case 'waveguide': { Re(80, 60, 180, 80, { fill: 'accent-bg', w: 3 }); for (let i = 0; i < 7; i++) { const x = 100 + i * 23, hgt = 34 * Math.sin(((x - 80) / 180) * Math.PI); L(x, 100 + hgt / 2, x, 100 - hgt / 2, { arrow: 1, c: 'E', w: 1.5 }); } L(80, 160, 260, 160, { both: 1, arrow: 1, c: 'ink-3', w: 1 }); Tx(170, 174, `a = ${spec.a} mm`, { size: 12 }); L(280, 60, 280, 140, { both: 1, arrow: 1, c: 'ink-3', w: 1 }); Tx(290, 100, `b = ${spec.b} mm`, { anchor: 'start', size: 12 }); Tx(170, 40, 'TE₁₀: E across the narrow dimension', { size: 12 }); break; }
    case 'dipole': { const hl = Math.min(80, 160 * spec.L); L(170, 105 - hl, 170, 100, { c: 'H', w: 4 }); L(170, 110, 170, 105 + hl, { c: 'H', w: 4 }); Ci(170, 105, 4, { fill: 'ink' }); Tx(186, 105, `l = ${spec.L}λ`, { anchor: 'start', size: 12 }); Pa('M 200 60 Q 250 105 200 150', { c: 'S', dash: '4 3' }); Pa('M 140 60 Q 90 105 140 150', { c: 'S', dash: '4 3' }); Tx(270, 60, 'radiation', { c: 'S', size: 12 }); break; }
    case 'array': { for (let k = 0; k < Math.min(spec.N, 12); k++) Ci(50 + k * 22, 120, 6, { fill: 'accent', c: 'accent' }); L(50, 145, 72, 145, { both: 1, arrow: 1, c: 'ink-3', w: 1 }); Tx(61, 160, `d = ${spec.d}λ`, { size: 12 }); Tx(170, 40, `N = ${spec.N} elements`, { size: 13 }); L(170, 100, 170, 55, { arrow: 1, c: 'S', dash: '4 3' }); Tx(184, 70, 'θ from the array axis →', { anchor: 'start', size: 11 }); break; }
    case 'generator': { Re(40, 30, 40, 150, { fill: 'E', c: 'none', op: 0.4 }); Tx(60, 105, 'N', { c: 'paper', size: 16 }); Re(260, 30, 40, 150, { fill: 'H', c: 'none', op: 0.4 }); Tx(280, 105, 'S', { c: 'paper', size: 16 }); for (let i = 0; i < 4; i++) L(85, 50 + i * 35, 255, 50 + i * 35, { arrow: 1, c: 'ink-3', w: 1 }); s.append(el('ellipse', { cx: 170, cy: 105, rx: 30, ry: 60, fill: 'none', stroke: col('accent'), 'stroke-width': 3 })); Tx(170, 196, 'B (horizontal) through a coil', { size: 12 }); if (spec.N) Tx(170, 16, `N = ${spec.N} turn${spec.N > 1 ? 's' : ''}${spec.R ? `, load R = ${spec.R} Ω` : ''}`, { size: 12 }); break; }
    case 'medium': case 'slab': { Re(20, 40, 300, 130, { fill: 'accent-bg', c: 'none' }); Pa('M 20 105 ' + Array.from({ length: 30 }, (_, i) => `L ${20 + i * 10} ${105 - 40 * Math.exp(-i / 12) * Math.sin(i * 0.9)}`).join(' '), { c: 'E', w: 2 }); Tx(170, 190, spec.label ? `medium: ${spec.label}` : 'lossy medium', { size: 12 }); L(30, 30, 120, 30, { arrow: 1, c: 'S' }); Tx(132, 30, 'propagation', { anchor: 'start', size: 11, c: 'S' }); break; }
    default: Tx(170, 105, '');
  }
  return s;
}
