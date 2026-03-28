"""
Unit tests for the Validator module
"""

import unittest
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.validator import CodeValidator, validate_code


class TestCodeValidator(unittest.TestCase):
    """Test cases for CodeValidator class"""

    def setUp(self):
        """Set up test fixtures"""
        self.validator = CodeValidator()

    def test_valid_python_code(self):
        """Test validation of valid Python code"""
        valid_code = """
def hello_world():
    '''Returns a greeting'''
    return "Hello, World!"

result = hello_world()
print(result)
"""
        result = self.validator.validate(valid_code)
        self.assertTrue(result.valid, "Valid code should pass validation")
        self.assertEqual(len(result.errors), 0, "Valid code should have no errors")

    def test_syntax_error_detection(self):
        """Test detection of syntax errors"""
        invalid_code = """
def broken_function()
    return "Missing colon"
"""
        result = self.validator.validate(invalid_code)
        self.assertFalse(result.valid, "Invalid code should fail validation")
        self.assertGreater(len(result.errors), 0, "Should detect syntax error")

    def test_long_line_detection(self):
        """Test detection of overly long lines"""
        long_line_code = """
def function():
    very_long_variable_name = "This is a very long line that exceeds the recommended maximum of 100 characters for better code readability and maintenance"
    return very_long_variable_name
"""
        result = self.validator.validate(long_line_code)
        # Should have warnings about long lines
        self.assertGreater(
            len(result.warnings),
            0,
            "Should warn about long lines",
        )

    def test_multiple_statements_detection(self):
        """Test detection of multiple statements on one line"""
        multi_stmt_code = """
x = 1; y = 2; z = 3
print(x); print(y)
"""
        result = self.validator.validate(multi_stmt_code)
        self.assertGreater(
            len(result.warnings),
            0,
            "Should warn about multiple statements",
        )

    def test_code_metrics(self):
        """Test code metrics calculation"""
        test_code = """
# This is a comment
def test_function(x: int) -> int:
    '''Docstring'''
    result = x * 2
    return result
"""
        result = self.validator.validate(test_code)
        self.assertIn("total_lines", result.metrics)
        self.assertIn("non_empty_lines", result.metrics)
        self.assertIn("comment_lines", result.metrics)
        self.assertGreater(result.metrics["total_lines"], 0)

    def test_function_detection(self):
        """Test that validator detects functions"""
        code_with_functions = """
def func1():
    pass

def func2():
    pass

class MyClass:
    pass
"""
        result = self.validator.validate(code_with_functions)
        self.assertIn("functions_count", result.metrics)
        self.assertEqual(result.metrics["functions_count"], 2)
        self.assertEqual(result.metrics["classes_count"], 1)

    def test_long_function_detection(self):
        """Test detection of overly long functions"""
        long_func_code = """
def long_function():
    x = 1
    y = 2
    z = 3
    a = 4
    b = 5
    c = 6
    d = 7
    e = 8
    f = 9
    g = 10
    h = 11
    i = 12
    j = 13
    k = 14
    l = 15
    m = 16
    n = 17
    o = 18
    p = 19
    q = 20
    r = 21
    s = 22
    t = 23
    u = 24
    v = 25
    w = 26
    x2 = 27
    y2 = 28
    z2 = 29
    a2 = 30
    b2 = 31
    c2 = 32
    d2 = 33
    e2 = 34
    f2 = 35
    g2 = 36
    h2 = 37
    i2 = 38
    j2 = 39
    k2 = 40
    l2 = 41
    m2 = 42
    n2 = 43
    o2 = 44
    p2 = 45
    q2 = 46
    r2 = 47
    s2 = 48
    t2 = 49
    u2 = 50
    return x + y
"""
        result = self.validator.validate(long_func_code)
        # Should have warnings about long function
        self.assertGreater(
            len(result.warnings),
            0,
            "Should warn about long function",
        )

    def test_indentation_error(self):
        """Test detection of indentation errors"""
        indent_error_code = """
def function():
x = 1  # Missing indentation
return x
"""
        result = self.validator.validate(indent_error_code)
        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)

    def test_unclosed_parenthesis(self):
        """Test detection of unclosed parenthesis"""
        unclosed_code = """
def function(x, y:
    return x + y
"""
        result = self.validator.validate(unclosed_code)
        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)

    def test_convenience_function(self):
        """Test convenience validate_code function"""
        code = "x = 1\nprint(x)"
        result = validate_code(code)
        self.assertIsInstance(result, dict)
        self.assertIn("valid", result)
        self.assertIn("errors", result)
        self.assertIn("warnings", result)
        self.assertIn("metrics", result)

    def test_empty_code(self):
        """Test validation of empty code"""
        empty_code = ""
        result = self.validator.validate(empty_code)
        self.assertTrue(result.valid, "Empty code should be valid")
        self.assertEqual(len(result.errors), 0)

    def test_comment_only_code(self):
        """Test validation of comment-only code"""
        comment_code = """
# This is a comment
# Another comment
"""
        result = self.validator.validate(comment_code)
        self.assertTrue(result.valid)

    def test_validation_result_to_dict(self):
        """Test conversion of ValidationResult to dictionary"""
        code = "print('hello')"
        result = self.validator.validate(code)
        result_dict = self.validator.to_dict(result)
        
        self.assertIsInstance(result_dict, dict)
        self.assertIn("valid", result_dict)
        self.assertIn("errors", result_dict)
        self.assertIn("warnings", result_dict)
        self.assertIn("metrics", result_dict)


class TestValidatorIntegration(unittest.TestCase):
    """Integration tests for validator with realistic code"""

    def test_class_definition(self):
        """Test validation of class definitions"""
        class_code = """
class DataProcessor:
    '''Process data efficiently'''
    
    def __init__(self, name: str) -> None:
        self.name = name
    
    def process(self, data: list) -> list:
        '''Process input data'''
        return [x * 2 for x in data]
"""
        validator = CodeValidator()
        result = validator.validate(class_code)
        
        self.assertTrue(result.valid)
        self.assertEqual(result.metrics["classes_count"], 1)
        self.assertEqual(result.metrics["functions_count"], 2)

    def test_complex_code_structure(self):
        """Test validation of complex code structure"""
        complex_code = """
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Result:
    status: str
    data: Optional[Dict] = None

def process_items(items: List[str]) -> Result:
    try:
        processed = [item.upper() for item in items]
        return Result(status="success", data={"items": processed})
    except Exception as e:
        return Result(status="error", data={"error": str(e)})
"""
        validator = CodeValidator()
        result = validator.validate(complex_code)
        
        self.assertTrue(result.valid)
        self.assertGreater(result.metrics["total_lines"], 0)


def run_tests():
    """Run all tests"""
    unittest.main(argv=[""], exit=False, verbosity=2)


if __name__ == "__main__":
    run_tests()
