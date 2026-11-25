// Renders the images used outside the app:
//   web/img/og.png           social preview card, 1280×640 (from scripts/og-card.html)
//   docs/media/home.png      README screenshot, desktop
//   docs/media/phone.png     README screenshot, phone
//   docs/media/smith.gif     README animation: Chapter 7, line length swept, Smith chart updating
// Everything is the real page running the in-browser engine (Pyodide), so it needs network access to cdn.jsdelivr.net.
//
//   node scripts/render_media.js        (needs Playwright with Chromium, Python 3 and ffmpeg)
const { chromium, devices } = require('playwright');
const { spawn, execFileSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const PORT = 8817;
const BASE = `http://127.0.0.1:${PORT}`;
const out = (p) => { fs.mkdirSync(path.dirname(path.join(ROOT, p)), { recursive: true }); return path.join(ROOT, p); };

(async () => {
  const server = spawn('python3', ['-m', 'http.server', String(PORT), '--bind', '127.0.0.1'], { cwd: ROOT, stdio: 'ignore' });
  await new Promise((r) => setTimeout(r, 800));
  const browser = await chromium.launch();
  try {
    // 1. social card
    const card = await (await browser.newContext({ viewport: { width: 1280, height: 640 }, colorScheme: 'light' })).newPage();
    await card.goto(`${BASE}/scripts/og-card.html`);
    await card.waitForSelector('body[data-ready]');
    await card.screenshot({ path: out('web/img/og.png') });

    // 2. desktop and phone screenshots of the landing page (what a visitor sees before anything downloads)
    const desk = await (await browser.newContext({ viewport: { width: 1280, height: 800 }, colorScheme: 'light' })).newPage();
    await desk.goto(`${BASE}/`, { waitUntil: 'networkidle' });
    await desk.waitForTimeout(800);
    await desk.screenshot({ path: out('docs/media/home.png') });
    const phone = await (await browser.newContext({ ...devices['iPhone 13'], deviceScaleFactor: 2, colorScheme: 'light', reducedMotion: 'reduce' })).newPage();
    await phone.goto(`${BASE}/`, { waitUntil: 'networkidle' });
    await phone.waitForTimeout(800);
    await phone.screenshot({ path: out('docs/media/phone.png') });

    // 3. GIF: Chapter 7 with the line length swept from ~0 to λ/2 and back: the arc grows into one full turn on the Smith chart
    const p = await (await browser.newContext({ viewport: { width: 1280, height: 860 }, colorScheme: 'light' })).newPage();
    await p.goto(`${BASE}/#/tlines`, { waitUntil: 'networkidle' });
    await p.waitForFunction(() => !document.querySelector('.engine-banner') && document.querySelector('.js-plotly-plot'), null, { timeout: 120000 });
    await p.evaluate(() => { document.querySelector('.ai-fab')?.remove(); window.scrollTo(0, document.querySelector('.work').getBoundingClientRect().top + scrollY - 12); });
    const box = await p.evaluate(() => { const a = document.querySelector('.work').getBoundingClientRect(); return { x: a.left - 12, y: a.top - 12, width: a.width + 24, height: 610 }; });
    const len = p.locator('.ctl', { hasText: 'line length' }).locator('input[type=text]');
    const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'ef-gif-'));
    const N = 48;
    for (let i = 0; i < N; i++) {
      const l = 0.005 + 0.145 * (0.5 - 0.5 * Math.cos((2 * Math.PI * i) / N));   // 5 mm → 150 mm (= λ/2 at 1 GHz) → 5 mm
      await len.fill(l.toFixed(4)); await len.dispatchEvent('change');
      await p.waitForTimeout(350);
      await p.screenshot({ path: path.join(tmp, `f${String(i).padStart(3, '0')}.png`), clip: box });
    }
    const gif = out('docs/media/smith.gif');
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', '8', '-i', path.join(tmp, 'f%03d.png'),
      '-vf', 'scale=860:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=none', gif]);
    fs.rmSync(tmp, { recursive: true });
    for (const f of ['web/img/og.png', 'docs/media/home.png', 'docs/media/phone.png', 'docs/media/smith.gif']) console.log(f, `${Math.round(fs.statSync(path.join(ROOT, f)).size / 1024)} kB`);
  } finally {
    await browser.close();
    server.kill();
  }
})();
