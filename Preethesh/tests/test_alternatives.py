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

    # Make the first generated candidate infeasible by using a custom generator.
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
