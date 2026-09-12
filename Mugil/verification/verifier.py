"""
Verification layer for the Autonomous Retail Supply Chain Agent.

Checks whether the execution result satisfies the requested
business constraints.
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
                    f"Expected: {expected_deadline}, "
                    f"actual: {actual_delivery_time}."
                )

    # --------------------------------------------------
    # Budget check
    # --------------------------------------------------

    # Support both "max_cost" and "budget"
    max_cost = constraints.get("max_cost", constraints.get("budget"))

    if max_cost is not None:
        actual_cost = actual.get("total_cost", 0)

        checks["budget_met"] = actual_cost <= max_cost

        if not checks["budget_met"]:
            errors.append(
                f"Maximum cost: {max_cost}, "
                f"actual cost: {actual_cost}."
            )

    # --------------------------------------------------
    # Final verification
    # --------------------------------------------------

    verified = len(errors) == 0

    return {
        "verified": verified,
        "status": "PASS" if verified else "FAIL",
        "recommendation": "CONTINUE" if verified else "REPLAN",
        "checks": checks,
        "errors": errors,
    }