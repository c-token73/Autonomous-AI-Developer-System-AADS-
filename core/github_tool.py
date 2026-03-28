"""
GitHub Tool Module - Safe GitHub operations with approval workflow and autonomous branching
"""

import os
import re
from typing import Optional, Dict, Tuple
from pathlib import Path
from datetime import datetime


class GitHubTool:
    """
    Manages safe GitHub operations including:
    - Creating feature branches with timestamps
    - Committing changes safely
    - Creating pull requests
    
    All operations require explicit approval before execution.
    Uses autonomous branching strategy for safe merging.
    """

    def __init__(self, repo_path: str = ".", github_token: Optional[str] = None):
        """
        Initialize GitHub tool.
        
        Args:
            repo_path: Path to repository
            github_token: GitHub API token (from environment)
        """
        self.repo_path = Path(repo_path)
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.current_branch = self._get_current_branch()
        self.pending_changes: Dict = {}
        self.auto_branch_prefix = "feature/ai-task"  # Autonomous branch prefix

    def _get_current_branch(self) -> str:
        """Get the current git branch name"""
        try:
            import subprocess

            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip() or "main"
        except Exception:
            return "main"

    def create_feature_branch(self, branch_name: str) -> Tuple[bool, str]:
        """
        Create a new feature branch locally (does NOT push to remote).
        
        Args:
            branch_name: Name of new branch
            
        Returns:
            Tuple of (success, message)
        """
        try:
            import subprocess

            # Validate branch name
            if not self._is_valid_branch_name(branch_name):
                return False, f"Invalid branch name: {branch_name}"

            # Create branch from current branch
            result = subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                return True, f"Created branch: {branch_name}"
            else:
                return False, f"Failed to create branch: {result.stderr}"
        except Exception as e:
            return False, f"Error creating branch: {str(e)}"

    def create_autonomous_branch(self, task_id: str = "") -> Tuple[bool, str]:
        """
        Create autonomous feature branch with timestamp (SAFE BRANCHING STRATEGY).
        
        Branch naming: feature/ai-task-{task_id}-{timestamp}
        
        Args:
            task_id: Optional task identifier
            
        Returns:
            Tuple of (success, branch_name)
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        task_id_part = task_id.replace("task_", "")[:10] if task_id else "auto"
        branch_name = f"{self.auto_branch_prefix}-{task_id_part}-{timestamp}"

        success, msg = self.create_feature_branch(branch_name)
        if success:
            self.current_branch = branch_name
            return True, branch_name
        return False, msg

    def stage_changes(self, file_path: str, content: str) -> Tuple[bool, str]:
        """
        Stage changes for commit without committing.
        
        Args:
            file_path: Path to file relative to repo
            content: New file content
            
        Returns:
            Tuple of (success, message)
        """
        try:
            full_path = self.repo_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write content to file
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Store in pending changes
            self.pending_changes[file_path] = {
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "status": "staged",
            }

            return True, f"Staged file: {file_path}"
        except Exception as e:
            return False, f"Error staging changes: {str(e)}"

    def review_pending_changes(self) -> Dict:
        """
        Review all pending changes before commit.
        
        Returns:
            Dictionary of pending changes with details
        """
        return {
            "branch": self.current_branch,
            "changes": self.pending_changes,
            "change_count": len(self.pending_changes),
            "ready_for_commit": len(self.pending_changes) > 0,
        }

    def commit_to_branch(
        self, file_path: str, content: str, message: str
    ) -> Tuple[bool, str]:
        """
        Commit changes to current branch (does NOT push to remote).
        
        SAFETY: This requires explicit approval workflow in app.
        
        Args:
            file_path: Path to file relative to repo
            content: File content to commit
            message: Commit message
            
        Returns:
            Tuple of (success, message)
        """
        try:
            import subprocess

            # First, stage the changes
            success, stage_msg = self.stage_changes(file_path, content)
            if not success:
                return False, stage_msg

            # Add file to git
            full_path = self.repo_path / file_path
            result = subprocess.run(
                ["git", "add", str(full_path)],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                return False, f"Failed to add file: {result.stderr}"

            # Commit changes
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                # Clear pending changes for this file
                if file_path in self.pending_changes:
                    del self.pending_changes[file_path]

                return True, f"Committed to {self.current_branch}: {message}"
            else:
                return False, f"Commit failed: {result.stderr}"
        except Exception as e:
            return False, f"Error committing changes: {str(e)}"

    def push_to_remote(self, remote: str = "origin") -> Tuple[bool, str]:
        """
        Push current branch to remote (requires explicit approval).
        
        SAFETY: Only pushes current branch, never to main by default.
        
        Args:
            remote: Remote name (default: origin)
            
        Returns:
            Tuple of (success, message)
        """
        try:
            import subprocess

            if self.current_branch == "main" or self.current_branch == "master":
                return False, "Cannot push directly to main/master branch"

            result = subprocess.run(
                ["git", "push", remote, self.current_branch],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return True, f"Pushed {self.current_branch} to {remote}"
            else:
                return False, f"Push failed: {result.stderr}"
        except Exception as e:
            return False, f"Error pushing: {str(e)}"

    def _is_valid_branch_name(self, name: str) -> bool:
        """Validate branch name"""
        if not name or len(name) == 0:
            return False
        # Simple validation
        invalid_chars = ["~", "^", ":", "?", "*", "[", "\\", " "]
        return not any(char in name for char in invalid_chars)

    def get_status(self) -> Dict:
        """
        Get current repository status.
        
        Returns:
            Dictionary with status information
        """
        try:
            import subprocess

            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            modified, added, removed = 0, 0, 0
            for line in result.stdout.split("\n"):
                if line.startswith("M"):
                    modified += 1
                elif line.startswith("A"):
                    added += 1
                elif line.startswith("D"):
                    removed += 1

            return {
                "current_branch": self.current_branch,
                "modified": modified,
                "added": added,
                "removed": removed,
                "pending_changes": len(self.pending_changes),
            }
        except Exception as e:
            return {
                "current_branch": self.current_branch,
                "error": str(e),
            }

    def reset_pending_changes(self) -> Tuple[bool, str]:
        """
        Reset all pending changes (useful for canceling draft).
        
        Returns:
            Tuple of (success, message)
        """
        try:
            self.pending_changes.clear()
            return True, "All pending changes cleared"
        except Exception as e:
            return False, f"Error clearing changes: {str(e)}"
