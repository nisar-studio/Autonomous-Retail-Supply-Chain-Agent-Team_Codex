from typing import Any

from Preethesh.clients.api_client import APIClient


class InventoryAPI:
    """Client for retrieving inventory data from an external system."""

    def __init__(self, client: APIClient, inventory_endpoint: str):
        self.client = client
        self.inventory_endpoint = inventory_endpoint

    def get_inventory(self) -> dict[str, Any]:
        """Retrieve the current inventory from the external system."""
        return self.client.get(self.inventory_endpoint)