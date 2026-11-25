# Explained solutions — pilot on "Maxwell & boundaries"

Date: 2026-11-25 · Status: draft, awaiting approval

## Intent

ElectroField is meant to become a product, not a demo. Today the two practice pages fall short:

- **Question bank** shows the solver's generic derivation table as "the solution". For a θ₂ question it also prints
  "Normal D jumps by ρs" with ρs = 0 and an energy density that was never asked. The student sees *a* calculation,
  not *the answer to their question*.
- **Worked problems** are 86 one-sentence numeric problems with a one-line "approach". No conceptual questions.

Goal: a student who reads a solution has no question left, and it is still short. Problems should be useful both
for exam preparation and for strong students who want to think. Everything shown stays engine-verified.

## Goals

1. Every solution is a written explanation first, in this order:
   **What is asked → Idea (which law, why) → Steps (short, each with its formula and the number) → Answer →
   "If the question had asked…" (variants with formulas and engine-computed values).**
   The raw engine derivation table and the independent checks move into a collapsed "Engine derivation & checks".
2. Worked problems: **15 per topic, 8 conceptual + 7 numerical.** Conceptual = a question answered in words
   (a model answer), backed where possible by an engine number or a small plot that proves the claim.
3. Question bank: three levels — 1 direct, 2 multi-step, 3 advanced (several ideas combined, inverse/design
   questions). Explanations use the same format, with the random numbers filled in.
4. Figures are clean and readable: they show what is given, never the answer; the solution may show a second
   figure drawn from engine values.

## Non-goals (this pilot)

- Grading of conceptual answers; a midterm/final exam mode (later, separate page).
- The other 9 topics — they follow after the pilot format is approved.
- Turkish UI. Content is English, Ulaby & Ravaioli / Cheng notation.
- LLM-written explanations at run time.

## Anti-goals (failure even if it "works")

- A cleaned-up dump of engine steps presented as an explanation.
- Any number in the prose that did not come from the engine (no hand-typed results).
- Long walls of text. Targets: explanation ≤ 6 steps, each ≤ 2 sentences; conceptual model answer ≤ 120 words.
- Copied textbook or exam wording/figures. Problems are original; `ref` cites the section only.
- Decoration: emoji, gradients, glow, "✨", filler sentences ("Great question!", "Let's dive in").

## Approaches considered

1. **Hand-written explanation, numbers from the engine** — chosen. Original prose per problem/template with named
   placeholders (`{E1t}`) filled from the engine result; variants re-run the engine with changed inputs.
   Most writing, but readable and verifiable.
2. Explanations generated from engine steps (filter + sentence per step type). Cheap, but reads like a dump —
   the thing being fixed.
3. LLM tutor writes explanations live. Not verifiable, needs a key, contradicts "everything verified".

## Design

### Content format (engine side)

A shared helper module `engine/explain.py` (new file → add to `ENGINE_FILES` in `web/js/api.js`):

```python
X(asked="…",                       # one sentence: what exactly is wanted
  idea="…",                        # the law and why it applies here (1–2 sentences)
  steps=[S("Split E₁ into parts along and across the boundary.",
           r"E_{1t}=|E_1|\sin\theta_1={E1t}\ \text{V/m}"), …],
  answer="θ₂ = {th2} °",
  whatif=[W("…if ε_r2 were doubled?", {"eps2": "2*eps2"},
            "tan θ₂ scales with ε₂/ε₁, so θ₂ grows toward 90°.", r"\theta_2=\tan^{-1}(…)={th2}")],
  vals={"E1t": lambda r: r["values"]["F1"][0], "th2": V("theta2_deg"), …})
```

- `vals` maps placeholder → extractor on the engine result. Rendering formats with the engine's `fmt`
  (4 significant figures, unit kept in text).
- A what-if re-runs the same route with changed params; its own checks must pass and its placeholders are
  filled from *that* run.
- Conceptual problems use `kind="concept"`, `answer_text` (model answer) and optional `evidence`: one engine
  call (or a sweep) whose numbers or small plot prove the claim, e.g. θ₂ vs ε_r2/ε_r1.
