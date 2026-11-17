# ElectroField

Built by **[Atahan Güney](https://atahanguney.github.io/)** (Atahan Guney) — electrical & electronics engineering, Antalya Bilim University.

An interactive applied-electromagnetics workbench. Every number on screen is computed by a Python engine, shown as a step-by-step derivation, and cross-checked by an independent method (complex root vs closed form, Jacobian vs finite differences, Maxwell-equation residuals, numerical integration).

Notation and coverage follow Ulaby & Ravaioli, *Fundamentals of Applied Electromagnetics*, and Cheng, *Field and Wave Electromagnetics*.

## Use it online

**https://atahanguney.github.io/ElectroField/** — the complete workbench runs in your browser: the same Python engine (`engine/`) is executed client-side with [Pyodide](https://pyodide.org) (NumPy and SciPy compiled to WebAssembly). The first visit downloads about 30 MB, after that it is cached.

### EM tutor (AI)

By default the **EM tutor** uses a **built-in tutor that needs no key and always works**: it reads the question (English or Turkish), extracts quantities with units (GHz, mm, nC, εr, Ω, …) and materials, runs the matching engine routes and writes the answer from formula templates filled only with engine results, plus a formula sheet for conceptual questions. It cannot state a number the engine did not compute.

Optionally, the page connects to a free language model with your own free key — Google Gemini ([aistudio.google.com/apikey](https://aistudio.google.com/apikey)), Groq or OpenRouter free models. The model never computes: it (1) picks engine routes and parameters, (2) the engine runs them with their independent checks, (3) the model explains the engine's numbers with the formulas, and (4) every number in the answer is matched against the engine output — unmatched numbers are flagged. Results come with graphs, the derivation and a link to the chapter. The key goes only from your browser to the chosen provider; it is stored in the browser only if you tick "remember".

### Worked problems, method of images, Biot–Savart, rules

- **Worked problems**: 86 original exam-level problems (8–9 per topic) with SVG figures, step-by-step and full solutions, a simple explanation and engine-verified answers. Each cites the textbook section that teaches the topic; none is a copy of a textbook or exam question.
- **Method of images**: charge above a grounded plane next to its equivalent Q / −Q pair, induced surface charge, force, energy, the uniqueness argument and a 90° corner.
- **Biot–Savart law**: the line integral evaluated as an explicit sum of current elements and compared with the closed forms for a finite wire, a loop and a square.
- **Rules & conventions**: hat notation, cross products, coordinate systems, operators, theorems, sign conventions, units, constants and exam pitfalls.
- Every topic page also has a plain-language "Simple explanation" next to the professional derivation.

### Verification report

The **Verification report** page runs 30 reference problems (at least three per module): the theoretical value is evaluated from the textbook closed form with plain arithmetic, the numerical value is what the site computes, and the table lists both with the percentage error. It can be downloaded as CSV. `tests/test_report.py` keeps every case passing.

`tests/test_routes.py` checks that the browser build (`engine/routes.py`) returns exactly the same results as the local server for every route.

## Run locally

```bash
pip install -r requirements.txt
python run.py
```

On Windows you can also double-click `Start_ElectroField.bat`. Opens http://127.0.0.1:8765. Verification suite (439 tests): `python -m pytest -q -p no:anyio tests`

### Assistant

The "Ask the assistant" panel uses Claude (`claude-opus-5-5`) with tool use: the model only chooses which engine solver to run and with which parameters; every number comes from the engine, and the matching chapter opens with those parameters. It needs Anthropic credentials before starting the server, e.g. `ANTHROPIC_API_KEY`. Everything else works offline without it.

## Chapters

| # | Chapter | Status |
|---|---------|--------|
| 0 | 1-D, 2-D and 3-D waves: plane / cylindrical / spherical spreading, field maps, "what if I increase…" table | ready |
| 1 | Vectors & coordinate systems: dl, ds, dv, dimensioned sections, conversions | ready |
| 2 | Electrostatics: point charges & images, Gauss's law, capacitors | ready |
| 3 | Magnetostatics: wires & forces, loops/Helmholtz/solenoid (exact), Ampère's law, inductance | ready |
| 4 | Maxwell's equations, boundary conditions, Faraday, displacement current | ready |
| 5 | Plane waves in lossy media: α, β, ηc, δs, power, sweeps | ready |
| 6 | Reflection & transmission: normal (lossy) and oblique incidence, Fresnel, Brewster, TIR | ready |
| 7 | Transmission lines: Γ, VSWR, Zin, standing waves, Smith chart, λ/4 and stub matching | ready |
| 8 | Waveguides & antennas: TE/TM modes, dispersion, dipoles, linear arrays | ready |

### Question bank

27 original problem templates (2–4 per chapter) in the style of Ulaby/Cheng end-of-chapter exercises. Numbers are drawn from a seeded generator, so `id/seed` reproduces a problem. Answers are computed by the engine and accepted only when the solver's own checks pass; the full derivation is shown and the chapter opens with the same values.

## Layout

```
engine/     physics + derivations + checks (NumPy/SciPy)
server/     FastAPI API, serves web/; assistant.py = Claude tool-use loop over the engine
web/        frontend (ES modules, Plotly, KaTeX)
tests/      pytest verification against textbook results
engine/routes.py  server-free dispatcher used by the browser build
legacy/     previous single-file WebGL workbench (legacy/index.html) and desktop solver
index.html  GitHub Pages entry point → web/
```

## License
MIT
