from dataclasses import dataclass
from typing import Callable, Any

@dataclass(frozen=True)
class AgentSpec:
    name: str
    capabilities: frozenset[str]
    runner: Callable[..., Any]

class AgentRegistry:
    def __init__(self): self._agents: dict[str, AgentSpec] = {}
    def register(self, name: str, capabilities: set[str] | list[str], runner: Callable[..., Any]):
        if not name or not callable(runner): raise ValueError("Agent name and callable runner are required")
        self._agents[name] = AgentSpec(name, frozenset(capabilities), runner)
    def get(self, name: str) -> AgentSpec:
        try: return self._agents[name]
        except KeyError as exc: raise ValueError(f"No agent registered as '{name}'") from exc
    def select(self, required_capabilities: list[str]) -> AgentSpec:
        required=set(required_capabilities)
        matches=[spec for spec in self._agents.values() if required.issubset(spec.capabilities)]
        if not matches: raise ValueError(f"No agent supports capabilities: {sorted(required)}")
        return sorted(matches, key=lambda x: x.name)[0]
    def describe(self):
        return {name: sorted(spec.capabilities) for name,spec in self._agents.items()}

registry=AgentRegistry()
