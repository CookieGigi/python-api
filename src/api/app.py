from typing import Callable

from fastapi import FastAPI
import structlog
import logging
import sys
from api.middleware.logging_middleware import LoggingMiddleware
from api.router import defaultRouter, healthRouter
from dependency_injector import containers
from api.exceptions import register_exception_handlers
from fastapi.middleware.cors import CORSMiddleware
from configuration import Config

_structlog_initialized = False


def _configure_structlog(config: Config):

    global _structlog_initialized
    if _structlog_initialized:
        return  # idempotent for reloader process
    _structlog_initialized = True

    shared_processors: list[Callable] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    is_json = config.log_format == "json" or config.env == "prod"

    if is_json:
        structlog_processors = shared_processors + [structlog.processors.JSONRenderer()]
        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
            foreign_pre_chain=shared_processors,
        )
    else:
        structlog_processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(colors=True),
            foreign_pre_chain=shared_processors,
        )

    level = getattr(logging, config.effective_log_level.upper())

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(level)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)

    structlog.configure(
        processors=structlog_processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # --- suppress uvicorn.access (middleware replaces it) ---
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.handlers.clear()
    uvicorn_access.propagate = False
    uvicorn_access.addHandler(logging.NullHandler())

    # --- route uvicorn.error through root logger for consistent formatting ---
    uvicorn_error = logging.getLogger("uvicorn.error")
    uvicorn_error.handlers.clear()
    uvicorn_error.propagate = True


def create_app(dependencies: containers.DeclarativeContainer) -> FastAPI:
    config = dependencies.config()
    _configure_structlog(config)

    llm = dependencies.llm_service()
    print(llm)

    app = FastAPI(debug=config.env == "dev")
    app.container = dependencies  # type: ignore
    register_exception_handlers(app)

    app.add_middleware(LoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["Authorization", "Content-Type"],
    )

    app.include_router(defaultRouter)
    app.include_router(healthRouter)

    return app
