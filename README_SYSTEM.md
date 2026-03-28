# 🤖 Autonomous AI Developer System (AADS)

A production-grade multi-agent AI system designed to automate software development tasks with safety controls and human approval workflows.

## 🎯 Objective

Build a sophisticated autonomous system that can:
- **Plan** software tasks into actionable steps
- **Generate** production-quality Python code
- **Validate** code for syntax and quality
- **Review** code for improvements and security
- **Commit** to GitHub only after explicit human approval

## ✨ Key Features

✅ **Multi-Agent Architecture** - Planner, Programmer, and Reviewer agents working in coordination
✅ **Code Validation** - AST-based syntax checking and quality metrics
✅ **Comprehensive Review** - Quality scoring, security checks, and best practices
✅ **Safe GitHub Integration** - Branch-based workflow with approval gates
✅ **Interactive Dashboard** - Streamlit-powered UI for full control
✅ **Production Ready** - Modular, testable, and maintainable code

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Streamlit UI (app.py)                          │
│         Interactive Dashboard & Control Center              │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│           TaskOrchestrator (core/orchestrator.py)           │
│    Coordinates agents and manages workflow state            │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌────────┐    ┌────────┐    ┌────────┐
   │ Planner│    │Program-│    │Reviewer│
   │ Agent  │────│ mer    │────│ Agent  │
   │        │    │ Agent  │    │        │
   └────────┘    └────────┘    └────────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
        ┌──────────────┼──────────────┬────────────┐
        │              │              │            │
        ▼              ▼              ▼            ▼
   ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌─────────┐
   │ Memory  │  │ Validator│  │ GitHub  │  │ Config  │
   │ Module  │  │ Module   │  │ Tool    │  │ & Env   │
   └─────────┘  └──────────┘  └─────────┘  └─────────┘
```

## 📁 Project Structure

```
Autonomous-AI-Developer-System-AADS-/
│
├── app.py                          # Main Streamlit dashboard
├── requirements.txt                # Python dependencies
├── .env                           # Environment configuration (template)
│
├── agents/                        # AI Agent modules
│   ├── __init__.py
│   ├── planner.py                # Task planning agent
│   ├── programmer.py             # Code generation agent
│   └── reviewer.py               # Code review agent
│
├── core/                          # Core system modules
│   ├── __init__.py
│   ├── memory.py                 # Repository context & file tracking
│   ├── validator.py              # Code validation & quality checks
│   ├── github_tool.py            # Safe GitHub operations
│   └── orchestrator.py           # Workflow orchestration
│
├── tests/                         # Test suite
│   ├── __init__.py
│   └── test_validator.py         # Unit tests for validator
│
└── README.md                      # This file
```

## 🔁 Workflow Steps

### Step 1️⃣: Task Input
User describes their coding task in natural language via the Streamlit UI.

### Step 2️⃣: Planning
**PlannerAgent** breaks down the task into:
- Actionable implementation steps
- Suggested code structure
- Timeline estimates
- Key considerations

### Step 3️⃣: Code Generation
**ProgrammerAgent** generates production-quality code based on the plan:
- Functions and classes
- Documentation and docstrings
- Error handling
- Type hints

### Step 4️⃣: Validation
**CodeValidator** performs:
- Syntax validation (AST parsing)
- Code quality metrics
- Structural analysis
- Error detection

### Step 5️⃣: Code Review
**ReviewerAgent** conducts comprehensive review:
- Quality scoring (0-100)
- Security vulnerability detection
- Best practices compliance
- Specific improvement suggestions

### Step 6️⃣: Approval & Commit
User reviews everything in the UI and explicitly approves:
- Code is staged to git
- Changes committed to feature branch
- **Never auto-commits** - always requires approval
- Never pushes to main by default

## 💻 Core Modules

### `core/memory.py` - RepositoryMemory
Manages repository context and file tracking:
```python
memory = RepositoryMemory(repo_path=".")
repo_map = memory.get_repo_map()  # Get repo structure
files = memory.list_files("agents")  # List files in directory
content = memory.get_file_content("agents/planner.py")  # Read file
```

### `core/validator.py` - CodeValidator
Validates Python code with comprehensive checks:
```python
validator = CodeValidator()
result = validator.validate(code, "filename.py")
# Returns: ValidationResult with valid, errors, warnings, metrics
```

**Validation Checks:**
- ✓ Syntax validation (AST)
- ✓ Code quality metrics
- ✓ Line length analysis
- ✓ Function complexity
- ✓ Documentation presence
- ✓ Type hints

### `core/github_tool.py` - GitHubTool
Safe GitHub operations with approval workflow:
```python
github = GitHubTool(repo_path=".", github_token=token)
success, msg = github.create_feature_branch("feature/task-123")
success, msg = github.stage_changes("file.py", content)
success, msg = github.commit_to_branch("file.py", content, "commit msg")
```

**Safety Features:**
- ✓ Creates feature branches (never commits to main)
- ✓ Stage-before-commit workflow
- ✓ Explicit commit approval required
- ✓ No auto-push to remote

### `core/orchestrator.py` - TaskOrchestrator
Coordinates the entire workflow:
```python
orchestrator = TaskOrchestrator(repo_path=".")
orchestrator.start_task(user_input)
orchestrator.create_plan(plan)
orchestrator.store_generated_code(code)
orchestrator.validate_code(code)
orchestrator.store_review_feedback(feedback)
orchestrator.execute_commit(file_path, content, message)
```

### `agents/planner.py` - PlannerAgent
Creates structured implementation plans:
```python
planner = PlannerAgent(orchestrator=orchestrator)
plan = planner.plan_task(user_input, context)
# Returns: plan with tasks, structure, timeline, considerations
```

### `agents/programmer.py` - ProgrammerAgent
Generates production-quality code:
```python
programmer = ProgrammerAgent(orchestrator=orchestrator)
code_result = programmer.generate_code(plan, context)
refactored = programmer.refactor_code(code, feedback, context)
optimized = programmer.optimize_code(code)
```

### `agents/reviewer.py` - ReviewerAgent
Performs comprehensive code review:
```python
reviewer = ReviewerAgent(orchestrator=orchestrator)
review = reviewer.review_code(code, plan, validation_result)
approval = reviewer.approve_code(code, threshold=70)
report = reviewer.generate_improvement_report(review)
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Autonomous-AI-Developer-System-AADS-.git
cd Autonomous-AI-Developer-System-AADS-

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy .env template and configure
cp .env .env.local

