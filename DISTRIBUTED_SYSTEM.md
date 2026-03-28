# Distributed Multi-Agent System Documentation

## Overview

The Autonomous AI Developer System now supports **distributed multi-agent execution**, enabling complex coding tasks to be decomposed and executed in parallel by specialized agents.

### Key Features

✅ **Task Decomposition** - Automatically breaks tasks into specialized subtasks  
✅ **Parallel Execution** - Multiple agents execute simultaneously using asyncio  
✅ **Specialized Agents** - Backend, Frontend, and Test agents with domain expertise  
✅ **Intelligent Aggregation** - Merges outputs while resolving conflicts  
✅ **Self-Improvement Integration** - Distributed code goes through quality improvement loop  
✅ **Learning System** - Tracks decomposition effectiveness and agent performance  
✅ **Safety Constraints** - Timeouts, parallel limits, and fallback mechanisms  

---

## Architecture

### Components

#### 1. **TaskDecomposer** (`core/task_decomposer.py`)
Analyzes task description and plan, breaks into specialized subtasks:
- Identifies backend requirements (API, DB, business logic)
- Identifies frontend requirements (UI, interactions, visualization)
- Identifies test requirements (unit tests, integration tests, edge cases)
- Determines parallelization strategy

**Example Decomposition:**
```
"Build login system" →
├── BackendTask: API endpoints, database models, authentication
├── FrontendTask: Login form, state management, error handling  
└── TestTask: Unit tests, integration tests, edge cases
```

#### 2. **DistributedCoordinator** (`core/coordinator.py`)
Main orchestration engine:
- Receives decomposed subtasks
- Manages parallel agent execution (with asyncio)
- Enforces timeouts and parallel limits
- Collects and aggregates results
- Tracks agent performance metrics

**Configuration:**
```python
MAX_PARALLEL_AGENTS = 3      # Max concurrent agents
AGENT_TIMEOUT = 30           # Seconds per agent
ENABLE_FALLBACK = True       # Fallback on failure
```

#### 3. **ResultAggregator** (`core/aggregator.py`)
Merges agent outputs:
- Combines code sections with unified imports
- Organizes code by layer (backend → frontend → tests)
- Merges dependencies and documentation
- Detects and resolves conflicts (duplicate functions, import conflicts)
- Produces final integrated code

#### 4. **Specialized Agents**
Each agent is domain-expert for specific code types:

##### BackendAgent (`agents/backend_agent.py`)
Generates:
- REST/GraphQL API endpoints
- Database models and ORM
- Business logic and algorithms
- Error handling and logging
- Caching and data processing

##### FrontendAgent (`agents/frontend_agent.py`)
Generates:
- Streamlit application structure
- Reusable UI components (cards, forms, tables)
- State management utilities
- Event handling system
- Interactive dashboards

##### TestAgent (`agents/test_agent.py`)
Generates:
- Unit test classes (unittest)
- Integration test suites
- Edge case coverage
- Pytest fixtures
- Test utilities and helpers

---

## Workflow

### Single-Agent Pipeline (Existing)
```
User Task
  ↓
Planner → Creates Plan
  ↓
Programmer → Generates Code
  ↓
Validator → Validates Syntax
  ↓
Reviewer → Reviews Code
  ↓
(Optional) Improvement Loop → Refactors until threshold
  ↓
User Approval → Commit
```

### Distributed Multi-Agent Pipeline (New)
```
User Task
  ↓
Planner → Creates Plan
  ↓
TaskDecomposer → Breaks into subtasks
  ↓
┌─ BackendAgent ──┐
├─ FrontendAgent ┼─ (Execute in Parallel)
└─ TestAgent ────┘
  ↓
ResultAggregator → Merges outputs, resolves conflicts
  ↓
Validator → Validates merged code
  ↓
Reviewer → Reviews integrated code
  ↓
(Optional) Improvement Loop → Refactors until threshold
  ↓
User Approval → Commit
```

---

## Usage

### Enable Distributed Mode in UI

