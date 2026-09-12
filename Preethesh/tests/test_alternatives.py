from Preethesh.tools.alternatives import AlternativeGenerator


def test_generate_supplier_alternatives():
    tool = AlternativeGenerator()

    suppliers = [
        {
            "action_id": "A001",
            "supplier_id": "S001",
        },
        {
            "action_id": "A002",
            "supplier_id": "S002",
        },
    ]

    alternatives = tool.generate_alternatives(
        item_id="laptop",
        quantity=10,
        location="warehouse",
        suppliers=suppliers,
        routes=[],
    )

    assert len(alternatives) == 2
    assert alternatives[0]["action_id"] == "A001"
    assert alternatives[0]["operation"] == "create"
    assert alternatives[0]["parameters"]["supplier_id"] == "S001"


def test_generate_route_alternatives():
    tool = AlternativeGenerator()

    routes = [
        {
            "action_id": "A003",
            "from_location": "warehouse",
            "to_location": "store",
        },
        {
            "action_id": "A004",
            "from_location": "warehouse2",
            "to_location": "store",
        },
    ]

    alternatives = tool.generate_alternatives(
        item_id="laptop",
        quantity=5,
        location="store",
        suppliers=[],
        routes=routes,
    )

    assert len(alternatives) == 2
    assert alternatives[0]["action_id"] == "A003"
    assert alternatives[0]["operation"] == "reroute"
    assert alternatives[0]["parameters"]["from_location"] == "warehouse"


def test_generate_mixed_alternatives():
    tool = AlternativeGenerator()

    suppliers = [
        {
            "action_id": "A001",
            "supplier_id": "S001",
        }
    ]

    routes = [
        {
            "action_id": "A002",
            "from_location": "warehouse",
            "to_location": "store",
        }
    ]

    alternatives = tool.execute(
        operation="generate",
        item_id="laptop",
        quantity=10,
        location="store",
        suppliers=suppliers,
        routes=routes,
    )

    assert len(alternatives) == 2
    assert alternatives[0]["action_id"] == "A001"
    assert alternatives[1]["action_id"] == "A002"


def test_invalid_quantity_rejected():
    tool = AlternativeGenerator()

    try:
        tool.generate_alternatives(
            item_id="laptop",
            quantity=0,
            location="store",
            suppliers=[],
            routes=[],
        )
        assert False
    except ValueError as error:
        assert str(error) == "Quantity must be greater than zero."