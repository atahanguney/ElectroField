import math
import pytest
from engine import worked

IDS = [p["id"] for p in worked.P]


@pytest.mark.parametrize("pid", IDS)
def test_problem_solves_and_verifies(pid):
    r = worked.solve(pid)
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]
    kind = next(p["kind"] for p in worked.P if p["id"] == pid)
    assert r["answers"] or kind == "concept"
    assert all(math.isfinite(a["value"]) for a in r["answers"])


def test_every_topic_has_at_least_eight():
    from collections import Counter
    n = Counter(p["topic"] for p in worked.P)
    assert set(n) == set(worked.TOPICS)
    assert min(n.values()) >= 8, n


def test_known_answers():
    get = lambda pid, i=0: worked.solve(pid)["answers"][i]["value"]
    by = {p["title"]: p["id"] for p in worked.P}
    assert get(by["Point source: doubling the distance"]) == pytest.approx(-6.0206, abs=1e-3)
    assert get(by["Resistive mismatch"], 1) == pytest.approx(2.0, rel=1e-9)
    assert get(by["Quarter-wave transformer at the voltage minimum"]) == pytest.approx(25.0, rel=1e-9)
    assert get(by["WR-90 cut-off"]) == pytest.approx(6.557, rel=1e-3)
    assert get(by["Brewster angle"]) == pytest.approx(63.435, abs=1e-3)
    assert get(by["Centre of a loop"]) == pytest.approx(20.0, rel=1e-9)


def test_ids_unique():
    assert len(set(IDS)) == len(IDS)


@pytest.fixture
def concept_problem():
    from engine.explain import X, S, V
    n = len(worked.P)
    worked.px("maxwell", "Ulaby & Ravaioli Sec. 4-8", "basic", "tmp concept", "Why?", {"type": "interface", "e1": 1, "e2": 4, "theta": 40},
              "mx/boundary", {"kind": "E", "eps1": 1, "eps2": 4, "F1": 100, "theta1_deg": 40}, [],
              X(asked="Why E₂t = E₁t.", idea="Thin loop.", steps=[S("E₂t = «t» V/m.")], answer_text="Because the loop integral vanishes.",
                vals={"t": V("F2", 0)}), "concept")
    yield worked.P[-1]["id"]
    del worked.P[n:]


def test_concept_problem_has_no_answers_but_explains(concept_problem):
    r = worked.solve(concept_problem)
    assert r["answers"] == []
    assert r["explain"]["answer_text"] and r["explain"]["verified"]
    assert "64.28" in r["explain"]["steps"][0]["say"]


def test_catalog_has_kind():
    cat = worked.catalog()["problems"]
    assert all(c["kind"] in ("numeric", "concept") for c in cat)
    assert all("x" not in c and "has_explain" in c for c in cat)


def test_old_problems_have_no_explain():
    old = next(p for p in worked.P if p.get("x") is None)
    assert worked.solve(old["id"])["explain"] is None
