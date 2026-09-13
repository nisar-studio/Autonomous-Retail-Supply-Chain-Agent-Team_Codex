from unittest.mock import patch

from Preethesh.clients.api_client import APIClient
from Preethesh.clients.inventory_client import InventoryAPI


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def read(self):
        return b'{"items": []}'


def test_get_inventory():
    client = APIClient("http://example.com")
    inventory_api = InventoryAPI(client, "/inventory")

    with patch(
        "Preethesh.clients.api_client.urlopen",
        return_value=FakeResponse(),
    ):
        result = inventory_api.get_inventory()

    assert result == {"items": []}