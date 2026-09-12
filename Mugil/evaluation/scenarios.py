"""
Evaluation scenarios for the Autonomous Retail Supply Chain Agent.

These scenarios simulate common supply-chain disruptions and define
the expected recovery outcome for evaluation and testing.
"""


def shipment_delay_scenario() -> dict:
    """
    Scenario 1:
    A shipment is delayed, but recovery should still succeed.
    """

    return {
        "scenario": "shipment_delay",
        "description": "Incoming shipment is delayed.",
        "goal": {
            "objective": "Maintain required inventory despite shipment delay.",
            "constraints": {
                "required_quantity": 100,
                "deadline": 24,
                "max_cost": 5000,
                "carbon_limit": 100,
            },
        },
        "actual": {
            "shipment_delayed": True,
            "recovery_available": True,
        },
        "expected_outcome": "RECOVERY_SUCCESS",
    }


def vendor_unavailable_scenario() -> dict:
    """
    Scenario 2:
    The original supplier is unavailable, so the agent should replan.
    """

    return {
        "scenario": "vendor_unavailable",
        "description": "Original supplier is unavailable.",
        "goal": {
            "objective": "Recover supply using another supplier.",
            "constraints": {
                "required_quantity": 100,
                "deadline": 24,
                "max_cost": 5000,
                "carbon_limit": 100,
            },
        },
        "actual": {
            "supplier_available": False,
            "alternative_supplier_available": True,
        },
        "expected_outcome": "REPLAN_SUCCESS",
    }


def route_unavailable_scenario() -> dict:
    """
    Scenario 3:
    The primary route is unavailable, but an alternate route exists.
    """

    return {
        "scenario": "route_unavailable",
        "description": "Primary delivery route is unavailable.",
        "goal": {
            "objective": "Deliver the required quantity using another route.",
            "constraints": {
                "required_quantity": 100,
                "deadline": 24,
                "max_cost": 5000,
                "carbon_limit": 100,
            },
        },
        "actual": {
            "route_available": False,
            "alternate_route_available": True,
        },
        "expected_outcome": "ALTERNATE_ROUTE_SUCCESS",
    }


def no_feasible_option_scenario() -> dict:
    """
    Scenario 4:
    No feasible recovery option exists, so the agent must report failure
    honestly instead of pretending recovery succeeded.
    """

    return {
        "scenario": "no_feasible_option",
        "description": "No feasible recovery option is available.",
        "goal": {
            "objective": "Recover the disrupted supply chain.",
            "constraints": {
                "required_quantity": 100,
                "deadline": 24,
                "max_cost": 5000,
                "carbon_limit": 100,
            },
        },
        "actual": {
            "feasible": False,
        },
        "expected_outcome": "FAILURE_REPORTED",
    }


def get_all_scenarios() -> list[dict]:
    """
    Return all evaluation scenarios.
    """

    return [
        shipment_delay_scenario(),
        vendor_unavailable_scenario(),
        route_unavailable_scenario(),
        no_feasible_option_scenario(),
    ]