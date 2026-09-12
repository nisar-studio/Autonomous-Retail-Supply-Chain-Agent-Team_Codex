from environment import Environment
from executor import Executor
from failure import FailureHandler


def create_handler():

    environment = Environment()

    executor = Executor(
        environment
    )

    return environment, executor, FailureHandler(
        executor
    )


def test_vendor_unavailable():

    _, _, handler = create_handler()

    result = handler.simulate_failure(
        "vendor_unavailable"
    )

    assert result["status"] == "failure"
    assert result["failure_type"] == "vendor_unavailable"
    assert result["replan_required"] is True


def test_route_unavailable():

    _, _, handler = create_handler()

    result = handler.simulate_failure(
        "route_unavailable"
    )

    assert result["status"] == "failure"
    assert result["failure_type"] == "route_unavailable"
    assert result["replan_required"] is True


def test_inventory_changed():

    environment, _, handler = create_handler()

    result = handler.apply_condition_change(
        "inventory_changed",
        item="Laptop",
        location="Warehouse",
        new_quantity=2
    )

    assert result["status"] == "success"

    assert environment.state[
        "inventory"
    ][
        ("Laptop", "Warehouse")
    ] == 2


def test_shipment_delayed():

    environment, _, handler = create_handler()

    result = handler.apply_condition_change(
        "shipment_delayed",
        shipment_id="S1",
        delay_hours=24
    )

    assert result["status"] == "success"

    assert environment.state[
        "shipments"
    ]["S1"]["status"] == "delayed"


def test_demand_increased():

    environment, _, handler = create_handler()

    result = handler.apply_condition_change(
        "demand_increased",
        item="Laptop",
        increased_quantity=5
    )

    assert result["status"] == "success"

    assert environment.state[
        "demand"
    ]["Laptop"] == 5


def test_controlled_failure_triggers_replanning():

    _, _, handler = create_handler()

    handler.simulate_failure(
        "vendor_unavailable",
        "Vendor A became unavailable."
    )

    plan = [
        {
            "action_id": "test-001",
            "action": "purchase",
            "params": {
                "item": "Laptop",
                "quantity": 5,
                "location": "Warehouse",
                "supplier_id": "Vendor A"
            }
        }
    ]

    result = handler.execute_with_failure_check(
        plan
    )

    assert result["status"] == "failure"

    assert result[
        "execution_result"
    ]["success"] is False

    assert result[
        "failure"
    ]["failure_type"] == "vendor_unavailable"

    assert result[
        "replan_required"
    ] is True

    assert result[
        "replanning_trigger"
    ]["action"] == "request_new_plan"