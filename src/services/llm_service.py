from langchain_core.messages import AIMessage, BaseMessage

from configuration import Config
from models.check_result import CheckResult
from langchain_litellm import ChatLiteLLM
from interfaces.health_check import HealthCheck
from services.health_check_registry import HealthCheckRegistry


class LLMService(HealthCheck):
    _config: Config
    _provider: ChatLiteLLM

    critical = False

    def __init__(self, config: Config, registry: HealthCheckRegistry) -> None:
        self._config = config

        self._provider = ChatLiteLLM(model="groq/openai/gpt-oss-120b")

        registry.register(self)

    def get_model(self) -> ChatLiteLLM:
        return self._provider

    async def chat(self, messages: list[BaseMessage]) -> AIMessage:
        """Convenience method that mirrors model.invoke but via service."""
        return await self._provider.ainvoke(messages)

    async def check(self) -> CheckResult:
        try:
            await self._provider.ainvoke(
                [{"role": "user", "content": "ping"}],
                max_tokens=1,
            )
            return CheckResult(name="llm", status="ok", error=None)
        except Exception as e:
            return CheckResult(name="llm", status="error", error=str(e))
