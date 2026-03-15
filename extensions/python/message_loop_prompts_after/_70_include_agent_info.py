from helpers.extension import Extension
from agent import LoopData


class IncludeAgentInfo(Extension):
    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        if not self.agent:
            return

        # read prompt
        from plugins._model_config.helpers.model_config import get_chat_model_config
        chat_cfg = get_chat_model_config(self.agent)

        # detect active preset
        override = self.agent.context.get_data("chat_model_override")
        preset_name = override.get("preset_name", "") if isinstance(override, dict) else ""

        agent_info_prompt = self.agent.read_prompt(
            "agent.extras.agent_info.md",
            number=self.agent.number,
            profile=self.agent.config.profile or "Default",
            llm=chat_cfg.get("provider", "") + "/" + chat_cfg.get("name", ""),
            preset=preset_name,
        )

        # add agent info to the prompt
        loop_data.extras_temporary["agent_info"] = agent_info_prompt
