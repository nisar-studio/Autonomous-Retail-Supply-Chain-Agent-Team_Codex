"""
Integration layer between the execution environment
and the Mugil evaluation system.

Flow:

Nisar SelectedAction
        │
        ├──────────────┐
        ▼              ▼
Execution        Mugil evaluation
response              │
        │              │
        ▼              ▼
adapt_execution_result()
        │
        ▼
evaluate_result()
        │
        ▼
CONTINUE / REPLAN
"""

from collections.abc import Sequence
from typing import Any

from Mugil.evaluation.execution_adapter import adapt_execution_result
from Mugil.evaluation.evaluator import evaluate_result


def evaluate_execution(
    execution_response: dict,
    goal: Any,
    expected: dict | None = None,
    selected_action: Any = None,
    excluded_action_ids: Sequence[str] | None = None,
) -> dict:
    """
    Convert an execution response into the Mugil format
    and evaluate it.

    selected_action:
        Optional action selected by Nisar. When provided,
        Mugil validates that action against the recovery goal.

    excluded_action_ids:
        Optional action IDs that must not be accepted.

    Returns:
        Complete Mugil evaluation result.
    """

    adapted_result = adapt_execution_result(
        execution_response,
        goal,
        expected,
    )

    return evaluate_result(
        adapted_result,
        action=selected_action,
        goal=goal if selected_action is not None else None,
        excluded_action_ids=excluded_action_ids,
    )
