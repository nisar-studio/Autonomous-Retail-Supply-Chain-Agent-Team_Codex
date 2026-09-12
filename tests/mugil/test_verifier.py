from Mugil.verification.verifier import verify_result


def test_verification_pass():
    result = {
        "goal": {
            "required_quantity": 100,
            "deadline": 4,
            "budget": 15000
        },
        "actual": {
            "delivered_quantity": 100,
            "delivery_time": 2.5,
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
            "deadline": 4,
            "budget": 15000
        },
        "actual": {
            "delivered_quantity": 70,
            "delivery_time": 2.5,
            "total_cost": 12500
        }
    }

    output = verify_result(result)

    assert output["verified"] is False
    assert output["status"] == "FAIL"
    assert output["recommendation"] == "REPLAN"
    assert len(output["errors"]) > 0


def test_verification_fails_deadline():
    result = {
        "goal": {
            "required_quantity": 100,
            "deadline": 4,
            "budget": 15000
        },
        "actual": {
            "delivered_quantity": 100,
            "delivery_time": 5,
            "total_cost": 12500
        }
    }

    output = verify_result(result)

    assert output["verified"] is False
    assert output["status"] == "FAIL"
    assert output["recommendation"] == "REPLAN"


def test_verification_fails_budget():
    result = {
        "goal": {
            "required_quantity": 100,
            "deadline": 4,
            "budget": 15000
        },
        "actual": {
            "delivered_quantity": 100,
            "delivery_time": 2.5,
            "total_cost": 18000
        }
    }

    output = verify_result(result)

    assert output["verified"] is False
    assert output["status"] == "FAIL"
    assert output["recommendation"] == "REPLAN"


def test_verification_passes_when_carbon_is_within_limit():
    result = {
        "goal": {
            "required_quantity": 100,
            "deadline": 4,
            "budget": 15000
        },
        "expected": {
            "required_quantity": 100,
            "deadline": 4,
            "max_cost": 15000,
            "carbon_limit": 50
        },
        "actual": {
            "delivered_quantity": 100,
            "delivery_time": 2.5,
            "total_cost": 12500,
            "carbon_emission": 40
        }
    }

    output = verify_result(result)

    assert output["verified"] is True
    assert output["status"] == "PASS"
    assert output["recommendation"] == "CONTINUE"
    assert output["checks"]["carbon_met"] is True


def test_verification_fails_when_carbon_exceeds_limit():
    result = {
        "goal": {
            "required_quantity": 100,
            "deadline": 4,
            "budget": 15000
        },
        "expected": {
            "required_quantity": 100,
            "deadline": 4,
            "max_cost": 15000,
            "carbon_limit": 50
        },
        "actual": {
            "delivered_quantity": 100,
            "delivery_time": 2.5,
            "total_cost": 12500,
            "carbon_emission": 65
        }
    }

    output = verify_result(result)

    assert output["verified"] is False
    assert output["status"] == "FAIL"
    assert output["recommendation"] == "REPLAN"
    assert output["checks"]["carbon_met"] is False
    assert "Carbon limit" in output["errors"][0]


def test_verification_fails_when_carbon_is_missing():
    result = {
        "goal": {
            "required_quantity": 100,
            "deadline": 4,
            "budget": 15000
        },
        "expected": {
            "required_quantity": 100,
            "deadline": 4,
            "max_cost": 15000,
            "carbon_limit": 50
        },
        "actual": {
            "delivered_quantity": 100,
            "delivery_time": 2.5,
            "total_cost": 12500
        }
    }

    output = verify_result(result)

    assert output["verified"] is False
    assert output["status"] == "FAIL"
    assert output["recommendation"] == "REPLAN"
    assert output["checks"]["carbon_met"] is False
    assert "Actual carbon emission is missing." in output["errors"]


def test_verification_passes_when_no_carbon_limit_is_provided():
    result = {
        "goal": {
            "required_quantity": 100,
            "deadline": 4,
            "budget": 15000
        },
        "expected": {
            "required_quantity": 100,
            "deadline": 4,
            "max_cost": 15000
        },
        "actual": {
            "delivered_quantity": 100,
            "delivery_time": 2.5,
            "total_cost": 12500
        }
    }

    output = verify_result(result)

    assert output["verified"] is True
    assert output["status"] == "PASS"
    assert output["recommendation"] == "CONTINUE"
    assert "carbon_met" not in output["checks"]