from Mugil.evaluation.timeline import create_timeline


def test_timeline_for_successful_result():
    result = {
        "verified": True,
        "recommendation": "CONTINUE"
    }

    timeline = create_timeline(result)

    assert len(timeline) == 6
    assert timeline[0]["step"] == "Goal received"
    assert timeline[0]["status"] == "COMPLETED"
    assert timeline[4]["step"] == "Verification"
    assert timeline[4]["status"] == "PASSED"
    assert timeline[5]["step"] == "Final outcome"
    assert timeline[5]["status"] == "CONTINUE"


def test_timeline_for_failed_result():
    result = {
        "verified": False,
        "recommendation": "REPLAN"
    }

    timeline = create_timeline(result)

    assert len(timeline) == 6
    assert timeline[4]["status"] == "FAILED"
    assert timeline[5]["status"] == "REPLAN"


def test_timeline_handles_invalid_result():
    timeline = create_timeline(None)

    assert timeline == []