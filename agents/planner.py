"""
Planner Agent - Breaks down tasks into actionable implementation plans
"""

from typing import Dict, List, Any
from datetime import datetime


class PlannerAgent:
    """
    The Planner Agent analyzes user requirements and creates structured
    implementation plans that guide the Programmer Agent.
    """

    def __init__(self, orchestrator=None):
        """
        Initialize the Planner Agent.
        
        Args:
            orchestrator: Reference to the TaskOrchestrator
        """
        self.orchestrator = orchestrator
        self.name = "Planner Agent"
        self.role = "Software Architect"

    def plan_task(self, user_input: str, context: Dict) -> Dict:
        """
        Create an implementation plan from user input.
        
        Args:
            user_input: The user's task description
            context: Repository and project context from orchestrator
            
        Returns:
            Dictionary containing structured plan
        """
        # Extract key information from input
        keywords = self._extract_keywords(user_input)
        complexity = self._assess_complexity(user_input)

        # Generate plan sections
        tasks = self._generate_tasks(user_input, keywords, context)
        structure = self._suggest_structure(keywords, context)
        timeline = self._estimate_timeline(tasks)

        plan = {
            "title": self._generate_title(user_input),
            "description": user_input,
            "complexity_level": complexity,
            "tasks": tasks,
            "suggested_structure": structure,
            "estimated_timeline": timeline,
            "key_considerations": self._identify_considerations(
                user_input, context
            ),
            "created_at": datetime.now().isoformat(),
            "agent": self.name,
        }

        # Store in orchestrator if available
        if self.orchestrator:
            self.orchestrator.create_plan(plan)

        return plan

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from input text"""
        keywords = []
        important_words = [
            "function",
            "class",
            "module",
            "api",
            "test",
            "database",
            "validation",
            "authentication",
            "error",
            "handle",
            "generate",
            "parse",
        ]

        text_lower = text.lower()
        for word in important_words:
            if word in text_lower:
                keywords.append(word)

        return keywords

    def _assess_complexity(self, text: str) -> str:
        """Assess task complexity level"""
        word_count = len(text.split())
        keyword_count = len(self._extract_keywords(text))

        if word_count < 50 and keyword_count <= 2:
            return "simple"
        elif word_count < 200:
            return "medium"
        else:
            return "complex"

    def _generate_tasks(self, user_input: str, keywords: List[str], context: Dict) -> List[Dict]:
        """Generate actionable tasks from user input"""
        tasks = []

        # Task 1: Analysis
        tasks.append(
            {
                "order": 1,
                "name": "Analyze Requirements",
                "description": "Review and understand the user requirements",
                "estimated_duration": "5 minutes",
            }
        )

        # Task 2: Design
        tasks.append(
            {
                "order": 2,
                "name": "Design Solution",
                "description": "Plan the code structure and architecture",
                "estimated_duration": "10 minutes",
            }
        )

        # Task 3: Implementation
        tasks.append(
            {
                "order": 3,
                "name": "Write Code",
                "description": "Implement the solution based on design",
                "estimated_duration": "15 minutes",
            }
        )

        # Task 4: Testing (if keywords suggest it)
        if "test" in keywords:
            tasks.append(
                {
                    "order": 4,
                    "name": "Write Tests",
                    "description": "Create unit tests for the implementation",
                    "estimated_duration": "10 minutes",
                }
            )

        # Task 5: Documentation
        tasks.append(
            {
                "order": len(tasks) + 1,
                "name": "Add Documentation",
                "description": "Document the code with docstrings and comments",
                "estimated_duration": "5 minutes",
            }
        )

        return tasks

    def _suggest_structure(self, keywords: List[str], context: Dict) -> Dict:
        """Suggest code structure based on keywords and context"""
        structure = {
            "main_functions": [],
            "classes": [],
            "imports": [],
            "files": [],
        }

        # Suggest structure based on keywords
        if "class" in keywords:
            structure["classes"].append("MainClass")

        if "function" in keywords:
            structure["main_functions"].append("main_function()")
            structure["main_functions"].append("helper_function()")

        # Always suggest standard imports
        structure["imports"] = [
            "from typing import Dict, List",
            "from dataclasses import dataclass",
        ]

        return structure

    def _estimate_timeline(self, tasks: List[Dict]) -> Dict:
        """Estimate total timeline for all tasks"""
        total_minutes = 0
        for task in tasks:
            # Parse duration strings like "10 minutes"
            duration_str = task.get("estimated_duration", "0 minutes")
            try:
                minutes = int(duration_str.split()[0])
                total_minutes += minutes
            except (ValueError, IndexError):
                total_minutes += 5  # Default 5 minutes

        return {
            "total_estimated_duration": f"{total_minutes} minutes",
            "total_hours": f"{total_minutes / 60:.1f} hours",
            "tasks_count": len(tasks),
        }

    def _identify_considerations(
        self, user_input: str, context: Dict
    ) -> List[str]:
        """Identify important considerations for implementation"""
        considerations = [
            "Ensure code follows repository conventions",
            "Validate all generated code before commit",
            "Add proper error handling",
            "Include type hints for better maintainability",
        ]

        # Add context-specific considerations
        if context.get("repository", {}).get("has_tests"):
            considerations.append("Consider existing test patterns")

        user_input_lower = user_input.lower()
        if any(word in user_input_lower for word in ["security", "auth", "token"]):
            considerations.append("Include security best practices")

        if any(
            word in user_input_lower for word in ["database", "data", "storage"]
        ):
            considerations.append("Follow data handling conventions")

        return considerations

    def _generate_title(self, user_input: str) -> str:
        """Generate a concise title for the task"""
        words = user_input.split()[:5]  # First 5 words
        title = " ".join(words)
        if len(user_input.split()) > 5:
            title += "..."
        return title

    def refine_plan(self, plan: Dict, feedback: str) -> Dict:
        """
        Refine the plan based on feedback.
        
        Args:
            plan: The current plan
            feedback: Feedback on the plan
            
        Returns:
            Refined plan
        """
        # Add feedback processing logic
        plan["feedback_received"] = feedback
        plan["refined_at"] = datetime.now().isoformat()
        plan["refinement_count"] = plan.get("refinement_count", 0) + 1

        return plan
