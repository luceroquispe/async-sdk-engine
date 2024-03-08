"""
example validation of complex nested json body:

[
    {"gday": {"mate": {"how": {"the": {"bloody": {"hell": ["are", "ya", 0]}}}}}},
    {"gday": {"mate": {"how": {"the": {"bloody": {"hell": ["are", "ya", 1]}}}}}},
    {"gday": {"mate": {"how": {"the": {"bloody": {"hell": ["are", "ya", 2]}}}}}},
]

"""

from __future__ import annotations

from typing import List, Optional, Union

from pydantic import BaseModel, RootModel


class Bloody(BaseModel):
    hell: List[Union[int, str]]


class The(BaseModel):
    bloody: Bloody


class How(BaseModel):
    the: The


class Mate(BaseModel):
    how: How


class Gday(BaseModel):
    mate: Mate


class GdayBody(BaseModel):
    gday: Optional[Gday] = None


class GdayBodyList(RootModel):
    root: List[GdayBody]
