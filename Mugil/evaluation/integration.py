"""
Integration layer between the execution environment
and the Mugil evaluation system.

Flow:

Pavan execution response
        ↓
adapt_execution_result()
        ↓
evaluate_result()
        ↓
Mugil evaluation result
"""

from Mugil.evaluation.execution_adapter import adapt_execution_result
from Mugil.evaluation.evaluator import evaluate_result


def evaluate_execution(
    execution_response: dict,
    goal: dict,
    expected: dict | None = None
) -> dict:
    """
    Convert an execution response into the Mugil format
    and evaluate it.

    Parameters:
        execution_response:
            Response returned by the execution environment.

        goal:
            Original recovery goal/constraints.

        expected:
            Optional expected constraints. If provided,
            these take priority during evaluation.

    Returns:
        Complete Mugil evaluation result.
    """

    adapted_result = adapt_execution_result(
        execution_response,
        goal,
        expected
    )

    return evaluate_result(adapted_result)