from typing import Annotated

from langgraph.graph import add_messages
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage


class AgentState(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages]
    model: str | None = Field(default=None)
