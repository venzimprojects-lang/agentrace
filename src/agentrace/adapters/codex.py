from .base import AgentAdapter


class CodexAdapter(AgentAdapter):
    def __init__(self) -> None:
        super().__init__(name="Codex", binary="codex")

    def command(self, prompt: str) -> list[str]:
        return [
            self.binary,
            "exec",
            "--sandbox",
            "workspace-write",
            "--ask-for-approval",
            "never",
            "--json",
            prompt,
        ]
