from Preethesh.models.schemas import Supplier
from Preethesh.tools.suppliers import SupplierTool


def test_add_and_get_supplier():
    suppliers = SupplierTool()

    supplier = Supplier(
        supplier_id="SUP001",
        name="ABC Suppliers",
        contact="9876543210",
    )

    suppliers.add_supplier(supplier)

    result = suppliers.get_supplier("SUP001")

    assert result is not None
    assert result.name == "ABC Suppliers"
    assert result.contact == "9876543210"


def test_get_all_suppliers():
    suppliers = SupplierTool()

    suppliers.add_supplier(
        Supplier(
            supplier_id="SUP001",
            name="ABC Suppliers",
        )
    )

    suppliers.add_supplier(
        Supplier(
            supplier_id="SUP002",
            name="XYZ Suppliers",
        )
    )

    result = suppliers.get_all_suppliers()

    assert len(result) == 2