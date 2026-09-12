from Preethesh.models.schemas import Order
from Preethesh.tools.orders import OrderTool


def test_create_and_get_order():
    orders = OrderTool()

    order = Order(
        order_id="ORD001",
        item_id="SKU001",
        quantity=50,
        supplier_id="SUP001",
    )

    orders.create_order(order)

    result = orders.get_order("ORD001")

    assert result is not None
    assert result.item_id == "SKU001"
    assert result.quantity == 50
    assert result.status == "pending"


def test_update_order_status():
    orders = OrderTool()

    order = Order(
        order_id="ORD001",
        item_id="SKU001",
        quantity=50,
        supplier_id="SUP001",
    )

    orders.create_order(order)

    updated = orders.update_order_status("ORD001", "confirmed")

    assert updated.status == "confirmed"


def test_duplicate_order_is_rejected():
    orders = OrderTool()

    order = Order(
        order_id="ORD001",
        item_id="SKU001",
        quantity=50,
        supplier_id="SUP001",
    )

    orders.create_order(order)

    try:
        orders.create_order(order)
        assert False, "Expected duplicate order to raise ValueError"
    except ValueError:
        pass