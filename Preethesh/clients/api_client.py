from typing import Any
from urllib.request import Request, urlopen
import json


class APIClient:
    """Simple JSON client for simulated external system APIs."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def _request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send a JSON request to an external API."""

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        body = None
        if data is not None:
            body = json.dumps(data).encode("utf-8")

        request = Request(
            url,
            data=body,
            method=method,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        with urlopen(request) as response:
            response_data = response.read().decode("utf-8")

        if not response_data:
            return {}

        return json.loads(response_data)

    def get(self, endpoint: str) -> dict[str, Any]:
        """Retrieve data from an external API."""
        return self._request("GET", endpoint)

    def post(
        self,
        endpoint: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Create or trigger an action through an external API."""
        return self._request("POST", endpoint, data)

    def put(
        self,
        endpoint: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Update data through an external API."""
        return self._request("PUT", endpoint, data)