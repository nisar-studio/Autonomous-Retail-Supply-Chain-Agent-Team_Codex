from Mugil.evaluation.execution_adapter import adapt_execution_result


def test_adapt_execution_result():
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

    output = adapt_execution_result(
        execution_response,
        goal
    )

    assert output["action_id"] == "A001"
    assert output["goal"] == goal

    assert output["actual"]["delivered_quantity"] == 100
    assert output["actual"]["delivery_time"] == 2.5
    assert output["actual"]["total_cost"] == 5000
    assert output["actual"]["carbon_emission"] == 12.4


def test_adapter_handles_missing_result():
    execution_response = {
        "action_id": "A002",
        "status": "failed"
    }

    goal = {
        "required_quantity": 100,
        "deadline": 4,
        "budget": 15000,
        "carbon_limit": 50
    }

    output = adapt_execution_result(
        execution_response,
        goal
    )

    assert output["action_id"] == "A002"
    assert output["actual"]["delivered_quantity"] is None
    assert output["actual"]["delivery_time"] is None
    assert output["actual"]["total_cost"] is None
    assert output["actual"]["carbon_emission"] is None


def test_adapter_handles_invalid_response():
    output = adapt_execution_result(
        None,
        {
            "required_quantity": 100
        }
    )

    assert output["action_id"] is None
    assert output["actual"] == {}


def test_adapter_preserves_expected_constraints():
    execution_response = {
        "action_id": "A003",
        "result": {
            "delivered_quantity": 80,
            "delivery_time": 3.0,
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

    output = adapt_execution_result(
        execution_response,
        goal,
        expected
    )

    assert output["expected"] == expected
    assert output["actual"]["delivered_quantity"] == 80