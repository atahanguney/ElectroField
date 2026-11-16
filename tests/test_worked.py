import math
import pytest
from engine import worked

IDS = [p["id"] for p in worked.P]


@pytest.mark.parametrize("pid", IDS)
def test_problem_solves_and_verifies(pid):
    r = worked.solve(pid)
    assert r["all_passed"], [c for c in r["checks"] if not c["passed"]]
    assert r["answers"] and all(math.isfinite(a["value"]) for a in r["answers"])


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
