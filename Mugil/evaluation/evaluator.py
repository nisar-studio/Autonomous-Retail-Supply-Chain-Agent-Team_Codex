"""
Main evaluation layer for the Autonomous Retail Supply Chain Agent.

Combines action validation, verification, performance metrics,
and robustness checks.
"""

from Mugil.verification.verifier import verify_result
from Mugil.evaluation.metrics import calculate_metrics
from Mugil.evaluation.action_validator import validate_selected_action
from Mugil.robustness.robustness import check_robustness


def evaluate_result(
    result: dict,
    action=None,
    goal=None,
    excluded_action_ids=None,
) -> dict:
    """
    Perform complete evaluation.

    Action validation is optional so existing callers
    continue to work unchanged.

    When action and goal are provided, the selected action
    is validated before the final recommendation is made.
    """

    verification = verify_result(result)
    metrics = calculate_metrics(result)
    robustness = check_robustness(result)

    action_validation = None

    if action is not None or goal is not None:
        action_validation = validate_selected_action(
            action,
            goal,
            excluded_action_ids,
        )

    # Preserve action_id for the controller/replanning layer.
    action_id = (
        result.get("action_id")
        if isinstance(result, dict)
        else None
    )

    # Overall decision
    if not verification["verified"]:
        recommendation = "REPLAN"
    elif not robustness["robust"]:
        recommendation = "REPLAN"
    elif (
        action_validation is not None
        and not action_validation["valid"]
    ):
        recommendation = "REPLAN"
    else:
        recommendation = "CONTINUE"

    # Existing behavior is preserved when action validation
    # is not requested.
    status_pass = (
        verification["verified"]
        and robustness["robust"]
        and (
            action_validation is None
            or action_validation["valid"]
        )
    )

    return {
        "action_id": action_id,
        "verified": verification["verified"],
        "status": "PASS" if status_pass else "FAIL",
        "recommendation": recommendation,
        "score": verification_score(
            verification,
            robustness,
        ),
        "checks": verification["checks"],
        "metrics": metrics,
        "robustness": robustness,
        "action_validation": action_validation,
        "errors": verification["errors"],
    }


def verification_score(
    verification: dict,
    robustness: dict,
) -> float:
    """Calculate a simple overall evaluation score."""

    checks = verification["checks"]

    if checks:
        passed = sum(
            1
            for value in checks.values()
            if value is True
        )

        verification_score_value = passed / len(checks)
    else:
        verification_score_value = 0.0

    robustness_score = (
        1.0 if robustness["robust"] else 0.0
    )

    return round(
        (verification_score_value + robustness_score) / 2,
        2,
    )