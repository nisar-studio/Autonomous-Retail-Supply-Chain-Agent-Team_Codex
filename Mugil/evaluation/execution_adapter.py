"""
Adapter between the execution response and the Mugil evaluator.

Converts the execution response into the standard Mugil
evaluation format while preserving the original recovery goal.
"""

from typing import Any


def adapt_execution_result(
    execution_response: dict,
    goal: Any,
    expected: dict | None = None,
) -> dict:
    """
    Convert an execution response into Mugil's evaluator input.

    The original goal is preserved so Nisar-style goal objects
    can also be evaluated.
    """

    if not isinstance(execution_response, dict):
        return {
            "action_id": None,
            "goal": goal,
            "expected": expected if isinstance(expected, dict) else {},
            "actual": {},
        }

    result = execution_response.get("result", {})

    if not isinstance(result, dict):
        result = {}

    return {
        "action_id": execution_response.get("action_id"),
        "goal": goal,
        "expected": expected if isinstance(expected, dict) else {},
        "actual": {
            "delivered_quantity": result.get("delivered_quantity"),
            "delivery_time": result.get("delivery_time"),
            "total_cost": result.get("total_cost"),
            "carbon_emission": result.get("carbon_emission"),
        },
    }