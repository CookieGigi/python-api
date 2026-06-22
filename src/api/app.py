from fastapi import FastAPI
from api.router import defaultRouter, healthRouter
from dependency_injector import containers
from api.exceptions import register_exception_handlers
from fastapi.middleware.cors import CORSMiddleware


def create_app(dependencies: containers.DeclarativeContainer) -> FastAPI:
    config = dependencies.config()
    app = FastAPI(debug=config.env == "dev")
    app.container = dependencies  # type: ignore
    register_exception_handlers(app)

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
