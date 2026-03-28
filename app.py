import sys
import os

# Menambahkan direktori root project ke sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


"""
Autonomous AI Developer System - Streamlit UI
Main dashboard for controlling code generation, validation, and approval workflow
"""

# pyright: reportMissingImports=false

try:
    import streamlit as st
except ImportError as e:
    raise ImportError(
        "streamlit tidak ditemukan. Pasang dependensi dengan: pip install streamlit"
    ) from e

import os
from pathlib import Path
from datetime import datetime
from typing import Optional
import importlib

# Import system components
from core.orchestrator import TaskOrchestrator
from core.memory import RepositoryMemory
from agents.planner import PlannerAgent
from agents.programmer import ProgrammerAgent
from agents.reviewer import ReviewerAgent


# Utility for runtime import checks

def safe_import_agent(agent_module: str, class_name: str):
    try:
        module = importlib.import_module(agent_module)
        return getattr(module, class_name)
    except ModuleNotFoundError:
        st.warning(
            f"Modul agen tidak ditemukan: {agent_module}. Mode terdistribusi akan menonaktifkan agen ini."
        )
        return None
    except AttributeError:
        st.warning(
            f"Kelas agen tidak ditemukan: {class_name} di {agent_module}. Pastikan kelas ada."
        )
        return None


BackendAgent = safe_import_agent("agents.backend_agent", "BackendAgent")
FrontendAgent = safe_import_agent("agents.frontend_agent", "FrontendAgent")
TestAgent = safe_import_agent("agents.test_agent", "TestAgent")


