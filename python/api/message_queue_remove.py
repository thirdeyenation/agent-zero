from python.helpers.api import ApiHandler, Request, Response
from python.helpers import message_queue as mq
from agent import AgentContext


class MessageQueueRemove(ApiHandler):
    """Remove message(s) from queue."""

    async def process(self, input: dict, request: Request) -> dict | Response:
        context = AgentContext.get(input.get("context", ""))
        if not context:
            return Response("Context not found", status=404)

        item_id = input.get("item_id")  # None means clear all
        remaining = mq.remove(context, item_id)
        return {"ok": True, "remaining": remaining}
