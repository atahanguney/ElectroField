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
    assert qb.generate(qid="c5-skin", seed=3)["fig"] is None



@pytest.mark.parametrize("seed", SEEDS)
def test_rhos_uses_one_unit_and_unicode_minus(seed):
    out = qb.check("c4-rhos", seed)
    assert all("C/m" not in s["tex"] or "nC/m" in s["tex"] for s in out["explain"]["steps"] if s["tex"])
    g = qb.generate(qid="c4-rhos", seed=seed)
    assert "= -" not in g["text"]


def test_rhos_negative_measurement_prints_unicode_minus():
    seed = next(s for s in range(400) if qb.BY_ID["c4-rhos"]["gen"](np.random.default_rng(s))["E2n"] < 0)
    assert "E₂n = −" in qb.generate(qid="c4-rhos", seed=seed)["text"]
