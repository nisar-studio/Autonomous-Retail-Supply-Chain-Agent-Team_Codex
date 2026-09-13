from Preethesh.models.schemas import InventoryItem
from Preethesh.tools.inventory import InventoryTool


def test_add_and_get_item():
    inventory = InventoryTool()

    item = InventoryItem(
        item_id="SKU001",
        name="Milk",
        quantity=20,
        reorder_level=10,
    )

    inventory.add_item(item)

    result = inventory.get_item("SKU001")

    assert result is not None
    assert result.name == "Milk"
    assert result.quantity == 20


def test_low_stock_items():
    inventory = InventoryTool()

    inventory.add_item(
        InventoryItem(
            item_id="SKU001",
            name="Milk",
            quantity=5,
            reorder_level=10,
        )
    )

    inventory.add_item(
        InventoryItem(
            item_id="SKU002",
            name="Bread",
            quantity=20,
            reorder_level=10,
        )
    )

    low_stock = inventory.get_low_stock_items()

    assert len(low_stock) == 1
    assert low_stock[0].item_id == "SKU001"


def test_update_quantity():
    inventory = InventoryTool()

    inventory.add_item(
        InventoryItem(
            item_id="SKU001",
            name="Milk",
            quantity=20,
            reorder_level=10,
        )
    )

    updated = inventory.update_quantity("SKU001", 8)

    assert updated.quantity == 8
def test_execute_low_stock():
    inventory = InventoryTool()

    inventory.add_item(
        InventoryItem(
            item_id="SKU001",
            name="Milk",
            quantity=5,
            reorder_level=10,
        )
    )

    result = inventory.execute(operation="low_stock")

    assert len(result) == 1
    assert result[0].item_id == "SKU001"