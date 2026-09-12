from typing import Any


class APIClient:
    """Simple client interface for external system APIs."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def get(self, endpoint: str) -> dict[str, Any]:
        """Retrieve data from an external API."""
        raise NotImplementedError("GET request not implemented yet.")

    def post(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """Send data to an external API."""
        raise NotImplementedError("POST request not implemented yet.")

    def put(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update data in an external API."""
        raise NotImplementedError("PUT request not implemented yet.")