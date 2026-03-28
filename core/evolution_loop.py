"""
Evolution Loop Module - Orchestrates continuous self-improvement cycles.
"""

import time
from pathlib import Path
from typing import Dict, List, Callable, Optional
from .task_generator import TaskGenerator
from .system_critic import SystemCritic
from .resource_governor import ResourceGovernor
from .stability_controller import StabilityController
from .architecture_engine import ArchitectureEngine
from .agent_generator import AgentGenerator


class EvolutionLoop:
    """Manages autonomous evolution cycles."""

    def __init__(
        self,
        orchestrator,
        planner_agent,
        programmer_agent,
        reviewer_agent,
        backend_agent=None,
        frontend_agent=None,
        test_agent=None,
        sleep_interval: int = 5,
        max_cycles: int = 5,
        max_tasks_per_cycle: int = 5,
        kill_switch: Optional[Callable[[], bool]] = None,
        resource_config: Optional[Dict[str, int]] = None,
        max_concurrent_agents: int = 3,
        improvement_threshold: float = 0.03,
        max_no_improve_cycles: int = 2,
    ):
        self.orchestrator = orchestrator
        self.task_generator = TaskGenerator(orchestrator.repo_path)
        self.system_critic = SystemCritic()
        self.resource_governor = ResourceGovernor(resource_config, max_concurrent_agents)
        self.stability_controller = StabilityController(improvement_threshold, max_no_improve_cycles)
        self.architecture_engine = ArchitectureEngine(orchestrator.repo_path)
        self.agent_generator = AgentGenerator(orchestrator.repo_path)

        self.planner_agent = planner_agent
        self.programmer_agent = programmer_agent
        self.reviewer_agent = reviewer_agent
        self.backend_agent = backend_agent
        self.frontend_agent = frontend_agent
        self.test_agent = test_agent

        self.sleep_interval = sleep_interval
        self.max_cycles = max_cycles
        self.max_tasks_per_cycle = max_tasks_per_cycle
        self.kill_switch = kill_switch or (lambda: False)

        self.evolution_history: List[Dict] = []
        self.orchestrator = orchestrator
        self.task_generator = TaskGenerator(orchestrator.repo_path)
        self.system_critic = SystemCritic()

        self.planner_agent = planner_agent
        self.programmer_agent = programmer_agent
        self.reviewer_agent = reviewer_agent
        self.backend_agent = backend_agent
        self.frontend_agent = frontend_agent
        self.test_agent = test_agent

        self.sleep_interval = sleep_interval
        self.max_cycles = max_cycles
        self.max_tasks_per_cycle = max_tasks_per_cycle
        self.kill_switch = kill_switch or (lambda: False)

        self.evolution_history: List[Dict] = []

    def _task_description(self, task_info: Dict[str, str]) -> str:
        if task_info.get("reason"):
            return f"{task_info['type'].capitalize()} {task_info['target']} ({task_info['reason']})"
        return f"{task_info['type'].capitalize()} {task_info['target']}"

    def run(self) -> Dict[str, List[Dict]]:
        """Run autonomous evolution loop."""

        cycle = 0
        overall_tasks = []
        previous_cycle_score = None

        while cycle < self.max_cycles and not self.kill_switch():
            cycle += 1
            self.orchestrator.current_iteration = cycle
            self.orchestrator.iteration_history = []

            resource_state = self.resource_governor.status()
            if resource_state.get("throttled"):
                break

            architecture_suggestions = self.architecture_engine.analyze_structure()
            agent_reconciliation = self.agent_generator.reconcile_agents(
                existing_agents=[path.stem for path in Path(self.orchestrator.repo_path, "agents").glob("*.py")]
            )

            generated_tasks = self.task_generator.generate_tasks(
                limit=self.max_tasks_per_cycle
            )

            if not generated_tasks:
                break

            cycle_results = []
            cycle_scores = []

            for task_info in generated_tasks:
                if self.kill_switch():
                    break

                if not self.resource_governor.can_spawn_agent("execution"):
                    time.sleep(0.5)
                    continue

                if not self.resource_governor.start_agent("execution"):
                    continue

                try:
                    task_desc = self._task_description(task_info)
                    self.orchestrator.start_task(task_desc)

                    context = self.orchestrator.get_agents_prompt_context()
                    plan = self.planner_agent.plan_task(task_desc, context)
                    self.orchestrator.create_plan(plan)

                    agent_registry = {}
                    if self.backend_agent:
                        agent_registry["backend"] = self.backend_agent.generate_code
                    if self.frontend_agent:
                        agent_registry["frontend"] = self.frontend_agent.generate_code
                    if self.test_agent:
                        agent_registry["test"] = self.test_agent.generate_code

                    if agent_registry:
                        execution = self.orchestrator.execute_distributed(
                            agent_registry, use_improvement_loop=True
                        )
                    else:
                        code_result = self.programmer_agent.generate_code(plan, context)
                        execution = {
                            "status": "success",
                            "code": code_result.get("code", ""),
                            "execution_summary": {},
                        }

                    validation = self.orchestrator.validate_code(execution.get("code"))
                    review = self.reviewer_agent.review_code(
                        execution.get("code", ""), plan, validation
                    )

                    score = review.get("score", 0) if isinstance(review, dict) else 0
                    cycle_scores.append(score)

                    task_success = validation.get("valid", False) and score >= 0
                    self.orchestrator.memory.save_task_history(
                        task_id=self.orchestrator.current_task.get("id", f"cycle_{cycle}"),
                        task_description=task_desc,
                        generated_code=execution.get("code", ""),
                        quality_score=score,
                        iterations=1,
                        success=task_success,
                    )

                    self.orchestrator.memory.save_distributed_execution(
                        task_id=self.orchestrator.current_task.get("id", f"cycle_{cycle}"),
                        task_description=task_desc,
                        agents_used=list(agent_registry.keys()),
                        code=execution.get("code", ""),
                        decomposition_strategy=execution.get("execution_summary", {}).get("decomposition_strategy", "unknown"),
                        conflicts_count=len(execution.get("execution_summary", {}).get("conflicts", []) or []),
                        execution_time=execution.get("execution_time", 0.0) or 0.0,
                        success=(execution.get("status") == "success" and task_success),
                    )

                    requires_approval = (
                        task_info.get("target", "").startswith("core/")
                        or "architecture" in task_info.get("reason", "").lower()
                    )

                    cycle_results.append(
                        {
                            "task": task_desc,
                            "validation": validation,
                            "review": review,
                            "execution": execution,
                            "requires_approval": requires_approval,
                        }
                    )

                    overall_tasks.append(task_info)

                finally:
                    self.resource_governor.stop_agent("execution")

                if self.kill_switch():
                    break

            critic_report = self.system_critic.analyze(self.orchestrator)
            suggested_tasks = critic_report.get("improvement_tasks", [])

            cycle_avg_score = sum(cycle_scores) / len(cycle_scores) if cycle_scores else 0.0
            stability_report = self.stability_controller.evaluate_cycle(cycle_avg_score, previous_cycle_score)
            previous_cycle_score = cycle_avg_score

            stable = stability_report.get("should_stop") or (
                len(suggested_tasks) == 0 or (len(overall_tasks) > 0 and len(suggested_tasks) < 2)
            )

            self.orchestrator.memory.evolution_history.append(
                {
                    "cycle": cycle,
                    "generated_tasks": generated_tasks,
                    "results": cycle_results,
                    "critic_report": critic_report,
                    "architecture_suggestions": architecture_suggestions,
                    "agent_reconciliation": agent_reconciliation,
                    "resource_status": resource_state,
                    "stability_report": stability_report,
                    "stable": stable,
                    "timestamp": time.time(),
                }
            )

            self.orchestrator.memory._persist_evolution_history()

            if stable:
                break

            time.sleep(self.sleep_interval)

        return {
            "cycles_run": cycle,
            "tasks_generated": overall_tasks,
            "evolution_history": self.orchestrator.memory.get_evolution_history(),
        }
