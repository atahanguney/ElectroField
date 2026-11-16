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
