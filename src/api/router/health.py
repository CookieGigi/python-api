from fastapi import APIRouter, Depends, Response

from dependency_injector.wiring import inject, Provide
from dependencies import APIDependencies
from configuration import Config
from services.health_check_service import HealthCheckService
from api.schemas.health import HealthResponse, ReadyResponse


router = APIRouter()


@router.get("/health")
@inject
async def get_health(
    config: Config = Depends(Provide[APIDependencies.config]),
) -> HealthResponse:
    return HealthResponse(version=config.version)


@router.get("/ready")
@inject
async def get_ready(
    response: Response,
    config: Config = Depends(Provide[APIDependencies.config]),
    check_service: HealthCheckService = Depends(
        Provide[APIDependencies.health_check_service]
    ),
) -> ReadyResponse:
    check_results, status = await check_service.run_checks()

    if status != "ok":
        response.status_code = 503
    return ReadyResponse(version=config.version, checks=check_results, status=status)
