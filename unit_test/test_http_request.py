from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import Response
from httpx import Limits
from httpx import Request

from src.http_requests import AsyncHandler, RequestInfo


@pytest.mark.parametrize(
    "method, path, body, params, expected_body, expected_params",
    [
        ("GET", "/path", None, None, None, None),
        ("POST", "/path", "body content", None, "body content", None),
        ("DELETE", "/path", None, None, None, None),
        ("GET", "/path", None, {"param1": "value1"}, None, {"param1": "value1"}),
        (
            "POST",
            "/path",
            "body content",
            {"param1": "value1"},
            "body content",
            {"param1": "value1"},
        ),
        ("DELETE", "/path", None, {"param1": "value1"}, None, {"param1": "value1"}),
    ],
    ids=[
        "get_no_body_no_params",
        "post_with_body_no_params",
        "delete_no_body_no_params",
        "get_no_body_with_params",
        "post_with_body_with_params",
        "delete_no_body_with_params",
    ],
)
def test_request_info_methods(
    method, path, body, params, expected_body, expected_params
):
    """Test that GET and DELETE methods do not have a body, and POST can have a body. Also test with and without params."""
    request_info = RequestInfo(method, path, body=body, params=params)

    assert request_info.method == method
    assert request_info.path == path
    assert request_info.body == expected_body
    assert request_info.params == expected_params


def test_request_info_repr():
    """Test the string representation of RequestInfo."""
    request_info = RequestInfo("POST", "/path", body="body content")
    expected_repr = (
        "RequestInfo(method: POST, path: /path, params: None, body: body content)"
    )
    assert repr(request_info) == expected_repr


async def mock_async_client(*args, **kwargs):
    """Mock the AsyncClient and its methods"""
    mock = AsyncMock()
    mock.get = AsyncMock(return_value=Response(200, content=b"OK"))
    mock.post = AsyncMock(return_value=Response(201, content=b"OK"))
    mock.put = AsyncMock(return_value=Response(200, content=b"OK"))
    mock.delete = AsyncMock(return_value=Response(204, content=b"OK"))

    mock_request = Request("GET", "http://test.com/path")
    for method in ["get", "post", "put", "delete"]:
        response = mock.__dict__[method].return_value
        response._request = mock_request
    return mock


def test_async_handler_init():
    """Test __init__ defaults"""
    handler = AsyncHandler(base_url="http://test.com")
    assert handler.base_url == "http://test.com"
    assert handler.headers is None
    assert handler.timeout == 15
    assert handler.verify is False
    assert handler.raise_on_error is True


@pytest.mark.trio
async def test_async_handler_context_manager():
    """Test __aenter__ and __aexit__"""
    handler = AsyncHandler(base_url="http://test.com")
    async with handler as h:
        assert h is handler


@pytest.mark.trio
@pytest.mark.parametrize(
    "method, path, body, expected_status",
    [
        ("GET", "/path", None, 200),
        ("POST", "/path", {"key": "value"}, 201),
        ("PUT", "/path", {"key": "value"}, 200),
        ("DELETE", "/path", None, 204),
    ],
)
async def test_make_request(method, path, body, expected_status):
    # Initialize AsyncHandler with mock client
    handler = AsyncHandler(base_url="http://test.com")
    handler.client = await mock_async_client()

    # Get the appropriate method from the mock client
    method_func = getattr(handler.client, method.lower())

    # Call make_request with the method, path, and body
    await handler.make_request(method_func, path, body=body)

    # Assert that the response was added to the handler's responses list
    assert len(handler.responses) == 1
    assert handler.responses[0].status_code == expected_status
