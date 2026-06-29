from fastapi import FastAPI
from api.middleware.logging_middleware import LoggingMiddleware
from api.router import defaultRouter, healthRouter, modelsRouter
from dependency_injector import containers
from api.exceptions import register_exception_handlers
from fastapi.middleware.cors import CORSMiddleware
from services.logger_service import LoggerService


def create_app(dependencies: containers.DeclarativeContainer) -> FastAPI:
    config = dependencies.config()
    LoggerService.configure(config)

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
    app.include_router(modelsRouter)

    return app
