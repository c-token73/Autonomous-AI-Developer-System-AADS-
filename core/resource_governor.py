"""
Resource Governor - Simulates CPU resource allocation and throttles agent execution.
"""

from typing import Dict, Optional


class ResourceGovernor:
    """Manage and simulate resource allocation among system components."""

    def __init__(self, config: Optional[Dict[str, int]] = None, max_concurrent_agents: int = 3):
        # Default equal split for planner/execution/review/evolution
        self.config = config or {
            "planner": 25,
            "execution": 25,
            "review": 25,
            "evolution": 25,
        }
        self.max_concurrent_agents = max_concurrent_agents
        self.active_agents = set()

    def get_allocation(self) -> Dict[str, int]:
        return self.config.copy()

    def can_spawn_agent(self, agent_name: str) -> bool:
        if len(self.active_agents) >= self.max_concurrent_agents:
            return False
        return True

    def start_agent(self, agent_name: str) -> bool:
        if not self.can_spawn_agent(agent_name):
            return False
        self.active_agents.add(agent_name)
        return True

    def stop_agent(self, agent_name: str) -> None:
        self.active_agents.discard(agent_name)

    def throttle(self, threshold: int = 80) -> bool:
        total = sum(self.config.values())
        usage = sum(self.config.values())
        if total == 0:
            return False

        percent = usage / total * 100
        return percent >= threshold

    def update_allocation(self, component: str, value: int) -> None:
        if component in self.config:
            self.config[component] = max(0, min(100, value))

    def status(self) -> Dict[str, any]:
        return {
            "allocation": self.get_allocation(),
            "max_concurrent_agents": self.max_concurrent_agents,
            "active_agents": list(self.active_agents),
            "active_count": len(self.active_agents),
            "throttled": self.throttle(),
        }
