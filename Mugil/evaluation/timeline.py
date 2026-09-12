"""
Activity timeline for the Autonomous Retail Supply Chain Agent.

Tracks the major stages of the recovery workflow.
"""


def create_timeline(result: dict) -> list:
    """
    Create an activity timeline from an evaluation result.
    """

    if not isinstance(result, dict):
        return []

    recommendation = result.get("recommendation", "UNKNOWN")

    timeline = [
        {
            "step": "Goal received",
            "status": "COMPLETED"
        },
        {
            "step": "Recovery planning",
            "status": "COMPLETED"
        },
        {
            "step": "Action selected",
            "status": "COMPLETED"
        },
        {
            "step": "Execution",
            "status": "COMPLETED"
        },
        {
            "step": "Verification",
            "status": (
                "PASSED"
                if result.get("verified") is True
                else "FAILED"
            )
        },
        {
            "step": "Final outcome",
            "status": recommendation
        }
    ]

    return timeline