"""
Aggregator - Merges outputs from multiple specialized agents into cohesive result
"""

from typing import Dict, List, Optional
from datetime import datetime


class ResultAggregator:
    """
    Combines code, documentation, and tests from parallel specialist agents
    into a single cohesive output. Handles conflict resolution and dependency management.
    """

    def __init__(self):
        """Initialize aggregator"""
        self.agent_results: Dict[str, Dict] = {}
        self.aggregation_history: List[Dict] = []

    def aggregate_results(self, agent_results: Dict[str, Dict]) -> Dict:
        """
        Aggregate results from multiple agents into unified output.
        
        Args:
            agent_results: Dict mapping agent type to result dict
                {
                    "backend": {"code": "...", "status": "success", ...},
                    "frontend": {"code": "...", "status": "success", ...},
                    "test": {"code": "...", "status": "success", ...},
                }
        
        Returns:
            Aggregated result with combined code, documentation, and metadata
        """
        self.agent_results = agent_results
        
        # Check for failures and fallback
        successful_agents = {
            agent: result for agent, result in agent_results.items()
            if result.get("status") == "success"
        }
        
        if not successful_agents:
            return {
                "status": "failed",
                "error": "All agents failed to produce results",
                "agents_status": {agent: result.get("status", "failed") 
                                 for agent, result in agent_results.items()},
            }
        
        # Merge code sections
        merged_code = self._merge_code_sections(successful_agents)
        
        # Merge documentation
        merged_docs = self._merge_documentation(successful_agents)
        
        # Merge dependencies
        merged_dependencies = self._merge_dependencies(successful_agents)
        
        # Resolve conflicts
        conflicts = self._detect_conflicts(successful_agents)
        
        aggregation_result = {
            "status": "success" if not conflicts else "partial_success",
            "merged_code": merged_code,
            "merged_documentation": merged_docs,
            "merged_dependencies": merged_dependencies,
            "conflict_count": len(conflicts),
            "conflicts": conflicts if conflicts else None,
            "agents_used": list(successful_agents.keys()),
            "failed_agents": [agent for agent in agent_results if agent not in successful_agents],
            "backend_code": successful_agents.get("backend", {}).get("code"),
            "frontend_code": successful_agents.get("frontend", {}).get("code"),
            "test_code": successful_agents.get("test", {}).get("code"),
            "aggregated_at": datetime.now().isoformat(),
        }
        
        self.aggregation_history.append(aggregation_result)
        
        return aggregation_result

    def _merge_code_sections(self, agent_results: Dict[str, Dict]) -> str:
        """Merge code from different agents with proper imports and organization"""
        sections = []
        
        # Collect all imports
        all_imports = set()
        for agent, result in agent_results.items():
            code = result.get("code", "")
            imports = self._extract_imports(code)
            all_imports.update(imports)
        
        # Start with unified imports
        merged = self._generate_import_section(sorted(all_imports))
        
        # Add module-level documentation
        merged += '\n"""\nUnified module from distributed multi-agent generation\n"""\n\n'
        
        # Backend code (typically should come first - setup)
        if "backend" in agent_results:
            backend_code = agent_results["backend"].get("code", "")
            merged += self._clean_code_section(backend_code, "backend")
            merged += "\n\n"
        
        # Frontend code (typically depends on backend)
        if "frontend" in agent_results:
            frontend_code = agent_results["frontend"].get("code", "")
            merged += self._clean_code_section(frontend_code, "frontend")
            merged += "\n\n"
        
        # Test code (typically at end)
        if "test" in agent_results:
            test_code = agent_results["test"].get("code", "")
            merged += self._clean_code_section(test_code, "test")
            merged += "\n\n"
        
        return merged

    def _merge_documentation(self, agent_results: Dict[str, Dict]) -> str:
        """Merge documentation from all agents"""
        docs = "# Distributed Multi-Agent Generated Module\n\n"
        docs += f"Generated: {datetime.now().isoformat()}\n\n"
        
        for agent_type, result in agent_results.items():
            agent_docs = result.get("documentation", f"Documentation for {agent_type} component")
            docs += f"## {agent_type.title()} Component\n"
            docs += f"{agent_docs}\n\n"
        
        return docs

    def _merge_dependencies(self, agent_results: Dict[str, Dict]) -> List[str]:
        """Merge and deduplicate dependencies from all agents"""
        all_deps = set()
        
        for agent, result in agent_results.items():
            deps = result.get("dependencies", [])
            if isinstance(deps, list):
                all_deps.update(deps)
        
        return sorted(list(all_deps))

    def _extract_imports(self, code: str) -> set:
        """Extract import statements from code"""
        imports = set()
        
        for line in code.split("\n"):
            line = line.strip()
            if line.startswith("import ") or line.startswith("from "):
                imports.add(line)
        
        return imports

    def _generate_import_section(self, imports: List[str]) -> str:
        """Generate organized import section"""
        if not imports:
            return ""
        
        # Categorize imports
        stdlib_imports = []
        third_party_imports = []
        local_imports = []
        
        stdlib_modules = {
            "os", "sys", "re", "json", "datetime", "time", "random",
            "math", "collections", "itertools", "functools", "typing",
            "pathlib", "subprocess", "threading", "asyncio", "unittest"
        }
        
        for imp in imports:
            if any(f" {mod}" in imp for mod in stdlib_modules) or \
               any(f"import {mod}" in imp for mod in stdlib_modules):
                stdlib_imports.append(imp)
            elif imp.startswith("from .") or imp.startswith("import ."):
                local_imports.append(imp)
            else:
                third_party_imports.append(imp)
        
        result = ""
        if stdlib_imports:
            result += "\n".join(stdlib_imports) + "\n"
        if third_party_imports:
            if stdlib_imports:
                result += "\n"
            result += "\n".join(third_party_imports) + "\n"
        if local_imports:
            if stdlib_imports or third_party_imports:
                result += "\n"
            result += "\n".join(local_imports) + "\n"
        
        return result + "\n"

    def _clean_code_section(self, code: str, section_type: str) -> str:
        """Clean and organize code section from agent"""
        lines = code.split("\n")
        cleaned_lines = []
        
        for line in lines:
            # Skip duplicate import statements (they're merged at top)
            if line.strip().startswith("import ") or line.strip().startswith("from "):
                continue
            # Skip module docstrings and comments from agent output (using main one)
            if line.strip().startswith('"""') and "generated" in line.lower():
                continue
            cleaned_lines.append(line)
        
        return "\n".join(cleaned_lines).strip()

    def _detect_conflicts(self, agent_results: Dict[str, Dict]) -> List[Dict]:
        """Detect potential conflicts between agent outputs"""
        conflicts = []
        
        # Check for duplicate function names
        function_names = {}
        for agent, result in agent_results.items():
            code = result.get("code", "")
            for line in code.split("\n"):
                if line.strip().startswith("def "):
                    func_name = line.split("(")[0].replace("def", "").strip()
                    if func_name in function_names:
                        conflicts.append({
                            "type": "duplicate_function",
                            "function": func_name,
                            "agents": [function_names[func_name], agent],
                        })
                    else:
                        function_names[func_name] = agent
        
        # Check for conflicting imports
        imports_by_agent = {}
        for agent, result in agent_results.items():
            code = result.get("code", "")
            imports = self._extract_imports(code)
            imports_by_agent[agent] = imports
        
        # Check for import version conflicts (same package, different imports)
        all_packages = set()
        for imports in imports_by_agent.values():
            for imp in imports:
                pkg = imp.split()[1].split(".")[0] if " " in imp else ""
                if pkg:
                    all_packages.add(pkg)
        
        for pkg in all_packages:
            pkg_imports = {}
            for agent, imports in imports_by_agent.items():
                for imp in imports:
                    if pkg in imp:
                        if pkg not in pkg_imports:
                            pkg_imports[pkg] = {}
                        pkg_imports[pkg][agent] = imp
            
            # Check for different import styles of same package
            if pkg in pkg_imports and len(pkg_imports[pkg]) > 1:
                conflicting_agents = list(pkg_imports[pkg].items())
                if len(set(imp for _, imp in conflicting_agents)) > 1:
                    conflicts.append({
                        "type": "conflicting_imports",
                        "package": pkg,
                        "imports": dict(conflicting_agents),
                    })
        
        return conflicts

    def get_aggregation_summary(self) -> Dict:
        """Get summary of last aggregation"""
        if not self.aggregation_history:
            return {"status": "no_aggregations"}
        
        last = self.aggregation_history[-1]
        return {
            "status": last["status"],
            "agents_used": last["agents_used"],
            "conflicts_detected": last["conflict_count"],
            "code_lines": len(last.get("merged_code", "").split("\n")),
        }
