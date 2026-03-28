"""
System Critic Module - Meta-agent that identifies weaknesses and recommends improvement tasks.
"""

from typing import Dict, List, Any


class SystemCritic:
    """Meta-level critic for autonomous system self-evaluation."""

    def analyze(self, orchestrator: Any) -> Dict[str, Any]:
        """Analyze system behavior and propose improvements."""
        memory = orchestrator.memory
        agent_performance = memory.get_agent_performance_from_history()
        decomposition_stats = memory.get_decomposition_effectiveness()
        iteration_stats = orchestrator.get_iteration_stats()
        evolution_history = getattr(memory, "evolution_history", [])

        weaknesses: List[str] = []
        improvement_tasks: List[Dict[str, str]] = []

        # Agent performance weaknesses
        for agent, stats in agent_performance.items():
            success_rate = stats.get("success_rate", 0)
            if success_rate < 0.80:
                weaknesses.append(
                    f"Low {agent} success rate: {success_rate:.0%}"
                )
                improvement_tasks.append(
                    {
                        "type": "refactor",
                        "target": f"agents/{agent}_agent.py",
                        "reason": "Improve agent reliability",
                    }
                )

        # Iteration and threshold weaknesses
        if iteration_stats.get("iterations", 0) >= 3 and not iteration_stats.get("threshold_met", False):
            weaknesses.append("Frequent improvement loops without reaching quality threshold")
            improvement_tasks.append(
                {
                    "type": "refactor",
                    "target": "core/orchestrator.py",
                    "reason": "Tuning improvement loop and scoring logic",
                }
            )

        # Decomposition stability
        for strategy, stats in decomposition_stats.items():
            if stats.get("success_rate", 1.0) < 0.7:
                weaknesses.append(
                    f"Decomposition strategy '{strategy}' has low success rate ({stats.get('success_rate', 0):.0%})"
                )
                improvement_tasks.append(
                    {
                        "type": "refactor",
                        "target": "core/task_decomposer.py",
                        "reason": f"Improve {strategy} handling",
                    }
                )

        # Evolution stability check
        if len(evolution_history) > 0:
            last_cycle = evolution_history[-1]
            if last_cycle.get("stable", False):
                weaknesses.append("The system is stable, diminishing returns detected")

        if not weaknesses:
            weaknesses.append("No major weaknesses detected; system performing well")

        if not improvement_tasks:
            improvement_tasks.append(
                {
                    "type": "test",
                    "target": "tests/",   # broad recommendation
                    "reason": "Maintain test coverage",
                }
            )

        return {
            "weaknesses": weaknesses,
            "improvement_tasks": improvement_tasks,
            "agent_performance": agent_performance,
            "iteration_stats": iteration_stats,
            "decomposition_stats": decomposition_stats,
            "evolution_cycles": len(evolution_history),
        }
