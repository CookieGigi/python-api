import asyncio

from models.check_result import CheckResult


class MockCheck:
    def __init__(
        self,
        name: str,
        critical: bool,
        result: CheckResult | Exception,
        delay: float = 0,
    ):
        self.name = name
        self.critical = critical
        self._result = result
        self._delay = delay

    async def check(self) -> CheckResult:
        if self._delay:
            await asyncio.sleep(self._delay)
        if isinstance(self._result, Exception):
            raise self._result
        return self._result
