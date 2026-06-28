from dependency_injector import containers, providers
from configuration import Config
from services.health_check_registry import HealthCheckRegistry
from services.health_check_service import HealthCheckService
from services.llm_service import LLMService
from services.logger_service import LoggerService


class APIDependencies(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["api"])

    config = providers.Singleton(Config)

    health_check_registry = providers.Singleton(HealthCheckRegistry)

    health_check_service = providers.Factory(
        HealthCheckService, registry=health_check_registry
    )

    logger_service = providers.Factory(LoggerService, config=config)

    llm_service = providers.Singleton(
        LLMService, config=config, registry=health_check_registry
    )