1. In Streamlit app, check **"🔄 Enable Distributed Multi-Agent Mode"**
2. Select which agents to use:
   - ☑️ Backend Agent (API/DB logic)
   - ☑️ Frontend Agent (UI/Streamlit)
   - ☑️ Test Agent (Unit/Integration tests)
3. Optionally enable **"🤖 Enable Autonomous Self-Improvement"**
4. Click **"🚀 Generate Draft"**

### Programmatic Usage

```python
from core.orchestrator import TaskOrchestrator
from agents.backend_agent import BackendAgent
from agents.frontend_agent import FrontendAgent
from agents.test_agent import TestAgent

# Initialize
orchestrator = TaskOrchestrator(repo_path=".")
orchestrator.start_task("Build user authentication system")
plan = planner.plan_task(task_input, context)
orchestrator.create_plan(plan)

# Create agent registry
from agents.backend_agent import BackendAgent
from agents.frontend_agent import FrontendAgent
from agents.test_agent import TestAgent

agent_registry = {
    "backend": BackendAgent(orchestrator).generate_code,
    "frontend": FrontendAgent(orchestrator).generate_code,
    "test": TestAgent(orchestrator).generate_code,
}

# Execute distributed
result = orchestrator.execute_distributed(
    agent_registry,
    use_improvement_loop=True
)

# Access results
print(result["code"])  # Merged code
print(result["execution_summary"]["agents"])  # Agent statuses
```

---

## Task Decomposition Strategy

### Detection Keywords

**Backend** (API, database, server, endpoint, model, algorithm, business logic, REST, GraphQL, authentication, authorization)

**Frontend** (UI, interface, dashboard, button, form, page, component, streamlit, visualization, state, input, output, display)

**Test** (test, unit, integration, edge case, validation, error handling, mock, pytest, coverage, QA)

### Parallelization Batches

Tasks are organized into parallel batches:

```
Batch 1 (Independent):
  - BackendTask
  - FrontendTask

Batch 2 (Dependent):
  - TestTask (depends on BackendTask)
```

Agents in the same batch execute simultaneously, respecting `MAX_PARALLEL_AGENTS` limit.

---

## Output Integration

### Code Organization

Final merged code is organized as:

```python
"""
Unified module from distributed multi-agent generation
"""

# Unified Imports (deduplicated, categorized)
import os
import sys
from typing import Dict, List

import streamlit as st
import pandas as pd

# ==================== BACKEND CODE ====================
# API endpoints, database models, business logic

class APIEndpoint:
    ...

class DatabaseManager:
    ...

# ==================== FRONTEND CODE ====================
# UI components, state management, event handling

class StreamlitApp:
    ...

class UIComponent:
    ...

# ==================== TEST CODE ====================
# Unit tests, integration tests

class TestFunctionality(unittest.TestCase):
    ...
```

---

## Conflict Resolution

### Detected Conflicts

#### 1. **Duplicate Function Names**
```python
# Backend generates: def process_data()
# Frontend generates: def process_data()
# → CONFLICT: Both agents define same function
```

**Resolution:** 
- First agent's version kept
- Second agent's version renamed to `process_data_frontend()`
- Logged in conflict report

#### 2. **Conflicting Imports**
```python
# Backend: from numpy import array
# Frontend: from array import array
# → CONFLICT: Different modules, same name
```

**Resolution:**
- Imports merged with explicit module paths
- Warnings logged
- Can be manually reviewed before merge

### Conflict Detection Output

```json
{
  "conflicts": [
    {
      "type": "duplicate_function",
      "function": "process_data",
      "agents": ["backend", "frontend"]
    },
    {
      "type": "conflicting_imports",
      "package": "array",
      "imports": {
        "backend": "from numpy import array",
        "frontend": "from array import array"
      }
    }
  ]
}
```

---

## Performance & Monitoring

### Execution Status Display

The Streamlit UI shows:

1. **Agent Execution Status**
   - ✓ Success, ✗ Failed, ⏭️ Not Executed

