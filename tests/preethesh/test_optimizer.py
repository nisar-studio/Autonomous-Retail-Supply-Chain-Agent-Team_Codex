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


def test_optimize_calculates_cost_delivery_time_and_carbon():
    optimizer = Optimizer(
        cost_calculator=lambda alternative: (
            alternative["quantity"] * alternative["cost_per_unit"]
        ),
        delivery_time_calculator=lambda alternative: alternative["transit_days"],
        carbon_calculator=lambda alternative: (
            alternative["quantity"] * alternative["carbon_per_unit"]
        ),
    )

    alternatives = [
        {
            "action_id": "A001",
            "feasible": True,
            "quantity": 10,
            "cost_per_unit": 500,
            "transit_days": 4,
            "carbon_per_unit": 3,
        },
        {
            "action_id": "A002",
            "feasible": True,
            "quantity": 10,
            "cost_per_unit": 400,
            "transit_days": 3,
            "carbon_per_unit": 2,
        },
    ]

    result = optimizer.optimize(
        goal={"budget": 5000, "deadline": 4},
        alternatives=alternatives,
    )

    assert result["action_id"] == "A002"
    assert result["total_cost"] == 4000
    assert result["delivery_time"] == 3
    assert result["carbon_emission"] == 20


def test_optimize_removes_infeasible_alternatives():
    optimizer = Optimizer()

    alternatives = [
        {
            "action_id": "A001",
            "feasible": False,
            "total_cost": 1000,
        },
        {
            "action_id": "A002",
            "feasible": True,
            "total_cost": 3000,
        },
    ]

    result = optimizer.optimize(
        goal={"budget": 5000},
        alternatives=alternatives,
    )

    assert result["action_id"] == "A002"


def test_optimize_applies_budget_and_deadline():
    optimizer = Optimizer()

    alternatives = [
        {
            "action_id": "A001",
            "feasible": True,
            "total_cost": 4000,
            "delivery_time": 6,
        },
        {
            "action_id": "A002",
            "feasible": True,
            "total_cost": 4500,
            "delivery_time": 3,
        },
    ]

    result = optimizer.optimize(
        goal={"budget": 5000, "deadline": 4},
        alternatives=alternatives,
    )

    assert result["action_id"] == "A002"


def test_execute_optimize_operation():
    optimizer = Optimizer(
        cost_calculator=lambda alternative: alternative["quantity"] * 100,
        delivery_time_calculator=lambda alternative: 2,
        carbon_calculator=lambda alternative: alternative["quantity"] * 5,
    )

    result = optimizer.execute(
        operation="optimize",
        goal={"budget": 2000, "deadline": 3},
        alternatives=[
            {
                "action_id": "A001",
                "feasible": True,
                "quantity": 10,
            }
        ],
    )

    assert result["action_id"] == "A001"
    assert result["total_cost"] == 1000
    assert result["delivery_time"] == 2
    assert result["carbon_emission"] == 50