from .base import AgentAdapter


class GeminiAdapter(AgentAdapter):
    def __init__(self) -> None:
        super().__init__(name="Gemini CLI", binary="gemini")

    def command(self, prompt: str) -> list[str]:
        return [
            self.binary,
            "-p",
            prompt,
            "--skip-trust",
            "--approval-mode",
            "auto_edit",
            "--output-format",
            "json",
        ]
