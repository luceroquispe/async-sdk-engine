"""
This module provides error handling classes the Client.
"""

from json import JSONDecodeError, loads
from typing import Any, Dict, Optional, Union

from httpx import Request, Response
from loguru import logger


class Error(Exception):
    """Generic class for  error handling."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"Error: Error message: {self.message}."


class ApiError(Error):
    """Process and expose error details sent by  API."""

    def __init__(self, error: str, response: Response) -> None:
        self.status_code: int = response.status_code
        self.reason_phrase: str = response.reason_phrase or ""
        self.errors: Optional[Union[str, Dict[str, Any]]] = ""
        if response.content:
            self.errors = self.error_parse_json_or_utf8(response.content)
        self.error_type: str = self.find_error_type_from_response(response=response)
        self.request_repr: Union[str, Request] = response.request or ""
        self.links: Union[str, Dict[Optional[str], Dict[str, str]]] = (
            response.links or ""
        )
        self.message: str = (
            f"{self.error_type} "
            f"{self.status_code} "
            f"{self.reason_phrase} "
            f"{self.errors}"
        )
        super().__init__(self.message)

    def is_jsonable(self, error: bytes) -> bool:
        """Inspect an object to see if it is json unserializeable

        Args:
            error (bytes): httpx response.content

        Returns:
            bool: If the object is jsonable
        """
        try:
            loads(error)
            return True
        except JSONDecodeError:
            return False

    def error_parse_json_or_utf8(
        self, response_content: bytes
    ) -> Union[Dict[str, Any], str, None]:
        """Parse the response content and return the most helpful valid string

        3 options:
            1. response is unable to be serialized into dictionary so return string
            2. response is able to so return dictionary
            3. Neither so return None or whatever it is

        Args:
            response_content (bytes): httpx response content

        Returns:
            _type_: _description_
        """
        if not self.is_jsonable(response_content):
            return response_content.decode("utf-8")
        error = loads(response_content)
        return error.get("errors") if isinstance(error, dict) else error

    def __str__(self) -> str:
        return (
            f"\nApiError: Error message: {self.message}\n"
            f"{self.request_repr} {self.links}"
        )

    def find_error_type_from_response(self, response: Response) -> str:
        """Return error type from all possible error types

        These errors only trigger and handle 400 & 500 status responses.
        There are no other errors
        """
        if response.is_client_error:
            return "Client error"
        if response.is_server_error:
            return "Server error"
        logger.warning("Error type logic needs fixing")
        return "Not a request error. The  error handling has a bug"


class CommunicationError(Error):
    """Error when connecting to ."""

    def __str__(self) -> str:
        return f"CommunicationError, {self.message}"
