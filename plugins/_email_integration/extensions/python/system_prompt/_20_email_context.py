from helpers.extension import Extension
from agent import LoopData
from plugins._email_integration.helpers.dispatcher import CTX_EMAIL_HANDLER


class EmailContextPrompt(Extension):

    async def execute(
        self,
        system_prompt: list[str] = [],
        loop_data: LoopData = LoopData(),
        **kwargs,
    ):
        if not self.agent:
            return

        # Only inject email conversation context if this chat was started by email
        if self.agent.context.data.get(CTX_EMAIL_HANDLER):
            prompt = self.agent.read_prompt("fw.email.system_context_reply.md")
            system_prompt.append(prompt)
