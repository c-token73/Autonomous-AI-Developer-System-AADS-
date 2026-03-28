"""
Validator Module - Code validation and quality checks
"""

import ast
import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, asdict


@dataclass
class ValidationResult:
    """Result of code validation"""

    valid: bool
    errors: List[str]
    warnings: List[str]
    metrics: Dict[str, Any]


class CodeValidator:
    """
    Validates Python code for syntax, structure, and basic quality.
    """

    def __init__(self):
        """Initialize validator"""
        self.syntax_errors: List[str] = []
        self.warnings: List[str] = []
        self.metrics: Dict[str, Any] = {}

    def validate(self, code: str, filename: str = "code.py") -> ValidationResult:
        """
        Comprehensive validation of Python code.
        
        Args:
            code: Python code to validate
            filename: Name of file being validated
            
        Returns:
            ValidationResult with validation details
        """
        self.syntax_errors = []
        self.warnings = []
        self.metrics = {}

        # Syntax validation
        syntax_valid = self._validate_syntax(code, filename)

        # If syntax is valid, perform additional checks
        if syntax_valid:
            self._check_code_quality(code)
            self._check_imports(code)
            self._check_functions(code)
            self._calculate_metrics(code)

        return ValidationResult(
            valid=syntax_valid and len(self.syntax_errors) == 0,
            errors=self.syntax_errors,
            warnings=self.warnings,
            metrics=self.metrics,
        )

    def _validate_syntax(self, code: str, filename: str) -> bool:
        """
        Validate Python syntax using AST.
        
        Args:
            code: Code to validate
            filename: Filename for error reporting
            
        Returns:
            True if code is syntactically valid
        """
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            error_msg = f"Syntax Error in {filename} at line {e.lineno}: {e.msg}"
            self.syntax_errors.append(error_msg)
            return False
        except Exception as e:
            self.syntax_errors.append(f"Parse Error: {str(e)}")
            return False

    def _check_code_quality(self, code: str) -> None:
        """Check for common code quality issues"""
        lines = code.split("\n")

        for idx, line in enumerate(lines, 1):
            # Check for multiple statements on one line
            if ";" in line and not line.strip().startswith("#"):
                self.warnings.append(
                    f"Line {idx}: Multiple statements on one line (contains ';')"
                )

            # Check for very long lines
            if len(line) > 100:
                self.warnings.append(
                    f"Line {idx}: Line too long ({len(line)} > 100 chars)"
                )

            # Check for unused imports (basic check)
            if line.strip().startswith("import ") or line.strip().startswith(
                "from "
            ):
                module = self._extract_module_name(line)
                if module and not self._is_module_used(code, module):
                    self.warnings.append(
                        f"Line {idx}: Potentially unused import: {module}"
                    )

    def _extract_module_name(self, import_line: str) -> str:
        """Extract module name from import statement"""
        if "import " in import_line:
            parts = import_line.split("import")
            if len(parts) > 1:
                return parts[-1].strip().split()[0]
        return ""

    def _is_module_used(self, code: str, module: str) -> bool:
        """Check if module is used in code (basic check)"""
        # This is a simplified check
        module_short = module.split(".")[0]
        return module_short in code

    def _check_imports(self, code: str) -> None:
        """Check import organization and structure"""
        try:
            tree = ast.parse(code)
            imports = self._extract_imports(tree)

            # Check if imports are grouped (basic check)
            import_lines = [i for i, line in enumerate(code.split("\n")) 
                          if line.strip().startswith("import ") 
                          or line.strip().startswith("from ")]
            
            if import_lines:
                self.metrics["imports_count"] = len(imports)
        except Exception:
            pass

    def _check_functions(self, code: str) -> None:
        """Check function definitions and structure"""
        try:
            tree = ast.parse(code)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

            self.metrics["functions_count"] = len(functions)
            self.metrics["classes_count"] = len(classes)

            # Check function lengths
            for func in functions:
                length = func.end_lineno - func.lineno if func.end_lineno else 0
                if length > 50:
                    self.warnings.append(
                        f"Function '{func.name}' is quite long ({length} lines)"
                    )
        except Exception:
            pass

    def _calculate_metrics(self, code: str) -> None:
        """Calculate code metrics"""
        lines = code.split("\n")
        non_empty_lines = [line for line in lines if line.strip()]
        comment_lines = [line for line in lines if line.strip().startswith("#")]

        self.metrics["total_lines"] = len(lines)
        self.metrics["non_empty_lines"] = len(non_empty_lines)
        self.metrics["comment_lines"] = len(comment_lines)
        self.metrics["comment_ratio"] = (
            len(comment_lines) / len(non_empty_lines)
            if non_empty_lines
            else 0
        )

    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract all imports from AST"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports

    def to_dict(self, result: ValidationResult) -> Dict:
        """Convert validation result to dictionary"""
        return asdict(result)


def validate_code(code: str, filename: str = "code.py") -> Dict:
    """
    Convenience function to validate code.
    
    Args:
        code: Python code to validate
        filename: Name of file
        
    Returns:
        Dictionary with validation results
    """
    validator = CodeValidator()
    result = validator.validate(code, filename)
    return validator.to_dict(result)
