from dataclasses import dataclass
from typing import Literal, TypedDict

class TextSchema(TypedDict):
    message: str
    type: Literal["text","token"] = "text"
