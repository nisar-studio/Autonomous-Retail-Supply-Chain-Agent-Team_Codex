from typing import Any
from Preethesh.tools.interfaces import ToolInterface


class RouteTool(ToolInterface):
    """Tool for investigating available transport routes."""

    def __init__(self):
        self._routes: list[dict[str, Any]] = []

    def execute(self, **kwargs: Any) -> Any:
        operation = kwargs.get("operation")

        if operation == "get_available_routes":
            return self.get_available_routes(
                kwargs["source"],
                kwargs["destination"],
            )

        if operation == "check_route":
            return self.check_route(kwargs["route_id"])

        if operation == "get_delivery_time":
            return self.get_delivery_time(kwargs["route_id"])

        raise ValueError(f"Unknown route operation: {operation}")

    def add_route(self, route: dict[str, Any]) -> dict[str, Any]:
        """Add a route to the simulated route data."""
        self._routes.append(route)
        return route

    def get_available_routes(
        self,
        source: str,
        destination: str,
    ) -> list[dict[str, Any]]:
        """Return routes between the requested locations."""
        return [
            route
            for route in self._routes
            if route.get("source") == source
            and route.get("destination") == destination
        ]

    def check_route(self, route_id: str) -> bool:
        """Return whether a route exists and is feasible."""
        for route in self._routes:
            if route.get("route_id") == route_id:
                return bool(route.get("feasible", False))
        return False

    def get_delivery_time(self, route_id: str) -> float:
        """Return the delivery time for a route."""
        for route in self._routes:
            if route.get("route_id") == route_id:
                return float(route["delivery_time"])
        raise KeyError(f"Route '{route_id}' not found.")