# Edit .env.local with your settings:
# - GITHUB_TOKEN: Your GitHub personal access token
# - LLM_API_KEY: Your AI model API key (if using LLM integration)
# - Other configuration options
```

### 3. Run the System

```bash
# Start the Streamlit dashboard
streamlit run app.py

# The app will open at: http://localhost:8501
```

### 4. Run Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=core --cov=agents

# Run specific test
pytest tests/test_validator.py -v
```

## 🧪 Testing

The system includes comprehensive unit tests for the validator:

```bash
# Run validator tests
python -m pytest tests/test_validator.py -v

# Run all tests
python -m pytest tests/ -v --tb=short
```

**Test Coverage:**
- ✓ Syntax error detection
- ✓ Code quality metrics
- ✓ Long line detection
- ✓ Function analysis
- ✓ Class detection
- ✓ Various error scenarios

## 📊 Code Quality Metrics

The validator automatically calculates:
- **Total Lines**: Line count of code
- **Non-Empty Lines**: Excluding blank lines
- **Comment Lines**: Number of comment lines
- **Comment Ratio**: Percentage of comments
- **Function Count**: Number of functions defined
- **Class Count**: Number of classes defined

## 🔒 Safety & Security

### Approval Workflow
✅ **No Auto-Commit:** ALL commits require explicit human approval via UI
✅ **Safe Branching:** Code committed to feature branches, never directly to main
✅ **Validation Gate:** Code must pass validation before approval option appears
✅ **Review Feedback:** Reviewer output shown before approval

### Security Checks
✅ **Secret Detection:** Warns about potential hardcoded secrets
✅ **SQL Injection:** Detects unsafe SQL query patterns
✅ **Code Injection:** Checks for dangerous eval() usage
✅ **Import Audit:** Analyzes import statements

### Git Safety
✅ **Create branches:** Feature branches for isolation
✅ **Stage changes:** Preview before committing
✅ **Commit messages:** Required commit message
✅ **No direct main:** Cannot push to main/master directly

## 🔧 Configuration Options

Key environment variables in `.env`:

