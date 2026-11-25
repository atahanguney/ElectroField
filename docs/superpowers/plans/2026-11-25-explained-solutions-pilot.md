# Explained Solutions — Maxwell Pilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the "engine table as solution" with written, engine-filled explanations (asked → idea → steps → answer → what-if) on the Maxwell & boundaries topic of both practice pages, with 15 worked problems (8 conceptual, 7 numerical) and 8 question-bank templates over levels 1–3.

**Architecture:** A new `engine/explain.py` turns an original-prose spec (`X`) plus an engine run into a JSON-safe `explain` object; every number in it comes from an engine result (placeholders `«name»`). `worked.solve` and `questions.check` attach it; a new `web/js/explain.js` renders it on both pages, with the old derivation table collapsed beneath. Inverse (level-3 design) questions use root finding on the engine forward model plus a residual check.

**Tech Stack:** Python 3.12, NumPy/SciPy (`scipy.optimize.brentq`), pytest; vanilla ES modules, KaTeX, Plotly.

**Spec:** `docs/superpowers/specs/2026-11-25-explained-solutions-design.md`

## Global Constraints

- Every number in prose/TeX comes from an engine result; no hand-typed results.
- Explanation ≤ 6 steps, each `say` ≤ 2 sentences; conceptual model answer ≤ 120 words.
- Original wording only; `ref` cites a section (Ulaby & Ravaioli / Cheng), never copies text or figures.
- No emoji, gradients, glow, filler sentences. E = red, H = blue, S = green, single accent.
- Content language: English, Ulaby notation.
- Frontend never computes physics; figures draw only givens or engine-returned values.
- Constants only from `engine/constants.py`. New engine file → `ENGINE_FILES` in `web/js/api.js`.
- Other chapters must keep working unchanged (no `explain` → old layout).
- Tests: `python -m pytest -q -p no:anyio tests`. Commits: one per area, short plain one-line messages, GitHub Desktop's bundled git (not on PATH).

## Review Focus

1. A seed that makes a level-3 inverse template unsolvable (target outside the bracket) — expect generation to pick valid data; test runs all templates × 5 seeds through `explain` (Task 4).
2. Placeholder typos (`«E2t»` with no extractor) — expect a `KeyError` at test time, never `«…»` on the page (Task 1 test `test_missing_placeholder_raises`, Task 3/4 "no « left" tests).
3. Extractor returning complex/list/None — `plain`/`fmt` must accept real floats only; extractor must index (Task 1 test `test_render_rejects_non_scalar`).
4. Worked problem with `answers=[]` (conceptual) — `solve` and the page must not crash, card shows model answer (Task 2 test `test_concept_problem_has_no_answers_but_explains`).
5. Pyodide build missing `explain.py` — page breaks only on GitHub Pages; checked manually with `/?backend=pyodide` (Task 6).

---

### Task 1: `engine/explain.py` — spec objects and renderer

**Files:**
- Create: `engine/explain.py`
- Modify: `web/js/api.js:9-10` (add `'explain.py'` to `ENGINE_FILES` before `'questions.py'`)
- Test: `tests/test_explain.py`

**Interfaces:**
- Produces:
  - `S(say: str, tex: str | None = None) -> dict`
  - `W(q: str, change: Callable[[dict], dict], say: str, tex: str | None = None) -> dict` — `change(params) -> new params`
  - `Sweep(param: str, values: list[float], y: Callable[[dict, dict], float], xlabel: str, ylabel: str, logx=False, logy=False) -> dict` — runs the engine once per value
  - `Series(x: Callable, ys: list[tuple[str, Callable]], xlabel: str, ylabel: str, logx=False, logy=False) -> dict` — plots arrays from the base run
  - `X(asked: str, idea: str, steps: list, answer: str = "", answer_text: str = "", whatif: list = (), evidence_say: str = "", plot: dict | None = None, mistake: str = "", fig: Callable[[dict, dict], dict] | None = None, vals: dict[str, Callable[[dict, dict], float]] = {}) -> dict`
  - `V(key: str, i: int | None = None) -> Callable[[dict, dict], float]` — `r["values"][key]` (or `[i]`)
  - `P(key: str) -> Callable` — reads the input params
  - `plain(x: float, sig=4) -> str` — "1.234 × 10⁻³" / "78.95" (prose); TeX uses `derivation.fmt`
  - `render(x: dict, run: Callable[[dict], dict], params: dict, result: dict) -> dict` returning
    `{"asked","idea","steps":[{"say","tex"}],"answer","answer_text","whatif":[{"q","say","tex","verified"}],"evidence_say","plot":{"x","ys":[{"name","y"}],"xlabel","ylabel","logx","logy"}|None,"mistake","fig":dict|None,"verified":bool}`
  - `invert(fn: Callable[..., dict], kw: dict, name: str, key: str | Callable, target: float, lo: float, hi: float, log=False) -> tuple[dict, float]` — `brentq` on `fn(**kw, name=x)` output − target; returns the final engine result with one extra check appended (label `"forward model reproduces the target"`, reference = target, computed = output at root, tol 1e-9) and `all_passed` recomputed.

