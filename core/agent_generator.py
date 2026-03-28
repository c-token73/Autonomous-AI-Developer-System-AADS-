"""
Agent Generator - Automatically creates new agent modules for missing capabilities.
"""

from pathlib import Path
from typing import List, Dict, Any


class AgentGenerator:
    """Generate agent stubs based on missing capabilities."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)

    def find_missing_capabilities(self, existing_agents: List[str]) -> List[str]:
        recommendations = []

        if "security" not in existing_agents:
            recommendations.append("security_agent")

        if "performance" not in existing_agents:
            recommendations.append("performance_agent")

        if "quality" not in existing_agents:
            recommendations.append("quality_agent")

        return recommendations

    def create_agent_stub(self, agent_name: str) -> Dict[str, Any]:
        file_path = self.repo_path / "agents" / f"{agent_name}.py"
        if file_path.exists():
            return {"status": "exists", "path": str(file_path)}

        class_name = agent_name.title().replace("_", "")

        file_content = (
            "#!/usr/bin/env python3\n\n"
            f'"""{agent_name} dynamically generated agent stub."""\n\n'
            f"class {class_name}:\n"
            "    def __init__(self, orchestrator):\n"
            "        self.orchestrator = orchestrator\n\n"
            "    def generate_code(self, task):\n"
            "        return {\n"
            "            \"code\": \"# TODO: implement agent logic\",\n"
            "            \"language\": \"python\",\n"
            "            \"documentation\": \"Auto-generated {agent_name}\",\n"
            "            \"dependencies\": [],\n"
            "            \"agent\": \"{agent_name}\",\n"
            "            \"subtask_id\": task.get(\"subtask_id\", \"auto\"),\n"
            "        }\n"
        )

        file_path.parent.mkdir(exist_ok=True, parents=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_content)

        return {"status": "created", "path": str(file_path)}

    def reconcile_agents(self, existing_agents: List[str]) -> Dict[str, Any]:
        missing = self.find_missing_capabilities(existing_agents)
        created = []
        for name in missing:
            created.append(self.create_agent_stub(name))

        return {
            "existing_agents": existing_agents,
            "created_agents": created,
            "missing_capabilities": missing,
        }
