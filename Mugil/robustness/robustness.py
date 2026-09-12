"""
Robustness checks for failure scenarios in the
Autonomous Retail Supply Chain Agent.
"""


def check_robustness(result: dict) -> dict:
    """
    Detect common execution failures and determine
    whether the system should recover or replan.
    """

    issues = []

    actual = result.get("actual", {})

    # Supplier failure
    if actual.get("supplier_available") is False:
        issues.append("Supplier unavailable.")

    # Shipment failure
    if actual.get("shipment_delayed") is True:
        issues.append("Shipment delayed.")

    # Inventory failure
    if actual.get("inventory_available") is False:
        issues.append("Required inventory unavailable.")

    # Tool/API failure
    if actual.get("tool_error") is True:
        issues.append("Tool or external API failure.")

    # Feasibility
    if actual.get("feasible") is False:
        issues.append("No feasible solution found.")

    robust = len(issues) == 0

    return {
        "robust": robust,
        "status": "PASS" if robust else "FAIL",
        "recommendation": "CONTINUE" if robust else "REPLAN",
        "issues": issues,
    }