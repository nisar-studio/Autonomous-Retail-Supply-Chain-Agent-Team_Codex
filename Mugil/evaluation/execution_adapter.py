"""
Adapter between the Pavan execution response and the Mugil evaluator.

Converts the execution response into the standard Mugil evaluation format.
"""


def adapt_execution_result(
    execution_response: dict,
    goal: dict,
    expected: dict | None = None
) -> dict:
    """
    Convert Pavan's Executor response into Mugil's evaluator input.
    """

    if not isinstance(execution_response, dict):
        return {
            "action_id": None,
            "goal": goal if isinstance(goal, dict) else {},
            "expected": expected if isinstance(expected, dict) else {},
            "actual": {}
        }

    result = execution_response.get("result", {})

    if not isinstance(result, dict):
        result = {}

    return {
        "action_id": execution_response.get("action_id"),
        "goal": goal if isinstance(goal, dict) else {},
        "expected": expected if isinstance(expected, dict) else {},
        "actual": {
            "delivered_quantity": result.get("delivered_quantity"),
            "delivery_time": result.get("delivery_time"),
            "total_cost": result.get("total_cost"),
            "carbon_emission": result.get("carbon_emission"),
        }
    }