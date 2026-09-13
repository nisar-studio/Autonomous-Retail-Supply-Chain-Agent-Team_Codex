from Preethesh.tools.action_adapter import ActionAdapter


def test_purchase_action():
    selected_action = {
        "action_id": "A001",
        "tool": "order",
        "operation": "create",
        "parameters": {
            "item_id": "laptop",
            "quantity": 10,
            "supplier_id": "SUP001",
            "location": "warehouse",
        },
    }

    result = ActionAdapter().adapt(selected_action)

    assert result == {
        "action_id": "A001",
        "action": "purchase",
        "params": {
            "item": "laptop",
            "quantity": 10,
            "location": "warehouse",
        },
    }


def test_transfer_action():
    selected_action = {
        "action_id": "A002",
        "tool": "inventory",
        "operation": "transfer",
        "parameters": {
            "item_id": "laptop",
            "quantity": 3,
            "source": "warehouse",
            "destination": "store",
        },
    }

    result = ActionAdapter().adapt(selected_action)

    assert result == {
        "action_id": "A002",
        "action": "transfer",
        "params": {
            "item": "laptop",
            "quantity": 3,
            "source": "warehouse",
            "destination": "store",
        },
    }


def test_reroute_action():
    selected_action = {
        "action_id": "A003",
        "tool": "inventory",
        "operation": "reroute",
        "parameters": {
            "item_id": "laptop",
            "quantity": 2,
            "from_location": "warehouse",
            "to_location": "store",
        },
    }

    result = ActionAdapter().adapt(selected_action)

    assert result == {
        "action_id": "A003",
        "action": "reroute",
        "params": {
            "item": "laptop",
            "quantity": 2,
            "from_location": "warehouse",
            "to_location": "store",
        },
    }
def test_transfer_action_with_item():
    selected_action = {
        "action_id": "A004",
        "tool": "inventory",
        "operation": "transfer",
        "parameters": {
            "item": "laptop",
            "quantity": 5,
            "source": "warehouse",
            "destination": "store",
        },
    }

    result = ActionAdapter().adapt(selected_action)

    assert result == {
        "action_id": "A004",
        "action": "transfer",
        "params": {
            "item": "laptop",
            "quantity": 5,
            "source": "warehouse",
            "destination": "store",
        },
    }
def test_action_id_is_preserved():
    selected_action = {
        "action_id": "A999",
        "tool": "order",
        "operation": "create",
        "parameters": {
            "item_id": "phone",
            "quantity": 5,
            "supplier_id": "SUP002",
            "location": "warehouse",
        },
    }

    result = ActionAdapter().adapt(selected_action)

    assert result["action_id"] == "A999"
def test_allocation_action():
    selected_action = {
        "action_id": "A005",
        "tool": "inventory",
        "operation": "allocate",
        "parameters": {
            "item_id": "laptop",
            "quantity": 2,
            "location": "store",
        },
    }

    result = ActionAdapter().adapt(selected_action)

    assert result == {
        "action_id": "A005",
        "action": "allocation",
        "params": {
            "item": "laptop",
            "quantity": 2,
            "location": "store",
        },
    }