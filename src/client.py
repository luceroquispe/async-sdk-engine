""" 
example client with Anything endpoint method
"""
from typing import Dict

from src.http_requests import Requests
from src.api import Anything


class ApiClient(Anything):
    """
    A client for making asynchronous HTTP requests.

    This class provides a wrapper around the Requests class for making HTTP requests asynchronously.
    It simplifies the process of sending requests by handling the setup of the HTTP client.
    """

    def __init__(
        self,
        base_url: str,
        headers: Dict[str, str] | None = None,
        verify: bool = False,
        timeout: int = 15,
        raise_on_error: bool = True,
    ):
        """
        Initialize the ApiClient with the given configuration.

        Args:
            base_url (str): The base URL for the API.
            verify (bool, optional): Whether to verify SSL certificates. Defaults to False.
            timeout (int, optional): The timeout for requests in seconds. Defaults to 15.
            raise_on_error (bool, optional): Whether to raise exceptions on HTTP errors. Defaults to True.
        """
        self.http_client = Requests(
            base_url=base_url,
            headers=headers,
            verify=verify,
            timeout=timeout,
            raise_on_error=raise_on_error,
        )

        self.base_url = base_url
        self.verify = verify
        self.timeout = timeout
        self.raise_on_error = raise_on_error

        super().__init__(self.http_client)

    def __repr__(self) -> str:
        """
        Return a string representation of the ApiClient instance.

        Returns:
            str: A string representation of the ApiClient instance, including its configuration.
        """
        return (
            f"ApiClient(base_url={self.base_url}, "
            f"verify={self.verify}, timeout={self.timeout}, "
            f"raise_on_error={self.raise_on_error})"
        )