- [ ] **Step 1: Write the failing tests** in `tests/test_explain.py`:
  - `test_placeholders_filled_from_engine`: `X(asked="θ₂?", idea="…", steps=[S("E₁t is «t» V/m.", r"E_{1t}=«t»")], answer="θ₂ = «th» °", vals={"t": V("F1", 0), "th": V("theta2_deg")})` rendered with `mx.boundary(kind="E", eps1=1, eps2=4, F1=132, theta1_deg=52)` → `"104.0"` in `steps[0]["say"]`, `"104.0"` in `steps[0]["tex"]`, `"78.95"` in `answer`, no `"«"` anywhere in `json.dumps(out)`.
  - `test_whatif_reruns_engine`: `W("εr₂ = 9?", lambda p: {**p, "eps2": 9}, "θ₂ = «th» °")` → text contains `plain(math.degrees(math.atan(9 * math.tan(math.radians(52)))))` and `verified is True`.
  - `test_missing_placeholder_raises`: `S("«nope»")` → `pytest.raises(KeyError)`.
  - `test_render_rejects_non_scalar`: extractor returning the list `r["values"]["F1"]` → `pytest.raises(TypeError)`.
  - `test_sweep_plot_uses_engine`: `Sweep("eps2", [1, 2, 4], V("F2", 0), "εr₂", "E₂t (V/m)")` → `plot["ys"][0]["y"]` all equal `F1·sin θ₁` to 1e-12.
  - `test_invert_finds_root_and_adds_check`: `invert(mx.currents, {"eps_r": 81, "sigma": 4}, "f", "ratio", 10.0, 1e3, 1e9, log=True)` → returned f equals `4 / (2π·81·EPS0·10)` (rel 1e-9); last check label is `"forward model reproduces the target"` and `passed`.
  - `test_plain_format`: `plain(0.001234) == "1.234 × 10⁻³"`, `plain(78.948) == "78.95"`, `plain(0) == "0"`.
- [ ] **Step 2: Run** `python -m pytest -q -p no:anyio tests/test_explain.py` → FAIL (`ModuleNotFoundError: engine.explain`).
- [ ] **Step 3: Implement `engine/explain.py`** with the interfaces above. Substitution: `re.sub(r"«(\w+)»", …)`; prose fields use `plain`, `tex` fields use `fmt`. A what-if's `verified` is that run's `all_passed`; `render(...)["verified"]` = base `all_passed` and every what-if/sweep run passed. `fig` is called with `(result, params)` and returned as-is (must be JSON-safe).
- [ ] **Step 4: Run** the test file → PASS; then the full suite → all pass.
- [ ] **Step 5: Commit** `engine/explain.py`, `tests/test_explain.py`, `web/js/api.js` — message: `Explanation renderer for solutions`.

### Task 2: Worked problems carry explanations and conceptual problems

**Files:**
- Modify: `engine/worked.py` (add `px`, extend `catalog`, `solve`)
- Test: `tests/test_worked.py`

