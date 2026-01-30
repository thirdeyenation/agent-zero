from python.helpers.api import ApiHandler, Request, Response
from python.helpers import message_queue as mq
from agent import AgentContext


class MessageQueueAdd(ApiHandler):
    """Add a message to the queue."""

    async def process(self, input: dict, request: Request) -> dict | Response:
        context = AgentContext.get(input.get("context", ""))
        if not context:
            return Response("Context not found", status=404)

        text = input.get("text", "").strip()
        attachments = input.get("attachments", [])  # filenames from /upload API

        if not text and not attachments:
            return Response("Empty message", status=400)

        item = mq.add(context, text, attachments)
        return {"ok": True, "item_id": item["id"], "queue_length": len(mq.get_queue(context))}
