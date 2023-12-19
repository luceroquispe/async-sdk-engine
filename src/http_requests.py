"""Async handling of all requests.

The purpose of this module is to abstract away the async runtime so that
users don't need to run functions with asyncio.run() or trio.run().

All requests are queued into a list of RequestInfo objects
then handled in the trio.nursery.
docs: https://trio.readthedocs.io/en/stable/reference-core.html#trio.Nursery
example: https://trio.readthedocs.io/en/stable/reference-core.html#nurseries-and-spawning

From within the nursery, requests are called with make_request method. Each response is
checked with "raise_for_status" and all future requests will crash with one bad API
response. For any error outside of 200 range will be handled by the error module.

This behaviour is optional with client instance arg "raise_on_error" default to True.
"""

from collections import namedtuple
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union, overload

import trio
from httpx import (
    AsyncClient,
    ConnectError,
    ConnectTimeout,
    HTTPStatusError,
    Limits,
    RemoteProtocolError,
    Response,
)
from loguru import logger

from src.errors import ApiError, CommunicationError


class RequestInfo(namedtuple("RequestInfo", ["method", "path", "params", "body"])):
    """
    A named tuple to represent request information.

    Parameters:
    - method (str): The HTTP method (GET, POST, PUT, PATCH, DELETE).
    - path (str): The URL path for the request.
    - params (Optional[Dict[str, Any]]): Query parameters for the request.
    - body (Any): Data to be sent in the request (for POST, PUT, and PATCH).

    Using __slots__ improves memory efficiency and attribute access speed.
    It restricts the creation of additional instance variables and enforces
    a strict attribute structure. This is helpful when making many async requests
    """

    __slots__ = ()

    def __new__(
        cls,
        method: str,
        path: str,
        params: Optional[Union[Dict[str, Any], str]] = None,
        body: Optional[Any] = None,
    ):
        """RequestInfo dto for all methods"""
        # GET and DELETE REST API requests must not have body
        if method.upper() in {"GET", "DELETE"}:
            body = None
        return super().__new__(cls, method, path, params, body)


class AsyncHandler:
    """A class for making asynchronous HTTP requests using the Trio library."""

    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 15,
        verify: bool = False,
        raise_on_error: Optional[bool] = True,
    ):
        """
        Initialize an AsyncHandler instance.

        Args:
            base_url (str): The base URL for the HTTP requests.
            headers (Dict[str, str]): The headers to include in each request.
            timeout (int, optional): The timeout for requests in seconds. Default 15.
            verify (bool, optional): Whether to verify SSL certificates. Defaults False.
        """
        self.base_url = base_url
        self.headers = headers
        self.timeout = timeout
        self.verify = verify
        self.raise_on_error = raise_on_error
        self.limits = Limits(max_connections=50)
        self.responses: List[Response] = []

    async def __aenter__(self):
        """boiler plate to allow AsyncHandler with statements using async context"""
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """boiler plate to allow AsyncHandler with statements using async context"""

    async def make_request(
        self,
        limit: trio.CapacityLimiter,
        https_method: Callable[..., Awaitable[Response]],
        path: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Union[dict, str, bytes]] = None,
    ) -> None:
        """
        Make an asynchronous HTTPS request and add responses to class attribute list

        Args:
            https_method (Callable[..., Response]): The HTTP method
            path (str): The path for the request.
            params (Optional[Dict[str, Any]], optional): Query parameters for the
                request. Defaults to None.
            body (Optional[Union[dict, str, bytes]], optional): Request body data.
                Defaults to None.
        """
        async with limit:
            method_name = https_method.__name__
            try:
                # Get and Delete requests have no body
                if method_name in ("get", "delete"):
                    response = await https_method(path, params=params)
                # all other methods have optional or mandatory body
                else:
                    response = await https_method(path, params=params, json=body)
            # Non status errors e.g. transport related raise
            except (ConnectError, ConnectTimeout, RemoteProtocolError) as err:
                raise CommunicationError(str(err)) from err
            # fail on error if not 200 or similar OK response
            if self.raise_on_error:
                try:
                    response.raise_for_status()
                except HTTPStatusError as err:
                    raise ApiError(str(err), response) from err
            self.responses.append(response)

    async def send_requests(self, requests: List[RequestInfo]):
        """
        Send a list of asynchronous HTTP requests.

        Args:
            requests (List[RequestInfo]): A list of RequestInfo objects
            representing the requests to send.
        """
        async with AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            verify=self.verify,
            timeout=self.timeout,
            limits=self.limits,
        ) as client:
            limit = trio.CapacityLimiter(50)  # limit whatever your server needs.
            async with trio.open_nursery() as nursery:
                for request in requests:
                    method = self.get_method_by_name(client, request.method)
                    nursery.start_soon(
                        self.make_request,
                        limit,
                        method,
                        request.path,
                        request.params,
                        request.body,
                    )

    def get_method_by_name(self, client: AsyncClient, method_name: str) -> Callable:
        """
        Get the appropriate HTTP method by name.

        Args:
            client (AsyncClient): The AsyncClient instance.
            method_name (str): The HTTP method name.

        Returns:
            Callable: The corresponding HTTP method.
        """
        method_map: Dict[str, Callable] = {
            "GET": client.get,
            "POST": client.post,
            "PUT": client.put,
            "PATCH": client.patch,
            "DELETE": client.delete,
        }
        return method_map.get(method_name.upper(), client.get)


class Requests:
    """Async class for making https requests"""

    def __init__(
        self,
        base_url: str = "https://httpbin.org/",
        headers: Optional[Dict[str, str]] = None,
        verify: bool = False,
        timeout: int = 15,
        raise_on_error: bool = True,
    ):
        self.base_url = base_url
        self.headers = headers
        self.verify = verify
        self.timeout = timeout
        self.raise_on_error = raise_on_error

    @overload
    def client_requests(self, requests: RequestInfo) -> Response:
        ...

    @overload
    def client_requests(self, requests: List[RequestInfo]) -> List[Response]:
        ...

    def client_requests(
        self,
        requests: Union[RequestInfo, List[RequestInfo]],
    ) -> Union[Response, List[Response]]:
        """
        This function sends one or more HTTP requests asynchronously using trio framework.

        Args:
            requests (Union[RequestInfo, List[RequestInfo]]): Single or list of requests.

        Returns:
            Union[Response, List[Response]]: If a single request was sent, returns a single
                response. If multiple requests were sent, returns a list of responses.
        """
        request_maker = AsyncHandler(
            base_url=self.base_url,
            headers=self.headers,
            verify=self.verify,
            timeout=self.timeout,
            raise_on_error=self.raise_on_error,
        )

        # Ensure requests is a list even if only one request is given
        if isinstance(requests, RequestInfo):
            requests = [requests]
        # run all requests async and append responses
        logger.debug(requests)
        trio.run(request_maker.send_requests, requests)
        return (
            request_maker.responses[0]
            if len(request_maker.responses) == 1
            else request_maker.responses
        )
