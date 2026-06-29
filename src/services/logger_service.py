import logging
from typing import Self

import structlog

from configuration import Config

_structlog_initialized = False


class LoggerService:
    _config: Config
    _logger: structlog.BoundLogger

    def __init__(self, config: Config) -> None:
        self._logger = structlog.get_logger(service=config.name)
        self._config = config

    def bind(self, **kwargs) -> Self:
        cls = type(self)
        new = cls.__new__(cls)
        new._logger = self._logger.bind(**kwargs)
        new._config = self._config
        return new

    def unbind(self, *keys: str) -> Self:
        cls = type(self)
        new = cls.__new__(cls)
        new._logger = self._logger.unbind(*keys)
        new._config = self._config
        return new

    def debug(self, event: str, **kwargs):
        self._logger.debug(event, **kwargs)

    def info(self, event: str, **kwargs):
        self._logger.info(event, **kwargs)

    def warning(self, event: str, **kwargs):
        self._logger.warning(event, **kwargs)

    def error(self, event: str, exc_info: bool = False, **kwargs):
        self._logger.error(event, exc_info=exc_info, **kwargs)

    def exception(self, event: str, **kwargs):
        self._logger.exception(event, **kwargs)

    @staticmethod
    def configure(config: Config) -> None:
        global _structlog_initialized
        if _structlog_initialized:
            return
        _structlog_initialized = True

        level = getattr(logging, config.effective_log_level.upper())
        is_json = config.log_format == "json" or config.env == "prod"
        renderer = (
            structlog.processors.JSONRenderer()
            if is_json
            else structlog.dev.ConsoleRenderer(colors=True)
        )

        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                renderer,
            ],
            wrapper_class=structlog.make_filtering_bound_logger(level),
        )
