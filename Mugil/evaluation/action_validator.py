"""
Validation of Nisar's selected recovery actions.
"""

from collections.abc import Mapping, Sequence
from typing import Any


SUPPORTED_OPERATIONS = {
    "purchase",
    "transfer",
    "reroute",
}


def _get_value(obj: Any, key: str, default: Any = None) -> Any:
    """Read a value from either a dict or an object/dataclass."""
    if isinstance(obj, Mapping):
        return obj.get(key, default)

    return getattr(obj, key, default)


def _get_parameters(action: Any) -> Mapping[str, Any]:
    """Safely extract action parameters."""
    parameters = _get_value(action, "parameters", {})

    if isinstance(parameters, Mapping):
        return parameters

    return {}


def validate_selected_action(
    action: Any,
    goal: Any,
    excluded_action_ids: Sequence[str] | None = None,
) -> dict:
    """
    Validate a SelectedAction against a RecoveryGoal.

    Returns:
        {
            "valid": bool,
            "status": "PASS" | "FAIL",
            "checks": {...},
            "errors": [...]
        }
    """

    if action is None:
        return {
            "valid": False,
            "status": "FAIL",
            "checks": {
                "action_present": False,
            },
            "errors": ["No action was selected."],
        }

    if goal is None:
        return {
            "valid": False,
            "status": "FAIL",
            "checks": {
                "goal_present": False,
            },
            "errors": ["Recovery goal is missing."],
        }

    action_id = _get_value(action, "action_id")
    operation = _get_value(action, "operation", "")
    parameters = _get_parameters(action)

    goal_location = _get_value(goal, "location")

    constraints = _get_value(goal, "constraints", {})
    if not isinstance(constraints, Mapping):
        constraints = {}

    excluded = set(excluded_action_ids or [])

    checks = {
        "action_present": True,
        "action_id_present": bool(action_id),
        "operation_supported": operation in SUPPORTED_OPERATIONS,
        "parameters_present": bool(parameters),
        "not_excluded": action_id not in excluded,
    }

    errors = []

    if not checks["action_id_present"]:
        errors.append("Action ID is missing.")

    if not checks["operation_supported"]:
        errors.append(f"Unsupported operation: {operation!r}.")

    if not checks["parameters_present"]:
        errors.append("Action parameters are missing.")

    if not checks["not_excluded"]:
        errors.append(f"Action {action_id!r} is excluded.")

    item = parameters.get("item")
    quantity = parameters.get("quantity")

    checks["item_present"] = item is not None

    if item is None:
        errors.append("Action item is missing.")

    required_quantity = constraints.get("required_quantity")

    if required_quantity is not None:
        if isinstance(quantity, (int, float)) and not isinstance(quantity, bool):
            checks["quantity_sufficient"] = quantity >= required_quantity

            if not checks["quantity_sufficient"]:
                errors.append(
                    f"Action quantity {quantity} is below "
                    f"required quantity {required_quantity}."
                )
        else:
            checks["quantity_sufficient"] = False
            errors.append("Action quantity is missing or invalid.")

    if goal_location is not None:
        action_location = parameters.get("location")

        if operation == "transfer":
            action_location = parameters.get("destination")
        elif operation == "reroute":
            action_location = parameters.get("to_location")

        checks["location_matches"] = action_location == goal_location

        if not checks["location_matches"]:
            errors.append(
                f"Action destination/location {action_location!r} "
                f"does not match goal location {goal_location!r}."
            )

    if operation == "purchase":
        if goal_location is not None:
            checks["purchase_location_present"] = bool(
                parameters.get("location")
            )

            if not checks["purchase_location_present"]:
                errors.append("Purchase action is missing its location.")

    if operation == "transfer":
        checks["source_present"] = bool(parameters.get("source"))
        checks["destination_present"] = bool(parameters.get("destination"))

        if not checks["source_present"]:
            errors.append("Transfer source is missing.")

        if not checks["destination_present"]:
            errors.append("Transfer destination is missing.")

    if operation == "reroute":
        checks["from_location_present"] = bool(
            parameters.get("from_location")
        )
        checks["to_location_present"] = bool(
            parameters.get("to_location")
        )

        if not checks["from_location_present"]:
            errors.append("Reroute source location is missing.")

        if not checks["to_location_present"]:
            errors.append("Reroute destination location is missing.")

    valid = len(errors) == 0

    return {
        "valid": valid,
        "status": "PASS" if valid else "FAIL",
        "checks": checks,
        "errors": errors,
    }