from typing import Optional

from Preethesh.models.schemas import InventoryItem
from Preethesh.tools.interfaces import ToolInterface


class InventoryTool(ToolInterface):
    """Tool for retrieving and managing inventory data."""

    def __init__(self):
        self._inventory: dict[str, InventoryItem] = {}

    def execute(self, **kwargs):
        """Execute an inventory operation."""
        operation = kwargs.get("operation")

        if operation == "get":
            return self.get_item(kwargs["item_id"])

        if operation == "get_all":
            return self.get_all_items()

        if operation == "low_stock":
            return self.get_low_stock_items()

        if operation == "update_quantity":
            return self.update_quantity(
                kwargs["item_id"],
                kwargs["quantity"],
            )

        raise ValueError(f"Unknown inventory operation: {operation}")

    def add_item(self, item: InventoryItem) -> InventoryItem:
        """Add an item to inventory."""
        self._inventory[item.item_id] = item
        return item

    def get_item(self, item_id: str) -> Optional[InventoryItem]:
        """Get an inventory item by ID."""
        return self._inventory.get(item_id)

    def get_all_items(self) -> list[InventoryItem]:
        """Return all inventory items."""
        return list(self._inventory.values())

    def get_low_stock_items(self) -> list[InventoryItem]:
        """Return items at or below their reorder level."""
        return [
            item
            for item in self._inventory.values()
            if item.quantity <= item.reorder_level
        ]

    def update_quantity(self, item_id: str, quantity: int) -> InventoryItem:
        """Update the quantity of an inventory item."""
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")

        item = self._inventory.get(item_id)

        if item is None:
            raise KeyError(f"Inventory item '{item_id}' not found.")

        item.quantity = quantity
        return item