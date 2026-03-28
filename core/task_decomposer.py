"""
Task Decomposer - Breaks complex tasks into specialized subtasks for parallel execution
"""

from typing import Dict, List, Optional
from datetime import datetime


class TaskDecomposer:
    """
    Breaks down a user task into structured subtasks that can be assigned to
    specialized agents (backend, frontend, test) for parallel execution.
    """

    # Task type keywords for classification
    BACKEND_KEYWORDS = [
        "api", "backend", "database", "server", "endpoint",
        "model", "algorithm", "business logic", "computation",
        "rest", "graphql", "authentication", "authorization"
    ]
    
    FRONTEND_KEYWORDS = [
        "ui", "frontend", "interface", "dashboard", "button",
        "form", "page", "component", "streamlit", "visualization",
        "state", "input", "output", "display", "layout"
    ]
    
    TEST_KEYWORDS = [
        "test", "unit", "integration", "edge case", "validation",
        "error handling", "mock", "pytest", "Coverage", "qa"
    ]

    def __init__(self):
        """Initialize task decomposer"""
        self.subtasks_generated = []
        self.last_decomposition = None

    def decompose_task(self, task_description: str, plan: Dict) -> Dict:
        """
        Decompose a task into specialized subtasks based on content analysis.
        
        Args:
            task_description: User's task description
            plan: Plan from planner agent
            
        Returns:
            Dictionary with decomposed subtasks
        """
        subtasks = []
        
        # Analyze task description and plan to identify what types of work are needed
        backend_content = self._extract_backend_content(task_description, plan)
        frontend_content = self._extract_frontend_content(task_description, plan)
        test_content = self._extract_test_content(task_description, plan)
        
        # Create backend subtask if content identified
        if backend_content:
            subtasks.append({
                "type": "backend",
                "task_id": f"backend_{datetime.now().timestamp()}",
                "description": backend_content,
                "priority": self._calculate_priority(backend_content, "backend"),
                "dependencies": [],
                "created_at": datetime.now().isoformat(),
            })
        
        # Create frontend subtask if content identified
        if frontend_content:
            subtasks.append({
                "type": "frontend",
                "task_id": f"frontend_{datetime.now().timestamp()}",
                "description": frontend_content,
                "priority": self._calculate_priority(frontend_content, "frontend"),
                "dependencies": ["backend"] if backend_content else [],
                "created_at": datetime.now().isoformat(),
            })
        
        # Create test subtask if content identified
        if test_content:
            subtasks.append({
                "type": "test",
                "task_id": f"test_{datetime.now().timestamp()}",
                "description": test_content,
                "priority": self._calculate_priority(test_content, "test"),
                "dependencies": ["backend", "frontend"] if (backend_content or frontend_content) else [],
                "created_at": datetime.now().isoformat(),
            })
        
        # If no specific types identified, create a generic full-stack task
        if not subtasks:
            subtasks = self._create_generic_subtasks(task_description, plan)
        
        decomposition = {
            "task_description": task_description,
            "subtask_count": len(subtasks),
            "subtasks": subtasks,
            "decomposition_strategy": self._identify_strategy(subtasks),
            "parallel_executable": self._identify_parallelizable(subtasks),
            "decomposed_at": datetime.now().isoformat(),
            "complexity_score": self._calculate_complexity(task_description),
        }
        
        self.last_decomposition = decomposition
        self.subtasks_generated.append(decomposition)
        
        return decomposition

    def _extract_backend_content(self, task_desc: str, plan: Dict) -> str:
        """Extract backend-related content from task"""
        task_lower = task_desc.lower()
        plan_str = str(plan).lower()
        
        # Check for backend keywords
        has_backend = any(kw in task_lower or kw in plan_str for kw in self.BACKEND_KEYWORDS)
        
        if not has_backend:
            return ""
        
        # Extract specific backend requirements
        backend_req = []
        if "database" in task_lower or "db" in task_lower:
            backend_req.append("Implement database models and queries")
        if "api" in task_lower or "endpoint" in task_lower:
            backend_req.append("Create REST/GraphQL endpoints")
        if "authentication" in task_lower:
            backend_req.append("Implement authentication and authorization")
        if "algorithm" in task_lower or "compute" in task_lower:
            backend_req.append("Implement core business logic and algorithms")
        
        if not backend_req:
            backend_req.append("Implement backend logic and data handling")
        
        backend_desc = (
            f"Backend Development Task:\n"
            f"- Original task: {task_desc}\n"
            f"- Requirements: {'; '.join(backend_req)}\n"
            f"- Focus: API endpoints, database operations, business logic\n"
        )
        
        return backend_desc

    def _extract_frontend_content(self, task_desc: str, plan: Dict) -> str:
        """Extract frontend-related content from task"""
        task_lower = task_desc.lower()
        plan_str = str(plan).lower()
        
        # Check for frontend keywords
        has_frontend = any(kw in task_lower or kw in plan_str for kw in self.FRONTEND_KEYWORDS)
        
        # Also check if task mentions UI/interface even without explicit keywords
        has_ui = "interface" in task_lower or "display" in task_lower or "show" in task_lower
        
        if not (has_frontend or has_ui):
            return ""
        
        # Extract specific frontend requirements
        frontend_req = []
        if "dashboard" in task_lower:
            frontend_req.append("Create dashboard with metrics and visualizations")
        if "form" in task_lower:
            frontend_req.append("Design input forms with validation")
        if "button" in task_lower or "interaction" in task_lower:
            frontend_req.append("Implement interactive components and handlers")
        if "streamlit" in task_lower:
            frontend_req.append("Use Streamlit for web interface")
        
        if not frontend_req:
            frontend_req.append("Create user interface and user interactions")
        
        frontend_desc = (
            f"Frontend Development Task:\n"
            f"- Original task: {task_desc}\n"
            f"- Requirements: {'; '.join(frontend_req)}\n"
            f"- Focus: UI components, user interactions, data visualization\n"
        )
        
        return frontend_desc

    def _extract_test_content(self, task_desc: str, plan: Dict) -> str:
        """Extract test-related content from task"""
        task_lower = task_desc.lower()
        plan_str = str(plan).lower()
        
        # Check for test keywords
        has_test = any(kw in task_lower or kw in plan_str for kw in self.TEST_KEYWORDS)
        
        if not has_test:
            return ""
        
        # Extract specific test requirements
        test_req = []
        if "unit" in task_lower:
            test_req.append("Write unit tests for all functions")
        if "integration" in task_lower:
            test_req.append("Write integration tests")
        if "edge case" in task_lower or "error" in task_lower:
            test_req.append("Cover edge cases and error scenarios")
        if "validation" in task_lower:
            test_req.append("Test input validation and constraints")
        
        if not test_req:
            test_req.append("Generate comprehensive test suite")
        
        test_desc = (
            f"Testing Task:\n"
            f"- Original task: {task_desc}\n"
            f"- Requirements: {'; '.join(test_req)}\n"
            f"- Focus: Unit tests, integration tests, edge cases\n"
        )
        
        return test_desc

    def _create_generic_subtasks(self, task_desc: str, plan: Dict) -> List[Dict]:
        """Create generic full-stack subtasks if no specific types detected"""
        return [
            {
                "type": "backend",
                "task_id": f"backend_{datetime.now().timestamp()}",
                "description": f"Implement core backend logic for: {task_desc}",
                "priority": 1,
                "dependencies": [],
                "created_at": datetime.now().isoformat(),
            },
            {
                "type": "frontend",
                "task_id": f"frontend_{datetime.now().timestamp()}",
                "description": f"Create user interface for: {task_desc}",
                "priority": 2,
                "dependencies": ["backend"],
                "created_at": datetime.now().isoformat(),
            },
            {
                "type": "test",
                "task_id": f"test_{datetime.now().timestamp()}",
                "description": f"Write tests for: {task_desc}",
                "priority": 3,
                "dependencies": ["backend"],
                "created_at": datetime.now().isoformat(),
            },
        ]

    def _calculate_priority(self, content: str, task_type: str) -> int:
        """Calculate priority (1=highest, 3=lowest) based on content length and keywords"""
        content_length = len(content)
        
        # Base priority by type
        priority_map = {"backend": 1, "frontend": 2, "test": 3}
        priority = priority_map.get(task_type, 2)
        
        # Increase priority if content is complex
        if content_length > 500:
            priority = max(1, priority - 1)
        
        return priority

    def _calculate_complexity(self, task_desc: str) -> float:
        """Calculate complexity score (0.0-1.0) based on task description"""
        keywords_indicating_complexity = [
            "algorithm", "machine learning", "distributed",
            "concurrent", "optimization", "security",
            "performance", "scalability", "real-time"
        ]
        
        task_lower = task_desc.lower()
        complexity = 0.3  # Base complexity
        
        for keyword in keywords_indicating_complexity:
            if keyword in task_lower:
                complexity += 0.1
        
        # Increase with task length
        complexity += min(0.2, len(task_desc) / 1000)
        
        return min(1.0, complexity)

    def _identify_strategy(self, subtasks: List[Dict]) -> str:
        """Identify decomposition strategy used"""
        if len(subtasks) == 1:
            return "single_task"
        elif len(subtasks) == 2:
            return "frontend_backend"
        elif len(subtasks) == 3:
            return "full_stack_with_tests"
        else:
            return "complex_multi_component"

    def _identify_parallelizable(self, subtasks: List[Dict]) -> List[List[str]]:
        """Identify which subtasks can run in parallel based on dependencies"""
        parallelizable = []
        
        # First round: independent tasks
        independent = [st["type"] for st in subtasks if not st.get("dependencies")]
        if independent:
            parallelizable.append(independent)
        
        # Subsequent rounds: tasks dependent on first round
        processed = set(independent)
        while len(processed) < len(subtasks):
            current_batch = []
            for st in subtasks:
                if st["type"] not in processed:
                    deps = st.get("dependencies", [])
                    if all(d in processed for d in deps):
                        current_batch.append(st["type"])
            if current_batch:
                parallelizable.append(current_batch)
                processed.update(current_batch)
            else:
                break
        
        return parallelizable

    def get_subtasks_summary(self) -> Dict:
        """Get summary of last decomposition"""
        if not self.last_decomposition:
            return {"status": "no_decomposition"}
        
        decomp = self.last_decomposition
        return {
            "subtask_count": decomp["subtask_count"],
            "subtask_types": [st["type"] for st in decomp["subtasks"]],
            "parallel_batches": decomp["parallel_executable"],
            "complexity": decomp["complexity_score"],
        }
