import pytest
from httpx import AsyncClient, ASGITransport
from api.app import create_app
from configuration import Config
from dependency_injector import containers, providers


class TestContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["api"])

    # pydantic_config instance as a singleton provider
    config = providers.Singleton(
        Config,
        _env_file=".env.test",  # optional: load from test env file
    )


@pytest.fixture
def test_config(monkeypatch):
    """Override env vars before container instantiates Config."""
    monkeypatch.setenv("ENV", "testing")
    return Config()


@pytest.fixture
def container(test_config):
    """Container with pre-configured test config."""
    container = TestContainer()
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
