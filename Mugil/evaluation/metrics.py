"""
Performance metrics for the autonomous supply-chain agent.
"""


def calculate_metrics(result: dict) -> dict:
    """Calculate basic supply-chain performance metrics."""

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
                delivered / required, 2
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

    return metrics