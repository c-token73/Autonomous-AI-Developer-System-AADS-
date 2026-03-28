"""
Orchestrator Module - Coordinates agents and workflow execution with self-improvement loops
and distributed multi-agent execution
"""

import asyncio
from typing import Dict, Any, Optional, List, Tuple, Callable
from datetime import datetime
from .memory import RepositoryMemory
from .validator import CodeValidator, ValidationResult
from .github_tool import GitHubTool
from .coordinator import DistributedCoordinator
from .task_decomposer import TaskDecomposer
from .aggregator import ResultAggregator
from .task_generator import TaskGenerator
from .system_critic import SystemCritic
from .evolution_loop import EvolutionLoop


# Self-improvement configuration
MAX_ITERATIONS = 5
QUALITY_THRESHOLD = 85


class TaskOrchestrator:
    """
    Orchestrates the workflow of planning → coding → validation → review → self-improvement.
    Manages interaction between agents and ensures safety checks with autonomous iteration.
    """

    def __init__(self, repo_path: str = "."):
        """
        Initialize orchestrator with repository context.
        
        Args:
            repo_path: Path to repository
        """
        self.repo_path = repo_path
        self.memory = RepositoryMemory(repo_path)
        self.validator = CodeValidator()
        self.github = GitHubTool(repo_path)
        self.current_task: Optional[Dict] = None
        self.current_plan: Optional[Dict] = None
        self.current_code: Optional[str] = None
        self.validation_result: Optional[ValidationResult] = None
        self.review_feedback: Optional[Dict] = None
        self.execution_history: List[Dict] = []
        self.iteration_history: List[Dict] = []  # Track iterations
        self.current_iteration = 0
        self.task_memory: Dict = {}  # Store context across calls
        
        # Distributed execution components
        self.coordinator = DistributedCoordinator()
        self.decomposer = TaskDecomposer()
        self.aggregator = ResultAggregator()
        self.distributed_execution_history: List[Dict] = []
        self.enable_distributed_mode = False

    def start_task(self, user_input: str, task_id: Optional[str] = None) -> Dict:
        """
        Start a new task in the orchestration workflow.
        
        Args:
            user_input: User's task description
            task_id: Optional task identifier
            
        Returns:
            Dictionary with task information
        """
        self.current_task = {
            "id": task_id or f"task_{datetime.now().timestamp()}",
            "input": user_input,
            "created_at": datetime.now().isoformat(),
            "status": "started",
            "step": "planning",
        }

        return self.current_task

    def create_plan(self, plan_content: Dict) -> Dict:
        """
        Store plan created by planner agent.
        
        Args:
            plan_content: Plan from planner agent
            
        Returns:
            Plan details
        """
        self.current_plan = {
            "content": plan_content,
            "created_at": datetime.now().isoformat(),
            "tasks": plan_content.get("tasks", []),
            "description": plan_content.get("description", ""),
        }

        if self.current_task:
            self.current_task["step"] = "coding"

        return self.current_plan

    def run_task(
        self,
        task_input: str,
        planner_agent,
        programmer_agent,
        reviewer_agent,
        use_distributed: bool = False,
        distributed_agents: Dict[str, Any] = None,
        use_autonomous: bool = False,
    ) -> Dict:
        """Run end-to-end workflow from task input through review.

        Args:
            task_input: task description string
            planner_agent: planner agent instance
            programmer_agent: programmer agent instance
            reviewer_agent: reviewer agent instance
            use_distributed: whether to execute distributed agents
            distributed_agents: dict mapping agent keys to callables
            use_autonomous: whether to run improvement loop

        Returns:
            Dictionary with plan, code, validation, and review.
        """
        self.start_task(task_input)

        context = self.get_agents_prompt_context()
        plan = planner_agent.plan_task(task_input, context)
        self.create_plan(plan)

        generated_code = ""
        distributed_execution = None

        if use_distributed and distributed_agents:
            distributed_execution = self.execute_distributed(
                distributed_agents,
                use_improvement_loop=use_autonomous,
            )

            generated_code = distributed_execution.get("code", "")
        else:
            # Single-agent path
            code_result = programmer_agent.generate_code(plan, context)
            generated_code = code_result.get("code", "")

            if use_autonomous:
                improved_code, _, _ = self.execute_autonomous_improvement_loop(
                    programmer_agent,
                    reviewer_agent,
                    generated_code,
                    plan,
                )
                generated_code = improved_code

        # Store code in orchestrator and memory
        self.store_generated_code(generated_code)

        # Validate and review
        validation = self.validate_code(generated_code)
        review = reviewer_agent.review_code(generated_code, plan, validation)
        self.store_review_feedback(review)

        return {
            "plan": plan,
            "code": generated_code,
            "validation": validation,
            "review": review,
            "distributed_execution": distributed_execution,
        }

    def store_generated_code(self, code: str, language: str = "python") -> Dict:
        """
        Store code generated by programmer agent.
        
        Args:
            code: Generated code
            language: Programming language
            
        Returns:
            Code storage details
        """
        self.current_code = code
        code_details = {
            "language": language,
            "length": len(code),
            "lines": len(code.split("\n")),
            "stored_at": datetime.now().isoformat(),
        }

        if self.current_task:
            self.current_task["step"] = "validation"

        return code_details

    def validate_code(self, code: Optional[str] = None) -> Dict:
        """
        Validate code using the validator.
        
        Args:
            code: Code to validate (uses current if not provided)
            
        Returns:
            Validation result as dictionary
        """
        code_to_validate = code or self.current_code
        if not code_to_validate:
            return {
                "valid": False,
                "errors": ["No code to validate"],
                "warnings": [],
                "metrics": {},
            }

        self.validation_result = self.validator.validate(
            code_to_validate, filename="generated_code.py"
        )

        if self.current_task:
            self.current_task["step"] = "review"

        return {
            "valid": self.validation_result.valid,
            "errors": self.validation_result.errors,
            "warnings": self.validation_result.warnings,
            "metrics": self.validation_result.metrics,
        }

    def store_review_feedback(self, feedback: Dict) -> Dict:
        """
        Store review feedback from reviewer agent.
        
        Args:
            feedback: Review feedback
            
        Returns:
            Feedback storage details
        """
        self.review_feedback = {
            "quality_score": feedback.get("quality_score", 0),
            "suggestions": feedback.get("suggestions", []),
            "security_issues": feedback.get("security_issues", []),
            "improvements": feedback.get("improvements", []),
            "reviewed_at": datetime.now().isoformat(),
        }

        if self.current_task:
            self.current_task["step"] = "awaiting_approval"

        return self.review_feedback

    def get_full_context(self) -> Dict:
        """
        Get complete context for agents (repository info + current state).
        
        Returns:
            Dictionary with all context information
        """
        return {
            "repository": self.memory.get_project_info(),
            "current_task": self.current_task,
            "current_plan": self.current_plan,
            "current_code_info": {
                "present": self.current_code is not None,
                "length": len(self.current_code) if self.current_code else 0,
            },
            "validation_status": {
                "valid": self.validation_result.valid
                if self.validation_result
                else None,
                "error_count": len(self.validation_result.errors)
                if self.validation_result
                else 0,
            },
            "review_feedback": self.review_feedback,
            "github_status": self.github.get_status(),
        }

    def get_agents_prompt_context(self) -> Dict:
        """
        Get formatted context for agent prompts.
        
        Returns:
            Formatted context for agents to use
        """
        context = {
            "task": self.current_task["input"] if self.current_task else "",
            "repo_structure": self.memory.get_repo_map(),
            "project_info": self.memory.get_project_info(),
        }

        if self.current_plan:
            context["existing_plan"] = self.current_plan["content"]

        if self.current_code:
            context["existing_code"] = self.current_code[:1000] + "..."  # Truncate

        return context

    def stage_for_approval(
        self,
        file_path: str,
        content: str,
        commit_message: str = "AI generated code",
    ) -> Dict:
        """
        Stage changes for user approval before commit.
        
        Args:
            file_path: File path to commit
            content: File content
            commit_message: Commit message
            
        Returns:
            Approval request details
        """
        success, msg = self.github.stage_changes(file_path, content)

        approval_request = {
            "file_path": file_path,
            "content_preview": content[:500] + "..."
            if len(content) > 500
            else content,
            "commit_message": commit_message,
            "staged_at": datetime.now().isoformat(),
            "status": "awaiting_approval",
            "staging_success": success,
            "staging_message": msg,
        }

        return approval_request

    def execute_commit(
        self, file_path: str, content: str, commit_message: str
    ) -> Dict:
        """
        Execute commit after user approval.
        
        IMPORTANT: This should only be called after user grants approval.
        
        Args:
            file_path: File to commit
            content: File content
            commit_message: Commit message
            
        Returns:
            Commit result
        """
        success, message = self.github.commit_to_branch(
            file_path, content, commit_message
        )

        commit_result = {
            "success": success,
            "message": message,
            "file_path": file_path,
            "committed_at": datetime.now().isoformat(),
            "branch": self.github.current_branch,
        }

        if success and self.current_task:
            self.current_task["step"] = "completed"

        self.execution_history.append(commit_result)

        return commit_result

    def reset_workflow(self) -> Dict:
        """
        Reset the current workflow for a new task.
        
        Returns:
            Confirmation message
        """
        self.current_task = None
        self.current_plan = None
        self.current_code = None
        self.validation_result = None
        self.review_feedback = None
        self.github.reset_pending_changes()

        return {"status": "reset", "message": "Workflow reset for new task"}

    def get_execution_history(self) -> List[Dict]:
        """
        Get history of executed commits.
        
        Returns:
            List of execution records
        """
        return self.execution_history

    def get_task_status(self) -> Dict:
        """
        Get current task and workflow status.
        
        Returns:
            Status dictionary
        """
        if not self.current_task:
            return {"status": "idle", "message": "No active task"}

        return {
            "task_id": self.current_task["id"],
            "current_step": self.current_task.get("step", "unknown"),
            "created_at": self.current_task["created_at"],
            "plan_available": self.current_plan is not None,
            "code_available": self.current_code is not None,
            "validation_passed": (
                self.validation_result.valid
                if self.validation_result
                else None
            ),
            "review_complete": self.review_feedback is not None,
            "pending_approval": (
                len(self.github.pending_changes) > 0
            ),
            "current_iteration": self.current_iteration,
            "iterations_history": self.iteration_history,
        }

    def execute_autonomous_improvement_loop(
        self,
        programmer_agent,
        reviewer_agent,
        initial_code: str,
        plan: Dict,
    ) -> Tuple[str, Dict, bool]:
        """
        Autonomously iterate on code until quality threshold is met.
        
        Args:
            programmer_agent: Programmer agent for code generation
            reviewer_agent: Reviewer agent for code review
            initial_code: Initial code to improve
            plan: Task plan for context
            
        Returns:
            Tuple of (final_code, review_feedback, threshold_met)
        """
        self.current_iteration = 0
        self.iteration_history = []
        current_code = initial_code

        for iteration in range(MAX_ITERATIONS):
            self.current_iteration = iteration + 1

            # Validate code first
            validation = self.validate_code(current_code)
            
            # If validation fails, send error back to programmer
            if not validation["valid"]:
                feedback = {
                    "type": "validation_error",
                    "errors": validation["errors"],
                    "iteration": self.current_iteration,
                    "timestamp": datetime.now().isoformat(),
                }
                self.iteration_history.append(feedback)
                
                # Refactor code based on errors
                refactor_result = programmer_agent.refactor_code(
                    current_code, validation["errors"], self.get_full_context()
                )
                current_code = refactor_result.get("refactored_code", current_code)
                continue

            # Review the code
            review = reviewer_agent.review_code(current_code, plan, validation)
            quality_score = review.get("score", 0)

            # Record iteration
            iteration_record = {
                "iteration": self.current_iteration,
                "quality_score": quality_score,
                "timestamp": datetime.now().isoformat(),
                "code_length": len(current_code),
                "validation_passed": True,
                "issues_count": len(review.get("issues", [])),
            }
            self.iteration_history.append(iteration_record)

            # Check if threshold is met
            if quality_score >= QUALITY_THRESHOLD:
                self.current_task["step"] = "improvement_complete"
                return current_code, review, True

            # If threshold not met and we have iterations left, improve
            if self.current_iteration < MAX_ITERATIONS:
                # Get improved code from reviewer if available
                improved_code = review.get("improved_code")
                if improved_code:
                    current_code = improved_code
                else:
                    # Ask programmer to refactor based on suggestions
                    refactor_result = programmer_agent.refactor_code(
                        current_code,
                        review.get("suggestions", []),
                        self.get_full_context(),
                    )
                    current_code = refactor_result.get(
                        "refactored_code", current_code
                    )

        # Max iterations reached
        self.current_task["step"] = "max_iterations_reached"
        return current_code, review if 'review' in locals() else {}, False

    def should_auto_improve(self, quality_score: float) -> bool:
        """
        Determine if code should be auto-improved.
        
        Args:
            quality_score: Current code quality score
            
        Returns:
            True if score is below threshold
        """
        return quality_score < QUALITY_THRESHOLD

    def get_iteration_stats(self) -> Dict:
        """
        Get statistics about iterations.
        
        Returns:
            Dictionary with iteration statistics
        """
        if not self.iteration_history:
            return {"iterations": 0, "total_score": 0, "improvement": 0}

        scores = [it.get("quality_score", 0) for it in self.iteration_history]
        return {
            "iterations": len(self.iteration_history),
            "initial_score": scores[0] if scores else 0,
            "final_score": scores[-1] if scores else 0,
            "improvement": (scores[-1] - scores[0]) if scores and len(scores) > 1 else 0,
            "avg_score": sum(scores) / len(scores) if scores else 0,
            "max_iterations": MAX_ITERATIONS,
            "threshold": QUALITY_THRESHOLD,
            "threshold_met": scores[-1] >= QUALITY_THRESHOLD if scores else False,
        }

    # ==================== DISTRIBUTED EXECUTION METHODS ====================

    def execute_distributed(
        self,
        agent_registry: Dict[str, Callable],
        use_improvement_loop: bool = True,
    ) -> Dict:
        """
        Execute task using distributed multi-agent system.
        
        Args:
            agent_registry: Dict mapping agent types to callable functions
                {
                    "backend": backend_agent.generate_code,
                    "frontend": frontend_agent.generate_code,
                    "test": test_agent.generate_code,
                }
            use_improvement_loop: Whether to apply improvement loop after aggregation
            
        Returns:
            Distributed execution result
        """
        if not self.current_plan or not self.current_task:
            return {
                "status": "failed",
                "error": "No active plan or task. Call start_task and create_plan first.",
            }
        
        try:
            # Run coordinator  to distribute and aggregate
            execution_result = asyncio.run(
                self.coordinator.coordinate_task(
                    self.current_task["input"],
                    self.current_plan["content"],
                    agent_registry,
                )
            )
            
            if execution_result.get("status") == "failed":
                return execution_result
            
            # Extract merged code
            distributed_code = execution_result.get("merged_code", "")
            
            # Apply improvement loop if enabled
            if use_improvement_loop and "programmer_agent" in agent_registry:
                # Create a wrapper for the improvement loop
                final_result = self._apply_improvement_to_distributed(
                    distributed_code,
                    execution_result,
                )
            else:
                final_result = distributed_code
            
            # Store in current_code
            self.current_code = distributed_code
            self.enable_distributed_mode = True
            
            # Record in history
            self.distributed_execution_history.append({
                "task_id": self.current_task["id"],
                "status": execution_result.get("status"),
                "agents_executed": execution_result.get("agents", {}),
                "decomposition": execution_result.get("decomposition"),
                "code_length": len(distributed_code),
                "conflicts": execution_result.get("conflicts"),
                "execution_time": execution_result.get("execution_time"),
                "executed_at": datetime.now().isoformat(),
            })
            
            return {
                "status": "success",
                "code": distributed_code,
                "execution_summary": {
                    "agents": execution_result.get("agents"),
                    "decomposition_strategy": execution_result.get(
                        "decomposition", {}
                    ).get("strategy"),
                    "complexity": execution_result.get("decomposition", {}).get(
                        "complexity"
                    ),
                    "conflicts": execution_result.get("conflicts"),
                },
            }
        
        except Exception as e:
            return {
                "status": "failed",
                "error": f"Distributed execution failed: {str(e)}",
            }

    def _apply_improvement_to_distributed(
        self,
        code: str,
        execution_result: Dict,
    ) -> str:
        """
        Apply improvement loop to distributed agent output.
        
        Args:
            code: Generated code from distributed agents
            execution_result: Result from distributed execution
            
        Returns:
            Improved code
        """
        # This is a hook point for applying the improvement loop
        # In a full implementation, this would call programmer and reviewer agents
        return code

    def run_evolution_loop(
        self,
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
    ) -> Dict:
        """Run an autonomous evolution loop that generates and executes tasks."""
        evolution = EvolutionLoop(
            orchestrator=self,
            planner_agent=planner_agent,
            programmer_agent=programmer_agent,
            reviewer_agent=reviewer_agent,
            backend_agent=backend_agent,
            frontend_agent=frontend_agent,
            test_agent=test_agent,
            sleep_interval=sleep_interval,
            max_cycles=max_cycles,
            max_tasks_per_cycle=max_tasks_per_cycle,
            kill_switch=kill_switch,
        )

        return evolution.run()

    def get_distributed_status(self) -> Dict:
        """
        Get distributed execution status and performance.
        
        Returns:
            Distributed system status
        """
        return {
            "distributed_mode_enabled": self.enable_distributed_mode,
            "coordinator_status": self.coordinator.get_execution_status(),
            "decomposer_summary": self.decomposer.get_subtasks_summary(),
            "aggregator_summary": self.aggregator.get_aggregation_summary(),
            "execution_count": len(self.distributed_execution_history),
            "agent_performance": self.coordinator.get_performance_summary(),
        }

    def get_distributed_history(self, limit: int = 10) -> List[Dict]:
        """
        Get recent distributed execution history.
        
        Args:
            limit: Number of recent executions to return
            
        Returns:
            List of execution records
        """
        return self.distributed_execution_history[-limit:]

