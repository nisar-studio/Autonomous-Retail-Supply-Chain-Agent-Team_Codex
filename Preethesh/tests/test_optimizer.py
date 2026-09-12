from Preethesh.tools.optimizer import Optimizer


def test_selects_lowest_cost():
    optimizer = Optimizer()

    alternatives = [
        {
            "action_id": "A001",
            "feasible": True,
            "total_cost": 5000,
            "delivery_time": 3,
            "carbon_emission": 20,
        },
        {
            "action_id": "A002",
            "feasible": True,
            "total_cost": 4000,
            "delivery_time": 4,
            "carbon_emission": 25,
        },
    ]

    result = optimizer.select_best(
        goal={"budget": 6000},
        alternatives=alternatives,
    )

    assert result["action_id"] == "A002"


def test_ignores_infeasible_alternative():
    optimizer = Optimizer()

    alternatives = [
        {
            "action_id": "A001",
            "feasible": False,
            "total_cost": 3000,
        },
        {
            "action_id": "A002",
            "feasible": True,
            "total_cost": 5000,
        },
    ]

    result = optimizer.select_best(
        goal={"budget": 6000},
        alternatives=alternatives,
    )

    assert result["action_id"] == "A002"


def test_respects_budget():
    optimizer = Optimizer()

    alternatives = [
        {
            "action_id": "A001",
            "feasible": True,
            "total_cost": 7000,
        },
        {
            "action_id": "A002",
            "feasible": True,
            "total_cost": 5000,
        },
    ]

    result = optimizer.select_best(
        goal={"budget": 6000},
        alternatives=alternatives,
    )

    assert result["action_id"] == "A002"


def test_uses_delivery_time_as_tiebreaker():
    optimizer = Optimizer()

    alternatives = [
        {
            "action_id": "A001",
            "feasible": True,
            "total_cost": 5000,
            "delivery_time": 4,
        },
        {
            "action_id": "A002",
            "feasible": True,
            "total_cost": 5000,
            "delivery_time": 2,
        },
    ]

    result = optimizer.select_best(
        goal={},
        alternatives=alternatives,
    )

    assert result["action_id"] == "A002"


def test_execute_select_operation():
    optimizer = Optimizer()

    alternatives = [
        {
            "action_id": "A001",
            "feasible": True,
            "total_cost": 5000,
        }
    ]

    result = optimizer.execute(
        operation="select",
        goal={"budget": 6000},
        alternatives=alternatives,
    )

    assert result["action_id"] == "A001"