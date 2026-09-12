from typing import Any

from Preethesh.tools.interfaces import ToolInterface


class AlternativeGenerator(ToolInterface):
    """Generates candidate recovery actions for a supply-chain problem."""

    def execute(self, **kwargs: Any) -> list[dict[str, Any]]:
        operation = kwargs.get("operation")

        if operation == "generate":
            return self.generate_alternatives(
                item_id=kwargs["item_id"],
                quantity=kwargs["quantity"],
                location=kwargs["location"],
                suppliers=kwargs.get("suppliers", []),
                routes=kwargs.get("routes", []),
            )

        raise ValueError(f"Unknown alternatives operation: {operation}")

    def generate_alternatives(
        self,
        item_id: str,
        quantity: int,
        location: str,
        suppliers: list[dict[str, Any]],
        routes: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Generate purchase and route-based recovery alternatives."""

        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        alternatives: list[dict[str, Any]] = []

        for supplier in suppliers:
            alternatives.append({
                "action_id": supplier["action_id"],
                "tool": "order",
                "operation": "create",
                "parameters": {
                    "item_id": item_id,
                    "quantity": quantity,
                    "supplier_id": supplier["supplier_id"],
                    "location": location,
                },
            })

        for route in routes:
            alternatives.append({
                "action_id": route["action_id"],
                "tool": "inventory",
                "operation": "reroute",
                "parameters": {
                    "item_id": item_id,
                    "quantity": quantity,
                    "from_location": route["from_location"],
                    "to_location": route["to_location"],
                },
            })

        return alternatives