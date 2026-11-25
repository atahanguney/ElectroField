import math
import pytest
from engine import questions as qb

IDS = [t["id"] for t in qb.T]


@pytest.mark.parametrize("qid", IDS)
@pytest.mark.parametrize("seed", [1, 7, 42, 1234, 99991])
def test_every_template_solves_and_verifies(qid, seed):
    g = qb.generate(qid=qid, seed=seed)
    assert g["text"] and g["id"] == qid
    out = qb.check(qid, seed)
    assert out["verified"], [c for c in out["checks"] if not c["passed"]]
    assert out["answer"] is not None and math.isfinite(out["answer"])
    assert qb.check(qid, seed, out["answer"])["correct"]


@pytest.mark.parametrize("qid", IDS)
def test_wrong_answer_rejected(qid):
    a = qb.check(qid, 5)["answer"]
    wrong = a * 1.2 + (1.0 if abs(a) < 5 else 0)
    assert not qb.check(qid, 5, wrong)["correct"]


def test_reproducible():
    assert qb.generate(qid="c5-skin", seed=3)["text"] == qb.generate(qid="c5-skin", seed=3)["text"]


def test_filter_by_chapter():
    for s in range(10):
        assert qb.generate(chapter="tlines", seed=s)["chapter"] == "tlines"


def test_all_chapters_covered():
    assert {t["chapter"] for t in qb.T} == {"dimensions", "coordinates", "electrostatics", "magnetostatics", "maxwell", "waves", "reflection", "tlines", "radiation"}


# ---------------------------------------------------------------- explained templates
import json
import numpy as np

SEEDS = [1, 7, 42, 1234, 99991]
EXPL = [t["id"] for t in qb.T if t.get("x")]
MAXW = [t for t in qb.T if t["chapter"] == "maxwell"]


@pytest.mark.parametrize("qid", EXPL)
@pytest.mark.parametrize("seed", SEEDS)
def test_every_template_explains(qid, seed):
    ex = qb.check(qid, seed)["explain"]
    assert ex and ex["verified"]
    assert "«" not in json.dumps(ex, ensure_ascii=False)
    assert ex["asked"] and ex["answer"] and 1 <= len(ex["steps"]) <= 6 and len(ex["whatif"]) >= 2


def test_maxwell_templates_all_explained():
    assert {t["id"] for t in MAXW} <= set(EXPL)


def test_maxwell_levels():
    from collections import Counter
    n = Counter(t["level"] for t in MAXW)
    assert set(n) == {1, 2, 3} and min(n.values()) >= 2, n


@pytest.mark.parametrize("qid", ["c4-gen-speed", "c4-ratio-freq", "c4-rhos"])
@pytest.mark.parametrize("seed", SEEDS)
def test_inverse_residual_check(qid, seed):
    out = qb.check(qid, seed)
    c = [c for c in out["checks"] if c["label"] == "forward model reproduces the target"]
    assert c and c[0]["passed"] and out["verified"]


@pytest.mark.parametrize("seed", SEEDS)
def test_slab_independent_of_middle(seed):
    p = qb.BY_ID["c4-slab"]["gen"](np.random.default_rng(seed))
    want = math.degrees(math.atan(p["e3"] * math.tan(math.radians(p["th"]))))
    assert qb.check("c4-slab", seed)["answer"] == pytest.approx(want, abs=1e-9)


@pytest.mark.parametrize("seed", SEEDS)
def test_ratio_freq_closed_form(seed):
    from engine.constants import EPS0
    p = qb.BY_ID["c4-ratio-freq"]["gen"](np.random.default_rng(seed))
    want = p["s"] / (2 * math.pi * EPS0 * p["er"] * p["k"]) * 1e-6
    assert qb.check("c4-ratio-freq", seed)["answer"] == pytest.approx(want, rel=1e-9)


@pytest.mark.parametrize("seed", SEEDS)
def test_rhos_closed_form(seed):
    from engine.constants import EPS0
    p = qb.BY_ID["c4-rhos"]["gen"](np.random.default_rng(seed))
    want = EPS0 * (p["e1"] * p["E"] * math.cos(math.radians(p["th"])) - p["e2"] * p["E2n"]) * 1e9
    assert qb.check("c4-rhos", seed)["answer"] == pytest.approx(want, rel=1e-9)


def test_question_figure_shows_givens_only():
    g = qb.generate(qid="c4-refraction", seed=3)
    assert g["fig"]["type"] == "interface" and "theta2" not in g["fig"]
    assert qb.generate(qid="c5-skin", seed=3)["fig"] == {"type": "slab", "label": "silver"}



