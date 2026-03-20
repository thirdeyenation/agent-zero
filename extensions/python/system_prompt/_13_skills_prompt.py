from typing import Any

from helpers.extension import Extension, call_extensions_async
from helpers import skills as skills_helper
from agent import Agent, LoopData


class SkillsPrompt(Extension):

    async def execute(
        self,
        system_prompt: list[str] = [],
        loop_data: LoopData = LoopData(),
        **kwargs: Any,
    ):
        if not self.agent:
            return
        prompt = await build_prompt(self.agent)
        if prompt:
            system_prompt.append(prompt)


async def build_prompt(agent: Agent) -> str:
    available = skills_helper.list_skills(agent=agent)
    result: list[str] = []
    for skill in available:
        name = skill.name.strip().replace("\n", " ")[:100]
        descr = skill.description.replace("\n", " ")[:500]
        result.append(f"**{name}** {descr}")

    if not result:
        return ""

    prompt = agent.read_prompt("agent.system.skills.md", skills="\n".join(result))

    data: dict[str, Any] = {"prompt": prompt}
    await call_extensions_async("system_prompt_skills", agent=agent, data=data)
    return data["prompt"]
