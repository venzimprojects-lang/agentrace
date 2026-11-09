from .base import AgentAdapter
from .claude import ClaudeAdapter
from .codex import CodexAdapter
from .gemini import GeminiAdapter


def default_adapters() -> list[AgentAdapter]:
    return [ClaudeAdapter(), CodexAdapter(), GeminiAdapter()]


__all__ = [
    "AgentAdapter",
    "ClaudeAdapter",
    "CodexAdapter",
    "GeminiAdapter",
    "default_adapters",
]
