from python.helpers.extension import Extension
from agent import LoopData


DATA_NAME_LOADED_SKILL = "loaded_skill"


class IncludeLoadedSkills(Extension):
    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        extras = loop_data.extras_persistent

        # Clear previous
        if "loaded_skills" in extras:
            del extras["loaded_skills"]

        # Get single loaded skill
        skill_data = self.agent.data.get(DATA_NAME_LOADED_SKILL)
        if not skill_data or not isinstance(skill_data, dict):
            return

        content = str(skill_data.get("content") or "").strip()
        if not content:
            return

        # Inject into extras
        extras["loaded_skills"] = self.agent.read_prompt(
            "agent.system.skills.loaded.md",
            skills=content,
        )
