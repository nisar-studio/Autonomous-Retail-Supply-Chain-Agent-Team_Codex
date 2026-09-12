from typing import Optional

from Preethesh.models.schemas import Supplier
from Preethesh.tools.interfaces import ToolInterface


class SupplierTool(ToolInterface):
    """Tool for retrieving and managing supplier data."""

    def __init__(self):
        self._suppliers: dict[str, Supplier] = {}

    def execute(self, **kwargs):
        """Execute a supplier operation."""
        operation = kwargs.get("operation")

        if operation == "get":
            return self.get_supplier(kwargs["supplier_id"])

        if operation == "get_all":
            return self.get_all_suppliers()

        if operation == "add":
            return self.add_supplier(kwargs["supplier"])

        raise ValueError(f"Unknown supplier operation: {operation}")

    def add_supplier(self, supplier: Supplier) -> Supplier:
        """Add a supplier."""
        self._suppliers[supplier.supplier_id] = supplier
        return supplier

    def get_supplier(self, supplier_id: str) -> Optional[Supplier]:
        """Get a supplier by ID."""
        return self._suppliers.get(supplier_id)

    def get_all_suppliers(self) -> list[Supplier]:
        """Return all suppliers."""
        return list(self._suppliers.values())