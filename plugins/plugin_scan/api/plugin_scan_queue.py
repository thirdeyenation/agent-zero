from agent import AgentContext
from python.helpers.api import ApiHandler, Input, Output, Request, Response


class PluginScanQueue(ApiHandler):
    """Set progress to 'Queued' without starting the agent or logging the prompt."""

    async def process(self, input: Input, request: Request) -> Output:
        ctxid: str = input.get("context", "")

        if not ctxid:
            return Response("Missing 'context'.", 400)

        context = AgentContext.get(ctxid)
        if context is None:
            return Response(f"Context {ctxid} not found.", 404)

        context.log.set_progress("icon://hourglass_empty Queued - waiting for another scan to finish", 0, True)

        return {"ok": True, "context": ctxid}
