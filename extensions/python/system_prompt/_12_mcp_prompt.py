from typing import Any

from helpers.extension import Extension, call_extensions_async
from helpers.mcp_handler import MCPConfig
from agent import Agent, LoopData


class MCPToolsPrompt(Extension):

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
    mcp_config = MCPConfig.get_instance()
    if not mcp_config.servers:
        return ""

    pre_progress = agent.context.log.progress
    agent.context.log.set_progress("Collecting MCP tools")
    tools = mcp_config.get_tools_prompt()
    agent.context.log.set_progress(pre_progress)

    data: dict[str, Any] = {"prompt": tools}
    await call_extensions_async("system_prompt_mcp", agent=agent, data=data)
    return data["prompt"]
