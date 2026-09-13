from types import SimpleNamespace

from Preethesh.tools.alternatives import AlternativeGenerator, AlternativeSelector


def make_state():
    return SimpleNamespace(
        inventory=(
            SimpleNamespace(
                sku="laptop",
                available_quantity=2,
                required_quantity=10,
            ),
        )
    )


def make_goal(location="warehouse_1"):
    return SimpleNamespace(
        affected_ids=("laptop",),
        location=location,
    )


# -------------------------
# AlternativeGenerator tests
# -------------------------

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


# -------------------------
# AlternativeSelector tests
# -------------------------

def test_selector_skips_excluded_action():
    generator = AlternativeGenerator()

    selector = AlternativeSelector(
        alternative_generator=generator,
        supplier_getter=lambda item_id, location: [
            {
                "action_id": "A001",
                "supplier_id": "SUP001",
            },
            {
                "action_id": "A002",
                "supplier_id": "SUP002",
            },
        ],
        route_getter=lambda item_id, location: [],
    )

    selected = selector.select_action(
        make_goal(),
        None,
        make_state(),
        excluded_action_ids=("A001",),
    )

    assert selected["action_id"] == "A002"
    assert selected["parameters"]["location"] == "warehouse_1"


def test_selector_returns_none_without_location():
    generator = AlternativeGenerator()

    selector = AlternativeSelector(
        alternative_generator=generator,
        supplier_getter=lambda item_id, location: [
            {
                "action_id": "A001",
                "supplier_id": "SUP001",
            }
        ],
        route_getter=lambda item_id, location: [],
    )

    goal = make_goal(location=None)

    assert selector.select_action(goal, None, make_state(), ()) is None


def test_selector_skips_infeasible_action():
    class FeasibleGenerator(AlternativeGenerator):
        def generate_alternatives(self, **kwargs):
            alternatives = super().generate_alternatives(**kwargs)
            alternatives[0]["feasible"] = False
            alternatives[1]["feasible"] = True
            return alternatives

    selector = AlternativeSelector(
        alternative_generator=FeasibleGenerator(),
        supplier_getter=lambda item_id, location: [
            {
                "action_id": "A001",
                "supplier_id": "SUP001",
            },
            {
                "action_id": "A002",
                "supplier_id": "SUP002",
            },
        ],
        route_getter=lambda item_id, location: [],
    )

    selected = selector.select_action(
        make_goal(),
        None,
        make_state(),
        (),
    )

    assert selected["action_id"] == "A002"