from Mugil.verification.verifier import verify_result


def test_verification_pass():
    result = {
        "goal": {
            "required_quantity": 100,
            "deadline": "2026-09-15T16:30:00",
            "budget": 15000
        },
        "actual": {
            "delivered_quantity": 100,
            "delivery_time": "2026-09-15T16:00:00",
            "total_cost": 12500
        }
    }

    output = verify_result(result)

    assert output["verified"] is True
    assert output["status"] == "PASS"
    assert output["recommendation"] == "CONTINUE"
    assert output["errors"] == []


def test_verification_fails_quantity():
    result = {
        "goal": {
            "required_quantity": 100,
            "deadline": "2026-09-15T16:30:00",
            "budget": 15000
        },
        "actual": {
            "delivered_quantity": 70,
            "delivery_time": "2026-09-15T16:00:00",
            "total_cost": 12500
        }
    }

    output = verify_result(result)

    assert output["verified"] is False
    assert output["status"] == "FAIL"
    assert output["recommendation"] == "REPLAN"
    assert len(output["errors"]) > 0