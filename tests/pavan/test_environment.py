import sys
from pathlib import Path

# Allow importing files from the Pavan folder
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "Pavan"))

from environment import Environment


def test_purchase_success():
    env = Environment()

    result = env.purchase("laptop", 10, "warehouse")

    assert result["status"] == "success"
    assert result["action"] == "purchase"
    assert result["item"] == "laptop"
    assert result["quantity"] == 10
    assert result["location"] == "warehouse"

    state = env.get_state()
    assert state["inventory"][("laptop", "warehouse")] == 10


def test_purchase_invalid_quantity():
    env = Environment()

    result = env.purchase("laptop", 0, "warehouse")

    assert result["status"] == "failure"
    assert "Quantity must be greater than 0" in result["error"]


def test_transfer_success():
    env = Environment()

    env.purchase("laptop", 10, "warehouse")

    result = env.transfer(
        "laptop",
        3,
        "warehouse",
        "store"
    )

    assert result["status"] == "success"
    assert result["action"] == "transfer"

    state = env.get_state()

    assert state["inventory"][("laptop", "warehouse")] == 7
    assert state["inventory"][("laptop", "store")] == 3


def test_transfer_insufficient_inventory():
    env = Environment()

    env.purchase("laptop", 5, "warehouse")

    result = env.transfer(
        "laptop",
        10,
        "warehouse",
        "store"
    )

    assert result["status"] == "failure"
    assert "Not enough laptop" in result["error"]

    state = env.get_state()

    # Inventory should remain unchanged after failed transfer
    assert state["inventory"][("laptop", "warehouse")] == 5
    assert ("laptop", "store") not in state["inventory"]


def test_transfer_invalid_quantity():
    env = Environment()

    env.purchase("laptop", 10, "warehouse")

    result = env.transfer(
        "laptop",
        0,
        "warehouse",
        "store"
    )

    assert result["status"] == "failure"
    assert "Quantity must be greater than 0" in result["error"]


def test_reroute_success():
    env = Environment()

    env.purchase("laptop", 10, "warehouse")

    result = env.reroute(
        "laptop",
        4,
        "warehouse",
        "store"
    )

    assert result["status"] == "success"
    assert result["action"] == "reroute"

    state = env.get_state()

    assert state["inventory"][("laptop", "warehouse")] == 6
    assert state["inventory"][("laptop", "store")] == 4


def test_reroute_insufficient_inventory():
    env = Environment()

    env.purchase("laptop", 5, "warehouse")

    result = env.reroute(
        "laptop",
        10,
        "warehouse",
        "store"
    )

    assert result["status"] == "failure"

    state = env.get_state()

    assert state["inventory"][("laptop", "warehouse")] == 5
    assert ("laptop", "store") not in state["inventory"]


def test_multiple_purchases():
    env = Environment()

    env.purchase("laptop", 10, "warehouse")
    env.purchase("laptop", 5, "warehouse")

    state = env.get_state()

    assert state["inventory"][("laptop", "warehouse")] == 15


def test_purchase_different_locations():
    env = Environment()

    env.purchase("laptop", 10, "warehouse")
    env.purchase("laptop", 5, "store")

    state = env.get_state()

    assert state["inventory"][("laptop", "warehouse")] == 10
    assert state["inventory"][("laptop", "store")] == 5