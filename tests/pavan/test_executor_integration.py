import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "Pavan"))

from environment import Environment
from executor import Executor


def test_selected_action_purchase():
    env = Environment()
    executor = Executor(env)

    selected_action = {
        "action_id": "A001",
        "tool": "order",
        "operation": "create",
        "parameters": {
            "item": "laptop",
            "quantity": 10,
            "location": "warehouse",
        },
    }

    result = executor.execute_selected_action(selected_action)

    assert result["action_id"] == "A001"
    assert result["status"] == "success"
    assert result["action"] == "purchase"

    state = result["state"]

    assert state["inventory"][("laptop", "warehouse")] == 10


def test_selected_action_transfer():
    env = Environment()
    executor = Executor(env)

    purchase = {
        "action_id": "A001",
        "tool": "order",
        "operation": "create",
        "parameters": {
            "item": "laptop",
            "quantity": 10,
            "location": "warehouse",
        },
    }

    transfer = {
        "action_id": "A002",
        "tool": "inventory",
        "operation": "transfer",
        "parameters": {
            "item": "laptop",
            "quantity": 3,
            "source": "warehouse",
            "destination": "store",
        },
    }

    executor.execute_selected_action(purchase)
    result = executor.execute_selected_action(transfer)

    assert result["action_id"] == "A002"
    assert result["status"] == "success"
    assert result["action"] == "transfer"

    state = result["state"]

    assert state["inventory"][("laptop", "warehouse")] == 7
    assert state["inventory"][("laptop", "store")] == 3


def test_selected_action_reroute():
    env = Environment()
    executor = Executor(env)

    purchase = {
        "action_id": "A001",
        "tool": "order",
        "operation": "create",
        "parameters": {
            "item": "laptop",
            "quantity": 10,
            "location": "warehouse",
        },
    }

    reroute = {
        "action_id": "A002",
        "tool": "inventory",
        "operation": "reroute",
        "parameters": {
            "item": "laptop",
            "quantity": 4,
            "from_location": "warehouse",
            "to_location": "store",
        },
    }

    executor.execute_selected_action(purchase)
    result = executor.execute_selected_action(reroute)

    assert result["action_id"] == "A002"
    assert result["status"] == "success"
    assert result["action"] == "reroute"

    state = result["state"]

    assert state["inventory"][("laptop", "warehouse")] == 6
    assert state["inventory"][("laptop", "store")] == 4


def test_action_id_is_preserved():
    env = Environment()
    executor = Executor(env)

    selected_action = {
        "action_id": "NISAR-12345",
        "tool": "order",
        "operation": "create",
        "parameters": {
            "item": "phone",
            "quantity": 5,
            "location": "warehouse",
        },
    }

    result = executor.execute_selected_action(selected_action)

    assert result["action_id"] == "NISAR-12345"
    assert result["result"]["action"] == "purchase"


def test_unsupported_selected_action():
    env = Environment()
    executor = Executor(env)

    selected_action = {
        "action_id": "A999",
        "tool": "unknown",
        "operation": "something",
        "parameters": {},
    }

    result = executor.execute_selected_action(selected_action)

    assert result["action_id"] == "A999"
    assert result["status"] == "failure"