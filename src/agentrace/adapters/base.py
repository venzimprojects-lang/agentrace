from __future__ import annotations

from dataclasses import dataclass
import shutil


@dataclass(frozen=True, slots=True)
class AgentAdapter:
    name: str
    binary: str

    def available(self) -> bool:
        return shutil.which(self.binary) is not None

    def version_command(self) -> list[str]:
        return [self.binary, "--version"]

    def command(self, prompt: str) -> list[str]:
        raise NotImplementedError
