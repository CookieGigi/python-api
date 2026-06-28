import pytest
from httpx import AsyncClient, ASGITransport
from api.app import create_app
from configuration import Config
from dependencies import APIDependencies


@pytest.fixture
def test_config(monkeypatch):
    """Override env vars before container instantiates Config."""
    monkeypatch.setenv("ENV", "testing")
    monkeypatch.setenv("VERSION", "test-version")
    return Config()


@pytest.fixture
def container(test_config):
    """Container with pre-configured test config."""
    container = APIDependencies()
    container.config.override(test_config)
    return container


@pytest.fixture
def app(container):
    return create_app(container)


@pytest.fixture
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture
def anyio_backend():
    return "asyncio"
