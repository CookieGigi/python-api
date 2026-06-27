from typing import Literal

import asyncio

from interfaces.health_check import HealthCheck
from services.health_check_registry import HealthCheckRegistry
from models.check_result import CheckResult


class HealthCheckService:
    registry: HealthCheckRegistry
    default_timeout: float

    def __init__(
        self, registry: HealthCheckRegistry, default_timeout: float = 0.5
    ) -> None:
        self.registry = registry
        self.default_timeout = default_timeout

    async def run_checks(
        self,
    ) -> tuple[list[CheckResult], Literal["ok", "degraded", "error"]]:
        checks = self.registry.get_checks()
        check_results = await asyncio.gather(
            *(self._run_check(check) for check in checks)
        )

        status: Literal["ok", "degraded", "error"] = "ok"
        for result, check in zip(check_results, checks):
            if result.status != "ok" and status != "error":
                status = "error" if check.critical else "degraded"

        return (check_results, status)

    async def _run_check(self, check: HealthCheck) -> CheckResult:
        try:
            return await asyncio.wait_for(check.check(), timeout=self.default_timeout)
        except asyncio.TimeoutError:
            return CheckResult(name=check.name, status="error", error="timeout")
        except Exception as e:
            return CheckResult(name=check.name, status="error", error=str(e))
