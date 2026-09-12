from typing import Optional

from Preethesh.models.schemas import Order
from Preethesh.tools.interfaces import ToolInterface


class OrderTool(ToolInterface):
    """Tool for creating and managing orders."""

    def __init__(self):
        self._orders: dict[str, Order] = {}

    def execute(self, **kwargs):
        """Execute an order operation."""
        operation = kwargs.get("operation")

        if operation == "create":
            return self.create_order(kwargs["order"])

        if operation == "get":
            return self.get_order(kwargs["order_id"])

        if operation == "get_all":
            return self.get_all_orders()

        if operation == "update_status":
            return self.update_order_status(
                kwargs["order_id"],
                kwargs["status"],
            )

        raise ValueError(f"Unknown order operation: {operation}")

    def create_order(self, order: Order) -> Order:
        """Create and store an order."""
        if order.order_id in self._orders:
            raise ValueError(
                f"Order '{order.order_id}' already exists."
            )

        self._orders[order.order_id] = order
        return order

    def get_order(self, order_id: str) -> Optional[Order]:
        """Get an order by ID."""
        return self._orders.get(order_id)

    def get_all_orders(self) -> list[Order]:
        """Return all orders."""
        return list(self._orders.values())

    def update_order_status(
        self,
        order_id: str,
        status: str,
    ) -> Order:
        """Update the status of an existing order."""
        order = self._orders.get(order_id)

        if order is None:
            raise KeyError(f"Order '{order_id}' not found.")

        order.status = status
        return order