@pytest.mark.parametrize("seed", SEEDS)
def test_rhos_uses_one_unit_and_unicode_minus(seed):
    out = qb.check("c4-rhos", seed)
    assert all("C/m" not in s["tex"] or "nC/m" in s["tex"] for s in out["explain"]["steps"] if s["tex"])
    g = qb.generate(qid="c4-rhos", seed=seed)
    assert "= -" not in g["text"]


def test_rhos_negative_measurement_prints_unicode_minus():
    seed = next(s for s in range(400) if qb.BY_ID["c4-rhos"]["gen"](np.random.default_rng(s))["E2n"] < 0)
    assert "E₂n = −" in qb.generate(qid="c4-rhos", seed=seed)["text"]


def test_every_template_has_explanation_and_figure():
    assert [t["id"] for t in qb.T if not t["x"]] == []
    assert [t["id"] for t in qb.T if not t["fig"]] == []


# ---------------------------------------------------------------- level 2–3 templates in every chapter
from engine.constants import EPS0 as _E0, MU0 as _M0, C0 as _C0
_g = lambda qid, s: qb.BY_ID[qid]["gen"](np.random.default_rng(s))
_a = lambda qid, s: qb.check(qid, s)["answer"]


def test_every_chapter_has_a_level_3_template():
    assert {t["chapter"] for t in qb.T if t["level"] == 3} == {t["chapter"] for t in qb.T}


@pytest.mark.parametrize("seed", SEEDS)
def test_closed_forms_of_new_templates(seed):
    p = _g("c2-coax-opt", seed)
    assert _a("c2-coax-opt", seed) == pytest.approx(p["b"] / math.e, rel=1e-5)
    p = _g("c2-null-point", seed)
    assert _a("c2-null-point", seed) == pytest.approx(p["d"] / (1 + math.sqrt(p["q2"] / p["q1"])), rel=1e-6)
    p = _g("c3-loop-half", seed)
    assert _a("c3-loop-half", seed) == pytest.approx(p["a"] * math.sqrt(2 ** (2 / 3) - 1), rel=1e-6)
    p = _g("c5-depth-freq", seed)
    al = p["L"] / p["d"] / (20 * math.log10(math.e))
    assert _a("c5-depth-freq", seed) == pytest.approx(al ** 2 / (math.pi * _M0 * 4) / 1e3, rel=2e-3)   # good-conductor limit
    p = _g("c8-array-delta", seed)
    assert _a("c8-array-delta", seed) == pytest.approx(-360 * p["d"] * math.cos(math.radians(p["t"])), abs=1e-6)
    p = _g("c8-wg-band", seed)
    a, b = p["a"] * 1e-3, qb._nice(p["a"] * p["ba"], 4) * 1e-3
    assert _a("c8-wg-band", seed) == pytest.approx(min(_C0 / a, _C0 / (2 * b)) / 1e9, rel=1e-9)
    p = _g("c1-vec-theta", seed)
    R = math.sqrt(p["x"] ** 2 + p["y"] ** 2 + p["z"] ** 2); th = math.acos(p["z"] / R); ph = math.atan2(p["y"], p["x"])
    want = p["Ax"] * math.cos(th) * math.cos(ph) + p["Ay"] * math.cos(th) * math.sin(ph) - p["Az"] * math.sin(th)
    assert _a("c1-vec-theta", seed) == pytest.approx(want, abs=1e-9)


@pytest.mark.parametrize("seed", SEEDS)
def test_lossy_spread_is_spreading_plus_absorption(seed):
    p = _g("c0-lossy-spread", seed)
    w, eps = 2 * math.pi * p["f"] * 1e6, 20 * _E0
    alpha = w * math.sqrt(_M0 * eps / 2 * (math.sqrt(1 + (p["s"] / (w * eps)) ** 2) - 1))
    R1, R2 = p["r1"], p["k"] * p["r1"]
    want = 20 * math.log10(R1 / R2) - 20 * math.log10(math.e) * alpha * (R2 - R1)
    assert _a("c0-lossy-spread", seed) == pytest.approx(want, abs=1e-6)


@pytest.mark.parametrize("seed", SEEDS)
def test_stub_and_angle_templates_verify(seed):
    for qid in ("c7-stub", "c6-angle-R"):
        out = qb.check(qid, seed)
        assert out["verified"], [c["label"] for c in out["checks"] if not c["passed"]]
    p = _g("c6-angle-R", seed)
    th = _a("c6-angle-R", seed)
    ct = math.sqrt(1 - math.sin(math.radians(th)) ** 2 / p["er"]); ci = math.cos(math.radians(th)); n2 = math.sqrt(p["er"])
    assert ((ci - n2 * ct) / (ci + n2 * ct)) ** 2 * 100 == pytest.approx(p["R"], rel=1e-6)
