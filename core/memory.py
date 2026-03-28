"""
Memory Module - Repository context and file tracking with task history
and distributed execution tracking
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class RepositoryMemory:
    """
    Manages repository structure, file context, and knowledge base
    for agents to reference during code generation.
    Also maintains task history for learning and context.
    """

    def __init__(self, repo_path: str = "."):
        """Initialize repository memory with given path"""
        self.repo_path = Path(repo_path)
        self.file_index: Dict[str, Dict] = {}
        self.structure_cache: Optional[Dict] = None
        self.task_history: List[Dict] = []
        self.history_file = self.repo_path / ".memory" / "task_history.json"
        self.distributed_execution_history: List[Dict] = []
        self.distributed_history_file = self.repo_path / ".memory" / "distributed_history.json"
        self.evolution_history: List[Dict] = []
        self.evolution_history_file = self.repo_path / ".memory" / "evolution_history.json"
        self._index_repository()
        self._load_task_history()
        self._load_distributed_history()
        self._load_evolution_history()

    def _index_repository(self) -> None:
        """Index all Python files in the repository"""
        self.file_index = {}
        for file_path in self.repo_path.rglob("*.py"):
            if self._should_index(file_path):
                self.file_index[str(file_path)] = {
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "indexed": True,
                }

    def _should_index(self, file_path: Path) -> bool:
        """Check if file should be indexed"""
        excluded = {".git", "__pycache__", ".pytest_cache", ".venv", "venv"}
        return not any(part in file_path.parts for part in excluded)

    def get_repo_map(self) -> Dict:
        """
        Get complete repository structure and file mapping.
        
        Returns:
            Dictionary containing repo structure, files, and metadata
        """
        if self.structure_cache:
            return self.structure_cache

        structure = {
            "root": str(self.repo_path),
            "files": self.file_index,
            "directories": self._get_directories(),
            "python_files": len(self.file_index),
            "metadata": {
                "has_tests": self._has_tests_directory(),
                "has_gitignore": (self.repo_path / ".gitignore").exists(),
            },
        }

        self.structure_cache = structure
        return structure

    def _get_directories(self) -> List[str]:
        """Get list of all directories in repo"""
        dirs = []
        for item in self.repo_path.rglob("*"):
            if item.is_dir() and self._should_index(item):
                dirs.append(str(item.relative_to(self.repo_path)))
        return sorted(dirs)

    def _has_tests_directory(self) -> bool:
        """Check if tests directory exists"""
        return (self.repo_path / "tests").exists()

    def get_file_content(self, file_path: str) -> Optional[str]:
        """
        Get content of a specific file from repository.
        
        Args:
            file_path: Path to file relative to repo
            
        Returns:
            File content or None if file doesn't exist
        """
        full_path = self.repo_path / file_path
        if full_path.exists() and full_path.is_file():
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
                return None
        return None

    def list_files(self, directory: str = "") -> List[str]:
        """
        List all Python files in a directory.
        
        Args:
            directory: Directory path relative to repo
            
        Returns:
            List of file paths
        """
        target_dir = self.repo_path / directory if directory else self.repo_path
        files = []
        if target_dir.exists() and target_dir.is_dir():
            for file_path in target_dir.glob("*.py"):
                files.append(str(file_path.relative_to(self.repo_path)))
        return sorted(files)

    def refresh(self) -> None:
        """Refresh the repository index and clear caches"""
        self.structure_cache = None
        self._index_repository()

    def save_knowledge_base(self, knowledge: Dict) -> str:
        """
        Save knowledge base for future reference.
        
        Args:
            knowledge: Dictionary of knowledge to save
            
        Returns:
            Path to saved knowledge file
        """
        kb_dir = self.repo_path / ".knowledge"
        kb_dir.mkdir(exist_ok=True)

        kb_file = kb_dir / "knowledge_base.json"
        with open(kb_file, "w", encoding="utf-8") as f:
            json.dump(knowledge, f, indent=2)

        return str(kb_file)

    def get_project_info(self) -> Dict:
        """
        Get high-level project information.
        
        Returns:
            Dictionary with project metadata
        """
        return {
            "repo_path": str(self.repo_path),
            "total_python_files": len(self.file_index),
            "structure": self.get_repo_map(),
            "has_tests": self._has_tests_directory(),
            "has_git": (self.repo_path / ".git").exists(),
            "task_history_available": len(self.task_history) > 0,
        }

    def _load_task_history(self) -> None:
        """Load task history from file if it exists"""
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.task_history = data.get("tasks", [])
            except Exception as e:
                print(f"Error loading task history: {e}")
                self.task_history = []
        else:
            self.task_history = []

    def save_task_history(
        self,
        task_id: str,
        task_description: str,
        generated_code: str,
        quality_score: float,
        iterations: int = 1,
        success: bool = True,
    ) -> None:
        """
        Save task to history for future reference and learning.
        
        Args:
            task_id: Unique task identifier
            task_description: Description of the task
            generated_code: Final generated code
            quality_score: Final quality score achieved
            iterations: Number of iterations performed
            success: Whether task completed successfully
        """
        task_record = {
            "task_id": task_id,
            "description": task_description,
            "code_preview": generated_code[:500] + "..."
            if len(generated_code) > 500
            else generated_code,
            "code_length": len(generated_code),
            "quality_score": quality_score,
            "iterations": iterations,
            "success": success,
            "saved_at": datetime.now().isoformat(),
        }

        self.task_history.append(task_record)

        # Save to file
        self._persist_task_history()

    def _persist_task_history(self) -> None:
        """Persist task history to file"""
        try:
            self.history_file.parent.mkdir(exist_ok=True, parents=True)
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "last_updated": datetime.now().isoformat(),
                        "task_count": len(self.task_history),
                        "tasks": self.task_history,
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            print(f"Error saving task history: {e}")

    def get_task_history(self, limit: int = 10) -> List[Dict]:
        """
        Get recent task history.
        
        Args:
            limit: Maximum number of tasks to return
            
        Returns:
            List of task records
        """
        return self.task_history[-limit:]

    def get_similar_tasks(self, description: str, threshold: float = 0.5) -> List[Dict]:
        """
        Find similar tasks in history (simple string matching).
        
        Args:
            description: Task description to match
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of similar task records
        """
        similar = []
        description_lower = description.lower()

        for task in self.task_history:
            task_desc_lower = task["description"].lower()
            
            # Simple keyword matching
            common_words = len(
                set(description_lower.split()) & set(task_desc_lower.split())
            )
            total_words = len(set(description_lower.split()) | set(task_desc_lower.split()))
            
            if total_words > 0:
                similarity = common_words / total_words
                if similarity >= threshold:
                    similar.append(task)

        return similar

    def get_learning_context(self) -> Dict:
        """
        Get context from task history for learning.
        
        Returns:
            Dictionary with learning insights
        """
        if not self.task_history:
            return {
                "total_tasks": 0,
                "average_score": 0,
                "success_rate": 0,
                "insights": [],
            }

        successful = [t for t in self.task_history if t.get("success", False)]
        scores = [t.get("quality_score", 0) for t in self.task_history]

        return {
            "total_tasks": len(self.task_history),
            "successful_tasks": len(successful),
            "success_rate": len(successful) / len(self.task_history)
            if self.task_history
            else 0,
            "average_score": sum(scores) / len(scores) if scores else 0,
            "best_score": max(scores) if scores else 0,
            "worst_score": min(scores) if scores else 0,
            "avg_iterations": (
                sum(t.get("iterations", 1) for t in self.task_history)
                / len(self.task_history)
                if self.task_history
                else 0
            ),
        }

    # ==================== DISTRIBUTED EXECUTION TRACKING ====================

    def _load_distributed_history(self) -> None:
        """Load distributed execution history from file if it exists"""
        if self.distributed_history_file.exists():
            try:
                with open(self.distributed_history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.distributed_execution_history = data.get("executions", [])
            except Exception as e:
                print(f"Error loading distributed history: {e}")
                self.distributed_execution_history = []
        else:
            self.distributed_execution_history = []

    def save_distributed_execution(
        self,
        task_id: str,
        task_description: str,
        agents_used: List[str],
        code: str,
        decomposition_strategy: str,
        conflicts_count: int = 0,
        execution_time: float = 0.0,
        success: bool = True,
    ) -> None:
        """
        Save distributed execution record for analysis and learning.
        
        Args:
            task_id: Task identifier
            task_description: Task description
            agents_used: List of agents that executed
            code: Generated code
            decomposition_strategy: Strategy used (e.g., "full_stack_with_tests")
            conflicts_count: Number of conflicts detected
            execution_time: Time taken in seconds
            success: Whether execution was successful
        """
        execution_record = {
            "task_id": task_id,
            "description": task_description,
            "agents_used": agents_used,
            "agent_count": len(agents_used),
            "code_length": len(code),
            "decomposition_strategy": decomposition_strategy,
            "conflicts": conflicts_count,
            "execution_time": execution_time,
            "success": success,
            "saved_at": datetime.now().isoformat(),
        }

        self.distributed_execution_history.append(execution_record)
        self._persist_distributed_history()

    def _persist_distributed_history(self) -> None:
        """Persist distributed execution history to file"""
        try:
            self.distributed_history_file.parent.mkdir(exist_ok=True, parents=True)
            with open(self.distributed_history_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "last_updated": datetime.now().isoformat(),
                        "execution_count": len(self.distributed_execution_history),
                        "executions": self.distributed_execution_history,
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            print(f"Error saving distributed history: {e}")

    def get_distributed_history(self, limit: int = 10) -> List[Dict]:
        """
        Get recent distributed execution history.
        
        Args:
            limit: Maximum number of executions to return
            
        Returns:
            List of distributed execution records
        """
        return self.distributed_execution_history[-limit:]

    def _load_evolution_history(self) -> None:
        """Load evolution cycle history from file if it exists"""
        if self.evolution_history_file.exists():
            try:
                with open(self.evolution_history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.evolution_history = data.get("cycles", [])
            except Exception as e:
                print(f"Error loading evolution history: {e}")
                self.evolution_history = []
        else:
            self.evolution_history = []

    def _persist_evolution_history(self) -> None:
        """Persist evolution cycle history to file"""
        try:
            self.evolution_history_file.parent.mkdir(exist_ok=True, parents=True)
            with open(self.evolution_history_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "last_updated": datetime.now().isoformat(),
                        "cycle_count": len(self.evolution_history),
                        "cycles": self.evolution_history,
                    },
                    f,
                    indent=2,
                )
        except Exception as e:
            print(f"Error saving evolution history: {e}")

    def save_evolution_cycle(
        self,
        cycle_number: int,
        tasks: List[Dict],
        results: List[Dict],
        critic_report: Dict,
        stable: bool,
    ) -> None:
        """Save a single evolution cycle record"""
        record = {
            "cycle": cycle_number,
            "tasks": tasks,
            "results": results,
            "critic_report": critic_report,
            "stable": stable,
            "saved_at": datetime.now().isoformat(),
        }
        self.evolution_history.append(record)
        self._persist_evolution_history()

    def get_evolution_history(self, limit: int = 10) -> List[Dict]:
        """Get recent evolution history records"""
        return self.evolution_history[-limit:]

    def get_agent_performance_from_history(self) -> Dict:
        """
        Analyze agent performance from distributed execution history.
        
        Returns:
            Agent performance metrics
        """
        agent_stats = {}

        for execution in self.distributed_execution_history:
            agents = execution.get("agents_used", [])
            success = execution.get("success", False)

            for agent in agents:
                if agent not in agent_stats:
                    agent_stats[agent] = {
                        "executions": 0,
                        "successes": 0,
                        "total_code_length": 0,
                    }

                agent_stats[agent]["executions"] += 1
                if success:
                    agent_stats[agent]["successes"] += 1
                agent_stats[agent]["total_code_length"] += execution.get("code_length", 0)

        # Calculate success rates
        for agent, stats in agent_stats.items():
            if stats["executions"] > 0:
                stats["success_rate"] = stats["successes"] / stats["executions"]
                stats["avg_code_length"] = stats["total_code_length"] / stats["executions"]

        return agent_stats

    def get_decomposition_effectiveness(self) -> Dict:
        """
        Analyze effectiveness of different decomposition strategies.
        
        Returns:
            Strategy effectiveness metrics
        """
        strategy_stats = {}

        for execution in self.distributed_execution_history:
            strategy = execution.get("decomposition_strategy", "unknown")
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {
                    "count": 0,
                    "successes": 0,
                    "avg_conflicts": 0,
                    "avg_time": 0,
                }

            strategy_stats[strategy]["count"] += 1
            if execution.get("success", False):
                strategy_stats[strategy]["successes"] += 1
            strategy_stats[strategy]["avg_conflicts"] += execution.get("conflicts", 0)
            strategy_stats[strategy]["avg_time"] += execution.get("execution_time", 0)

        # Calculate averages
        for strategy, stats in strategy_stats.items():
            if stats["count"] > 0:
                stats["success_rate"] = stats["successes"] / stats["count"]
                stats["avg_conflicts"] = stats["avg_conflicts"] / stats["count"]
                stats["avg_time"] = stats["avg_time"] / stats["count"]

        return strategy_stats

