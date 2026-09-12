from Mugil.evaluation.evaluator import evaluate_result


def test_evaluation_pass():
    result = {
        "goal": {
            "required_quantity": 100,
            "deadline": "2026-09-15T16:30:00",
            "budget": 15000
        },
        "expected": {
            "required_quantity": 100,
            "deadline": "2026-09-15T16:30:00",
            "max_cost": 15000
        },
        "actual": {
            "delivered_quantity": 100,
            "delivery_time": "2026-09-15T16:00:00",
            "total_cost": 12500,
            "supplier_available": True,
            "shipment_delayed": False,
            "inventory_available": True,
            "tool_error": False,
            "feasible": True
        }
    }

    output = evaluate_result(result)

    assert output["verified"] is True
    assert output["status"] == "PASS"
    assert output["recommendation"] == "CONTINUE"
    assert output["score"] == 1.0


def test_evaluation_replans_when_verification_fails():
    result = {
        "goal": {
            "required_quantity": 100,
            "deadline": "2026-09-15T16:30:00",
            "budget": 15000
        },
        "expected": {
            "required_quantity": 100,
            "deadline": "2026-09-15T16:30:00",
            "max_cost": 15000
        },
        "actual": {
            "delivered_quantity": 70,
            "delivery_time": "2026-09-15T16:00:00",
            "total_cost": 12500,
            "supplier_available": True,
            "shipment_delayed": False,
            "inventory_available": True,
            "tool_error": False,
            "feasible": True
        }
    }

    output = evaluate_result(result)

    assert output["verified"] is False
    assert output["status"] == "FAIL"
    assert output["recommendation"] == "REPLAN"


def test_evaluation_replans_when_robustness_fails():
    result = {
        "goal": {
            "required_quantity": 100,
            "deadline": "2026-09-15T16:30:00",
            "budget": 15000
        },
        "expected": {
            "required_quantity": 100,
            "deadline": "2026-09-15T16:30:00",
            "max_cost": 15000
        },
        "actual": {
            "delivered_quantity": 100,
            "delivery_time": "2026-09-15T16:00:00",
            "total_cost": 12500,
            "supplier_available": False,
            "shipment_delayed": False,
            "inventory_available": True,
            "tool_error": False,
            "feasible": True
        }
    }

    output = evaluate_result(result)

    assert output["recommendation"] == "REPLAN"
    assert output["status"] == "FAIL"
    assert output["robustness"]["robust"] is False


def test_evaluation_contains_metrics():
    result = {
        "goal": {
            "required_quantity": 100,
            "deadline": "2026-09-15T16:30:00",
            "budget": 15000
        },
        "expected": {
            "required_quantity": 100
        },
        "actual": {
            "delivered_quantity": 80,
            "delivery_time": "2026-09-15T16:00:00",
            "total_cost": 12000,
            "carbon_emission": 50,
            "supplier_available": True,
            "shipment_delayed": False,
            "inventory_available": True,
            "tool_error": False,
            "feasible": True
        }
    }

    output = evaluate_result(result)

    assert "metrics" in output
    assert output["metrics"]["quantity_fulfillment_rate"] == 0.8
    assert output["metrics"]["total_cost"] == 12000
    assert output["metrics"]["delivery_time"] == "2026-09-15T16:00:00"
    assert output["metrics"]["carbon_emission"] == 50

def test_evaluation_preserves_action_id():
    result = {
        "action_id": "A001",
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
            "total_cost": 12500,
            "supplier_available": True,
            "shipment_delayed": False,
            "inventory_available": True,
            "tool_error": False,
            "feasible": True
        }
    }

    output = evaluate_result(result)

    assert output["action_id"] == "A001"