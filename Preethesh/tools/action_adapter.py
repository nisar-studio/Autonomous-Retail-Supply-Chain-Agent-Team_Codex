from typing import Any


class ActionAdapter:
    """Maps Nisar SelectedAction objects to Pavan executable actions."""

    def adapt(self, selected_action: dict[str, Any]) -> dict[str, Any]:
        """Convert a SelectedAction into Pavan's executable action format."""

        operation = selected_action["operation"]
        parameters = selected_action.get("parameters", {})

        if operation == "create":
            return {
                "action_id": selected_action["action_id"],
                "action": "purchase",
                "params": {
                    "item": parameters["item_id"],
                    "quantity": parameters["quantity"],
                    "location": parameters["location"],
                },
            }

        if operation == "transfer":
            return {
                "action_id": selected_action["action_id"],
                "action": "transfer",
                "params": {
                    "item": parameters.get("item_id", parameters.get("item")),
                    "quantity": parameters["quantity"],
                    "source": parameters["source"],
                    "destination": parameters["destination"],
                },
            }

        if operation == "reroute":
            return {
                "action_id": selected_action["action_id"],
                "action": "reroute",
                "params": {
                    "item": parameters.get("item_id", parameters.get("item")),
                    "quantity": parameters["quantity"],
                    "from_location": parameters["from_location"],
                    "to_location": parameters["to_location"],
                },
            }

        raise ValueError(f"Unsupported operation: {operation}")