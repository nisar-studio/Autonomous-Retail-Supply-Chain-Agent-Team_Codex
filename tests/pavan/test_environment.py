import sys
from pathlib import Path

import pytest


# Add Pavan directory to Python path.
sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[2] / "Pavan")
)

from environment import Environment


# ==============================================================
# LOCATION TESTS
# ==============================================================

def test_set_and_get_item_location():
    env = Environment()

    result = env.set_item_location(
        "laptop",
        "warehouse_1"
    )

    assert result["status"] == "success"
    assert result["item"] == "laptop"
    assert result["location"] == "warehouse_1"

    assert env.get_item_location(
        "laptop"
    ) == "warehouse_1"


def test_missing_item_location_returns_none():
    env = Environment()

    assert env.get_item_location(
        "unknown_item"
    ) is None


def test_has_item_location():
    env = Environment()

    assert env.has_item_location(
        "laptop"
    ) is False

    env.set_item_location(
        "laptop",
        "warehouse_1"
    )

    assert env.has_item_location(
        "laptop"
    ) is True


def test_get_all_item_locations():
    env = Environment()

    env.set_item_location(
        "laptop",
        "warehouse_1"
    )

    env.set_item_location(
        "phone",
        "warehouse_2"
    )

    locations = env.get_all_item_locations()

    assert locations == {
        "laptop": "warehouse_1",
        "phone": "warehouse_2",
    }


def test_location_requires_item():
    env = Environment()

    with pytest.raises(ValueError):
        env.set_item_location(
            "",
            "warehouse_1"
        )


def test_location_requires_location():
    env = Environment()

    with pytest.raises(ValueError):
        env.set_item_location(
            "laptop",
            ""
        )


# ==============================================================
# PURCHASE TESTS
# ==============================================================

def test_purchase_updates_inventory_and_location():
    env = Environment()

    result = env.purchase(
        "laptop",
        10,
        "warehouse_1"
    )

    assert result["status"] == "success"

    assert env.state["inventory"][
        ("laptop", "warehouse_1")
    ] == 10

    assert env.get_item_location(
        "laptop"
    ) == "warehouse_1"


def test_purchase_returns_evaluation_metrics():
    env = Environment()

    result = env.purchase(
        "laptop",
        10,
        "warehouse_1"
    )

    assert result["delivered_quantity"] == 10
    assert result["delivery_time"] == 24.0
    assert result["total_cost"] == 1000.0
    assert result["carbon_emission"] == 5.0


def test_purchase_requires_location():
    env = Environment()

    result = env.purchase(
        "laptop",
        10,
        None
    )

    assert result["status"] == "failure"


def test_purchase_rejects_zero_quantity():
    env = Environment()

    result = env.purchase(
        "laptop",
        0,
        "warehouse_1"
    )

    assert result["status"] == "failure"


def test_purchase_rejects_negative_quantity():
    env = Environment()

    result = env.purchase(
        "laptop",
        -5,
        "warehouse_1"
    )

    assert result["status"] == "failure"


# ==============================================================
# TRANSFER TESTS
# ==============================================================

def test_transfer_updates_inventory_and_location():
    env = Environment()

    env.purchase(
        "laptop",
        10,
        "warehouse_1"
    )

    result = env.transfer(
        "laptop",
        4,
        "warehouse_1",
        "store_1"
    )

    assert result["status"] == "success"

    assert env.state["inventory"][
        ("laptop", "warehouse_1")
    ] == 6

    assert env.state["inventory"][
        ("laptop", "store_1")
    ] == 4

    assert env.get_item_location(
        "laptop"
    ) == "store_1"


def test_transfer_returns_evaluation_metrics():
    env = Environment()

    env.purchase(
        "laptop",
        10,
        "warehouse_1"
    )

    result = env.transfer(
        "laptop",
        4,
        "warehouse_1",
        "store_1"
    )

    assert result["delivered_quantity"] == 4
    assert result["delivery_time"] == 4.0
    assert result["total_cost"] == 80.0
    assert result["carbon_emission"] == 0.8


def test_transfer_fails_when_inventory_is_insufficient():
    env = Environment()

    env.purchase(
        "laptop",
        2,
        "warehouse_1"
    )

    result = env.transfer(
        "laptop",
        5,
        "warehouse_1",
        "store_1"
    )

    assert result["status"] == "failure"


def test_transfer_requires_source():
    env = Environment()

    result = env.transfer(
        "laptop",
        5,
        None,
        "store_1"
    )

    assert result["status"] == "failure"


def test_transfer_requires_destination():
    env = Environment()

    result = env.transfer(
        "laptop",
        5,
        "warehouse_1",
        None
    )

    assert result["status"] == "failure"


# ==============================================================
# REROUTE TESTS
# ==============================================================

def test_reroute_updates_inventory_and_location():
    env = Environment()

    env.purchase(
        "laptop",
        10,
        "warehouse_1"
    )

    result = env.reroute(
        "laptop",
        3,
        "warehouse_1",
        "warehouse_2"
    )

    assert result["status"] == "success"

    assert env.state["inventory"][
        ("laptop", "warehouse_1")
    ] == 7

    assert env.state["inventory"][
        ("laptop", "warehouse_2")
    ] == 3

    assert env.get_item_location(
        "laptop"
    ) == "warehouse_2"


def test_reroute_returns_evaluation_metrics():
    env = Environment()

    env.purchase(
        "laptop",
        10,
        "warehouse_1"
    )

    result = env.reroute(
        "laptop",
        3,
        "warehouse_1",
        "warehouse_2"
    )

    assert result["delivered_quantity"] == 3
    assert result["delivery_time"] == 6.0
    assert result["total_cost"] == 90.0

    # round() in Environment prevents
    # 0.8999999999999999 floating-point output.
    assert result["carbon_emission"] == 0.9


def test_reroute_fails_when_inventory_is_insufficient():
    env = Environment()

    env.purchase(
        "laptop",
        2,
        "warehouse_1"
    )

    result = env.reroute(
        "laptop",
        5,
        "warehouse_1",
        "warehouse_2"
    )

    assert result["status"] == "failure"


def test_reroute_requires_source():
    env = Environment()

    result = env.reroute(
        "laptop",
        5,
        None,
        "warehouse_2"
    )

    assert result["status"] == "failure"


def test_reroute_requires_destination():
    env = Environment()

    result = env.reroute(
        "laptop",
        5,
        "warehouse_1",
        None
    )

    assert result["status"] == "failure"


# ==============================================================
# STATE TESTS
# ==============================================================

def test_get_state_contains_location_data():
    env = Environment()

    env.set_item_location(
        "laptop",
        "warehouse_1"
    )

    state = env.get_state()

    assert "inventory" in state
    assert "locations" in state
    assert "balances" in state
    assert "allocations" in state

    assert state["locations"] == {
        "laptop": "warehouse_1"
    }


# ==============================================================
# HISTORY TESTS
# ==============================================================

def test_successful_action_is_recorded_in_history():
    env = Environment()

    env.purchase(
        "laptop",
        10,
        "warehouse_1"
    )

    history = env.get_history()

    assert len(history) == 1
    assert history[0]["action"] == "purchase"
    assert history[0]["status"] == "success"


def test_failed_action_is_recorded_in_history():
    env = Environment()

    env.purchase(
        "laptop",
        0,
        "warehouse_1"
    )

    history = env.get_history()

    assert len(history) == 1
    assert history[0]["status"] == "failure"