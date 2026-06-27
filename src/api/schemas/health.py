from typing import Literal

from pydantic import BaseModel, Field

from models.check_result import CheckResult


class HealthResponse(BaseModel):
    status: Literal["ok"] = Field(default="ok")
    version: str = Field(default="0.0.0")


class ReadyResponse(BaseModel):
    status: Literal["ok", "degraded", "error"] = Field(default="ok")
    version: str = Field(default="0.0.0")
    checks: list[CheckResult] = Field(default=[])
