from pydantic import BaseModel
from enum import Enum


class Engine(str, Enum):
    di = "di"
    openai = "openai"
