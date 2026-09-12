from dataclasses import dataclass
from typing import Optional


@dataclass
class InventoryItem:
    """Represents an inventory item."""

    item_id: str
    name: str
    quantity: int
    reorder_level: int
    supplier_id: Optional[str] = None


@dataclass
class Supplier:
    """Represents a supplier."""

    supplier_id: str
    name: str
    contact: Optional[str] = None


@dataclass
class Order:
    """Represents an order."""

    order_id: str
    item_id: str
    quantity: int
    supplier_id: str
    status: str = "pending"