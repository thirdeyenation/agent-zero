from typing import Any

from helpers.extension import Extension, call_extensions_async
from agent import Agent, LoopData


class SecretsPrompt(Extension):

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
    try:
        from helpers.secrets import get_secrets_manager
        from helpers.settings import get_settings

        secrets_manager = get_secrets_manager(agent.context)
        secrets = secrets_manager.get_secrets_for_prompt()
        variables = get_settings()["variables"]
        prompt = agent.read_prompt(
            "agent.system.secrets.md", secrets=secrets, vars=variables
        )

        data: dict[str, Any] = {"prompt": prompt}
        await call_extensions_async("system_prompt_secrets", agent=agent, data=data)
        return data["prompt"]
    except Exception:
        return ""
