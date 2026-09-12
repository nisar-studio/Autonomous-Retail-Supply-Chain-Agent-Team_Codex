from Preethesh.tools.route_tool import RouteTool


def test_add_and_get_available_routes():
    tool = RouteTool()

    route = {
        "route_id": "R001",
        "source": "warehouse",
        "destination": "store",
        "feasible": True,
        "delivery_time": 2.5,
    }

    tool.add_route(route)

    routes = tool.get_available_routes("warehouse", "store")

    assert routes == [route]


def test_check_route():
    tool = RouteTool()

    tool.add_route({
        "route_id": "R001",
        "source": "warehouse",
        "destination": "store",
        "feasible": True,
        "delivery_time": 2.5,
    })

    assert tool.check_route("R001") is True
    assert tool.check_route("UNKNOWN") is False


def test_get_delivery_time():
    tool = RouteTool()

    tool.add_route({
        "route_id": "R001",
        "source": "warehouse",
        "destination": "store",
        "feasible": True,
        "delivery_time": 2.5,
    })

    assert tool.get_delivery_time("R001") == 2.5


def test_execute_operations():
    tool = RouteTool()

    tool.add_route({
        "route_id": "R001",
        "source": "warehouse",
        "destination": "store",
        "feasible": True,
        "delivery_time": 2.5,
    })

    assert len(tool.execute(
        operation="get_available_routes",
        source="warehouse",
        destination="store",
    )) == 1

    assert tool.execute(
        operation="check_route",
        route_id="R001",
    ) is True

    assert tool.execute(
        operation="get_delivery_time",
        route_id="R001",
    ) == 2.5