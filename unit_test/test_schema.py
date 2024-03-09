# tests/test_schema.py

import pytest

# tests/test_schema.py

import pytest
from pydantic import ValidationError
from src.schema import GdayBodyList


# Parametrized test data with custom identifiers as inputs
@pytest.mark.parametrize(
    "json_data, expected_success",
    [
        (
            [
                {
                    "gday": {
                        "mate": {"how": {"the": {"bloody": {"hell": ["are", "ya", 0]}}}}
                    }
                },
                {
                    "gday": {
                        "mate": {"how": {"the": {"bloody": {"hell": ["are", "ya", 1]}}}}
                    }
                },
                {
                    "gday": {
                        "mate": {"how": {"the": {"bloody": {"hell": ["are", "ya", 2]}}}}
                    }
                },
            ],
            True,
        ),
        (
            [
                {
                    "gday": {
                        "mate": {
                            "how": {
                                "the": {"bloody": {"who": ["are", "ya", "invalid"]}}
                            }
                        }
                    }
                }
            ],
            False,
        ),
        ({"gday": {"mate": {"how": {"the": {"bloody": ["are", "ya", None]}}}}}, False),
    ],
    ids=["valid_data", "invalid_data", "missing_key"],
)
def test_gday_body_list_validation(json_data, expected_success):
    if expected_success:
        # Test successful validation
        gday_body_list = GdayBodyList(root=json_data)
        assert isinstance(gday_body_list, GdayBodyList)
    else:
        # Test unsuccessful validation (expecting a ValidationError)
        with pytest.raises(ValidationError):
            GdayBodyList(root=json_data)