2. **Decomposition Strategy**
   - `single_task` - No decomposition needed
   - `frontend_backend` - 2 parallel agents
   - `full_stack_with_tests` - 3 parallel agents
   - `complex_multi_component` - Complex task

3. **Task Complexity Score** (0-1.0)
   - Factors: Keywords, task length, algorithm complexity

4. **Conflict Metrics**
   - Green: No conflicts
   - Yellow: 1-2 conflicts
   - Red: 3+ conflicts

### Agent Performance Tracking

Memory system tracks:
- Agent execution count
- Success rate per agent
- Average code generation size
- Execution times

**View Performance:**
```python
status = orchestrator.get_distributed_status()
print(status["agent_performance"])
# {
#   "backend": {"executions": 5, "success_rate": 0.8},
#   "frontend": {"executions": 5, "success_rate": 1.0},
#   "test": {"executions": 4, "success_rate": 0.75}
# }
```

### Decomposition Effectiveness

Track which strategies work best:

```python
effectiveness = memory.get_decomposition_effectiveness()
# {
#   "full_stack_with_tests": {
#       "count": 10,
#       "success_rate": 0.9,
#       "avg_conflicts": 0.5,
#       "avg_time": 8.3
#   }
# }
```

---

## Safety Features

### 1. **Timeout Protection**
Each agent has 30-second timeout:
```python
AGENT_TIMEOUT = 30  # seconds
```
If agent takes longer, task fails with timeout error.

### 2. **Parallel Limit**
Maximum 3 agents run simultaneously:
```python
MAX_PARALLEL_AGENTS = 3
```
Prevents resource exhaustion, ensures predictable performance.

### 3. **Fallback Mechanism**
If distributed execution fails:
```python
ENABLE_FALLBACK = True
```
System automatically falls back to single-agent pipeline.

### 4. **Validation Gate**
Merged code still validated before approval:
- Syntax checking
- Import validation
- Structure analysis

### 5. **Approval Requirements**
All commits still require explicit user approval.
Distributed execution doesn't bypass approval gate.

---

## Integration with Improvement Loop

When enabled, distributed code goes through the autonomous improvement loop:

```
Distributed Code Generated
  ↓
Validation → Check syntax
  ↓ (if valid)
Review → Get quality score
  ↓
If score < 85 and iterations < 5:
  ↓
  Refactor → Ask programmer to improve
  ↓
  Validate again → Loop
Else:
  ✓ Return improved code
```

The programmer agent can refactor the merged distributed code if quality score is below threshold.

---

## Memory & Learning

### Distributed Execution History

Stored in `.memory/distributed_history.json`:

```json
{
  "task_id": "task_123",
  "description": "Build login system",
  "agents_used": ["backend", "frontend", "test"],
  "agent_count": 3,
  "code_length": 2547,
  "decomposition_strategy": "full_stack_with_tests",
  "conflicts": 0,
  "execution_time": 8.5,
  "success": true,
  "saved_at": "2024-03-28T10:30:45.123456"
}
```

### Learning from History

```python
# Get agent performance from past executions
perf = memory.get_agent_performance_from_history()

# Get strategy effectiveness
strategies = memory.get_decomposition_effectiveness()

# Use insights for future tasks
if strategies["full_stack_with_tests"]["success_rate"] > 0.8:
    recommend_distributed_mode()
```

---

## Limitations & Future Enhancements

### Current Limitations
- Agents execute in parallel but independently (limited communication)
- Conflict resolution is automatic but simplistic
- No inter-agent dependency management during execution
- Test agent doesn't have access to generated backend/frontend code

### Future Enhancements
- **Agent Communication** - Agents can request/share generated code
- **Smart Conflict Resolution** - ML-based resolution of naming conflicts
- **Code Dependencies** - Test agent receives actual generated code to test
- **Incremental Refinement** - Agents can revise output based on other agents
- **Load Balancing** - Dynamic parallel limits based on system resources
- **Caching** - Reuse previously generated similar components

---

## Configuration

### Settings in `core/coordinator.py`

