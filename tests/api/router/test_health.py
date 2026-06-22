import pytest


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
