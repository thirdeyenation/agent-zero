from helpers.extension import Extension
from agent import LoopData
from plugins._telegram_integration.helpers.handler import CTX_TG_BOT


class TelegramContextPrompt(Extension):

    async def execute(
        self,
        system_prompt: list[str] = [],
        loop_data: LoopData = LoopData(),
        **kwargs,
    ):
        if not self.agent:
            return

        if self.agent.context.data.get(CTX_TG_BOT):
            system_prompt.append(
                self.agent.read_prompt("fw.telegram.system_context_reply.md")
            )
