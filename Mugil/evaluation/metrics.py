"""
Performance and recovery metrics for the
Autonomous Retail Supply Chain Agent.
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

    Supports:
    1. Flat expected dictionaries.
    2. Dictionary goals with nested "constraints".
    3. Nisar-style objects/dataclasses with .constraints.
    4. Existing flat goal dictionaries for backward compatibility.
    """

    # Explicit expected constraints have priority.
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
        False -> deadline violated
        None  -> invalid/incompatible values
    """

    # Numeric deadlines represent hours.
    if _is_number(deadline) and _is_number(delivery_time):
        return delivery_time <= deadline

    # ISO datetime deadlines.
    if isinstance(deadline, str) and isinstance(delivery_time, str):
        try:
            deadline_dt = datetime.fromisoformat(deadline)
            delivery_dt = datetime.fromisoformat(delivery_time)

            return delivery_dt <= deadline_dt

        except ValueError:
            return None

    return None


def calculate_metrics(result: dict) -> dict:
    """
    Calculate supply-chain performance and recovery metrics.

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

    Optional recovery values:
        recovery_success
        recovery_attempts
        recovery_successes
        replan_count
        recovery_cost
        recovery_time
    """

    # --------------------------------------------------
    # Handle invalid input safely
    # --------------------------------------------------

    if not isinstance(result, dict):
        return {}

    expected = result.get("expected", {})
    goal = result.get("goal", {})
    actual = result.get("actual", {})

    if not isinstance(actual, Mapping):
        actual = {}

    constraints = _get_constraints(
        expected,
        goal,
    )

    metrics = {}

    # --------------------------------------------------
    # Quantity fulfillment
    # --------------------------------------------------

    if "required_quantity" in constraints:
        required = constraints["required_quantity"]
        delivered = actual.get("delivered_quantity")

        if (
            _is_number(required)
            and required > 0
            and _is_number(delivered)
        ):
            metrics["quantity_fulfillment_rate"] = round(
                delivered / required,
                2,
            )
        else:
            metrics["quantity_fulfillment_rate"] = 0.0

    # --------------------------------------------------
    # Cost
    # --------------------------------------------------

    if "total_cost" in actual:
        metrics["total_cost"] = actual["total_cost"]

    # --------------------------------------------------
    # Delivery time
    # --------------------------------------------------

    if "delivery_time" in actual:
        metrics["delivery_time"] = actual["delivery_time"]

    # --------------------------------------------------
    # Carbon emissions
    # --------------------------------------------------

    if "carbon_emission" in actual:
        metrics["carbon_emission"] = actual["carbon_emission"]

    # --------------------------------------------------
    # Recovery success rate
    # --------------------------------------------------

    if "recovery_success_rate" in result:
        metrics["recovery_success_rate"] = result[
            "recovery_success_rate"
        ]

    elif (
        "recovery_attempts" in result
        and "recovery_successes" in result
    ):
        attempts = result["recovery_attempts"]
        successes = result["recovery_successes"]

        if (
            _is_number(attempts)
            and _is_number(successes)
            and attempts > 0
        ):
            metrics["recovery_success_rate"] = round(
                successes / attempts,
                2,
            )
        else:
            metrics["recovery_success_rate"] = 0.0

    elif "recovery_success" in result:
        metrics["recovery_success_rate"] = (
            1.0 if result["recovery_success"] else 0.0
        )

    # --------------------------------------------------
    # Number of replans
    # --------------------------------------------------

    if "replan_count" in result:
        metrics["replan_count"] = result["replan_count"]

    # --------------------------------------------------
    # Recovery cost
    # --------------------------------------------------

    if "recovery_cost" in result:
        metrics["recovery_cost"] = result["recovery_cost"]

    # --------------------------------------------------
    # Recovery time
    # --------------------------------------------------

    if "recovery_time" in result:
        metrics["recovery_time"] = result["recovery_time"]

    # --------------------------------------------------
    # Constraint violations
    # --------------------------------------------------

    violations = []

    # --------------------------------------------------
    # Quantity violation
    # --------------------------------------------------

    if "required_quantity" in constraints:
        required = constraints["required_quantity"]
        delivered = actual.get("delivered_quantity")

        if (
            not _is_number(required)
            or not _is_number(delivered)
            or delivered < required
        ):
            violations.append("quantity")

    # --------------------------------------------------
    # Cost violation
    # --------------------------------------------------

    max_cost = constraints.get(
        "max_cost",
        constraints.get("budget"),
    )

    if max_cost is not None:
        actual_cost = actual.get("total_cost")

        if (
            not _is_number(max_cost)
            or not _is_number(actual_cost)
            or actual_cost > max_cost
        ):
            violations.append("cost")

    # --------------------------------------------------
    # Deadline violation
    # --------------------------------------------------

    if "deadline" in constraints:
        deadline = constraints["deadline"]
        delivery_time = actual.get("delivery_time")

        deadline_result = _deadline_is_met(
            deadline,
            delivery_time,
        )

        if deadline_result is not True:
            violations.append("deadline")

    # --------------------------------------------------
    # Carbon violation
    # --------------------------------------------------

    carbon_limit = constraints.get("carbon_limit")

    if carbon_limit is not None:
        carbon = actual.get("carbon_emission")

        if (
            not _is_number(carbon_limit)
            or not _is_number(carbon)
            or carbon > carbon_limit
        ):
            violations.append("carbon")

    # --------------------------------------------------
    # Final metrics
    # --------------------------------------------------

    metrics["constraint_violations"] = violations
    metrics["constraint_violation_count"] = len(
        violations
    )

    return metrics