from environment import Environment
from executor import Executor
from failure import FailureHandler


# =============================================================
# HELPER
# =============================================================

def create_executor():

    environment = Environment()

    executor = Executor(
        environment
    )

    return environment, executor


# =============================================================
# TEST 1 - PURCHASE
# =============================================================

def test_purchase():

    environment, executor = create_executor()

    result = executor.execute_step({

        "action_id": "test-001",

        "action": "purchase",

        "params": {

            "item": "Laptop",

            "quantity": 10,

            "location": "Warehouse",
        },
    })

    assert result["status"] == "success"

    assert (
        result["action_id"]
        == "test-001"
    )

    assert (
        result["result"]["delivered_quantity"]
        == 10
    )

    assert (
        result["result"]["delivery_time"]
        == 24.0
    )

    assert (
        result["result"]["total_cost"]
        == 1000
    )

    assert (
        result["result"]["carbon_emission"]
        == 5.0
    )


# =============================================================
# TEST 2 - ALLOCATION
# =============================================================

def test_allocation():

    environment, executor = create_executor()

    purchase = executor.execute_step({

        "action_id": "test-002",

        "action": "purchase",

        "params": {

            "item": "Laptop",

            "quantity": 10,

            "location": "Warehouse",
        },
    })

    assert purchase["status"] == "success"

    result = executor.execute_allocation(

        action_id="test-003",

        item="Laptop",

        quantity=5,

        location="Warehouse",
    )

    assert result["status"] == "success"

    assert (
        result["action_id"]
        == "test-003"
    )

    assert (
        result["result"]["allocated_quantity"]
        == 5
    )

    assert (
        result["result"]["total_allocated"]
        == 5
    )


# =============================================================
# TEST 3 - TRANSFER
# =============================================================

def test_transfer():

    environment, executor = create_executor()

    purchase = executor.execute_step({

        "action_id": "test-004",

        "action": "purchase",

        "params": {

            "item": "Laptop",

            "quantity": 10,

            "location": "Warehouse",
        },
    })

    assert purchase["status"] == "success"

    result = executor.execute_step({

        "action_id": "test-005",

        "action": "transfer",

        "params": {

            "item": "Laptop",

            "quantity": 3,

            "source": "Warehouse",

            "destination": "Store",
        },
    })

    assert result["status"] == "success"

    assert (
        result["action_id"]
        == "test-005"
    )

    assert (
        result["result"]["delivered_quantity"]
        == 3
    )

    assert (
        result["result"]["delivery_time"]
        == 4.0
    )

    assert (
        result["result"]["total_cost"]
        == 60
    )

    assert (
        result["result"]["carbon_emission"]
        == 0.6
    )


# =============================================================
# TEST 4 - REROUTE
# =============================================================

