from Mugil.evaluation.action_validator import validate_selected_action


def test_valid_purchase_action():
    action = {
        "action_id": "A001",
        "operation": "purchase",
        "parameters": {
            "item": "laptop",
            "quantity": 10,
            "location": "warehouse_1",
        },
    }

    goal = {
        "goal_id": "G001",
        "objective": "Recover laptop inventory",
        "location": "warehouse_1",
        "constraints": {
            "required_quantity": 10,
        },
    }

    result = validate_selected_action(action, goal)

    assert result["valid"] is True
    assert result["status"] == "PASS"


def test_action_fails_when_quantity_is_insufficient():
    action = {
        "action_id": "A002",
        "operation": "purchase",
        "parameters": {
            "item": "laptop",
            "quantity": 5,
            "location": "warehouse_1",
        },
    }

    goal = {
        "goal_id": "G001",
        "objective": "Recover laptop inventory",
        "location": "warehouse_1",
        "constraints": {
            "required_quantity": 10,
        },
    }

    result = validate_selected_action(action, goal)

    assert result["valid"] is False
    assert result["checks"]["quantity_sufficient"] is False


def test_action_fails_when_location_does_not_match():
    action = {
        "action_id": "A003",
        "operation": "purchase",
        "parameters": {
            "item": "laptop",
            "quantity": 10,
            "location": "warehouse_2",
        },
    }

    goal = {
        "goal_id": "G001",
        "objective": "Recover laptop inventory",
        "location": "warehouse_1",
        "constraints": {
            "required_quantity": 10,
        },
    }

    result = validate_selected_action(action, goal)

    assert result["valid"] is False
    assert result["checks"]["location_matches"] is False


def test_excluded_action_is_rejected():
    action = {
        "action_id": "A004",
        "operation": "purchase",
        "parameters": {
            "item": "laptop",
            "quantity": 10,
            "location": "warehouse_1",
        },
    }

    goal = {
        "goal_id": "G001",
        "objective": "Recover laptop inventory",
        "location": "warehouse_1",
        "constraints": {
            "required_quantity": 10,
        },
    }

    result = validate_selected_action(
        action,
        goal,
        excluded_action_ids=["A004"],
    )

    assert result["valid"] is False
    assert result["checks"]["not_excluded"] is False


def test_transfer_action_requires_source_and_destination():
    action = {
        "action_id": "A005",
        "operation": "transfer",
        "parameters": {
            "item": "laptop",
            "quantity": 10,
            "destination": "warehouse_1",
        },
    }

    goal = {
        "goal_id": "G001",
        "objective": "Recover laptop inventory",
        "location": "warehouse_1",
        "constraints": {
            "required_quantity": 10,
        },
    }

    result = validate_selected_action(action, goal)

    assert result["valid"] is False
    assert result["checks"]["source_present"] is False


def test_unsupported_operation_is_rejected():
    action = {
        "action_id": "A006",
        "operation": "delete_inventory",
        "parameters": {
            "item": "laptop",
            "quantity": 10,
            "location": "warehouse_1",
        },
    }

    goal = {
        "goal_id": "G001",
        "objective": "Recover laptop inventory",
        "location": "warehouse_1",
        "constraints": {
            "required_quantity": 10,
        },
    }

    result = validate_selected_action(action, goal)

    assert result["valid"] is False
    assert result["checks"]["operation_supported"] is False


def test_missing_action_is_rejected():
    goal = {
        "goal_id": "G001",
        "objective": "Recover laptop inventory",
        "location": "warehouse_1",
        "constraints": {},
    }

    result = validate_selected_action(None, goal)

    assert result["valid"] is False
    assert result["status"] == "FAIL"


def test_dataclass_like_nisar_objects_are_supported():
    class RecoveryGoal:
        def __init__(self):
            self.goal_id = "G001"
            self.objective = "Recover laptop inventory"
            self.location = "warehouse_1"
            self.constraints = {
                "required_quantity": 10
            }

    class SelectedAction:
        def __init__(self):
            self.action_id = "A007"
            self.operation = "purchase"
            self.parameters = {
                "item": "laptop",
                "quantity": 10,
                "location": "warehouse_1",
            }

    result = validate_selected_action(
        SelectedAction(),
        RecoveryGoal(),
    )

    assert result["valid"] is True
    assert result["status"] == "PASS"