"""Auto-send email reply when agent responds in an email session."""

import asyncio
from helpers.extension import Extension
from helpers.print_style import PrintStyle
from agent import AgentContext, LoopData
from plugins._email_integration.helpers.dispatcher import CTX_EMAIL_HANDLER, CTX_EMAIL_ATTACHMENTS


class EmailAutoReply(Extension):

    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        if not self.agent or self.agent.number != 0:
            return

        context = self.agent.context
        if not context.data.get(CTX_EMAIL_HANDLER):
            return

        response_text = _extract_last_response(context)
        if not response_text:
            return

        attachments = context.data.pop(CTX_EMAIL_ATTACHMENTS, [])
        if attachments:
            PrintStyle.info(f"Email: sending reply with {len(attachments)} attachment(s)")
        asyncio.create_task(self._send_reply(context, response_text, attachments))

    async def _send_reply(
        self, context: AgentContext, response_text: str, attachments: list[str],
    ):
        from plugins._email_integration.helpers.handler import send_email_reply
        await send_email_reply(context, response_text, attachments)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _extract_last_response(context: AgentContext) -> str:
    with context.log._lock:
        logs = list(context.log.logs)
    if not logs:
        return ""
    for item in reversed(logs):
        if item.type == "response":
            return item.content or ""
    return ""
