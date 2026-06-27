from typing import Protocol

from models.check_result import CheckResult


class HealthCheck(Protocol):
    name: str
    critical: bool

    async def check(self) -> CheckResult:
        return CheckResult(name="default", status="ok", error=None)
