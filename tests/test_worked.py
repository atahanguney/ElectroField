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


def test_every_problem_is_explained():
    assert [p["id"] for p in worked.P if p.get("x") is None] == []


# ---------------------------------------------------------------- explained Maxwell pilot
import json
import re
from engine.constants import EPS0

MAX = [p for p in worked.P if p["topic"] == "maxwell"]
_sentences = lambda s: len([x for x in re.split(r"(?<=[.!?])\s+", s.strip()) if x])


def test_maxwell_has_15_problems_8_concept_7_numeric():
    kinds = [p["kind"] for p in MAX]
    assert len(MAX) == 15 and kinds.count("concept") == 8 and kinds.count("numeric") == 7


@pytest.mark.parametrize("pid", [p["id"] for p in MAX])
def test_maxwell_explanations_complete(pid):
    prob = next(p for p in MAX if p["id"] == pid)
    ex = worked.solve(pid)["explain"]
    assert ex and ex["verified"]
    assert "«" not in json.dumps(ex, ensure_ascii=False)
    assert ex["asked"] and ex["idea"] and 1 <= len(ex["steps"]) <= 6
    assert all(_sentences(s["say"]) <= 2 for s in ex["steps"]), [s["say"] for s in ex["steps"]]
    if prob["kind"] == "numeric":
        assert ex["answer"] and len(ex["whatif"]) >= 2
    else:
        assert ex["answer_text"] and len(ex["answer_text"].split()) <= 120


def test_maxwell_known_answers():
    by = {p["title"]: p["id"] for p in MAX}
    get = lambda t, i=0: worked.solve(by[t])["answers"][i]["value"]
    s60, c60 = math.sin(math.radians(60)), math.cos(math.radians(60))
    assert get("Refraction of E at a dielectric", 0) == pytest.approx(math.hypot(100 * s60, 100 * c60 / 5), rel=1e-12)
    assert get("Refraction of E at a dielectric", 1) == pytest.approx(math.degrees(math.atan(5 * math.tan(math.radians(60)))), rel=1e-12)
    V = 50 * 0.3 * 0.04 * 2 * math.pi * 60
    assert get("Generator driving a load", 0) == pytest.approx(V, rel=2e-4)
    assert get("Generator driving a load", 1) == pytest.approx(V ** 2 / 20, rel=4e-4)
    assert get("Charge relaxation: copper vs distilled water") == pytest.approx(EPS0 / 5.8e7, rel=1e-12)


def _ex(title):
    return worked.solve(next(p["id"] for p in MAX if p["title"].startswith(title)))["explain"]


def test_sea_water_uses_engine_crossover_and_ulaby_labels():
    ex = _ex("Sea water")
    fc = worked.solve(next(p["id"] for p in MAX if p["title"].startswith("Sea water")))
    assert "near 1 GHz" not in ex["answer_text"]
    assert "low-loss dielectric" in ex["answer_text"]
    assert "lossy dielectric at 100 GHz" not in next(p["text"] for p in MAX if p["title"].startswith("Sea water"))


def test_wet_soil_at_1ghz_is_quasi_conductor():
    assert "quasi-conductor" in _ex("Wet soil")["whatif"][0]["say"]


def test_relaxation_question_asks_only_what_it_answers():
    p = next(p for p in MAX if p["title"].startswith("Charge relaxation"))
    assert "Compare" not in p["text"]


def test_wording_fixes_from_review():
    assert "unless it is exactly normal" not in _ex("Why H in iron")["answer_text"]
    assert "long sides" not in _ex("Zero flux")["answer_text"]
    assert "which may be along B" not in _ex("Which way")["mistake"]
    assert "εr from 1 to 4" not in _ex("What a surface charge")["evidence_say"]


def test_transformer_problems_draw_a_tilted_loop():
    for t in ("EMF in a tilted loop", "Which way"):
        assert next(p for p in MAX if p["title"].startswith(t))["fig"]["type"] == "tloop"


# ---------------------------------------------------------------- every explained topic: 15 problems, 8 conceptual + 7 numerical
DONE = list(worked.TOPICS)


@pytest.mark.parametrize("topic", DONE)
def test_topic_has_15_problems_8_concept_7_numeric(topic):
    kinds = [p["kind"] for p in worked.P if p["topic"] == topic]
    assert len(kinds) == 15 and kinds.count("concept") == 8 and kinds.count("numeric") == 7, kinds


@pytest.mark.parametrize("pid", [p["id"] for p in worked.P if p.get("x")])
def test_every_explanation_is_complete(pid):
    prob = next(p for p in worked.P if p["id"] == pid)
    ex = worked.solve(pid)["explain"]
    assert ex["verified"] and "«" not in json.dumps(ex, ensure_ascii=False)
    assert ex["asked"] and ex["idea"] and 1 <= len(ex["steps"]) <= 6
    assert all(_sentences(s["say"]) <= 2 for s in ex["steps"]), [s["say"] for s in ex["steps"]]
    if prob["kind"] == "numeric":
        assert ex["answer"] and len(ex["whatif"]) >= 2
    else:
        assert ex["answer_text"] and len(ex["answer_text"].split()) <= 120, len(ex["answer_text"].split())
