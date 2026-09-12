"""
Performance metrics for the autonomous supply-chain agent.
"""


def calculate_metrics(result: dict) -> dict:
    """Calculate basic supply-chain performance metrics."""

    expected = result.get("expected", {})
    actual = result.get("actual", {})

    metrics = {}

    # Quantity fulfillment
    if "required_quantity" in expected:
        required = expected["required_quantity"]
        delivered = actual.get("delivered_quantity", 0)

        metrics["quantity_fulfillment_rate"] = round(
            delivered / required, 2
        ) if required > 0 else 0.0

    # Cost
    if "total_cost" in actual:
        metrics["total_cost"] = actual["total_cost"]

    # Delivery time
    if "delivery_time" in actual:
        metrics["delivery_time"] = actual["delivery_time"]

    # Carbon
    if "carbon_emission" in actual:
        metrics["carbon_emission"] = actual["carbon_emission"]

    return metrics