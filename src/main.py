import json

from loguru import logger

from src.client import ApiClient

client = ApiClient("https://httpbin.org/")

responses = client.get_anything(
    [
        {"gday": {"mate": {"how": {"the": {"bloody": {"hell": ["are", "ya", 0]}}}}}},
        {"gday": {"mate": {"how": {"the": {"bloody": {"hell": ["are", "ya", 1]}}}}}},
        {"gday": {"mate": {"how": {"the": {"bloody": {"hell": ["are", "ya", 2]}}}}}},
    ]
)

for response in responses:
    tidy_json_str_response = json.dumps(response.json(), indent=2)
    logger.debug(tidy_json_str_response)
