"""
Architecture Engine - Proposes structural redesign improvements for the repository.
"""

from pathlib import Path
from typing import Dict, List, Any


class ArchitectureEngine:
    """Analyzes codebase structure and suggests safe refactoring moves."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)

    def analyze_structure(self) -> Dict[str, Any]:
        """Analyze repository tree and suggest architecture improvements."""
        suggestions: List[Dict[str, Any]] = []
        components = list(self.repo_path.rglob("*.py"))

        # Detect overly large modules
        for file_path in components:
            if file_path.name.startswith("test_") or "tests" in file_path.parts:
                continue

            try:
                size_kb = file_path.stat().st_size / 1024.0
            except OSError:
                size_kb = 0

            if size_kb > 300:  # big module
                suggestions.append(
                    {
                        "change": "split_module",
                        "target": str(file_path.relative_to(self.repo_path)),
                        "description": f"File exceeds {size_kb:.1f} KB, consider splitting into smaller modules.",
                        "risk_level": "medium",
                    }
                )

        # Detect unbalanced core distribution
        core_files = [f for f in components if f.parts and f.parts[0] == "core"]
        if len(core_files) > 20:
            suggestions.append(
                {
                    "change": "refactor",
                    "target": "core/",
                    "description": "Core module count is high; review for modularization and splitting by responsibility.",
                    "risk_level": "low",
                }
            )

        # flag missing stability controller in architecture
        if not (self.repo_path / "core" / "stability_controller.py").exists():
            suggestions.append(
                {
                    "change": "add_module",
                    "target": "core/stability_controller.py",
                    "description": "Add stability controller to detect low improvement rates and stop loops.",
                    "risk_level": "low",
                }
            )

        # Choose max risk from suggestions
        risk_level = "low"
        for s in suggestions:
            if s.get("risk_level") == "high":
                risk_level = "high"
                break
            if s.get("risk_level") == "medium" and risk_level != "high":
                risk_level = "medium"

        return {
            "changes": suggestions,
            "risk_level": risk_level,
            "summary": {
                "modules_scanned": len(components),
                "core_count": len(core_files),
                "suggestion_count": len(suggestions),
            },
        }

    def propose_changes(self, approved: bool, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Return change plan if approved; no file writes unless explicit commit flow exists."""
        if not approved:
            return {"status": "skipped", "changes": [], "reason": "Not approved"}

        # This is a safe placeholder; actual implementation must involve manual review
        return {"status": "approved", "planned_changes": changes}
