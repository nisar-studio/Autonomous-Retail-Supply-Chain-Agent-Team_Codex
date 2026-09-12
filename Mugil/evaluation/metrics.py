"""
Performance and recovery metrics for the
Autonomous Retail Supply Chain Agent.
"""


def calculate_metrics(result: dict) -> dict:
    """
    Calculate supply-chain performance and recovery metrics.

    Expected constraints:
        required_quantity -> units
        deadline          -> hours
        max_cost/budget   -> environment currency
        carbon_limit      -> kg CO2e

    Actual values:
        delivered_quantity -> units
        delivery_time      -> hours
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

    # Handle invalid input safely
    if not isinstance(result, dict):
        return {}

    expected = result.get("expected", {})
    goal = result.get("goal", {})
    actual = result.get("actual", {})

    # Use expected constraints when available.
    # Otherwise fall back to goal constraints.
    constraints = expected if expected else goal

    metrics = {}

    # --------------------------------------------------
    # Quantity fulfillment
    # --------------------------------------------------

    if "required_quantity" in constraints:
        required = constraints["required_quantity"]
        delivered = actual.get("delivered_quantity", 0)

        if isinstance(required, (int, float)) and required > 0:
            metrics["quantity_fulfillment_rate"] = round(
                delivered / required,
                2
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

        if attempts > 0:
            metrics["recovery_success_rate"] = round(
                successes / attempts,
                2
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

    # Quantity violation
    if "required_quantity" in constraints:
        required = constraints["required_quantity"]
        delivered = actual.get("delivered_quantity", 0)

        if delivered < required:
            violations.append("quantity")

    # Cost violation
    max_cost = constraints.get(
        "max_cost",
        constraints.get("budget")
    )

    if max_cost is not None:
        actual_cost = actual.get("total_cost")

        if actual_cost is not None and actual_cost > max_cost:
            violations.append("cost")

    # Deadline violation
    if "deadline" in constraints:
        deadline = constraints["deadline"]
        delivery_time = actual.get("delivery_time")

        if (
            delivery_time is not None
            and delivery_time > deadline
        ):
            violations.append("deadline")

    # Carbon violation
    carbon_limit = constraints.get("carbon_limit")

    if carbon_limit is not None:
        carbon = actual.get("carbon_emission")

        if carbon is not None and carbon > carbon_limit:
            violations.append("carbon")

    metrics["constraint_violations"] = violations
    metrics["constraint_violation_count"] = len(violations)

    return metrics