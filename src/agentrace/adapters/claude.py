from .base import AgentAdapter


class ClaudeAdapter(AgentAdapter):
    def __init__(self) -> None:
        super().__init__(name="Claude Code", binary="claude")

    def command(self, prompt: str) -> list[str]:
        return [
            self.binary,
            "-p",
            prompt,
            "--permission-mode",
            "acceptEdits",
            "--output-format",
            "json",
        ]
