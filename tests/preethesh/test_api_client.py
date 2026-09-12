from Preethesh.clients.api_client import APIClient


def test_api_client_base_url():
    client = APIClient("http://example.com/")

    assert client.base_url == "http://example.com"