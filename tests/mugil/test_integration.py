from Mugil.evaluation.integration import evaluate_execution


def test_successful_execution_is_evaluated_correctly():
    execution_response = {
        "action_id": "A001",
        "action": {
            "tool": "order",
            "operation": "create"
        },
        "status": "success",
        "result": {
            "delivered_quantity": 100,
            "delivery_time": 2.5,
            "total_cost": 5000,
            "carbon_emission": 12.4
        },
        "state": {}
    }

    goal = {
        "required_quantity": 100,
        "deadline": 4,
        "budget": 15000,
        "carbon_limit": 50
    }

    output = evaluate_execution(
        execution_response,
        goal
    )

    assert output["action_id"] == "A001"
    assert output["verified"] is True
    assert output["status"] == "PASS"
    assert output["recommendation"] == "CONTINUE"


def test_failed_execution_triggers_replan():
    execution_response = {
        "action_id": "A002",
        "action": {
            "tool": "inventory",
            "operation": "transfer"
        },
        "status": "success",
        "result": {
            "delivered_quantity": 60,
            "delivery_time": 5,
            "total_cost": 18000,
            "carbon_emission": 70
        },
        "state": {}
    }

    goal = {
        "required_quantity": 100,
        "deadline": 4,
        "budget": 15000,
        "carbon_limit": 50
    }

    output = evaluate_execution(
        execution_response,
        goal
    )

    assert output["action_id"] == "A002"
    assert output["verified"] is False
    assert output["status"] == "FAIL"
    assert output["recommendation"] == "REPLAN"


def test_integration_preserves_expected_constraints():
    execution_response = {
        "action_id": "A003",
        "status": "success",
        "result": {
            "delivered_quantity": 100,
            "delivery_time": 2,
            "total_cost": 4000,
            "carbon_emission": 20
        }
    }

    goal = {
        "required_quantity": 100,
        "deadline": 4
    }

    expected = {
        "required_quantity": 100,
        "deadline": 4,
        "max_cost": 5000,
        "carbon_limit": 30
    }

    output = evaluate_execution(
        execution_response,
        goal,
        expected
    )

    assert output["verified"] is True
    assert output["recommendation"] == "CONTINUE"