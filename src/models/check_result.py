from typing import Literal

from pydantic import BaseModel


class CheckResult(BaseModel):
    name: str
    status: Literal["ok", "error"]
    error: str | None
