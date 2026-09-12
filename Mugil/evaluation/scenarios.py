"""
Failure and recovery scenarios for the
Autonomous Retail Supply Chain Agent.

These scenarios provide deterministic test cases
for demonstrating recovery and replanning behavior.
"""


def shipment_delay_scenario() -> dict:
    """
    Scenario 1:
    Shipment is delayed, but recovery succeeds.
    """

    return {
        "scenario": "shipment_delay",
        "description": "Shipment delay with successful recovery.",
        "actual": {
            "supplier_available": True,
            "shipment_delayed": True,
            "inventory_available": True,
            "tool_error": False,
            "feasible": True
        },
        "expected_outcome": "RECOVERY_SUCCESS"
    }


def vendor_unavailable_scenario() -> dict:
    """
    Scenario 2:
    Vendor is unavailable, so the agent replans
    and another option succeeds.
    """

    return {
        "scenario": "vendor_unavailable",
        "description": "Vendor unavailable followed by successful replanning.",
        "actual": {
            "supplier_available": False,
            "shipment_delayed": False,
            "inventory_available": True,
            "tool_error": False,
            "feasible": True
        },
        "expected_outcome": "REPLAN_SUCCESS"
    }


def route_unavailable_scenario() -> dict:
    """
    Scenario 3:
    Route is unavailable and the agent finds
    an alternative route.
    """

    return {
        "scenario": "route_unavailable",
        "description": "Unavailable route followed by an alternate route.",
        "actual": {
            "supplier_available": True,
            "shipment_delayed": False,
            "inventory_available": True,
            "tool_error": False,
            "feasible": True,
            "route_available": False,
            "alternate_route_available": True
        },
        "expected_outcome": "ALTERNATE_ROUTE_SUCCESS"
    }


def no_feasible_option_scenario() -> dict:
    """
    Scenario 4:
    No feasible option exists and the system
    reports failure honestly.
    """

    return {
        "scenario": "no_feasible_option",
        "description": "No feasible recovery option is available.",
        "actual": {
            "supplier_available": False,
            "shipment_delayed": True,
            "inventory_available": False,
            "tool_error": False,
            "feasible": False
        },
        "expected_outcome": "FAILURE_REPORTED"
    }


def get_all_scenarios() -> list:
    """
    Return all required recovery scenarios.
    """

    return [
        shipment_delay_scenario(),
        vendor_unavailable_scenario(),
        route_unavailable_scenario(),
        no_feasible_option_scenario()
    ]