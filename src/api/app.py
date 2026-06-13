from fastapi import FastAPI
from .router import defaultRouter


def create_app() -> FastAPI:
    app = FastAPI()

    app.include_router(defaultRouter)

    return app
