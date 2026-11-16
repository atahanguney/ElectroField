# ElectroField — working rules

Interactive applied-electromagnetics workbench (Ulaby & Ravaioli / Cheng notation) for EE students and engineers.

## Architecture
- `engine/` — all physics (NumPy/SciPy). Every solver returns `Derivation.out(...)`: `values`, `steps` (TeX), `checks` (independent verification), `all_passed`.
- `engine/routes.py` — the same routes without FastAPI; GitHub Pages runs it in the browser via Pyodide (`web/js/api.js` picks server or Pyodide). New route ⇒ add it to both `server/main.py` and `ROUTES`, and a case in `tests/test_routes.py` (parity test). New engine file ⇒ add it to `ENGINE_FILES` in `web/js/api.js`. Test the static build locally with `/?backend=pyodide`.
- `server/main.py` — FastAPI, thin `/api/*` wrappers; also serves `web/` and `/vendor/plotly.min.js` from the plotly pip package.
- `web/` — vanilla ES modules, Plotly, KaTeX (CDN). `js/app.js` = router + chapter list; one file per chapter in `js/modules/`; shared helpers in `js/ui.js`. The frontend never computes physics (only Re{phasor·e^{jωt}} for animation and drawing aids).
- `tests/` — pytest against textbook closed forms and limits. `python -m pytest -q -p no:anyio tests`
- `legacy/` — old single-file version, kept for reference only.

## Rules
- Every new quantity needs ≥1 independent check (alternative formula, limit, numerical residual/integral) and a test.
- Constants only from `engine/constants.py` (CODATA via scipy).
- UI style: textbook/instrument; single accent colour; E = red, H = blue, S = green; no gradients, glow, emoji, glass.
- Textbook problems: write original problems in Ulaby/Cheng style and cite chapter/section — never copy problem text or figures.
- Work in small steps; edit files instead of rewriting; report changes as a short per-file list.

- Assistant (`server/assistant.py`): add one tool per new solver (schema in TOOLS + branch in `_run` returning `(result, {chapter, params})`) and a case in `tests/test_assistant_tools.py`. Chapter `render(view, ch, init)` must accept those params.
- Dev server: `.claude/launch.json` runs uvicorn with `--reload` on engine/ and server/.

## Roadmap
Done: 0 1-D/2-D/3-D waves · 1 Coordinates · 2 Electrostatics · 3 Magnetostatics · 4 Maxwell/boundaries/Faraday/displacement · 5 Plane waves · 6 Reflection · 7 Transmission lines/Smith · 8 Waveguides/antennas · assistant (18 tools). 125 tests.
EM tutor (`web/js/modules/tutor.js`): browser-side, user's free key (Gemini/Groq/OpenRouter; keyless Pollinations now needs Cloudflare Turnstile, unusable). Plan JSON → engine routes → explain → number audit. New route ⇒ add it to ROUTES there too.
Verification report (`engine/report.py`): theory written in plain `math`, never via engine code; add ≥3 cases per new module.
Accessibility/SEO: `a11y()` in ui.js names controls, plots and fixes heading order; keep root `index.html` = `web/index.html` with `web/` prefixes (tested). Lighthouse 12: perf 99–100, a11y 100, SEO 100.
Question bank done (`engine/questions.py`, 27 templates; add a template with `q(...)` + a solver adapter — `tests/test_questions.py` runs every template on 5 seeds).
Ideas next: more templates per chapter, Turkish UI option, lossy waveguides, Poisson/Laplace numerical solver (FDM) for arbitrary electrode shapes.
