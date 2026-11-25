from engine import report


def test_every_reference_case_passes():
    r = report.run()
    bad = [x for x in r["rows"] if not (x["passed"] and x["engine_checks_passed"])]
    assert not bad, bad
    assert r["all_passed"]


def test_every_module_has_cases():
    mods = {m["module"] for m in report.run()["modules"]}
    assert len(mods) == 9
    assert all(m["cases"] >= 3 for m in report.run()["modules"])


def test_inverse_solver_cases():
    rows = [x for x in report.run()["rows"] if x["route"] == "qb/check"]
    assert len(rows) >= 3 and all(x["passed"] and x["engine_checks_passed"] for x in rows)


def test_engine_checks_read_from_question_bank_verdict(monkeypatch):
    from engine import questions as qb
    real = qb.check
    monkeypatch.setattr(qb, "check", lambda *a, **k: {**real(*a, **k), "verified": False})
    rows = [x for x in report.run()["rows"] if x["route"] == "qb/check"]
    assert rows and not any(x["engine_checks_passed"] for x in rows)
