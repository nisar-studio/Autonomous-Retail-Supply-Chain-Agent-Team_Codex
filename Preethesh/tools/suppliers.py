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

        if operation == "get_available_vendors":
            return self.get_available_vendors()

        if operation == "get_vendor_capacity":
            return self.get_vendor_capacity(kwargs["supplier_id"])

        if operation == "get_vendor_status":
            return self.get_vendor_status(kwargs["supplier_id"])

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

    def get_available_vendors(self) -> list[Supplier]:
        """Return suppliers currently available and able to supply."""
        return [
            supplier
            for supplier in self._suppliers.values()
            if supplier.status == "available" and supplier.capacity > 0
        ]

    def get_vendor_capacity(self, supplier_id: str) -> int:
        """Return the available capacity of a supplier."""
        supplier = self._suppliers.get(supplier_id)

        if supplier is None:
            raise KeyError(f"Supplier '{supplier_id}' not found.")

        return supplier.capacity

    def get_vendor_status(self, supplier_id: str) -> str:
        """Return the current status of a supplier."""
        supplier = self._suppliers.get(supplier_id)

        if supplier is None:
            raise KeyError(f"Supplier '{supplier_id}' not found.")

        return supplier.status