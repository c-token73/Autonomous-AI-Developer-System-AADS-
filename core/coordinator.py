"""
Coordinator - Main brain for distributed task execution across specialized agents
Manages task decomposition, parallel agent execution, and result aggregation
"""

import asyncio
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from .task_decomposer import TaskDecomposer
from .aggregator import ResultAggregator


# Distributed system configuration
MAX_PARALLEL_AGENTS = 3
AGENT_TIMEOUT = 30  # seconds
ENABLE_FALLBACK = True


class DistributedCoordinator:
    """
    Coordinates distributed multi-agent task execution.
    Decomposes tasks, manages parallel agent execution, and aggregates results.
    """

    def __init__(self):
        """Initialize coordinator with decomposer and aggregator"""
        self.decomposer = TaskDecomposer()
        self.aggregator = ResultAggregator()
        self.active_agents: List[str] = []
        self.execution_history: List[Dict] = []
        self.agent_performance: Dict[str, Dict] = {}  # Track agent success rates

    async def coordinate_task(
        self,
        task_description: str,
        plan: Dict,
        agent_registry: Dict[str, Callable],
    ) -> Dict:
        """
        Main coordination method: decompose task and execute agents in parallel.
        
        Args:
            task_description: User's task description
            plan: Plan from planner agent
            agent_registry: Dict mapping agent type to callable agent
                {
                    "backend": backend_agent.generate_code,
                    "frontend": frontend_agent.generate_code,
                    "test": test_agent.generate_code,
                }
        
        Returns:
            Aggregated result from all agents
        """
        execution_start = datetime.now()
        
        # Step 1: Decompose task into subtasks
        decomposition = self.decomposer.decompose_task(task_description, plan)
        
        if decomposition["subtask_count"] == 0:
            return {
                "status": "failed",
                "error": "Could not decompose task into subtasks",
                "fallback": "Use single-agent pipeline",
            }
        
        # Step 2: Execute agents in parallel based on decomposition
        parallel_batches = decomposition["parallel_executable"]
        agent_results = {}
        
        for batch_idx, agent_batch in enumerate(parallel_batches):
            try:
                # Execute batch of agents in parallel (respecting MAX_PARALLEL_AGENTS)
                batch_results = await self._execute_agent_batch(
                    agent_batch,
                    decomposition["subtasks"],
                    agent_registry,
                    batch_idx,
                )
                agent_results.update(batch_results)
            except Exception as e:
                self._log_batch_failure(batch_idx, str(e))
                if not ENABLE_FALLBACK:
                    return {
                        "status": "failed",
                        "error": f"Parallel execution failed: {str(e)}",
                        "batch": batch_idx,
                    }
        
        # Step 3: Aggregate results from all agents
        aggregation_result = self.aggregator.aggregate_results(agent_results)
        
        # Step 4: Prepare final output
        execution_end = datetime.now()
        execution_time = (execution_end - execution_start).total_seconds()
        
        final_result = {
            "status": aggregation_result["status"],
            "merged_code": aggregation_result.get("merged_code"),
            "merged_documentation": aggregation_result.get("merged_documentation"),
            "merged_dependencies": aggregation_result.get("merged_dependencies"),
            "decomposition": {
                "subtask_count": decomposition["subtask_count"],
                "strategy": decomposition["decomposition_strategy"],
                "complexity": decomposition["complexity_score"],
            },
            "agents": {
                "backend": agent_results.get("backend", {}).get("status", "not_executed"),
                "frontend": agent_results.get("frontend", {}).get("status", "not_executed"),
                "test": agent_results.get("test", {}).get("status", "not_executed"),
            },
            "conflicts": aggregation_result.get("conflicts"),
            "execution_time": execution_time,
            "executed_at": datetime.now().isoformat(),
        }
        
        # Track execution
        self.execution_history.append(final_result)
        
        return final_result

    async def _execute_agent_batch(
        self,
        agent_types: List[str],
        subtasks: List[Dict],
        agent_registry: Dict[str, Callable],
        batch_idx: int,
    ) -> Dict[str, Dict]:
        """
        Execute a batch of agents in parallel, respecting MAX_PARALLEL_AGENTS limit.
        
        Args:
            agent_types: List of agent types to execute
            subtasks: All subtasks (for filtering by type)
            agent_registry: Registered agents
            batch_idx: Batch index for logging
            
        Returns:
            Results from all agents in batch
        """
        # Limit parallel execution
        limited_agents = agent_types[:MAX_PARALLEL_AGENTS]
        
        if len(agent_types) > MAX_PARALLEL_AGENTS:
            self._log_parallel_limit(len(agent_types), MAX_PARALLEL_AGENTS)
        
        # Create tasks for parallel execution
        tasks = []
        for agent_type in limited_agents:
            if agent_type not in agent_registry:
                continue
            
            # Find subtask for this agent
            subtask = next((st for st in subtasks if st["type"] == agent_type), None)
            if not subtask:
                continue
            
            # Create async execution task
            task = asyncio.create_task(
                self._execute_agent_with_timeout(
                    agent_type,
                    agent_registry[agent_type],
                    subtask,
                )
            )
            tasks.append(task)
        
        # Execute all tasks concurrently
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        batch_results = {}
        for agent_type, result in zip(limited_agents, results_list):
            if isinstance(result, Exception):
                batch_results[agent_type] = {
                    "status": "failed",
                    "error": str(result),
                    "code": "",
                }
                self._update_agent_performance(agent_type, False)
            else:
                batch_results[agent_type] = result
                self._update_agent_performance(agent_type, result.get("status") == "success")
        
        return batch_results

    async def _execute_agent_with_timeout(
        self,
        agent_type: str,
        agent_func: Callable,
        subtask: Dict,
    ) -> Dict:
        """
        Execute agent with timeout protection.
        
        Args:
            agent_type: Type of agent
            agent_func: Agent's callable function
            subtask: Subtask to execute
            
        Returns:
            Agent result or timeout error
        """
        try:
            self.active_agents.append(agent_type)
            
            # Call agent with timeout
            result = await asyncio.wait_for(
                asyncio.to_thread(agent_func, subtask),
                timeout=AGENT_TIMEOUT,
            )
            
            result["status"] = "success"
            result["agent_type"] = agent_type
            result["subtask_id"] = subtask.get("task_id")
            
            return result
        
        except asyncio.TimeoutError:
            return {
                "status": "timeout",
                "error": f"Agent {agent_type} exceeded timeout ({AGENT_TIMEOUT}s)",
                "agent_type": agent_type,
                "subtask_id": subtask.get("task_id"),
                "code": "",
            }
        
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "agent_type": agent_type,
                "subtask_id": subtask.get("task_id"),
                "code": "",
            }
        
        finally:
            if agent_type in self.active_agents:
                self.active_agents.remove(agent_type)

    def _update_agent_performance(self, agent_type: str, success: bool):
        """Update performance metrics for an agent"""
        if agent_type not in self.agent_performance:
            self.agent_performance[agent_type] = {
                "executions": 0,
                "successes": 0,
                "failures": 0,
                "success_rate": 0.0,
            }
        
        perf = self.agent_performance[agent_type]
        perf["executions"] += 1
        
        if success:
            perf["successes"] += 1
        else:
            perf["failures"] += 1
        
        perf["success_rate"] = perf["successes"] / perf["executions"]

    def _log_batch_failure(self, batch_idx: int, error: str):
        """Log batch execution failure"""
        print(f"⚠️ Batch {batch_idx} failed: {error}")

    def _log_parallel_limit(self, requested: int, limit: int):
        """Log when parallel limit is exceeded"""
        print(f"⚠️ Parallel limit: {requested} agents requested, executing {limit} in parallel")

    def get_execution_status(self) -> Dict:
        """Get current execution status"""
        return {
            "active_agents": self.active_agents,
            "total_executions": len(self.execution_history),
            "last_execution": self.execution_history[-1] if self.execution_history else None,
            "agent_performance": self.agent_performance,
        }

    def get_performance_summary(self) -> Dict:
        """Get performance summary across all agents"""
        summary = {}
        
        for agent_type, perf in self.agent_performance.items():
            summary[agent_type] = {
                "executions": perf["executions"],
                "success_rate": f"{perf['success_rate']:.1%}",
                "successes": perf["successes"],
                "failures": perf["failures"],
            }
        
        return summary
