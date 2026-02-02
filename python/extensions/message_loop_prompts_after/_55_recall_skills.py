from python.helpers.extension import Extension
from agent import LoopData
from python.helpers import skills as skills_helper
from python.helpers import projects, frameworks


class RecallSkills(Extension):
    """
    Surface relevant SKILL.md-based Skills into the prompt (token-efficient).

    Uses lightweight lexical matching and injects a compact
    "relevant skills" list into extras for the current user message.
    """

    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        # Only on the first iteration of the message loop (new user instruction)
        if loop_data.iteration != 0:
            return

        # Determine query from current user message
        user_instruction = (
            loop_data.user_message.output_text() if loop_data.user_message else ""
        ).strip()
        if not user_instruction or len(user_instruction) < 8:
            return

        # Get active project + framework for scoped discovery
        project_name = (
            projects.get_context_project_name(self.agent.context)
            if self.agent.context
            else None
        )
        framework = frameworks.get_active_framework(self.agent.context)
        framework_id = framework.id if framework else None

        matches = skills_helper.search_skills(
            user_instruction,
            limit=6,
            project_name=project_name,
            framework_id=framework_id,
        )
        if not matches:
            return

        lines = []
        for s in matches:
            desc = (s.description or "").strip() or "(no description)"
            if len(desc) > 220:
                desc = desc[:220].rstrip() + "…"
            lines.append(f"- {s.name} [{s.source}]: {desc}")

        skills_block = "\n".join(lines)
        loop_data.extras_temporary["skills"] = self.agent.parse_prompt(
            "agent.system.skills.md", skills=skills_block
        )