def test_reroute():

    environment, executor = create_executor()

    # ---------------------------------------------------------
    # Purchase 10 laptops at Warehouse
    # ---------------------------------------------------------

    purchase = executor.execute_step({

        "action_id": "test-006",

        "action": "purchase",

        "params": {

            "item": "Laptop",

            "quantity": 10,

            "location": "Warehouse",
        },
    })

    assert purchase["status"] == "success"

    # ---------------------------------------------------------
    # Transfer 3 laptops from Warehouse to Store
    # ---------------------------------------------------------

    transfer = executor.execute_step({

        "action_id": "test-007",

        "action": "transfer",

        "params": {

            "item": "Laptop",

            "quantity": 3,

            "source": "Warehouse",

            "destination": "Store",
        },
    })

    assert transfer["status"] == "success"

    # ---------------------------------------------------------
    # Check Store inventory before reroute
    # ---------------------------------------------------------

    store_inventory = (
        environment
        .get_state()
        ["inventory"]
        .get(
            ("Laptop", "Store"),
            0
        )
    )

    assert store_inventory == 3

    # ---------------------------------------------------------
    # Reroute 2 laptops from Store to Office
    # ---------------------------------------------------------

    result = executor.execute_step({

        "action_id": "test-008",

        "action": "reroute",

        "params": {

            "item": "Laptop",

            "quantity": 2,

            "source": "Store",

            "destination": "Office",
        },
    })

    # ---------------------------------------------------------
    # Print complete result if failure occurs
    # ---------------------------------------------------------

    if result["status"] != "success":

        print(
            "\n========== REROUTE FAILED =========="
        )

        print(
            "Execution result:"
        )

        print(result)

        print(
            "\nEnvironment state:"
        )

        print(
            environment.get_state()
        )

        print(
            "=====================================\n"
        )

    assert result["status"] == "success"

    assert (
        result["action_id"]
        == "test-008"
    )

    assert (
        result["result"]["delivered_quantity"]
        == 2
    )

    assert (
        result["result"]["delivery_time"]
        == 6.0
    )

    assert (
        result["result"]["total_cost"]
        == 60
    )

    assert (
        result["result"]["carbon_emission"]
        == 0.6
    )

    # ---------------------------------------------------------
    # Verify final inventory
    # ---------------------------------------------------------

    remaining_store_inventory = (
        environment
        .get_state()
        ["inventory"]
        .get(
            ("Laptop", "Store"),
            0
        )
    )

    office_inventory = (
        environment
        .get_state()
        ["inventory"]
        .get(
            ("Laptop", "Office"),
            0
        )
    )

    assert remaining_store_inventory == 1

    assert office_inventory == 2


# =============================================================
# TEST 5 - ACTION ID PRESERVATION
# =============================================================

def test_action_id_preserved():

    environment, executor = create_executor()

    result = executor.execute_step({

        "action_id":
            "nisar-action-123",

        "action": "purchase",

        "params": {

            "item": "Phone",

            "quantity": 2,

            "location": "Warehouse",
        },
    })

    assert result["status"] == "success"

    assert (
        result["action_id"]
        == "nisar-action-123"
    )


# =============================================================
# TEST 6 - INVALID TRANSFER
# =============================================================

def test_invalid_transfer_fails():

    environment, executor = create_executor()

    result = executor.execute_step({

        "action_id":
            "test-failure-001",

        "action": "transfer",

        "params": {

            "item": "Laptop",

            "quantity": 100,

            "source": "Warehouse",

            "destination": "Store",
        },
    })

    assert result["status"] == "failure"


# =============================================================
# TEST 7 - FAILURE HANDLER
# =============================================================

def test_failure_handler_replanning():

    environment, executor = create_executor()

    failure_handler = FailureHandler(
        executor
    )

    failure = (
        failure_handler
        .simulate_failure(

            "inventory_unavailable",

            "Laptop inventory is unavailable."
        )
    )

    assert failure["status"] == "failure"

    assert (
        failure["replan_required"]
        is True
    )

    handled = (
        failure_handler
        .handle_failure(
            failure
        )
    )

    assert (
        handled["replan_required"]
        is True
    )

    assert (
        handled["recovery_action"]
        == "Find another inventory source."
    )


# =============================================================
# TEST 8 - EXECUTION FAILURE -> REPLANNING
# =============================================================

def test_execution_failure_triggers_replanning():

    environment, executor = create_executor()

    failure_handler = FailureHandler(
        executor
    )

    plan = [

        {

            "action_id":
                "test-plan-001",

            "action":
                "transfer",

            "params": {

                "item":
                    "Laptop",

                "quantity":
                    100,

                "source":
                    "Warehouse",

                "destination":
                    "Store",
            },
        }
    ]

    result = (
        failure_handler
        .execute_with_failure_check(
            plan
        )
    )

    assert result["status"] == "failure"

    assert (
        result["replan_required"]
        is True
    )

    assert (
        result[
            "replanning_trigger"
        ][
            "action"
        ]
        == "request_new_plan"
    )

    assert (
        result["failure"][
            "failure_type"
        ]
        == "execution_failure"
    )