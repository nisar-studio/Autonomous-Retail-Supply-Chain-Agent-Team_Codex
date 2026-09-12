from Preethesh.tools.carbon_tool import CarbonTool


def test_calculate_cost():
    tool = CarbonTool()

    result = tool.calculate_cost(
        quantity=10,
        cost_per_unit=500,
    )

    assert result == 5000


def test_calculate_carbon():
    tool = CarbonTool()

    result = tool.calculate_carbon(
        quantity=10,
        carbon_per_unit=1.24,
    )

    assert result == 12.4


def test_execute_operations():
    tool = CarbonTool()

    assert tool.execute(
        operation="calculate_cost",
        quantity=10,
        cost_per_unit=500,
    ) == 5000

    assert tool.execute(
        operation="calculate_carbon",
        quantity=10,
        carbon_per_unit=1.24,
    ) == 12.4


def test_negative_quantity_rejected():
    tool = CarbonTool()

    try:
        tool.calculate_cost(
            quantity=-1,
            cost_per_unit=500,
        )
        assert False
    except ValueError as error:
        assert str(error) == "Quantity cannot be negative."


def test_negative_cost_rejected():
    tool = CarbonTool()

    try:
        tool.calculate_cost(
            quantity=10,
            cost_per_unit=-500,
        )
        assert False
    except ValueError as error:
        assert str(error) == "Cost per unit cannot be negative."