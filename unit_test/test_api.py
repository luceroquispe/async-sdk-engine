import pytest
from src.client import ApiClient


@pytest.mark.parametrize(
    "base_url, verify, timeout, raise_on_error",
    [
        (
            "https://api.example.com",
            False,
            15,
            True,
        ),
        (
            "https://api.example.com",
            True,
            30,
            False,
        ),
        # Add more test cases as needed
    ],
    ids=["defaults", "non-defaults"],
)
def test_api_client_initialization(base_url, verify, timeout, raise_on_error):
    """
    Test the initialization of the ApiClient with different configurations.
    """
    client = ApiClient(
        base_url=base_url, verify=verify, timeout=timeout, raise_on_error=raise_on_error
    )

    # Assert that the client's attributes are set correctly
    assert client.base_url == base_url
    assert client.verify == verify
    assert client.timeout == timeout
    assert client.raise_on_error == raise_on_error
