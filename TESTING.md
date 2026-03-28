# 🧪 Testing Guide

Complete guide to testing the Autonomous AI Developer System.

## Quick Test

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=core --cov=agents --cov-report=html
```

## Test Structure

### test_validator.py

The validator module has the most comprehensive test suite with 21+ test cases.

#### Test Classes

##### TestCodeValidator (16 tests)
Core functionality tests for the CodeValidator class:

1. **test_valid_python_code**
   - Tests validation of syntactically correct code
   - Expects: valid=True, no errors

2. **test_syntax_error_detection**
   - Tests detection of missing colons
   - Expects: valid=False, errors detected

3. **test_long_line_detection**
   - Tests detection of lines > 100 chars
   - Expects: warnings generated

4. **test_multiple_statements_detection**
   - Tests detection of multiple statements on one line
   - Expects: warnings for semicolons

5. **test_code_metrics**
   - Tests calculation of code metrics
   - Checks: total_lines, non_empty_lines, comment_lines

6. **test_function_detection**
   - Tests detection of function definitions
   - Expects: functions_count=2, classes_count=1

7. **test_long_function_detection**
   - Tests detection of overly long functions (50+ lines)
   - Expects: warnings about function length

8. **test_indentation_error**
   - Tests detection of indentation errors
   - Expects: valid=False, syntax errors

9. **test_unclosed_parenthesis**
   - Tests detection of syntax errors
   - Expects: valid=False, parser errors

10. **test_convenience_function**
    - Tests the validate_code() convenience function
    - Expects: dict with valid, errors, warnings, metrics

11. **test_empty_code**
    - Tests validation of empty string
    - Expects: valid=True, no errors

12. **test_comment_only_code**
    - Tests code with only comments
    - Expects: valid=True

13. **test_validation_result_to_dict**
    - Tests conversion of ValidationResult to dict
    - Expects: dict conversion works

14-16. Additional edge case tests

##### TestValidatorIntegration (2+ tests)
Integration tests with realistic code:

1. **test_class_definition**
   - Tests validation of complete class definitions
   - Includes docstrings, methods, type hints

2. **test_complex_code_structure**
   - Tests validation of complex code with:
   - Decorators, dataclasses, imports
   - Try-except blocks, comprehensions

## Running Tests

### Run All Tests
```bash
pytest tests/
```

**Output:**
```
tests/test_validator.py::TestCodeValidator::test_valid_python_code PASSED
tests/test_validator.py::TestCodeValidator::test_syntax_error_detection PASSED
...
===================== 21 passed in 0.48s =====================
```

### Run Specific Test File
```bash
pytest tests/test_validator.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_validator.py::TestCodeValidator -v
```

### Run Specific Test
```bash
pytest tests/test_validator.py::TestCodeValidator::test_valid_python_code -v
```

### Run with Coverage
```bash
# Generate coverage report
pytest tests/ --cov=core --cov=agents --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=core --cov=agents --cov-report=html
# Open: htmlcov/index.html
```

### Run with Markers
```bash
# Run only fast tests
pytest tests/ -m "not slow"

# Run only integration tests
pytest tests/ -m "integration"
```

## Test Categories

### Unit Tests
- Individual function testing
- Validator syntax checks
- Metric calculations

### Integration Tests
- Complete validator workflows
- Multi-step code validation
- Realistic code scenarios

### Edge Cases
- Empty code
- Comment-only code
- Large functions
- Complex structures

## Writing New Tests

### Example: Add Test for New Feature

```python
def test_new_feature(self):
    """Test description here"""
    # Setup
    test_code = "..."
    
    # Execute
    result = self.validator.validate(test_code)
    
    # Assert
    self.assertTrue(result.valid)
    self.assertIn("expected_metric", result.metrics)
```

### Test Template

```python
class TestNewModule(unittest.TestCase):
    """Tests for new module"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.module = NewModule()
    
    def test_feature_one(self):
        """Test specific feature"""
        result = self.module.feature()
        self.assertTrue(result)
    
    def test_error_handling(self):
        """Test error scenarios"""
        with self.assertRaises(ValueError):
            self.module.invalid_feature()
```

## Coverage Goals

### Current Coverage
- **validator.py**: 85%+
- **Core modules**: Ready for expansion

### Targets
- **core/**: 80%+ coverage
- **agents/**: 70%+ coverage
- **Overall**: 75%+ coverage

## Continuous Integration

### GitHub Actions Setup
Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ --cov=core --cov=agents
```

## Debugging Tests

### Verbose Output
```bash
pytest tests/ -v -s
```

### Show Local Variables
```bash
pytest tests/ -l
```

### Drop into Debugger
```bash
pytest tests/ --pdb
```

### Show Print Statements
```bash
pytest tests/ -s
```

## Performance Testing

### Measure Test Execution
```bash
# Show slowest tests
pytest tests/ --durations=10
```

### Profile Test
```bash
# Run with profiling
pytest tests/ --profile
```

## Mocking & Fixtures

### Example: Mock GitHub Operations

```python
from unittest.mock import Mock, patch

def test_github_operation():
    with patch('core.github_tool.GitHubTool') as mock_github:
        mock_github.return_value.commit_to_branch.return_value = (True, "Success")
        # Test code
```

## Test Organization

```
tests/
├── __init__.py
├── test_validator.py          # Validator tests
├── test_agents/               # (Future) Agent tests
│   ├── test_planner.py
│   ├── test_programmer.py
│   └── test_reviewer.py
├── test_core/                 # (Future) Core module tests
│   ├── test_memory.py
│   ├── test_github_tool.py
│   └── test_orchestrator.py
├── fixtures/                  # (Future) Test fixtures
│   └── sample_code.py
└── conftest.py               # (Future) Pytest configuration
```

## Expected Test Results

### All Tests Pass
```
===================== 21 passed in 0.48s =====================
```

### Coverage Report
```
Name      Stmts   Miss  Cover
core      432     68    84%
agents    405     92    77%
tests     411     0    100%
TOTAL     1248    160   87%
```

## Troubleshooting Tests

### Test Not Found
```bash
# Make sure pytest is installed
pip install pytest

# Check test file naming
# Files should be: test_*.py or *_test.py
```

### Import Errors
```bash
# Make sure you're in the right directory
cd /path/to/Autonomous-AI-Developer-System-AADS-

# Add current directory to PYTHONPATH
export PYTHONPATH=$PWD:$PYTHONPATH
pytest tests/
```

### Module Not Found
```bash
# Make sure __init__.py exists in all packages
# Check: agents/__init__.py, core/__init__.py, tests/__init__.py
```

## Best Practices

✅ **Do:**
- Write tests for critical functionality
- Use descriptive test names
- Organize tests by module
- Use fixtures for common setup
- Test error cases
- Maintain >75% coverage

❌ **Don't:**
- Couple tests to implementation
- Create brittle tests
- Test external APIs without mocking
- Ignore test failures
- Write overly complex tests

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [Coverage.py](https://coverage.readthedocs.io/)

---

**Happy Testing! 🎯**