# Page configuration
st.set_page_config(
    page_title="Autonomous AI Developer System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better UI
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5em;
        font-weight: bold;
        color: #FF6B35;
        margin-bottom: 10px;
    }
    .section-header {
        font-size: 1.5em;
        font-weight: bold;
        color: #1E3A8A;
        margin-top: 20px;
        border-bottom: 2px solid #FF6B35;
        padding-bottom: 10px;
    }
    .status-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        margin: 5px 0;
    }
    .status-success {
        background-color: #10b981;
        color: white;
    }
    .status-warning {
        background-color: #f59e0b;
        color: white;
    }
    .status-error {
        background-color: #ef4444;
        color: white;
    }
    .status-info {
        background-color: #3b82f6;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = TaskOrchestrator(repo_path=".")

    if "planner" not in st.session_state:
        st.session_state.planner = PlannerAgent(
            st.session_state.orchestrator
        )

    if "programmer" not in st.session_state:
        st.session_state.programmer = ProgrammerAgent(
            st.session_state.orchestrator
        )

    if "reviewer" not in st.session_state:
        st.session_state.reviewer = ReviewerAgent(
            st.session_state.orchestrator
        )

    if "draft_code" not in st.session_state:
        st.session_state.draft_code = None

    if "current_plan" not in st.session_state:
        st.session_state.current_plan = None

    if "validation_result" not in st.session_state:
        st.session_state.validation_result = None

    if "review_result" not in st.session_state:
        st.session_state.review_result = None

    if "approval_pending" not in st.session_state:
        st.session_state.approval_pending = False

    if "commit_message" not in st.session_state:
        st.session_state.commit_message = ""

    if "file_path" not in st.session_state:
        st.session_state.file_path = "generated_code.py"

    if "iteration_history" not in st.session_state:
        st.session_state.iteration_history = []

    if "iteration_stats" not in st.session_state:
        st.session_state.iteration_stats = None

    if "threshold_met" not in st.session_state:
        st.session_state.threshold_met = False

    if "distributed_execution_result" not in st.session_state:
        st.session_state.distributed_execution_result = None

    if "enable_distributed_mode" not in st.session_state:
        st.session_state.enable_distributed_mode = False

    if "distributed_agents" not in st.session_state:
        st.session_state.distributed_agents = []

    if "autonomous_evolution_mode" not in st.session_state:
        st.session_state.autonomous_evolution_mode = False

    if "evolution_status" not in st.session_state:
        st.session_state.evolution_status = "idle"

    if "evolution_cycles_completed" not in st.session_state:
        st.session_state.evolution_cycles_completed = 0

    if "evolution_tasks_generated" not in st.session_state:
        st.session_state.evolution_tasks_generated = []

    if "evolution_critic_report" not in st.session_state:
        st.session_state.evolution_critic_report = None

    if "kill_switch" not in st.session_state:
        st.session_state.kill_switch = False


def render_header():
    """Render the main header section"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(
            '<div class="main-header">🤖 Autonomous AI Developer System</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            "Production-grade code generation with autonomous self-improvement"
        )
    
    with col2:
        if st.button("🔄 Reset Workflow", key="reset_btn"):
            st.session_state.orchestrator.reset_workflow()
            st.session_state.draft_code = None
            st.session_state.current_plan = None
            st.session_state.validation_result = None
            st.session_state.review_result = None
            st.session_state.approval_pending = False
            st.session_state.iteration_history = []
            st.session_state.threshold_met = False
            st.success("Workflow reset successfully!")
            st.rerun()


def render_task_input():
    """Render task input section"""
    st.markdown(
        '<div class="section-header">📝 Step 1: Task Input</div>',
        unsafe_allow_html=True,
    )

    with st.form("task_input_form"):
        task_input = st.text_area(
            "Describe your coding task:",
            placeholder="E.g., Create a function that validates email addresses and returns True/False",
            height=100,
            key="task_input",
        )

        file_path = st.text_input(
            "File path (relative to repo):",
            value="generated_code.py",
            key="file_path_input",
        )

        col1, col2 = st.columns(2)
        
        with col1:
            # Autonomous improvement toggle
            enable_autonomous = st.checkbox(
                "🤖 Enable Autonomous Self-Improvement (auto-refactor until quality threshold met)",
                value=True,
            )
        
        with col2:
            # Distributed mode toggle
            enable_distributed = st.checkbox(
                "🔄 Enable Distributed Multi-Agent Mode (parallel specialized agents)",
                value=False,
            )

        if enable_distributed:
            st.markdown("#### Select Agents for Parallel Execution")
            col1, col2, col3 = st.columns(3)
            with col1:
                use_backend = st.checkbox("Backend Agent (API/DB logic)", value=True)
            with col2:
                use_frontend = st.checkbox("Frontend Agent (UI/Streamlit)", value=True)
            with col3:
                use_test = st.checkbox("Test Agent (Unit/Integration tests)", value=True)
            
            selected_agents = []
            if use_backend:
                selected_agents.append("backend")
            if use_frontend:
                selected_agents.append("frontend")
            if use_test:
                selected_agents.append("test")
            
            st.session_state.distributed_agents = selected_agents

        st.markdown("#### 🌱 Autonomous Evolution Mode")
        st.session_state.autonomous_evolution_mode = st.checkbox(
            "Enable Autonomous Evolution (self-generated tasks and improvements)",
            value=st.session_state.autonomous_evolution_mode,
        )

        if st.session_state.autonomous_evolution_mode:
            st.info("Autonomous evolution is active. Evolution loop will run after draft generation.")

        backend_agent_obj = None
        frontend_agent_obj = None
        test_agent_obj = None

        generate_btn = st.form_submit_button(
            "🚀 Generate Draft", type="primary"
        )

        if generate_btn and task_input:
            with st.spinner("Generating draft..."):
                # Step 1: Planner
                st.session_state.orchestrator.start_task(task_input)
                context = st.session_state.orchestrator.get_agents_prompt_context()

                #Plan
                plan = st.session_state.planner.plan_task(task_input, context)
                st.session_state.current_plan = plan

                agent_registry = {}
                if enable_distributed:
                    with st.spinner("Setting up distributed agents..."):
                        if "backend" in st.session_state.distributed_agents and BackendAgent:
                            backend_agent = BackendAgent(st.session_state.orchestrator)
                            backend_agent_obj = backend_agent
                            agent_registry["backend"] = backend_agent.generate_code
                        elif "backend" in st.session_state.distributed_agents:
                            st.warning("BackendAgent tidak diinisialisasi karena modul tidak tersedia.")

                        if "frontend" in st.session_state.distributed_agents and FrontendAgent:
                            frontend_agent = FrontendAgent(st.session_state.orchestrator)
                            frontend_agent_obj = frontend_agent
                            agent_registry["frontend"] = frontend_agent.generate_code
                        elif "frontend" in st.session_state.distributed_agents:
                            st.warning("FrontendAgent tidak diinisialisasi karena modul tidak tersedia.")

                        if "test" in st.session_state.distributed_agents and TestAgent:
                            test_agent = TestAgent(st.session_state.orchestrator)
                            test_agent_obj = test_agent
                            agent_registry["test"] = test_agent.generate_code
                        elif "test" in st.session_state.distributed_agents:
                            st.warning("TestAgent tidak diinisialisasi karena modul tidak tersedia.")

                with st.spinner("Running crew AI workflow..."):
                    result = st.session_state.orchestrator.run_task(
                        task_input,
                        st.session_state.planner,
                        st.session_state.programmer,
                        st.session_state.reviewer,
                        use_distributed=enable_distributed,
                        distributed_agents=agent_registry,
                        use_autonomous=enable_autonomous,
                    )

                st.session_state.current_plan = result.get("plan")
                st.session_state.draft_code = result.get("code")
                st.session_state.validation_result = result.get("validation")
                st.session_state.review_result = result.get("review")
                st.session_state.distributed_execution_result = result.get("distributed_execution")
                st.session_state.iteration_history = st.session_state.orchestrator.iteration_history
                st.session_state.threshold_met = result.get("review", {}).get("score", 0) >= 85

                if st.session_state.autonomous_evolution_mode:
                    st.session_state.evolution_status = "running"
                    evolution_result = st.session_state.orchestrator.run_evolution_loop(
                        planner_agent=st.session_state.planner,
                        programmer_agent=st.session_state.programmer,
                        reviewer_agent=st.session_state.reviewer,
                        backend_agent=backend_agent_obj,
                        frontend_agent=frontend_agent_obj,
                        test_agent=test_agent_obj,
                        sleep_interval=5,
                        max_cycles=3,
                        max_tasks_per_cycle=3,
                        kill_switch=lambda: st.session_state.kill_switch,
                    )
                    st.session_state.evolution_cycles_completed = evolution_result.get("cycles_run", 0)
                    st.session_state.evolution_tasks_generated = evolution_result.get("tasks_generated", [])
                    st.session_state.evolution_critic_report = st.session_state.orchestrator.memory.get_evolution_history()[-1] if st.session_state.orchestrator.memory.get_evolution_history() else None
                    st.session_state.evolution_status = "completed"

                st.session_state.file_path = file_path
                st.success("✓ Draft generation complete!")
                st.rerun()

                if st.session_state.autonomous_evolution_mode:
                    st.session_state.evolution_status = "running"
                    with st.spinner("Running autonomous evolution loop..."):
                        evolution_result = st.session_state.orchestrator.run_evolution_loop(
                            planner_agent=st.session_state.planner,
                            programmer_agent=st.session_state.programmer,
                            reviewer_agent=st.session_state.reviewer,
                            backend_agent=backend_agent_obj,
                            frontend_agent=frontend_agent_obj,
                            test_agent=test_agent_obj,
                            sleep_interval=5,
                            max_cycles=3,
                            max_tasks_per_cycle=3,
                            kill_switch=lambda: st.session_state.kill_switch,
                        )
                        st.session_state.evolution_cycles_completed = evolution_result.get("cycles_run", 0)
                        st.session_state.evolution_tasks_generated = evolution_result.get("tasks_generated", [])
                        st.session_state.evolution_critic_report = st.session_state.orchestrator.memory.get_evolution_history()[-1] if st.session_state.orchestrator.memory.get_evolution_history() else None
                        st.session_state.evolution_status = "completed"

                st.session_state.file_path = file_path
                st.success("✓ Draft generation complete!")
                st.rerun()


def render_plan_display():
    """Render plan display section"""
    if not st.session_state.current_plan:
        return

    st.markdown(
        '<div class="section-header">📋 Step 2: Implementation Plan</div>',
        unsafe_allow_html=True,
    )

    plan = st.session_state.current_plan

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Complexity", plan.get("complexity_level", "Unknown"))

    with col2:
        st.metric("Tasks", len(plan.get("tasks", [])))

    with col3:
        timeline = plan.get("estimated_timeline", {})
        st.metric("Est. Time", timeline.get("total_estimated_duration", "N/A"))

    with st.expander("📋 View Full Plan", expanded=False):
        st.write("**Title:**", plan.get("title"))
        st.write("**Description:**", plan.get("description"))

        st.write("**Tasks:**")
        for task in plan.get("tasks", []):
            st.write(
                f"- **{task['name']}** ({task['estimated_duration']}): "
                f"{task['description']}"
            )

        st.write("**Key Considerations:**")
        for consideration in plan.get("key_considerations", []):
            st.write(f"- {consideration}")


def render_code_display():
    """Render generated code display section"""
    if not st.session_state.draft_code:
        return

    st.markdown(
        '<div class="section-header">💻 Step 3: Generated Code</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([3, 1])

    with col1:
        code_lines = len(st.session_state.draft_code.split("\n"))
        st.write(f"**Lines of Code:** {code_lines}")

    with col2:
        copy_btn = st.button("📋 Copy Code")
        if copy_btn:
            st.info("Code copied to clipboard!")

    st.code(st.session_state.draft_code, language="python")


def render_validation_display():
    """Render validation results display"""
    if not st.session_state.validation_result:
        return

    st.markdown(
        '<div class="section-header">✓ Step 4: Code Validation</div>',
        unsafe_allow_html=True,
    )

    validation = st.session_state.validation_result

    # Status indicator
    if validation["valid"]:
        st.markdown(
            '<span class="status-badge status-success">✓ VALID</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="status-badge status-error">✗ INVALID</span>',
            unsafe_allow_html=True,
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Syntax Valid", "✓ Yes" if validation["valid"] else "✗ No")

    with col2:
        st.metric("Errors", len(validation.get("errors", [])))

    with col3:
        st.metric("Warnings", len(validation.get("warnings", [])))

    # Display errors
    if validation.get("errors"):
        st.error("**Errors Found:**")
        for error in validation["errors"]:
            st.write(f"- {error}")

    # Display warnings
    if validation.get("warnings"):
        st.warning("**Warnings:**")
        for warning in validation["warnings"]:
            st.write(f"- {warning}")

    # Display metrics
    if validation.get("metrics"):
        st.info("**Code Metrics:**")
        metrics = validation["metrics"]
        metric_cols = st.columns(len(metrics))
        for idx, (key, value) in enumerate(metrics.items()):
            with metric_cols[idx % len(metric_cols)]:
                st.metric(key.replace("_", " ").title(), value)


def render_review_display():
    """Render code review display"""
    if not st.session_state.review_result:
        return

    st.markdown(
        '<div class="section-header">👥 Step 5: Code Review</div>',
        unsafe_allow_html=True,
    )

    review = st.session_state.review_result

    # Quality scores
    col1, col2, col3 = st.columns(3)

    with col1:
        quality = review.get("code_quality_score", 0)
        st.metric("Quality Score", f"{quality:.0f}/100")

    with col2:
        overall = review.get("overall_score", 0)
        st.metric("Overall Score", f"{overall:.0f}/100")

    with col3:
        issues = len(review.get("issues_found", []))
        color = "🟢" if issues == 0 else "🟡" if issues < 3 else "🔴"
        st.metric("Issues Found", f"{color} {issues}")

    # Review sections
    if review.get("suggestions"):
        with st.expander("💡 Suggestions", expanded=True):
            for suggestion in review["suggestions"]:
                st.write(f"- {suggestion}")

    if review.get("improvements"):
        with st.expander("⬆️ Improvements", expanded=True):
            for improvement in review["improvements"]:
                st.write(
                    f"**{improvement['category']}**: {improvement['suggestion']}"
                )
                st.caption(f"Benefit: {improvement['benefit']}")

    if review.get("security_issues"):
        with st.expander("🔒 Security Issues", expanded=True):
            for issue in review["security_issues"]:
                severity_color = {
                    "CRITICAL": "🔴",
                    "HIGH": "🟠",
                    "MEDIUM": "🟡",
                }
                severity_icon = severity_color.get(issue["severity"], "")
                st.error(
                    f"{severity_icon} [{issue['severity']}] {issue['issue']}"
                )
                st.write(f"→ {issue['recommendation']}")

    if review.get("best_practices"):
        with st.expander("✓ Best Practices Met", expanded=False):
            for practice in review["best_practices"]:
                st.success(practice)


def render_iteration_display():
    """Render autonomous improvement iteration tracking"""
    if not st.session_state.iteration_history:
        return

    st.markdown(
        '<div class="section-header">🔄 Autonomous Improvement Iterations</div>',
        unsafe_allow_html=True,
    )

    # Iteration summary
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Iterations", len(st.session_state.iteration_history))

    with col2:
        current_score = st.session_state.iteration_history[-1].get("score", 0)
        st.metric("Current Score", f"{current_score}/100")

    with col3:
        initial_score = st.session_state.iteration_history[0].get("score", 0)
        improvement = current_score - initial_score
        st.metric("Total Improvement", f"{improvement:+.0f} points")

    with col4:
        threshold_status = "✓ MET" if st.session_state.threshold_met else "⏳ IN PROGRESS"
        st.metric("Status", threshold_status)

    # Score progression chart
    scores = [iter_data.get("score", 0) for iter_data in st.session_state.iteration_history]
    iterations = list(range(1, len(scores) + 1))
    
    chart_data = {"Iteration": iterations, "Quality Score": scores}
    st.line_chart(
        {
            "Quality Score": scores,
            "Target Threshold (85)": [85] * len(scores),
        },
        color=["#FF6B35", "#1E3A8A"],
        use_container_width=True,
    )

    # Detailed iteration log
    with st.expander("📋 Show Iteration Logs", expanded=False):
        for idx, iter_data in enumerate(st.session_state.iteration_history, 1):
            with st.container():
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    st.write(f"**Iteration {idx}**")
                
                with col2:
                    status_icon = "✓" if iter_data.get("score", 0) >= 85 else "⚠️"
                    st.write(f"{status_icon} Score: {iter_data.get('score', 0)}/100")
                
                with col3:
                    st.write(f"Issues: {len(iter_data.get('issues', []))}")
                
                # Show improvement reason
                if iter_data.get("reason"):
                    st.caption(f"📝 Reason: {iter_data['reason']}")
                
                # Show issues if any
                if iter_data.get("issues"):
                    with st.expander(f"Issues Found ({len(iter_data['issues'])})"):
                        for issue in iter_data["issues"]:
                            st.warning(issue)
                
                st.divider()


def render_distributed_execution_display():
    """Render distributed multi-agent execution details"""
    if not st.session_state.distributed_execution_result:
        return

    st.markdown(
        '<div class="section-header">🔀 Distributed Multi-Agent Execution</div>',
        unsafe_allow_html=True,
    )

    dist_result = st.session_state.distributed_execution_result

    # Agent execution status
    st.markdown("#### Agent Execution Status")
    col1, col2, col3 = st.columns(3)

    agents = dist_result.get("execution_summary", {}).get("agents", {})

    with col1:
        backend_status = agents.get("backend", "not_executed")
        status_icon = "✓" if backend_status == "success" else "✗" if backend_status == "failed" else "⏭️"
        st.write(f"{status_icon} Backend: {backend_status}")

    with col2:
        frontend_status = agents.get("frontend", "not_executed")
        status_icon = "✓" if frontend_status == "success" else "✗" if frontend_status == "failed" else "⏭️"
        st.write(f"{status_icon} Frontend: {frontend_status}")

    with col3:
        test_status = agents.get("test", "not_executed")
        status_icon = "✓" if test_status == "success" else "✗" if test_status == "failed" else "⏭️"
        st.write(f"{status_icon} Test: {test_status}")

    # Decomposition and complexity
    st.markdown("#### Task Decomposition")
    exec_summary = dist_result.get("execution_summary", {})
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Decomposition Strategy",
            exec_summary.get("decomposition_strategy", "N/A"),
        )

    with col2:
        complexity = exec_summary.get("complexity", 0)
        st.metric("Task Complexity", f"{complexity:.2f}")

    with col3:
        conflict_count = exec_summary.get("conflicts") or 0
        if isinstance(conflict_count, list):
            conflict_count = len(conflict_count)
        conflict_icon = "🟢" if conflict_count == 0 else "🟡" if conflict_count < 3 else "🔴"
        st.metric("Conflicts Detected", f"{conflict_icon} {conflict_count}")

    # Conflicts details if any
    if exec_summary.get("conflicts"):
        with st.expander("⚠️ Conflict Details", expanded=True):
            for conflict in exec_summary["conflicts"]:
                st.warning(f"**{conflict.get('type', 'Unknown')}**: {conflict}")

    # Parallel execution info
    with st.expander("📊 Parallel Execution Info", expanded=False):
        st.write(
            """
        **Parallel Execution Benefits:**
        - Backend and Frontend agents execute simultaneously
        - Test agent executes after backend is ready
        - Significantly faster than sequential execution
        - Automatic conflict resolution on code merge
        """
        )


def render_evolution_dashboard():
    """Render autonomous evolution dashboard."""
    if not st.session_state.autonomous_evolution_mode:
        return

    st.markdown(
        '<div class="section-header">🌱 Autonomous Evolution Dashboard</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Mode", "ON" if st.session_state.autonomous_evolution_mode else "OFF")
    with col2:
        st.metric("Status", st.session_state.evolution_status.title())
    with col3:
        st.metric("Cycles", st.session_state.evolution_cycles_completed)
    with col4:
        pending = len(st.session_state.evolution_tasks_generated)
        st.metric("Auto Tasks", pending)

    if st.session_state.evolution_critic_report:
        with st.expander("🧠 Latest Critic Report", expanded=False):
            st.write(st.session_state.evolution_critic_report)

            last_meta = st.session_state.evolution_critic_report
            resource_status = last_meta.get("resource_status") or {}
            stability_report = last_meta.get("stability_report") or {}
            architecture_suggestions = last_meta.get("architecture_suggestions") or {}

            if resource_status:
                st.markdown("#### CPU Resource Simulation")
                st.write(resource_status.get("allocation", {}))
                st.write(f"Active Agents: {resource_status.get('active_count', 0)}")
                st.write(f"Throttled: {resource_status.get('throttled', False)}")

            if stability_report:
                st.markdown("#### Stability Status")
                st.write(f"Improvement this cycle: {stability_report.get('improvement', 0):.2f}")
                st.write(f"No-improve cycles: {stability_report.get('no_improve_counter', 0)}")
                st.write(f"Should stop: {stability_report.get('should_stop', False)}")

            if architecture_suggestions:
                st.markdown("#### Architecture Suggestions")
                st.write(f"Risk level: {architecture_suggestions.get('risk_level', 'N/A')}")
                for c in architecture_suggestions.get('changes', []):
                    st.write(f"- {c.get('change')}: {c.get('target')} ({c.get('risk_level')})")

    if st.session_state.evolution_tasks_generated:
        critical_tasks = [t for t in st.session_state.evolution_tasks_generated if t.get("target", "").startswith("core/")]
        with st.expander("🛠️ Auto-generated Tasks", expanded=False):
            st.write(st.session_state.evolution_tasks_generated)

        if critical_tasks:
            st.warning(
                f"⚠️ {len(critical_tasks)} auto-generated task(s) target core/ components and require manual approval before committing."
            )


def render_approval_section():
    """Render approval and commit section"""
    if (
        not st.session_state.draft_code
        or not st.session_state.validation_result
    ):
        return

    st.markdown(
        '<div class="section-header">✅ Step 6: Approval & Commit</div>',
        unsafe_allow_html=True,
    )

    # Check if validation passed
    if not st.session_state.validation_result.get("valid"):
        st.error(
            "⚠️ Code validation failed. Fix errors before proceeding."
        )
        return

    # Display quality threshold status (if iterations were run)
    if st.session_state.iteration_history:
        current_score = st.session_state.iteration_history[-1].get("score", 0)
        threshold = 85
        
        if current_score >= threshold:
            st.success(
                f"✓ Quality threshold met! Score: {current_score}/{threshold}"
            )
        else:
            st.warning(
                f"⚠️ Score: {current_score}/{threshold} (Need {threshold - current_score} more points)"
            )

    # Approval request
    st.info(
        "👇 Review the draft above carefully before approving commit."
    )

    col1, col2 = st.columns(2)

    with col1:
        commit_msg = st.text_input(
            "Commit message:",
            value="Add AI-generated code",
            key="commit_msg_input",
        )

    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        approve_btn = st.button(
            "✅ Approve & Commit", type="primary", key="approve_btn"
        )

    if approve_btn:
        with st.spinner("Processing approval..."):
            # Stage changes
            approval_request = st.session_state.orchestrator.stage_for_approval(
                st.session_state.file_path,
                st.session_state.draft_code,
                commit_msg,
            )

            if approval_request["staging_success"]:
                st.success(f"✓ Staged: {st.session_state.file_path}")

                # Execute commit
                commit_result = st.session_state.orchestrator.execute_commit(
                    st.session_state.file_path,
                    st.session_state.draft_code,
                    commit_msg,
                )

                if commit_result["success"]:
                    st.success("✅ Commit successful!")
                    st.balloons()

                    # Display commit details
                    st.code(
                        f"""Branch: {commit_result['branch']}
File: {commit_result['file_path']}
Message: {commit_msg}
Timestamp: {commit_result['committed_at']}""",
                        language="text",
                    )

                    # Reset workflow
                    st.session_state.draft_code = None
                    st.session_state.current_plan = None
                    st.session_state.validation_result = None
                    st.session_state.review_result = None
                else:
                    st.error(f"❌ Commit failed: {commit_result['message']}")
            else:
                st.error(
                    f"❌ Staging failed: {approval_request['staging_message']}"
                )


def render_reject_section():
    """Render reject draft option"""
    if (
        not st.session_state.draft_code
        or st.session_state.approval_pending
    ):
        return

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("❌ Reject Draft"):
            st.session_state.draft_code = None
            st.session_state.current_plan = None
            st.session_state.validation_result = None
            st.session_state.review_result = None
            st.session_state.iteration_history = []
            st.session_state.threshold_met = False
            st.info("Draft rejected. Start a new task.")
            st.rerun()

    with col2:
        if st.button("🔄 Regenerate"):
            st.info("Regeneration feature coming soon!")


def render_sidebar():
    """Render sidebar with system information"""
    with st.sidebar:
        st.markdown("### 📊 System Status")

        orchestrator = st.session_state.orchestrator
        status = orchestrator.get_task_status()

        if status["status"] == "idle":
            st.info("No active task")
        else:
            st.write(f"**Task Step:** {status['current_step']}")
            st.write(f"**Plan:** {'✓' if status['plan_available'] else '✗'}")
            st.write(f"**Code:** {'✓' if status['code_available'] else '✗'}")
            st.write(
                f"**Validation:** {'✓' if status['validation_passed'] else '✗'}"
            )
            st.write(
                f"**Review:** {'✓' if status['review_complete'] else '✗'}"
            )

        st.markdown("---")
        st.markdown("### � Distributed System")
        
        dist_status = orchestrator.get_distributed_status()
        st.write(f"**Mode:** {'Enabled' if dist_status['distributed_mode_enabled'] else 'Disabled'}")
        st.write(f"**Total Executions:** {dist_status['execution_count']}")
        
        # Agent performance
        perf = dist_status.get("agent_performance", {})
        if perf:
            st.write("**Agent Success Rates:**")
            for agent, stats in perf.items():
                rate = f"{float(stats.get('success_rate', 0)):.0%}"
                st.write(f"  - {agent}: {rate}")

        # Evolution health summary
        st.markdown("### 🧩 Evolution Health")
        st.write(f"Autonomous Mode: {'ON' if st.session_state.autonomous_evolution_mode else 'OFF'}")
        st.write(f"Cycles Completed: {st.session_state.evolution_cycles_completed}")
        st.write(f"Current Status: {st.session_state.evolution_status}")
        if st.session_state.evolution_critic_report:
            critic = st.session_state.evolution_critic_report
            stability_report = critic.get('stability_report', {})
            arch = critic.get('architecture_suggestions', {})
            st.write(f"Stability: {'Stop' if stability_report.get('should_stop') else 'Continue'}")
            st.write(f"Architecture risk: {arch.get('risk_level', 'N/A')}")

        st.markdown("---")
        st.markdown("### 🔧 Configuration")

        kill = st.checkbox("🛑 Kill Switch", value=st.session_state.kill_switch, help="Stop autonomous evolution immediately")
        st.session_state.kill_switch = kill

        debug_mode = st.checkbox("Debug Mode", value=False)
        if debug_mode:
            st.markdown("**Debug Information:**")
            st.write(f"Repo Path: {orchestrator.repo_path}")
            st.write(f"Pending Changes: {len(orchestrator.github.pending_changes)}")
            
            if st.button("Show Distributed History"):
                history = orchestrator.get_distributed_history(limit=5)
                st.json(history)

        st.markdown("---")
        st.markdown("### 📚 About")
        st.write(
            """
        **Autonomous AI Developer System**
        **with Distributed Multi-Agent Execution**
        
        A production-grade system for:
        - 🎯 Task Planning
        - 💻 Code Generation (Single & Distributed)
        - 🔀 Parallel Agent Execution
        - ✓ Code Validation
        - 👥 Code Review
        - ✅ Safe Commit with Approval
        
        **Features:**
        - Single-agent pipeline (default)
        - Distributed multi-agent mode
        - Autonomous self-improvement
        - Task memory & learning
        - Conflict resolution
        
        **Safety First:** All commits require approval.
        """
        )


def main():
    """Main application function"""
    initialize_session_state()
    render_header()
    render_sidebar()

    # Main content area
    render_task_input()
    render_plan_display()
    render_code_display()
    render_validation_display()
    render_review_display()
    render_distributed_execution_display()
    render_evolution_dashboard()
    render_iteration_display()
    render_approval_section()
    render_reject_section()


if __name__ == "__main__":
    main()
