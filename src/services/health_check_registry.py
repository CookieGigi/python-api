from interfaces.health_check import HealthCheck


class HealthCheckRegistry:
    _checks: list[HealthCheck]

    def __init__(self) -> None:
        self._checks = []

    def register(self, check: HealthCheck):
        self._checks.append(check)

    def get_checks(self) -> list[HealthCheck]:
        return self._checks