```python
# Maximum parallel agents executing simultaneously
MAX_PARALLEL_AGENTS = 3

# Timeout per agent (seconds)
AGENT_TIMEOUT = 30

# Enable fallback to single-agent on failure
ENABLE_FALLBACK = True
```

### Settings in `core/orchestrator.py`

```python
# Improvement loop configuration
MAX_ITERATIONS = 5  # Max autonomous improvement iterations
QUALITY_THRESHOLD = 85  # Target quality score (0-100)
```

---

## Troubleshooting

### Issue: "All agents failed to produce results"
**Cause:** All specialized agents encountered errors  
**Solution:** Check error logs, ensure agents are properly imported

### Issue: High conflict count in merge
**Cause:** Agents generating overlapping functionality  
**Solution:** Review decomposition strategy, adjust task description to be more specific

### Issue: Agent timeout
**Cause:** Agent took longer than 30 seconds  
**Solution:** Increase `AGENT_TIMEOUT` or simplify task

### Issue: Distributed code quality lower than single-agent
**Cause:** Agents not fully optimized for domain  
**Solution:** Enable improvement loop, increase `QUALITY_THRESHOLD`

---

## Examples

### Example 1: Simple CRUD API

**Input:** "Create a basic CRUD API for users with Streamlit dashboard and tests"

**Decomposition:**
- Backend: User model, CRUD endpoints, database operations
- Frontend: User dashboard, form for adding users, list view
- Test: Unit tests for CRUD operations, form validation tests

**Execution:** ~8-10 seconds for all 3 agents in parallel
**Conflicts:** 0 (clear separation of concerns)
**Quality:** 92/100 (high quality due to specialization)

### Example 2: Complex System

**Input:** "Build a machine learning pipeline with API, web UI, monitoring dashboard, and comprehensive tests"

**Decomposition:**
- Backend: ML model training, API endpoints, data processing
- Frontend: Model UI, parameter tuning interface, monitoring dashboard
- Test: Model unit tests, API integration tests, UI tests

**Execution:** ~12-15 seconds for all agents
**Conflicts:** 1-2 (shared utilities)
**Quality:** 88/100 (resolved through improvement loop)

---

## Best Practices

1. **Be Specific in Task Descriptions**
   - ❌ "Make a system"
   - ✅ "Create a REST API with user authentication, frontend form for login, and comprehensive test suite"

2. **Leverage Specialization**
   - Use distributed mode for tasks with clear backend/frontend separation
   - Use single-agent for small, cohesive tasks

3. **Monitor Agent Performance**
   - Check "Debug Mode" in sidebar to see agent success rates
   - Disables agents with low success rates

4. **Enable Improvement Loop**
   - Especially useful with distributed mode
   - Code from multiple agents benefits from quality refinement

5. **Review Conflicts**
   - Always check conflict report
   - Manually resolve ambiguous naming

---

## API Reference

### TaskOrchestrator Methods

**`execute_distributed(agent_registry, use_improvement_loop=True)`**
- Execute task using distributed multi-agent system
- Returns: `{"status": "success", "code": "...", "execution_summary": {...}}`

**`get_distributed_status()`**
- Get current distributed execution status and metrics
- Returns: Status dictionary with agent performance

**`get_distributed_history(limit=10)`**
- Get recent distributed executions
- Returns: List of execution records

### RepositoryMemory Methods

**`save_distributed_execution(...)`**
- Save distributed execution record for learning

**`get_distributed_history(limit=10)`**
- Get recent distributed executions

**`get_agent_performance_from_history()`**
- Analyze agent performance metrics

**`get_decomposition_effectiveness()`**
- Get strategy effectiveness analysis

---

## Conclusion

The distributed multi-agent system enables sophisticated task execution by leveraging specialized agents. It provides:

- **Efficiency** through parallel execution
- **Quality** through domain specialization
- **Reliability** through conflict resolution and fallback mechanisms
- **Intelligence** through task learning and performance tracking
- **Safety** through approval gates and validation

Use distributed mode for complex, multi-layered tasks to accelerate development while maintaining code quality.
