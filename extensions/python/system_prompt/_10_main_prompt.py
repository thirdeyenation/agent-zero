from typing import Any

from helpers.extension import Extension, call_extensions_async
from agent import Agent, LoopData


class MainPrompt(Extension):

    async def execute(
        self,
        system_prompt: list[str] = [],
        loop_data: LoopData = LoopData(),
        **kwargs: Any,
    ):
        if not self.agent:
            return
        prompt = await build_prompt(self.agent)
        system_prompt.append(prompt)


async def build_prompt(agent: Agent) -> str:
    data: dict[str, Any] = {"prompt": agent.read_prompt("agent.system.main.md")}
    await call_extensions_async("system_prompt_main", agent=agent, data=data)
    return data["prompt"]