- Inverse/design questions (level 3, e.g. "what rotation speed gives 120 V peak?") are solved by root-finding
  on the engine forward model; the forward residual is added as an extra independent check.

Rendering happens in Python (`explain.render(x, result)`) so the frontend only displays strings — keeps the
rule "the frontend never computes physics". Routes `wk/solve` and `qb/check` return an extra `explain` object;
problems without one fall back to today's table (other chapters keep working during roll-out).

### Page layout (both pages)

```
[Problem n · conceptual|numerical · level · Ulaby §4-8]
Problem text (2–4 sentences, all data stated)        [figure: givens only]
[Show solution] [Next step]

What is asked   one line
Idea            law + why it applies
Step 1  sentence          formula = number unit
Step 2  …
Answer          θ₂ = 78.95°   ✓ verified (3 checks)
If the question had asked…
  • |E₂| instead?   formula = number
  • ε_r2 doubled?   formula = number, one-line reason
▸ Engine derivation & independent checks (collapsed)
[Open the chapter with these values →]
```

Conceptual cards: text → model answer → evidence (number/plot) → "A common mistake" line where useful.

### Pilot content — topic "Maxwell & boundaries" (Ulaby ch. 4-8, 5-7, 6)

Worked problems, 15 (rewrite the existing 8 numeric into 7 richer ones + 8 new conceptual). Draft list:

Numerical (7): E refraction at a dielectric (|E₂|, θ₂); boundary with surface charge; H entering iron;
AC generator with a load (peak EMF, average power); transformer EMF; conductor-or-dielectric crossover
frequency for wet soil; charge relaxation time in copper vs. distilled water.

Conceptual (8): why tangential E is continuous (thin-loop argument); what a surface charge does to normal D;
why H inside iron lies nearly along the surface (shielding); a ring spinning about an axis parallel to a uniform
B — is there an EMF?; Lenz's law direction for an approaching magnet; why Ampère's law needs displacement current
(charging capacitor); why sea water is a conductor at 1 kHz but a dielectric at 100 GHz; why excess charge lives
on a conductor's surface.

Question bank, Maxwell chapter: give the 3 existing templates explanations + variants, and add ~5 templates
so every level has ≥2: H-boundary angle (L2), surface charge from measured fields (L3, inverse), field through a
slab into a third medium — θ₃ independent of the slab (L3), generator speed for a target EMF (L3, inverse),
|J_c|/|J_d| target frequency (L2).

Material data (σ, εr, μr of copper, sea water, soil, iron…) use the values tabulated in Ulaby & Ravaioli's
appendix tables, cited by section.

### Figures

- `figures.js` gets an angle-arc helper and a readable label layout; minimum 12 px text, labels never on lines.
- Question figure shows givens only. A solution figure (e.g. interface with E₂ and θ₂) is drawn from values the
  engine returns, never computed in JS.
- E red, H blue, S green, single accent; "not to scale" stated when it is not.
- Evidence plots use the existing Plotly style (axis titles with units, no legend when one trace).

### Tests

- `tests/test_worked.py`: Maxwell topic has 15 problems, 8 concept / 7 numeric; every explanation renders
  with no leftover `{…}`; every what-if run passes its checks; length limits hold.
- `tests/test_questions.py`: every template × 5 seeds renders its explanation and variants; new L3 inverse
  templates pass the forward-residual check.
- `tests/test_routes.py`: parity for the extended `wk/solve` and `qb/check` payloads.
- `engine/report.py`: ≥3 cases for the inverse solvers (theory in plain `math`).

## Left to the builder

- Exact placeholder syntax and how `explain.py` formats units/significant figures.
- Whether content moves to one file per topic when rolling out (fine to keep in `worked.py`/`questions.py`
  for the pilot).
- Final wording of each problem, within the length limits and anti-goals above.

## After the pilot

User reviews the Maxwell pages. Once the format is approved, roll out to the other 9 topics
(one topic per commit), then the exam mode as a separate project.
