import pytest
from httpx import AsyncClient, ASGITransport

from api.app import create_app
from dependencies import APIDependencies
from services.health_check_registry import HealthCheckRegistry
from models.check_result import CheckResult

from tests.mocks.health_check import MockCheck


@pytest.fixture
async def failing_critical_client(test_config):
    container = APIDependencies()
    container.config.override(test_config)

    registry = HealthCheckRegistry()
    registry.register(MockCheck("db", critical=True, result=RuntimeError("db down")))
    container.health_check_registry.override(registry)

    async with AsyncClient(
        transport=ASGITransport(app=create_app(container)),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture
async def failing_non_critical_client(test_config):
    container = APIDependencies()
    container.config.override(test_config)

    registry = HealthCheckRegistry()
    registry.register(
        MockCheck(
            "cache",
            critical=False,
            result=CheckResult(name="cache", status="error", error="cache down"),
        )
    )
    container.health_check_registry.override(registry)

    async with AsyncClient(
        transport=ASGITransport(app=create_app(container)),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.mark.anyio
async def test_health_ok(client):
    r = await client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body == {"status": "ok", "version": "test-version"}


@pytest.mark.anyio
async def test_ready_ok(client):
    r = await client.get("/ready")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["version"] == "test-version"
    assert body["checks"] == []


@pytest.mark.anyio
async def test_ready_critical_failure(failing_critical_client):
    r = await failing_critical_client.get("/ready")

    assert r.status_code == 503
    body = r.json()
    assert body["status"] == "error"
    assert body["checks"][0]["name"] == "db"
    assert body["checks"][0]["status"] == "error"
    assert (
        body["checks"][0]["error"] is not None
        and "db down" in body["checks"][0]["error"]
    )


@pytest.mark.anyio
async def test_ready_non_critical_failure(failing_non_critical_client):
    r = await failing_non_critical_client.get("/ready")

    body = r.json()
    assert r.status_code == 503
    assert body["status"] == "degraded"
    assert body["checks"][0]["name"] == "cache"
    assert body["checks"][0]["status"] == "error"
    assert body["checks"][0]["error"] == "cache down"
