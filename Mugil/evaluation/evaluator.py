"""
Main evaluation layer for the Autonomous Retail Supply Chain Agent.

Combines verification, performance metrics, and robustness checks.
"""

from Mugil.verification.verifier import verify_result
from Mugil.evaluation.metrics import calculate_metrics
from Mugil.robustness.robustness import check_robustness


def evaluate_result(result: dict) -> dict:
    """
    Perform complete evaluation of an execution result.

    Returns verification, metrics, robustness,
    action_id and an overall recommendation.
    """

    verification = verify_result(result)
    metrics = calculate_metrics(result)
    robustness = check_robustness(result)

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
    else:
        recommendation = "CONTINUE"

    return {
        "action_id": action_id,
        "verified": verification["verified"],
        "status": (
            "PASS"
            if verification["verified"] and robustness["robust"]
            else "FAIL"
        ),
        "recommendation": recommendation,
        "score": verification_score(
            verification,
            robustness
        ),
        "checks": verification["checks"],
        "metrics": metrics,
        "robustness": robustness,
        "errors": verification["errors"],
    }


def verification_score(
    verification: dict,
    robustness: dict
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
        2
    )