**Interfaces:**
- Consumes: `explain.render`, `X` (Task 1).
- Produces:
  - `px(topic, ref, level, title, text, fig, route, params, answers, x, kind)` — `kind ∈ {"numeric", "concept"}`; stores `approach = x["idea"]`, `simple = ""`, `x`, `kind`. Same id scheme as `p`.
  - Catalog entries gain `"kind"` (default `"numeric"` for old `p` entries) and `"has_explain": bool`; `x` is excluded from the catalog.
  - `solve(pid)` adds `"explain": render(x, lambda q: routes.call(route, q), params, r)` when the problem has `x`, else `None`; `answers` may be `[]` for `kind="concept"`.

- [ ] **Step 1: Failing tests** — `test_concept_problem_has_no_answers_but_explains` (register a temporary concept `px` in a fixture that removes it afterwards; `solve` returns `answers == []`, `explain["answer_text"]` non-empty, `explain["verified"]`); `test_catalog_has_kind` (every entry has `kind`); relax `test_problem_solves_and_verifies` to allow empty answers only when `kind == "concept"`.
- [ ] **Step 2: Run** → FAIL (`px` undefined).
- [ ] **Step 3: Implement** in `engine/worked.py`.
- [ ] **Step 4: Run** full suite → PASS.
- [ ] **Step 5: Commit** `engine/worked.py`, `tests/test_worked.py` — `Worked problems can carry explanations`.

### Task 3: Maxwell worked content — 7 numerical + 8 conceptual

**Files:**
- Modify: `engine/worked.py` (replace the 8 `p(T, …)` calls under `T = "maxwell"` with 15 `px` calls)
- Modify: `web/js/figures.js` (`interface`: θ₁ angle arc; optional `F2`/`theta2` drawn only when the spec carries them; `generator`: show N, R when given)
- Test: `tests/test_worked.py`

**Interfaces:**
- Consumes: `px` (Task 2), `X/S/W/V/P/Sweep/Series` (Task 1). Solution figures use `X(fig=lambda r, p: {"type": "interface", …, "theta2": r["values"]["theta2_deg"], "F2": True})`.

Problems (route · params · answers). Prose is written fresh within the Global Constraints; each numeric one has ≥2 what-ifs.

