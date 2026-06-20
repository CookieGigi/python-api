from fastapi import FastAPI
from .router import defaultRouter
from dependency_injector import containers


def create_app(dependencies: containers.DeclarativeContainer) -> FastAPI:
    config = dependencies.config()
    app = FastAPI(debug=config.env == "dev")
    app.container = dependencies

    app.include_router(defaultRouter)

    return app
