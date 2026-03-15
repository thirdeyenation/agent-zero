"""Intercept response tool to capture email attachments."""

from helpers.extension import Extension
from helpers.print_style import PrintStyle
from plugins._email_integration.helpers.dispatcher import CTX_EMAIL_HANDLER, CTX_EMAIL_ATTACHMENTS


class EmailResponseAttachments(Extension):

    async def execute(self, tool_name: str = "", **kwargs):
        if tool_name != "response":
            return
        if not self.agent:
            return
        if not self.agent.context.data.get(CTX_EMAIL_HANDLER):
            return

        tool = self.agent.loop_data.current_tool
        if not tool:
            return

        attachments = tool.args.get("attachments", [])
        if attachments:
            self.agent.context.data[CTX_EMAIL_ATTACHMENTS] = attachments
            PrintStyle.info(f"Email: queued {len(attachments)} attachment(s)")
