from typing import List, Dict, Any

from httpx import Response

from src.http_requests import Requests, RequestInfo
from src.schema import GdayBodyList


class Anything:
    """Anything endpoint requests with validation"""

    def __init__(self, requests: Requests):
        self.requests = requests.client_requests

    def get_anything(self, gday_body_list: List[Dict[str, Any]]) -> List[Response]:
        """GET request of /anything endpoint

        https://httpbin.org/anything

        Args:

        Returns:
            Response: The response object containing the retrieved asset(s) data.

        Raises:
            ValueError: If the input asset_id is not of type int or list.

        Example Usage:

        ```python
        >>> responses = client.get_anything(
            [
                {"gday": {"mate": {"how": {"the": {"bloody": {"hell": ["are", "ya", 0]}}}}}},
                {"gday": {"mate": {"how": {"the": {"bloody": {"hell": ["are", "ya", 1]}}}}}},
                {"gday": {"mate": {"how": {"the": {"bloody": {"hell": ["are", "ya", 2]}}}}}},
            ]
        )
        ```
        """
        # Validate and do nothing if ok
        GdayBodyList.model_validate(gday_body_list)
        # request
        request_info = [
            RequestInfo(method="GET", path="anything", params=None, body=body)
            for body in gday_body_list
        ]
        return self.requests(requests=request_info)
