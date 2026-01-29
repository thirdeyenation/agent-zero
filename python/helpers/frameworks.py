"""
Development Framework Registry for Agent Zero.

This module defines the available development frameworks that can be used
to guide agent workflows. Each framework provides structured methodologies
for software development tasks.

Frameworks are selected globally in settings or overridden per-project.
When a framework is active, its skills are prioritized in skill discovery
and framework context is injected into the system prompt.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Literal, Optional

if TYPE_CHECKING:
    from agent import AgentContext

# Supported framework identifiers
FrameworkId = Literal[
    "none",
    "gsd",
    "superpowers",
    "bmad",
    "bmad-builder",
    "bmad-cis",
    "bmad-gds",
    "speckit",
    "prp",
    "agentos",
    "amplihack",
    "agent-zero-dev",
]

ALL_FRAMEWORK_IDS: List[str] = [
    "none",
    "gsd",
    "superpowers",
    "bmad",
    "bmad-builder",
    "bmad-cis",
    "bmad-gds",
    "speckit",
    "prp",
    "agentos",
    "amplihack",
    "agent-zero-dev",
]


@dataclass(slots=True)
class FrameworkWorkflow:
    """A single workflow step within a framework."""

    name: str  # e.g., "plan-phase"
    skill_name: str  # Maps to SKILL.md name, e.g., "gsd-plan-phase"
    description: str
    sequence: int  # Order in workflow (1-based)


@dataclass(slots=True)
class Framework:
    """A development framework definition."""

    id: FrameworkId
    name: str  # Display name
    description: str
    skill_prefix: str  # Namespace for skills, e.g., "gsd", "bmad"
    workflows: List[FrameworkWorkflow] = field(default_factory=list)


# ─────────────────────────────────────────────────────────────────────────────
# Framework Registry
# ─────────────────────────────────────────────────────────────────────────────

FRAMEWORK_REGISTRY: dict[str, Framework] = {
    "none": Framework(
        id="none",
        name="None",
        description="No development framework. Agent operates with standard skills only.",
        skill_prefix="",
        workflows=[],
    ),
    "gsd": Framework(
        id="gsd",
        name="GSD (Get Stuff Done)",
        description="A structured methodology emphasizing planning before implementation. Features clear phases: project setup, discussion, planning, execution, verification, and milestone completion.",
        skill_prefix="gsd",
        workflows=[
            FrameworkWorkflow(
                name="New Project",
                skill_name="gsd-new-project",
                description="Initialize project structure, requirements, and roadmap",
                sequence=1,
            ),
            FrameworkWorkflow(
                name="Discuss Phase",
                skill_name="gsd-discuss-phase",
                description="Capture implementation decisions and preferences before planning",
                sequence=2,
            ),
            FrameworkWorkflow(
                name="Plan Phase",
                skill_name="gsd-plan-phase",
                description="Research, create atomic task plans, and verify against requirements",
                sequence=3,
            ),
            FrameworkWorkflow(
                name="Execute Phase",
                skill_name="gsd-execute-phase",
                description="Run plans in parallel waves with fresh context per task",
                sequence=4,
            ),
            FrameworkWorkflow(
                name="Verify Work",
                skill_name="gsd-verify-work",
                description="Manual user acceptance testing with automatic fix generation",
                sequence=5,
            ),
            FrameworkWorkflow(
                name="Complete Milestone",
                skill_name="gsd-complete-milestone",
                description="Archive milestone, tag release, prepare for next iteration",
                sequence=6,
            ),
        ],
    ),
    "superpowers": Framework(
        id="superpowers",
        name="Superpowers",
        description="A comprehensive development workflow framework for Claude Code. Emphasizes TDD, brainstorming, planning, subagent execution, code review, and proper branch management.",
        skill_prefix="sp",
        workflows=[
            FrameworkWorkflow(
                name="Brainstorming",
                skill_name="sp-brainstorming",
                description="Socratic design refinement before writing code",
                sequence=1,
            ),
            FrameworkWorkflow(
                name="Git Worktrees",
                skill_name="sp-git-worktrees",
                description="Create isolated workspace on new branch for development",
                sequence=2,
            ),
            FrameworkWorkflow(
                name="Writing Plans",
                skill_name="sp-writing-plans",
                description="Break work into bite-sized tasks (2-5 min each) with verification",
                sequence=3,
            ),
            FrameworkWorkflow(
                name="Test-Driven Development",
                skill_name="sp-test-driven-development",
                description="RED-GREEN-REFACTOR: test first, minimal code, commit",
                sequence=4,
            ),
            FrameworkWorkflow(
                name="Executing Plans",
                skill_name="sp-executing-plans",
                description="Dispatch subagents per task with two-stage review",
                sequence=5,
            ),
            FrameworkWorkflow(
                name="Code Review",
                skill_name="sp-code-review",
                description="Review against plan, report issues by severity",
                sequence=6,
            ),
            FrameworkWorkflow(
                name="Finishing Branch",
                skill_name="sp-finishing-branch",
                description="Verify tests, merge/PR options, cleanup worktree",
                sequence=7,
            ),
        ],
    ),
    "bmad": Framework(
        id="bmad",
        name="BMAD (Business-Minded Agile Development)",
        description="A business-focused agile methodology with 21 specialized agents. Features two paths: Quick (spec→dev→review) for small tasks, Full (brief→PRD→arch→epics→sprint→stories) for complex projects.",
        skill_prefix="bmad",
        workflows=[
            FrameworkWorkflow(
                name="Quick Spec",
                skill_name="bmad-quick-spec",
                description="(Quick Path) Analyze codebase and produce tech-spec with stories",
                sequence=1,
            ),
            FrameworkWorkflow(
                name="Product Brief",
                skill_name="bmad-product-brief",
                description="(Full Path) Define problem, users, and MVP scope",
                sequence=2,
            ),
            FrameworkWorkflow(
                name="Create PRD",
                skill_name="bmad-create-prd",
                description="Full requirements with personas, metrics, and risks",
                sequence=3,
            ),
            FrameworkWorkflow(
                name="Architecture",
                skill_name="bmad-create-architecture",
                description="Technical decisions and system design",
                sequence=4,
            ),
            FrameworkWorkflow(
                name="Create Epics",
                skill_name="bmad-create-epics",
                description="Break work into prioritized epics and stories",
                sequence=5,
            ),
            FrameworkWorkflow(
                name="Sprint Planning",
                skill_name="bmad-sprint-planning",
                description="Initialize sprint tracking and story selection",
                sequence=6,
            ),
            FrameworkWorkflow(
                name="Developer Story",
                skill_name="bmad-dev-story",
                description="Implement individual stories with guidance",
                sequence=7,
            ),
            FrameworkWorkflow(
                name="Code Review",
                skill_name="bmad-code-review",
                description="Validate quality and completeness",
                sequence=8,
            ),
        ],
    ),
    "bmad-builder": Framework(
        id="bmad-builder",
        name="BMad Builder",
        description="Meta-module for creating custom BMad agents, workflows, and domain-specific modules. Build specialized AI agents with custom expertise, structured workflows, and shareable module packages.",
        skill_prefix="bmb",
        workflows=[
            FrameworkWorkflow(
                name="Build Agent",
                skill_name="bmb-agent",
                description="Create specialized AI agents with custom expertise and tools",
                sequence=1,
            ),
            FrameworkWorkflow(
                name="Build Workflow",
                skill_name="bmb-workflow",
                description="Design structured workflows with steps and cross-workflow communication",
                sequence=2,
            ),
            FrameworkWorkflow(
                name="Build Module",
                skill_name="bmb-module",
                description="Package agents and workflows into shareable BMad modules",
                sequence=3,
            ),
        ],
    ),
    "bmad-cis": Framework(
        id="bmad-cis",
        name="BMad Creative Intelligence Suite",
        description="Tools for the fuzzy front-end of development—where ideas are born, problems are reframed, and solutions emerge through structured creativity. Features innovation, design thinking, and brainstorming workflows.",
        skill_prefix="cis",
        workflows=[
            FrameworkWorkflow(
                name="Brainstorm",
                skill_name="cis-brainstorm",
                description="Generate ideas with structured techniques (SCAMPER, Reverse Brainstorming)",
                sequence=1,
            ),
            FrameworkWorkflow(
                name="Design Thinking",
                skill_name="cis-design-thinking",
                description="Human-centered design through empathy, ideation, and prototyping",
                sequence=2,
            ),
            FrameworkWorkflow(
                name="Problem Solve",
                skill_name="cis-problem-solve",
                description="Systematic problem diagnosis and root cause analysis",
                sequence=3,
            ),
            FrameworkWorkflow(
                name="Innovation",
                skill_name="cis-innovation",
                description="Business model innovation and disruption opportunity analysis",
                sequence=4,
            ),
            FrameworkWorkflow(
                name="Storytelling",
                skill_name="cis-storytelling",
                description="Craft compelling narratives for products and features",
                sequence=5,
            ),
            FrameworkWorkflow(
                name="Presentation",
                skill_name="cis-presentation",
                description="Structure and deliver persuasive presentations",
                sequence=6,
            ),
        ],
    ),
    "bmad-gds": Framework(
        id="bmad-gds",
        name="BMad Game Dev Studio",
        description="Six specialized game development agents: Game Designer (Samus Shepard), Game Architect (Cloud Dragonborn), Game Developer (Link Freeman), Game Scrum Master (Max), Game QA (GLaDOS), and Game Solo Dev (Indie). Two paths: Full (brief→GDD→arch→sprint→stories) for team projects, Quick Flow for solo/indie dev.",
        skill_prefix="gds",
        workflows=[
            FrameworkWorkflow(
                name="Brainstorm Game",
                skill_name="gds-brainstorm-game",
                description="Guided game ideation with Game Designer (Samus Shepard)",
                sequence=1,
            ),
            FrameworkWorkflow(
                name="Create Game Brief",
                skill_name="gds-create-brief",
                description="Define game vision, core loop, and target experience",
                sequence=2,
            ),
            FrameworkWorkflow(
                name="Create GDD",
                skill_name="gds-create-gdd",
                description="Full Game Design Document with mechanics and systems",
                sequence=3,
            ),
            FrameworkWorkflow(
                name="Game Architecture",
                skill_name="gds-create-architecture",
                description="Technical architecture with Game Architect (Cloud Dragonborn)",
                sequence=4,
            ),
            FrameworkWorkflow(
                name="Sprint Planning",
                skill_name="gds-sprint-planning",
                description="Plan sprints with Game Scrum Master (Max)",
                sequence=5,
            ),
            FrameworkWorkflow(
                name="Dev Story",
                skill_name="gds-dev-story",
                description="Implement stories with Game Developer (Link Freeman)",
                sequence=6,
            ),
            FrameworkWorkflow(
                name="QA Framework",
                skill_name="gds-qa-framework",
                description="Set up testing with Game QA (GLaDOS)",
                sequence=7,
            ),
            FrameworkWorkflow(
                name="Quick Flow",
                skill_name="gds-quick-flow",
                description="Solo dev fast path with Game Solo Dev (Indie)",
                sequence=8,
            ),
        ],
    ),
    "speckit": Framework(
        id="speckit",
        name="Spec Kit",
        description="A specification-driven approach emphasizing upfront clarity. Starts with constitution definition, progresses through specification, planning, task generation, and implementation.",
        skill_prefix="speckit",
        workflows=[
            FrameworkWorkflow(
                name="Constitution",
                skill_name="speckit-constitution",
                description="Define project principles and constraints",
                sequence=1,
            ),
            FrameworkWorkflow(
                name="Specify",
                skill_name="speckit-specify",
                description="Create detailed specifications",
                sequence=2,
            ),
            FrameworkWorkflow(
                name="Plan",
                skill_name="speckit-plan",
                description="Generate implementation roadmap from specs",
                sequence=3,
            ),
            FrameworkWorkflow(
                name="Tasks",
                skill_name="speckit-tasks",
                description="Break plan into actionable tasks",
                sequence=4,
            ),
            FrameworkWorkflow(
                name="Implement",
                skill_name="speckit-implement",
                description="Execute tasks following specifications",
                sequence=5,
            ),
        ],
    ),
    "prp": Framework(
        id="prp",
        name="PRP (Prompt-Response Protocol)",
        description="A lightweight two-phase methodology: generate comprehensive PRPs (prompts) for tasks, then execute them. Ideal for well-defined, repeatable tasks.",
        skill_prefix="prp",
        workflows=[
            FrameworkWorkflow(
                name="Generate PRP",
                skill_name="prp-generate",
                description="Create detailed prompt specification for task",
                sequence=1,
            ),
            FrameworkWorkflow(
                name="Execute PRP",
                skill_name="prp-execute",
                description="Execute the generated prompt systematically",
                sequence=2,
            ),
        ],
    ),
    "agentos": Framework(
        id="agentos",
        name="AgentOS",
        description="A standards-based framework focusing on project initialization and adherence to coding standards. Emphasizes consistent project structure and quality gates.",
        skill_prefix="agentos",
        workflows=[
            FrameworkWorkflow(
                name="Project Install",
                skill_name="agentos-project-install",
                description="Initialize project with standard structure",
                sequence=1,
            ),
            FrameworkWorkflow(
                name="Standards",
                skill_name="agentos-standards",
                description="Apply and verify coding standards",
                sequence=2,
            ),
        ],
    ),
    "amplihack": Framework(
        id="amplihack",
        name="AMPLIHACK",
        description="A multi-agent orchestration framework with specialized agents. Features auto workflow selection, analysis, cascade patterns, debate workflows, fix workflows, and modular building.",
        skill_prefix="amplihack",
        workflows=[
            FrameworkWorkflow(
                name="Auto",
                skill_name="amplihack-auto",
                description="Automatic workflow selection based on task complexity",
                sequence=1,
            ),
            FrameworkWorkflow(
                name="Analyze",
                skill_name="amplihack-analyze",
                description="Deep code/requirements analysis with multiple perspectives",
                sequence=2,
            ),
            FrameworkWorkflow(
                name="Cascade",
                skill_name="amplihack-cascade",
                description="Sequential multi-agent processing for complex tasks",
                sequence=3,
            ),
            FrameworkWorkflow(
                name="Debate",
                skill_name="amplihack-debate",
                description="Multi-perspective debate for technical decisions",
                sequence=4,
            ),
            FrameworkWorkflow(
                name="Fix",
                skill_name="amplihack-fix",
                description="Systematic error resolution with pattern-specific context",
                sequence=5,
            ),
            FrameworkWorkflow(
                name="Modular Build",
                skill_name="amplihack-modular-build",
                description="Build code following brick philosophy with modules",
                sequence=6,
            ),
        ],
    ),
    "agent-zero-dev": Framework(
        id="agent-zero-dev",
        name="Agent Zero Dev",
        description="Development framework for extending and building features for Agent Zero. Provides patterns, templates, and code generators for creating tools, extensions, skills, API endpoints, subordinate profiles, and project configurations.",
        skill_prefix="a0dev",
        workflows=[
            FrameworkWorkflow(
                name="Quickstart",
                skill_name="a0dev-quickstart",
                description="5-minute guide to extending Agent Zero",
                sequence=1,
            ),
            FrameworkWorkflow(
                name="Create Tool",
                skill_name="a0dev-create-tool",
                description="Create new agent capabilities (tools)",
                sequence=2,
            ),
            FrameworkWorkflow(
                name="Create Extension",
                skill_name="a0dev-create-extension",
                description="Hook into agent lifecycle events",
                sequence=3,
            ),
            FrameworkWorkflow(
                name="Create Skill",
                skill_name="a0dev-create-skill",
                description="Build reusable instruction bundles (SKILL.md)",
                sequence=4,
            ),
            FrameworkWorkflow(
                name="Create API",
                skill_name="a0dev-create-api",
                description="Add Web UI / REST API endpoints",
                sequence=5,
            ),
            FrameworkWorkflow(
                name="Create Subordinate",
                skill_name="a0dev-create-subordinate",
                description="Create specialized agent profiles",
                sequence=6,
            ),
            FrameworkWorkflow(
                name="Create Project",
                skill_name="a0dev-create-project",
                description="Set up project-specific configuration",
                sequence=7,
            ),
            FrameworkWorkflow(
                name="Dev Workflow",
                skill_name="a0dev-workflow",
                description="Full Agent Zero development workflow",
                sequence=8,
            ),
        ],
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────


def get_framework(framework_id: str) -> Optional[Framework]:
    """
    Get a framework by its ID.

    Args:
        framework_id: The framework identifier (e.g., "gsd", "bmad")

    Returns:
        Framework object if found, None otherwise
    """
    return FRAMEWORK_REGISTRY.get(framework_id)


def list_frameworks() -> List[Framework]:
    """
    List all available frameworks.

    Returns:
        List of all Framework objects in registry order
    """
    return [FRAMEWORK_REGISTRY[fid] for fid in ALL_FRAMEWORK_IDS if fid in FRAMEWORK_REGISTRY]


def get_active_framework(context: "AgentContext") -> Optional[Framework]:
    """
    Get the active framework for an agent context.

    Priority:
    1. Project-level override (if project has dev_framework set)
    2. Global setting (settings.dev_framework)
    3. None (no framework active)

    Args:
        context: The agent context

    Returns:
        Active Framework object, or None if "none" is selected
    """
    from python.helpers import projects
    from python.helpers.settings import get_settings

    framework_id: str = "none"

    # Check project-level override first
    project_name = projects.get_context_project_name(context)
    if project_name:
        try:
            project_data = projects.load_basic_project_data(project_name)
            project_fw = project_data.get("dev_framework", "")
            if project_fw and project_fw != "":
                framework_id = project_fw
        except Exception:
            pass

    # Fall back to global setting
    if framework_id == "none" or not framework_id:
        settings = get_settings()
        framework_id = settings.get("dev_framework", "none")

    if framework_id == "none" or not framework_id:
        return None

    return get_framework(framework_id)


def get_framework_options() -> List[dict]:
    """
    Get framework options formatted for settings UI select field.

    Returns:
        List of dicts with 'value' and 'label' keys
    """
    return [
        {"value": fw.id, "label": fw.name}
        for fw in list_frameworks()
    ]
