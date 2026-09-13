from typing import Any, Sequence

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
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        alternatives: list[dict[str, Any]] = []

        for supplier in suppliers:
            alternatives.append(
                {
                    "action_id": supplier["action_id"],
                    "tool": "order",
                    "operation": "create",
                    "parameters": {
                        "item_id": item_id,
                        "quantity": quantity,
                        "supplier_id": supplier["supplier_id"],
                        "location": location,
                    },
                }
            )

        for route in routes:
            alternatives.append(
                {
                    "action_id": route["action_id"],
                    "tool": "inventory",
                    "operation": "reroute",
                    "parameters": {
                        "item_id": item_id,
                        "quantity": quantity,
                        "from_location": route["from_location"],
                        "to_location": route["to_location"],
                    },
                }
            )

        return alternatives


class AlternativeSelector(ToolInterface):
    """Selects a feasible recovery action using goal.location."""

    def __init__(
        self,
        alternative_generator: AlternativeGenerator,
        supplier_getter,
        route_getter,
    ) -> None:
        self._generator = alternative_generator
        self._supplier_getter = supplier_getter
        self._route_getter = route_getter

    def execute(self, **kwargs: Any) -> dict[str, Any] | None:
        operation = kwargs.get("operation")

        if operation == "select":
            return self.select_action(
                kwargs["goal"],
                kwargs["plan"],
                kwargs["state"],
                kwargs.get("excluded_action_ids", ()),
            )

        raise ValueError(f"Unknown selector operation: {operation}")

    def select_action(
        self,
        goal: Any,
        plan: Any,
        state: Any,
        excluded_action_ids: Sequence[str],
    ) -> dict[str, Any] | None:
        location = getattr(goal, "location", None)

        if not location:
            return None

        affected_ids = tuple(goal.affected_ids)

        if not affected_ids:
            return None

        item_id = affected_ids[0]
        quantity = self._required_quantity(state, item_id)

        if quantity <= 0:
            return None

        suppliers = self._supplier_getter(item_id, location)
        routes = self._route_getter(item_id, location)

        alternatives = self._generator.generate_alternatives(
            item_id=item_id,
            quantity=quantity,
            location=location,
            suppliers=list(suppliers),
            routes=list(routes),
        )

        excluded = set(excluded_action_ids)

        for alternative in alternatives:
            action_id = alternative.get("action_id")

            if not action_id or action_id in excluded:
                continue

            if alternative.get("feasible", True) is False:
                continue

            return alternative

        return None

    @staticmethod
    def _required_quantity(state: Any, item_id: str) -> int:
        for inventory in state.inventory:
            if inventory.sku == item_id:
                return max(
                    inventory.required_quantity - inventory.available_quantity,
                    0,
                )

        return 0