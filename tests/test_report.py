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
