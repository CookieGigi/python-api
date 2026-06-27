import time

import pytest

from services.health_check_registry import HealthCheckRegistry
from models.check_result import CheckResult
from services.health_check_service import HealthCheckService

from tests.mocks.health_check import MockCheck


def make_service(*checks: MockCheck, timeout: float = 0.1) -> HealthCheckService:
    registry = HealthCheckRegistry()
    for check in checks:
        registry.register(check)
    return HealthCheckService(registry, default_timeout=timeout)


@pytest.mark.anyio
async def test_all_checks_pass():
    service = make_service(
        MockCheck(
            "db", critical=True, result=CheckResult(name="db", status="ok", error=None)
        ),
    )
    checks, status = await service.run_checks()

    assert status == "ok"
    assert len(checks) == 1
    assert checks[0].status == "ok"


@pytest.mark.anyio
async def test_non_critical_fails():
    service = make_service(
        MockCheck(
            "cache",
            critical=False,
            result=CheckResult(name="cache", status="error", error="down"),
        ),
    )
    checks, status = await service.run_checks()

    assert status == "degraded"
    assert checks[0].status == "error"


@pytest.mark.anyio
async def test_critical_fails():
    service = make_service(
        MockCheck(
            "db",
            critical=True,
            result=CheckResult(name="db", status="error", error="down"),
        ),
    )
    checks, status = await service.run_checks()

    assert status == "error"
    assert checks[0].status == "error"


@pytest.mark.anyio
async def test_error_not_overwritten_by_degraded():
    service = make_service(
        MockCheck(
            "db",
            critical=True,
            result=CheckResult(name="db", status="error", error="down"),
        ),
        MockCheck(
            "cache",
            critical=False,
            result=CheckResult(name="cache", status="error", error="down"),
        ),
    )
    checks, status = await service.run_checks()

    assert status == "error"


@pytest.mark.anyio
async def test_exception_caught():
    service = make_service(
        MockCheck("db", critical=True, result=RuntimeError("boom")),
    )
    checks, status = await service.run_checks()

    assert status == "error"
    assert checks[0].status == "error"
    assert checks[0].error is not None and "boom" in checks[0].error


@pytest.mark.anyio
async def test_timeout_caught():
    service = make_service(
        MockCheck(
            "slow",
            critical=True,
            result=CheckResult(name="slow", status="ok", error=None),
            delay=1.0,
        ),
    )
    checks, status = await service.run_checks()

    assert status == "error"
    assert checks[0].status == "error"
    assert checks[0].error == "timeout"


@pytest.mark.anyio
async def test_checks_run_concurrently():
    service = make_service(
        MockCheck(
            "a",
            critical=True,
            result=CheckResult(name="a", status="ok", error=None),
            delay=0.2,
        ),
        MockCheck(
            "b",
            critical=True,
            result=CheckResult(name="b", status="ok", error=None),
            delay=0.2,
        ),
        timeout=1.0,
    )

    start = time.monotonic()
    checks, status = await service.run_checks()
    elapsed = time.monotonic() - start

    assert status == "ok"
    assert elapsed < 0.35
