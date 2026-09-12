from Mugil.evaluation.integration import evaluate_execution


def test_e2e_valid_action_continues():
    action = {
        "action_id": "A001",
        "operation": "purchase",
        "parameters": {
            "item": "laptop",
            "quantity": 100,
            "location": "warehouse_1",
        },
    }

    response = {
        "action_id": "A001",
        "status": "success",
        "result": {
            "delivered_quantity": 100,
            "delivery_time": 2,
            "total_cost": 4000,
            "carbon_emission": 20,
        },
    }

    goal = {
        "goal_id": "G001",
        "objective": "Recover laptop inventory",
        "location": "warehouse_1",
        "constraints": {
            "required_quantity": 100,
            "deadline": 4,
            "max_cost": 5000,
            "carbon_limit": 30,
        },
    }

    output = evaluate_execution(
        response,
        goal,
        selected_action=action,
    )

    assert output["verified"] is True
    assert output["action_validation"]["valid"] is True
    assert output["recommendation"] == "CONTINUE"


def test_e2e_invalid_action_triggers_replan():
    action = {
        "action_id": "A002",
        "operation": "purchase",
        "parameters": {
            "item": "laptop",
            "quantity": 100,
            "location": "warehouse_2",
        },
    }

    response = {
        "action_id": "A002",
        "status": "success",
        "result": {
            "delivered_quantity": 100,
            "delivery_time": 2,
            "total_cost": 4000,
            "carbon_emission": 20,
        },
    }

    goal = {
        "goal_id": "G001",
        "objective": "Recover laptop inventory",
        "location": "warehouse_1",
        "constraints": {
            "required_quantity": 100,
            "deadline": 4,
            "max_cost": 5000,
            "carbon_limit": 30,
        },
    }

    output = evaluate_execution(
        response,
        goal,
        selected_action=action,
    )

    assert output["action_validation"]["valid"] is False
    assert output["recommendation"] == "REPLAN"


def test_e2e_failed_execution_triggers_replan():
    action = {
        "action_id": "A003",
        "operation": "purchase",
        "parameters": {
            "item": "laptop",
            "quantity": 100,
            "location": "warehouse_1",
        },
    }

    response = {
        "action_id": "A003",
        "status": "failed",
        "result": {
            "delivered_quantity": 40,
            "delivery_time": 8,
            "total_cost": 8000,
            "carbon_emission": 60,
        },
    }

    goal = {
        "goal_id": "G001",
        "objective": "Recover laptop inventory",
        "location": "warehouse_1",
        "constraints": {
            "required_quantity": 100,
            "deadline": 4,
            "max_cost": 5000,
            "carbon_limit": 30,
        },
    }

    output = evaluate_execution(
        response,
        goal,
        selected_action=action,
    )

    assert output["verified"] is False
    assert output["recommendation"] == "REPLAN"


def test_e2e_excluded_action_triggers_replan():
    action = {
        "action_id": "A004",
        "operation": "purchase",
        "parameters": {
            "item": "laptop",
            "quantity": 100,
            "location": "warehouse_1",
        },
    }

    response = {
        "action_id": "A004",
        "status": "success",
        "result": {
            "delivered_quantity": 100,
            "delivery_time": 2,
            "total_cost": 4000,
            "carbon_emission": 20,
        },
    }

    goal = {
        "goal_id": "G001",
        "objective": "Recover laptop inventory",
        "location": "warehouse_1",
        "constraints": {
            "required_quantity": 100,
            "deadline": 4,
            "max_cost": 5000,
            "carbon_limit": 30,
        },
    }

    output = evaluate_execution(
        response,
        goal,
        selected_action=action,
        excluded_action_ids=["A004"],
    )

    assert output["action_validation"]["valid"] is False
    assert output["recommendation"] == "REPLAN"