```env
# GitHub
GITHUB_TOKEN=your_token
GITHUB_REPO_PATH=.
APPROVAL_REQUIRED=true          # Require approval before commit
AUTO_PUSH=false                 # Never auto-push

# Code Quality
MIN_CODE_QUALITY_SCORE=70       # Minimum quality to approve
STRICT_VALIDATION=false         # Strict validation mode

# Features
ENABLE_AUTO_COMMIT=false        # Never auto-commit
ENABLE_PULL_REQUEST_CREATION=false
ENABLE_CODE_FORMATTING=true
ENABLE_SECURITY_CHECKS=true
```

## 📈 Quality Scoring

Code is scored on multiple dimensions:

### Code Quality Score (0-100)
- Base: 50 points
- +10: Has docstrings
- +10: Has type hints
- +10: Has error handling
- +10: Good organization
- -10: Very long functions

### Overall Score
- 40% weight: Code quality
- 60% weight: Improvement potential

Approval threshold: **70+ points**

## 🎨 Streamlit UI Features

### Dashboard Sections
1. **Task Input** - Describe your coding task
2. **Implementation Plan** - Review the plan
3. **Generated Code** - View and copy code
4. **Validation Results** - Check syntax and metrics
5. **Code Review** - Read reviewer feedback
6. **Approval & Commit** - Approve and commit changes

### Interactive Elements
- 📊 Real-time metrics and scores
- 🔄 Reset workflow button
- ✅ Approval with custom commit message
- ❌ Reject draft option
- 📋 Copy code to clipboard
- 🔧 Debug mode in sidebar

## 🤝 Contributing

To extend the system:

1. **Add new agents:** Create new files in `agents/` directory
2. **Enhance validators:** Modify validation rules in `core/validator.py`
3. **Add features:** Update orchestrator and UI accordingly
4. **Write tests:** Add tests in `tests/` directory

## 📚 Documentation

### Module Documentation
Each module includes:
- Class docstrings
- Method docstrings with parameters
- Type hints throughout
- Usage examples

### Generated Code Documentation
Generated code includes:
- Module-level docstrings
- Function docstrings
- Type hints on all parameters
- Return value documentation

## 🐛 Troubleshooting

### Git Errors
```bash
# Check git status
git status

# View current branch
git branch

# Check git configuration
git config -l
```

### Streamlit Issues
```bash
# Clear Streamlit cache
streamlit cache clear

# Run with verbose logging
streamlit run app.py --logger.level=debug
```

### Import Errors
```bash
# Verify installations
pip list | grep -E "(streamlit|crewai|pygithub)"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📝 Example Usage

### Example 1: Create an Email Validator
```
Task: Create a function that validates email addresses using regex
The function should return True if valid, False otherwise.
Include error handling for edge cases.
```

**Output:**
- Plan with validation strategy
- Generated email validation function
- Code validation results
- Review feedback on security
- Ready to commit after approval

### Example 2: Create a Data Processing Class
```
Task: Create a Python class called DataProcessor that:
- Accepts a list of dictionaries in __init__
- Has a filter method that filters by a key
- Has a transform method that applies a function
- Include proper documentation
```

**Output:**
- Plan with class structure
- Full class implementation
- Quality metrics and validation
- Review with best practices
- Safe commit workflow

## 🎓 Learning Resources

- [Python ast module](https://docs.python.org/3/library/ast.html)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Git Workflows](https://git-scm.com/book/en/v2/Git-Branching-Branching-Workflows)
- [Type Hints in Python](https://docs.python.org/3/library/typing.html)

## 📄 License

MIT License - See LICENSE file for details

## 🙋 Support

For issues or questions:
1. Check existing documentation
2. Review error messages carefully
3. Check git status and branch
4. Review .env configuration
5. Run tests to verify installation

## 🔮 Future Enhancements

- 🔄 Integration with LLM APIs (OpenAI, Claude, etc.)
- 📊 Advanced code metrics and analytics
- 🔗 Pull request creation and management
- 📈 Code quality history and trends
- 🎯 Custom validation rules
- 🤖 More specialized agents
- 🌐 Web-based deployment
- 📱 Mobile UI support

---

**Built with ❤️ for autonomous, safe, and intelligent code generation**

*Last Updated: March 28, 2026*
