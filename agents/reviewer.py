"""
Reviewer Agent - Analyzes code quality and suggests improvements
"""

import ast
from typing import Dict, List, Optional
from datetime import datetime


class ReviewerAgent:
    """
    The Reviewer Agent performs comprehensive code review,
    identifying issues, suggesting improvements, and checking
    for security vulnerabilities and best practices.
    """

    def __init__(self, orchestrator=None):
        """
        Initialize the Reviewer Agent.
        
        Args:
            orchestrator: Reference to the TaskOrchestrator
        """
        self.orchestrator = orchestrator
        self.name = "Reviewer Agent"
        self.role = "Code Reviewer & Quality Assurance"

    def review_code(
        self, code: str, plan: Dict, validation_result: Optional[Dict] = None
    ) -> Dict:
        """
        Perform comprehensive code review.
        
        Args:
            code: Code to review
            plan: Original plan for context
            validation_result: Results from validator (if available)
            
        Returns:
            Detailed review feedback with score
        """
        review = {
            "score": 0,  # Primary quality score (0-100)
            "code_quality_score": 0,
            "suggestions": [],
            "improvements": [],
            "security_issues": [],
            "best_practices": [],
            "issues": [],  # Alias for issues_found
            "improved_code": None,  # Optional improved code
            "reviewed_at": datetime.now().isoformat(),
            "agent": self.name,
        }

        # Perform different checks
        review["code_quality_score"] = self._calculate_quality_score(code)
        review["suggestions"] = self._generate_suggestions(code, plan)
        review["improvements"] = self._suggest_improvements(code)
        review["security_issues"] = self._check_security(code)
        review["best_practices"] = self._check_best_practices(code)
        review["issues"] = self._identify_issues(
            code, validation_result
        )

        # Calculate overall score (this is the primary score for improvement loops)
        review["score"] = int(
            review["code_quality_score"] * 0.4
            + self._calculate_improvement_potential(review) * 0.6
        )
        
        # Ensure score is in valid range
        review["score"] = min(100, max(0, review["score"]))
        review["overall_score"] = review["score"]

        # Store in orchestrator if available
        if self.orchestrator:
            self.orchestrator.store_review_feedback(review)

        return review

    def _calculate_quality_score(self, code: str) -> float:
        """Calculate code quality score (0-100)"""
        score = 50.0  # Base score

        lines = code.split("\n")
        non_empty_lines = [l for l in lines if l.strip()]

        # Check for docstrings
        if '"""' in code or "'''" in code:
            score += 10

        # Check for type hints
        if "->" in code or ": " in code:
            score += 10

        # Check for error handling
        if "try:" in code and "except" in code:
            score += 10

        # Check code organization
        if "def " in code and "class " in code:
            score += 10

        # Penalize very long functions
        long_functions = code.count("\n    " * 5) > 3
        if long_functions:
            score -= 10

        # Ensure score is in valid range
        return min(100, max(0, score))

    def _generate_suggestions(self, code: str, plan: Dict) -> List[str]:
        """Generate specific suggestions for code improvement"""
        suggestions = []

        # Check plan alignment
        if "test" in plan.get("description", "").lower():
            if "def test_" not in code:
                suggestions.append(
                    "Implement test functions as per plan requirements"
                )

        # Check for common improvements
        if "class " not in code:
            suggestions.append(
                "Consider using classes for better code organization"
            )

        if len(code.split("\n")) < 30:
            suggestions.append(
                "Add more detailed implementation or helper functions"
            )

        if '"""' not in code:
            suggestions.append("Add module-level docstring")

        return suggestions

    def _suggest_improvements(self, code: str) -> List[Dict]:
        """Suggest specific improvements with rationales"""
        improvements = []

        # Suggest adding type hints
        improvements.append({
            "category": "Type Safety",
            "suggestion": "Add comprehensive type hints to all functions",
            "benefit": "Improved IDE support and early error detection",
            "difficulty": "Low",
        })

        # Suggest better error handling
        if "raise " not in code and "try:" not in code:
            improvements.append({
                "category": "Error Handling",
                "suggestion": "Add error handling for edge cases",
                "benefit": "Better robustness and user experience",
                "difficulty": "Medium",
            })

        # Suggest logging
        if "import logging" not in code and "print(" in code:
            improvements.append({
                "category": "Logging",
                "suggestion": "Replace print statements with logging module",
                "benefit": "Better debugging and production monitoring",
                "difficulty": "Low",
            })

        # Suggest configuration management
        if "config" not in code.lower():
            improvements.append({
                "category": "Configuration",
                "suggestion": "Extract hardcoded values to configuration",
                "benefit": "Better maintainability and flexibility",
                "difficulty": "Medium",
            })

        return improvements

    def _check_security(self, code: str) -> List[Dict]:
        """Check for potential security issues"""
        security_issues = []

        # Check for eval
        if "eval(" in code:
            security_issues.append({
                "severity": "CRITICAL",
                "issue": "Use of eval() detected",
                "recommendation": "Replace eval() with safer alternatives",
            })

        # Check for hardcoded secrets
        if any(
            word in code.lower()
            for word in ["password", "secret", "key", "token"]
        ):
            if "os.getenv" not in code and "environ" not in code:
                security_issues.append({
                    "severity": "HIGH",
                    "issue": "Potential hardcoded secrets detected",
                    "recommendation": "Use environment variables for secrets",
                })

        # Check for SQL injection risks (if using SQL)
        if "sql" in code.lower() or "query" in code.lower():
            if "format(" in code or "%" in code and "=" in code:
                security_issues.append({
                    "severity": "HIGH",
                    "issue": "Potential SQL injection vulnerability",
                    "recommendation": "Use parameterized queries",
                })

        return security_issues

    def _check_best_practices(self, code: str) -> List[str]:
        """Check code against best practices"""
        practices = []

        # PEP 8 checks
        if "_" in code and code.count("_") > code.count(" "):
            practices.append("✓ Good use of snake_case naming convention")

        # Modularity check
        if "import " in code:
            practices.append("✓ Code imports dependencies appropriately")

        if "def " in code and code.count("def") < 10:
            practices.append("✓ Reasonable function decomposition")

        if '"""' in code:
            practices.append("✓ Includes documentation")

        # Check for requirements
        if "try:" in code and "except" in code:
            practices.append("✓ Includes error handling")

        return practices

    def _identify_issues(
        self, code: str, validation_result: Optional[Dict] = None
    ) -> List[Dict]:
        """Identify specific issues found in code"""
        issues = []

        # Extract issues from validation if available
        if validation_result:
            for error in validation_result.get("errors", []):
                issues.append({
                    "type": "compile_error",
                    "severity": "CRITICAL",
                    "message": error,
                })

            for warning in validation_result.get("warnings", []):
                issues.append({
                    "type": "warning",
                    "severity": "LOW",
                    "message": warning,
                })

        # Additional static analysis
        if len(code) > 5000:
            issues.append({
                "type": "size_warning",
                "severity": "MEDIUM",
                "message": f"Large file ({len(code)} characters) - consider splitting",
            })

        return issues

    def _calculate_improvement_potential(self, review: Dict) -> float:
        """Calculate how much the code can improve (0-1)"""
        potential = 0.5

        # More suggestions = more potential for improvement
        potential += len(review["suggestions"]) * 0.05

        # More improvements = more potential
        potential += len(review["improvements"]) * 0.03

        # Ensure in range
        return min(1.0, max(0.0, potential))

    def approve_code(self, code: str, threshold: float = 70.0) -> Dict:
        """
        Determine if code should be approved for commit.
        
        Args:
            code: Code to check
            threshold: Minimum quality score threshold
            
        Returns:
            Approval decision
        """
        review = self.review_code(code, {})
        score = review.get("overall_score", 0)

        approved = score >= threshold

        return {
            "approved": approved,
            "score": score,
            "threshold": threshold,
            "message": (
                "✓ Code approved for commit"
                if approved
                else "✗ Code needs improvements before commit"
            ),
            "review": review,
        }

    def generate_improvement_report(self, review: Dict) -> str:
        """
        Generate a human-readable improvement report.
        
        Args:
            review: Review result
            
        Returns:
            Formatted report string
        """
        report = f"""
# Code Review Report
Generated: {review['reviewed_at']}

## Summary
- Quality Score: {review['code_quality_score']:.1f}/100
- Overall Score: {review['overall_score']:.1f}/100
- Issues Found: {len(review['issues_found'])}
- Suggestions: {len(review['suggestions'])}

## Suggestions
"""
        for i, suggestion in enumerate(review["suggestions"], 1):
            report += f"\n{i}. {suggestion}"

        report += "\n\n## Improvements\n"
        for improvement in review["improvements"]:
            report += f"\n- **{improvement['category']}**: {improvement['suggestion']}"
            report += f"\n  Benefit: {improvement['benefit']}"

        if review["security_issues"]:
            report += "\n\n## Security Issues\n"
            for issue in review["security_issues"]:
                report += (
                    f"\n- [{issue['severity']}] {issue['issue']}"
                )
                report += f"\n  → {issue['recommendation']}"

        return report
