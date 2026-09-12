from Mugil.evaluation.action_validator import validate_selected_action


def make_goal():
    return {
        "goal_id": "G001",
        "objective": "Recover laptop inventory",
        "location": "warehouse_1",
        "constraints": {
            "required_quantity": 10,
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


def test_missing_goal_is_rejected():
    result = validate_selected_action(
        make_action(),
        None,
    )

    assert result["valid"] is False
    assert result["status"] == "FAIL"


def test_missing_action_id_is_rejected():
    action = make_action()
    action["action_id"] = ""

    result = validate_selected_action(
        action,
        make_goal(),
    )

    assert result["valid"] is False
    assert result["checks"]["action_id_present"] is False


def test_missing_parameters_are_rejected():
    action = make_action()
    action["parameters"] = {}

    result = validate_selected_action(
        action,
        make_goal(),
    )

    assert result["valid"] is False
    assert result["checks"]["parameters_present"] is False


def test_invalid_quantity_is_rejected():
    action = make_action()
    action["parameters"]["quantity"] = "ten"

    result = validate_selected_action(
        action,
        make_goal(),
    )

    assert result["valid"] is False
    assert result["checks"]["quantity_sufficient"] is False


def test_negative_quantity_is_rejected():
    action = make_action()
    action["parameters"]["quantity"] = -5

    result = validate_selected_action(
        action,
        make_goal(),
    )

    assert result["valid"] is False
    assert result["checks"]["quantity_sufficient"] is False


def test_purchase_without_location_is_rejected():
    action = make_action()
    action["parameters"].pop("location")

    result = validate_selected_action(
        action,
        make_goal(),
    )

    assert result["valid"] is False
    assert result["checks"]["location_matches"] is False


def test_transfer_with_wrong_destination_is_rejected():
    action = {
        "action_id": "A002",
        "operation": "transfer",
        "parameters": {
            "item": "laptop",
            "quantity": 10,
            "source": "warehouse_2",
            "destination": "warehouse_3",
        },
    }

    result = validate_selected_action(
        action,
        make_goal(),
    )

    assert result["valid"] is False
    assert result["checks"]["location_matches"] is False


def test_reroute_with_wrong_destination_is_rejected():
    action = {
        "action_id": "A003",
        "operation": "reroute",
        "parameters": {
            "item": "laptop",
            "quantity": 10,
            "from_location": "warehouse_2",
            "to_location": "warehouse_3",
        },
    }

    result = validate_selected_action(
        action,
        make_goal(),
    )

    assert result["valid"] is False
    assert result["checks"]["location_matches"] is False


def test_invalid_parameters_type_is_handled_safely():
    action = make_action()
    action["parameters"] = "invalid"

    result = validate_selected_action(
        action,
        make_goal(),
    )

    assert result["valid"] is False
    assert result["status"] == "FAIL"


def test_empty_excluded_action_list_does_not_reject_action():
    result = validate_selected_action(
        make_action(),
        make_goal(),
        excluded_action_ids=[],
    )

    assert result["valid"] is True
    assert result["checks"]["not_excluded"] is True