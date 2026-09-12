"""
Verification layer for the Autonomous Retail Supply Chain Agent.

Checks whether the execution result satisfies the requested
business constraints.
"""

from collections.abc import Mapping
from datetime import datetime
from typing import Any


CONSTRAINT_KEYS = {
    "required_quantity",
    "deadline",
    "max_cost",
    "budget",
    "carbon_limit",
}


def _get_constraints(
    expected: Any,
    goal: Any,
) -> Mapping[str, Any]:
    """
    Extract constraints from expected data or goal.

    Supports both:
    1. Existing flat constraint dictionaries.
    2. Nisar-style goals with nested constraints.
    """

    # Preferred: explicit expected constraints.
    if isinstance(expected, Mapping) and expected:
        return expected

    # Dictionary-style goal.
    if isinstance(goal, Mapping):
        nested_constraints = goal.get("constraints")

        if isinstance(nested_constraints, Mapping):
            return nested_constraints

        # Backward compatibility with existing Mugil tests.
        flat_constraints = {
            key: goal[key]
            for key in CONSTRAINT_KEYS
            if key in goal
        }

        if flat_constraints:
            return flat_constraints

    # Nisar-style dataclass/object.
    constraints = getattr(goal, "constraints", {})

    if isinstance(constraints, Mapping):
        return constraints

    return {}


def _is_number(value: Any) -> bool:
    """Return True for numeric values, excluding booleans."""
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
    )


def _deadline_is_met(
    deadline: Any,
    delivery_time: Any,
) -> bool | None:
    """
    Compare deadline and delivery time.

    Supports:
    - numeric hours
    - ISO datetime strings

    Returns:
        True  -> deadline satisfied
        False -> deadline missed
        None  -> invalid/incompatible values
    """

    # Numeric values represent hours.
    if _is_number(deadline) and _is_number(delivery_time):
        return delivery_time <= deadline

    # ISO datetime values.
    if isinstance(deadline, str) and isinstance(delivery_time, str):
        try:
            deadline_dt = datetime.fromisoformat(deadline)
            delivery_dt = datetime.fromisoformat(delivery_time)

            return delivery_dt <= deadline_dt

        except ValueError:
            return None

    return None


def verify_result(result: dict) -> dict:
    """
    Verify an execution result.

    Input:
        {
            "goal": {...},
            "expected": {...},
            "actual": {...}
        }

    Expected constraints:
        required_quantity -> units
        deadline          -> hours or ISO datetime
        max_cost/budget   -> environment currency
        carbon_limit      -> kg CO2e

    Actual values:
        delivered_quantity -> units
        delivery_time      -> hours or ISO datetime
        total_cost         -> environment currency
        carbon_emission    -> kg CO2e

    Output:
        {
            "verified": bool,
            "status": "PASS" | "FAIL",
            "recommendation": "CONTINUE" | "REPLAN",
            "checks": {...},
            "errors": [...]
        }
    """

    errors = []
    checks = {}

    # --------------------------------------------------
    # Input validation
    # --------------------------------------------------

    if not isinstance(result, dict):
        return {
            "verified": False,
            "status": "FAIL",
            "recommendation": "REPLAN",
            "checks": {},
            "errors": ["Result must be a dictionary."],
        }

    goal = result.get("goal", {})
    expected = result.get("expected", {})
    actual = result.get("actual", {})

    if not isinstance(actual, Mapping):
        actual = {}

    constraints = _get_constraints(expected, goal)

    # --------------------------------------------------
    # Goal check
    # --------------------------------------------------

    checks["goal_present"] = bool(goal)

    if not goal:
        errors.append("No goal provided.")

    # --------------------------------------------------
    # Quantity check
    # --------------------------------------------------

    if "required_quantity" in constraints:
        required = constraints["required_quantity"]
        delivered = actual.get("delivered_quantity")

        if not _is_number(required):
            checks["quantity_met"] = False
            errors.append("Required quantity is invalid.")

        elif not _is_number(delivered):
            checks["quantity_met"] = False
            errors.append(
                "Actual delivered quantity is missing or invalid."
            )

        else:
            checks["quantity_met"] = delivered >= required

            if not checks["quantity_met"]:
                errors.append(
                    f"Required quantity: {required}, "
                    f"delivered: {delivered}."
                )

    # --------------------------------------------------
    # Deadline check
    # --------------------------------------------------

    if "deadline" in constraints:
        expected_deadline = constraints["deadline"]
        actual_delivery_time = actual.get("delivery_time")

        if actual_delivery_time is None:
            checks["deadline_met"] = False
            errors.append("Actual delivery time is missing.")

        else:
            deadline_result = _deadline_is_met(
                expected_deadline,
                actual_delivery_time,
            )

            if deadline_result is None:
                checks["deadline_met"] = False
                errors.append(
                    "Deadline or actual delivery time is invalid."
                )

            else:
                checks["deadline_met"] = deadline_result

                if not checks["deadline_met"]:
                    errors.append(
                        f"Delivery deadline missed. "
                        f"Expected: {expected_deadline}, "
                        f"actual: {actual_delivery_time}."
                    )

    # --------------------------------------------------
    # Budget check
    # --------------------------------------------------

    max_cost = constraints.get(
        "max_cost",
        constraints.get("budget"),
    )

    if max_cost is not None:
        actual_cost = actual.get("total_cost")

        if not _is_number(max_cost):
            checks["budget_met"] = False
            errors.append(
                "Maximum cost/budget is invalid."
            )

        elif not _is_number(actual_cost):
            checks["budget_met"] = False
            errors.append(
                "Actual total cost is missing or invalid."
            )

        else:
            checks["budget_met"] = actual_cost <= max_cost

            if not checks["budget_met"]:
                errors.append(
                    f"Maximum cost: {max_cost}, "
                    f"actual cost: {actual_cost}."
                )

    # --------------------------------------------------
    # Carbon check
    # --------------------------------------------------

    carbon_limit = constraints.get("carbon_limit")

    if carbon_limit is not None:
        actual_carbon = actual.get("carbon_emission")

        if not _is_number(carbon_limit):
            checks["carbon_met"] = False
            errors.append("Carbon limit is invalid.")

        elif not _is_number(actual_carbon):
            checks["carbon_met"] = False
            errors.append(
                "Actual carbon emission is missing."
            )

        else:
            checks["carbon_met"] = (
                actual_carbon <= carbon_limit
            )

            if not checks["carbon_met"]:
                errors.append(
                    f"Carbon limit: {carbon_limit} kgCO2e, "
                    f"actual emission: {actual_carbon} kgCO2e."
                )

    # --------------------------------------------------
    # Final verification
    # --------------------------------------------------

    verified = len(errors) == 0

    return {
        "verified": verified,
        "status": "PASS" if verified else "FAIL",
        "recommendation": (
            "CONTINUE" if verified else "REPLAN"
        ),
        "checks": checks,
        "errors": errors,
    }