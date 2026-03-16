"""Send progress email without ending the agent loop."""

from helpers.tool import Tool, Response
from plugins._email_integration.helpers.dispatcher import CTX_EMAIL_HANDLER


class EmailUpdate(Tool):

    async def execute(self, **kwargs) -> Response:
        if not self.agent.context.data.get(CTX_EMAIL_HANDLER):
            return Response(
                message=self.agent.read_prompt(
                    "fw.email.update_error.md",
                    error="not in an email session"),
                break_loop=False,
            )

        text = self.args.get("text", "")
        if not text:
            return Response(
                message=self.agent.read_prompt(
                    "fw.email.update_error.md",
                    error="text is required",
                ),
                break_loop=False,
            )

        attachments = list(self.args.get("attachments", []))

        from plugins._email_integration.helpers.handler import send_email_reply
        error = await send_email_reply(self.agent.context, text, attachments or None)

        if error:
            return Response(
                message=self.agent.read_prompt(
                    "fw.email.update_error.md", error=error,
                ),
                break_loop=False,
            )

        return Response(
            message=self.agent.read_prompt("fw.email.update_ok.md"),
            break_loop=False,
        )
