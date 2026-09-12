"""
Verification layer for the Autonomous Retail Supply Chain Agent.

Checks whether the execution result satisfies the requested
business constraints.

Units:
    required_quantity -> units/items
    deadline          -> hours
    max_cost/budget   -> environment currency
    carbon_limit      -> kg CO2e

Actual values:
    delivered_quantity -> units/items
    delivery_time      -> hours
    total_cost         -> environment currency
    carbon_emission    -> kg CO2e
"""


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
        deadline          -> hours
        max_cost          -> environment currency
        carbon_limit      -> kg CO2e

    Actual values:
        delivered_quantity -> units
        delivery_time      -> hours
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
            "errors": ["Result must be a dictionary."]
        }

    goal = result.get("goal", {})
    expected = result.get("expected", {})
    actual = result.get("actual", {})

    # Use expected constraints when available.
    # Otherwise fall back to goal constraints.
    constraints = expected if expected else goal

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
        delivered = actual.get("delivered_quantity", 0)

        checks["quantity_met"] = delivered >= required

        if not checks["quantity_met"]:
            errors.append(
                f"Required quantity: {required}, "
                f"delivered: {delivered}."
            )

    # --------------------------------------------------
    # Deadline check
    # --------------------------------------------------

    # Deadline and delivery_time are both measured in hours.
    if "deadline" in constraints:
        expected_deadline = constraints["deadline"]
        actual_delivery_time = actual.get("delivery_time")

        if actual_delivery_time is None:
            checks["deadline_met"] = False
            errors.append("Actual delivery time is missing.")
        else:
            checks["deadline_met"] = (
                actual_delivery_time <= expected_deadline
            )

            if not checks["deadline_met"]:
                errors.append(
                    f"Delivery deadline missed. "
                    f"Expected: {expected_deadline} hours, "
                    f"actual: {actual_delivery_time} hours."
                )

    # --------------------------------------------------
    # Budget check
    # --------------------------------------------------

    # Support both "max_cost" and "budget".
    max_cost = constraints.get(
        "max_cost",
        constraints.get("budget")
    )

    if max_cost is not None:
        actual_cost = actual.get("total_cost", 0)

        checks["budget_met"] = actual_cost <= max_cost

        if not checks["budget_met"]:
            errors.append(
                f"Maximum cost: {max_cost}, "
                f"actual cost: {actual_cost}."
            )

    # --------------------------------------------------
    # Carbon check
    # --------------------------------------------------

    # Carbon limit and carbon emission are measured in kg CO2e.
    carbon_limit = constraints.get("carbon_limit")

    if carbon_limit is not None:
        actual_carbon = actual.get("carbon_emission")

        if actual_carbon is None:
            checks["carbon_met"] = False
            errors.append("Actual carbon emission is missing.")
        else:
            checks["carbon_met"] = actual_carbon <= carbon_limit

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