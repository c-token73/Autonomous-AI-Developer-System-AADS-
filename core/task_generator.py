"""
Task Generator Module - Automatically discovers and generates self-improvement tasks.
"""

import re
from typing import List, Dict
from pathlib import Path
from .memory import RepositoryMemory


class TaskGenerator:
    """Generates tasks by scanning repository for potential improvements."""

    MISSING_TEST_PREFIXES = ["test_", ""]
    MISSING_TEST_SUFFIXES = ["_test.py", "Test.py"]
    LARGE_FILE_LINE_THRESHOLD = 250

    def __init__(self, repo_path: str = "."):
        self.memory = RepositoryMemory(repo_path)

    def _is_test_file(self, file_path: str) -> bool:
        return "tests" in file_path.replace('\\\\', '/').split('/') or file_path.endswith("_test.py") or file_path.startswith("test_")

    def _find_has_test(self, file_path: str) -> bool:
        path_obj = Path(file_path)
        if self._is_test_file(file_path):
            return True

        base_name = path_obj.stem
        # Search in tests/ and same folder naming patterns
        for candidate in self.memory.list_files("tests"):
            candidate_obj = Path(candidate)
            if candidate_obj.stem in [f"test_{base_name}", f"{base_name}_test", base_name]:
                return True

        # Also test maybe in same dir
        parent_dir = path_obj.parent
        for prefix in ["test_", ""]:
            for suffix in ["_test.py", "Test.py", ".py"]:
                candidate_name = f"{prefix}{base_name}{suffix}" if suffix != ".py" else f"{prefix}{base_name}.py"
                candidate_file = parent_dir / candidate_name
                if candidate_file.exists():
                    if self._is_test_file(str(candidate_file)):
                        return True

        return False

    def _has_todo(self, content: str) -> bool:
        return bool(re.search(r"\\b(TODO|FIXME)\\b", content, re.IGNORECASE))

    def _is_large_file(self, content: str) -> bool:
        return len(content.splitlines()) >= self.LARGE_FILE_LINE_THRESHOLD

    def generate_tasks(self, limit: int = 10) -> List[Dict[str, str]]:
        """Generate improvement tasks based on a repo scan."""
        tasks: List[Dict[str, str]] = []
        self.memory.refresh()

        for file_path in sorted(self.memory.file_index.keys()):
            relative_path = str(Path(file_path).relative_to(Path(self.memory.repo_path)))
            if self._is_test_file(relative_path):
                continue

            # Load file content safely
            content = self.memory.get_file_content(relative_path) or ""

            # Detect TODO/FIXME patterns
            if self._has_todo(content):
                tasks.append({"type": "refactor", "target": relative_path, "reason": "TODO/FIXME found"})

            # Detect missing tests
            if not self._find_has_test(relative_path):
                tasks.append({"type": "test", "target": relative_path, "reason": "missing tests"})

            # Large file detection
            if self._is_large_file(content):
                tasks.append({"type": "refactor", "target": relative_path, "reason": "large file"})

            if len(tasks) >= limit:
                break

        # Deduplicate tasks by target+type
        unique = {}
        for t in tasks:
            key = (t["type"], t["target"])
            if key not in unique:
                unique[key] = t

        return list(unique.values())

    def summarize_tasks(self, tasks: List[Dict[str, str]]) -> Dict[str, int]:
        """Provide a task summary for dashboard display."""
        summary = {"total": len(tasks), "refactor": 0, "test": 0}

        for t in tasks:
            ttype = t.get("type")
            if ttype in summary:
                summary[ttype] += 1

        return summary
