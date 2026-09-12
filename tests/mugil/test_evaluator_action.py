from Mugil.evaluation.evaluator import evaluate_result


def make_result():
    return {
        "action_id": "A001",
        "goal": {
            "goal_id": "G001",
            "objective": "Recover laptop inventory",
            "location": "warehouse_1",
        },
        "expected": {
            "required_quantity": 10,
            "deadline": 48,
            "max_cost": 2000,
            "carbon_limit": 10,
        },
        "actual": {
            "delivered_quantity": 10,
            "delivery_time": 24,
            "total_cost": 1000,
            "carbon_emission": 5,
        },
    }


def make_action():
    return {
        "action_id": "A001",
        "operation": "purchase",
        "parameters": {
            "item": "laptop",
            "quantity": 10,
            "location": "warehouse_1",
        },
    }


def make_goal():
    return {
        "goal_id": "G001",
        "objective": "Recover laptop inventory",
        "location": "warehouse_1",
        "constraints": {
            "required_quantity": 10,
        },
    }


def test_valid_action_allows_continue():
    result = make_result()

    evaluation = evaluate_result(
        result,
        action=make_action(),
        goal=make_goal(),
    )

    assert evaluation["action_validation"]["valid"] is True
    assert evaluation["verified"] is True
    assert evaluation["recommendation"] == "CONTINUE"
    assert evaluation["status"] == "PASS"


def test_invalid_action_causes_replan():
    result = make_result()

    action = make_action()
    action["parameters"]["quantity"] = 5

    evaluation = evaluate_result(
        result,
        action=action,
        goal=make_goal(),
    )

    assert evaluation["action_validation"]["valid"] is False
    assert evaluation["recommendation"] == "REPLAN"
    assert evaluation["status"] == "FAIL"


def test_excluded_action_causes_replan():
    result = make_result()

    evaluation = evaluate_result(
        result,
        action=make_action(),
        goal=make_goal(),
        excluded_action_ids=["A001"],
    )

    assert evaluation["action_validation"]["valid"] is False
    assert evaluation["recommendation"] == "REPLAN"


def test_existing_evaluator_still_works_without_action_validation():
    result = make_result()

    evaluation = evaluate_result(result)

    assert evaluation["action_validation"] is None
    assert evaluation["verified"] is True
    assert evaluation["recommendation"] == "CONTINUE"
    assert evaluation["status"] == "PASS"