| # | kind | title | route · params | answers / evidence |
|---|---|---|---|---|
| 1 | numeric | Refraction of E at a dielectric | `mx/boundary` E, eps1 1, eps2 5, F1 100, θ 60 | \|E₂\| V/m, θ₂ °; what-if eps2 2.5, θ₁ 0 |
| 2 | numeric | Boundary with surface charge | E, eps1 2, eps2 4, F1 1000, θ 30, source 2e-9 | \|E₂\|, θ₂; what-if ρs = 0 |
| 3 | numeric | H entering iron | H, mu1 1, mu2 1000, F1 10, θ 45 | θ₂ °, \|H₂\| A/m; what-if μr 100 |
| 4 | numeric | Generator driving a load | `mx/faraday` motional N 50, B0 0.3, w 0.2, l 0.2, f 60, R 10 | V̂ V, P_av W; what-if f 120 |
| 5 | numeric | EMF in a tilted loop | transformer N 10, B0 0.05, w 0.1, l 0.1, f 1000, α 30 | V̂; what-if α 90 |
| 6 | numeric | Wet soil: conductor or dielectric? | `mx/currents` εr 20, σ 0.05, f 1e6 | f_c MHz; what-if f 1e9 → ratio |
| 7 | numeric | Charge relaxation: copper vs distilled water | εr 1, σ 5.8e7 | τ s; what-if εr 81, σ 2e-4 (Ulaby App. B) |
| 8 | concept | Why tangential E cannot jump | boundary E, eps1 1, eps2 4, F1 100, θ 40 | Sweep eps2 [1,2,4,8,16] → E₂t |
| 9 | concept | What a surface charge does to D | same, source varies | Sweep source [0,0.5,1,2]e-9 → E₂n |
| 10 | concept | Why H in iron hugs the surface | H, mu2 varies, θ 30 | Sweep mu2 [1,10,100,1000] → θ₂ |
| 11 | concept | Zero flux, maximum EMF | faraday motional (problem 4 data) | Series t → Φ, V_emf |
| 12 | concept | Which way does the induced current flow? (Lenz) | faraday transformer | Series t → Φ, V_emf (sign) |
| 13 | concept | Why Ampère's law needs displacement current | currents εr 1, σ 0, f 1e6 | text only (Jd value cited) |
| 14 | concept | Sea water: conductor at 1 kHz, dielectric at 100 GHz | currents εr 81, σ 4 | Series sweep f → ratio, log–log; answer notes the constant-εr idealisation (real water's εr falls above ~10 GHz) |
| 15 | concept | Why excess charge lives on a conductor's surface | currents εr 1, σ 5.8e7 | τ cited |

- [ ] **Step 1: Failing tests** — `test_maxwell_has_15_problems_8_concept_7_numeric`; `test_maxwell_explanations_complete` (every Maxwell problem has `explain`, no `«` in `json.dumps`, `verified`, steps ≤ 6, each `say` ≤ 2 sentences by counting `. ` terminators, numeric ones have ≥2 what-ifs); `test_concept_answers_short` (≤ 120 words); `test_maxwell_known_answers` with closed forms in the test: #1 θ₂ = atan(5·tan 60°) → 83.41°, \|E₂\| = hypot(100 sin60, 100 cos60/5); #4 V̂ = 50·0.3·0.04·2π·60 (rel 2e-4), P_av = V̂²/20; #7 τ = EPS0/5.8e7.
- [ ] **Step 2: Run** → FAIL (8 problems, no explain).
- [ ] **Step 3: Write the 15 `px` entries** and the figure changes.
- [ ] **Step 4: Run** full suite → PASS (check `test_every_topic_has_at_least_eight` still holds).
- [ ] **Step 5: Commit** — engine + tests: `Maxwell worked problems rewritten with explanations`; figures separately: `Clearer interface and generator figures`.

### Task 4: Question bank — explanations, level 3, Maxwell templates

**Files:**
- Modify: `engine/questions.py`
- Test: `tests/test_questions.py`

**Interfaces:**
- Consumes: Task 1 (`render`, `invert`, spec helpers).
- Produces:
  - Templates accept optional `x=X(...)` (vals take `(r, p)`), optional `fig=lambda p: spec` (givens only).
  - `generate(...)` adds `"fig": t["fig"](p) or None`; `catalog()` adds `"levels": [1, 2, 3]`.
  - `check(...)` adds `"explain": render(t["x"], lambda q: t["solve"](q)[0], p, r)` or `None`.
  - Inverse adapters call `invert` so the residual check appears in `checks`.

Maxwell templates (8; existing three get `x`):

| id | level | asks | data ranges | solve |
|---|---|---|---|---|
| c4-refraction | 2 | θ₂ | existing | existing |
| c4-generator | 1 | V̂ | existing | existing |
| c4-crossover | 1 | f_c | existing | existing |
| c4-h-refraction | 2 | θ₂ of H (°, abs 0.2) | μr₂ ∈ {50, 200, 1000, 4000}, θ₁ 20–70, H₁ 1–50 A/m | `mx.boundary(kind="H")` |
| c4-ratio-freq | 2 | f where \|J_c\|/\|J_d\| = k (MHz) | εr ∈ {5, 10, 25, 81}, σ log 1e-3–5, k ∈ {0.1, 10, 100} | `invert(mx.currents, …, "f", "ratio", k, …, log=True)` |
| c4-rhos | 3 | ρs (nC/m²) from measured E₂n | εr₁ ∈ {1, 2}, εr₂ ∈ {3, 5, 9}, E₁ 200–2000 V/m, θ₁ 10–60, ρs_true ∈ {−3,−1,1,2,4} nC/m² (E₂n stated = engine forward value, 4 s.f.) | `invert(mx.boundary, …, "source", lambda r: r["values"]["F2"][1], E2n, −1e-6, 1e-6)` (`invert`'s `key` is a values key or a callable on the result) |
| c4-slab | 3 | θ₃ after a slab (°, abs 0.2) | εr₁ 1, εr₂ ∈ {2, 4, 10}, εr₃ ∈ {3, 6, 9}, θ₁ 20–60 | chain two `mx.boundary` runs; result merges both runs' checks; explanation shows tan θ₃ = (ε₃/ε₁) tan θ₁ |
| c4-gen-speed | 3 | rev/s for target V̂ | N, B, w, l as c4-generator, V̂ target 20–400 V | `invert(mx.faraday, {mode: motional, …}, "f", "V_peak", target, 0.1, 1e5, log=True)`, tol 1 % |

- [ ] **Step 1: Failing tests** — `test_every_template_explains` (parametrised ids × seeds [1, 7, 42, 1234, 99991]: templates with `x` render, no `«`, `explain["verified"]`); `test_maxwell_levels` (Maxwell templates span levels {1, 2, 3}, ≥2 per level); `test_inverse_residual_check` (`c4-gen-speed`, `c4-ratio-freq`, `c4-rhos` include the `"forward model reproduces the target"` check, passed); `test_slab_independent_of_middle` (c4-slab answer equals `degrees(atan(εr₃·tan θ₁))` from the generated params). Existing tests stay. In `tests/test_routes.py` add parity cases `("qb/check", {"id": "c4-slab", "seed": 3})` and `("wk/solve", {"id": "max1"})`.
- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3: Implement** the template changes and adapters.
- [ ] **Step 4: Run** full suite → PASS.
- [ ] **Step 5: Commit** `engine/questions.py`, `tests/test_questions.py` — `Question bank: explained Maxwell problems, level 3`.

### Task 5: Frontend — shared explanation view, both pages

**Files:**
- Create: `web/js/explain.js`
- Modify: `web/js/modules/worked.js`, `web/js/modules/questions.js`, `web/css/*.css` (whichever holds `.wk-*`; add `.ex-*` rules)
- Modify: `web/js/figures.js` only if Task 3 left a figure gap

**Interfaces:**
- Consumes: `explain` payload (Task 1 shape), `fig` from `qb/new` (Task 4), `kind` from `wk/catalog` (Task 2).
- Produces: `explainView(ex: object, { stepwise?: boolean }) -> { el: HTMLElement, next(): boolean }` — order: What is asked · Idea · Steps (say + KaTeX) · Answer with "✓ verified" or model answer · Evidence (text + one Plotly plot, axis titles with units, legend only when >1 trace) · A common mistake · If the question had asked… · solution figure. `next()` reveals one more step and returns false when done.

- [ ] **Step 1: Worked page** — when `has_explain`: "Next step" uses `explainView(...).next`, "Full solution" shows the whole view; the engine table + checks go inside `<details><summary>Engine derivation & independent checks</summary>`. Badge shows `conceptual` / `numerical`. "Simple explanation" button hidden when `simple` is empty. Old problems unchanged.
- [ ] **Step 2: Question bank** — level select gains `['3', 'Level 3 — advanced']`; question figure shown beside the text when `q.fig`; after Check/Show solution, `explainView` first, then collapsed engine derivation & checks. Templates without `explain` keep today's layout.
- [ ] **Step 3: Verify in the browser** — `preview_start` the dev server from `.claude/launch.json`; open worked problems → Maxwell and the question bank filtered to Maxwell, each level. Check: no console errors, KaTeX renders, no `«`, plots have axis titles, figures readable at 375 px wide (`resize_window` mobile, then back to desktop). Screenshot each page.
- [ ] **Step 4: Commit** — `web/js/explain.js` + modules + css: `Explained solution view on practice pages`.

### Task 6: Report, docs, Pyodide check

**Files:**
- Modify: `engine/report.py` (≥3 cases for `invert`: currents ratio → f vs `σ/(2πε k)`; faraday speed vs `V̂/(N B A 2π)`; boundary ρs vs `ε₁E₁n − ε₂E₂n`, theory in plain `math`)
- Modify: `CLAUDE.md` (roadmap line: explanation format, `engine/explain.py`, Maxwell pilot done, test count)
- Test: existing report tests

- [ ] **Step 1:** Add the 3 report cases; run full suite → PASS.
- [ ] **Step 2:** Open `/?backend=pyodide` in the preview, solve one worked Maxwell problem and one level-3 question → explanation renders (proves `explain.py` is served).
- [ ] **Step 3: Commit** — report: `Verification cases for inverse solvers`; docs: `Notes on the explained-solution format`.
