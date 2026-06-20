from dependency_injector import containers, providers
from .configuration import Config


class APIDependencies(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=[".api"])

    config = providers.Singleton(Config)
