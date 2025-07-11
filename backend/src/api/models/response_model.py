from pydantic import BaseModel


class UserInput(BaseModel):
    query: str
    chat_history: list[dict[str, str]] = []
    list_sources: bool = False
    list_context: bool = False


class ContextSource(BaseModel):
    source: str = ""
    context: str = ""


class ChatResponse(BaseModel):
    response: str
    context_sources: list[ContextSource] = []
    tools: list[str] = []


class ChatToolResponse(BaseModel):
    response: str
    sources: list[str] = []
    context: list[str] = []
    tools: list[str] = []
