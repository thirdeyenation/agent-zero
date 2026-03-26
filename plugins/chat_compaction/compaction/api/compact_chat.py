"""API handler for chat compaction."""
import importlib
from helpers.api import ApiHandler, Input, Output, Request, Response
from agent import AgentContext


class CompactChat(ApiHandler):
    """Compact the current chat history into a summarized message."""

    async def process(self, input: Input, request: Request) -> Output:
        ctxid = input.get("context", "")
        action = input.get("action", "compact")

        if not ctxid:
            return Response("Missing context id", 400)

        context = AgentContext.get(ctxid)
        if not context:
            return Response("Context not found", 404)

        # Validate context is not running
        if context.is_running():
            return Response("Cannot compact while agent is running", 409)

        # Check if there's enough content to compact
        # Count user-visible log items (what the user sees in the UI)
        visible_count = len(context.log.logs)
        if visible_count <= 1:
            return Response("Not enough messages to compact", 400)

        # Force reload compactor module to pick up latest changes
        import usr.plugins.compaction.helpers.compactor as _compactor_mod
        importlib.reload(_compactor_mod)

        if action == "stats":
            # Return statistics for confirmation modal
            stats = await _compactor_mod.get_compaction_stats(context)
            return {"ok": True, "stats": stats}

        elif action == "compact":
            # Get plugin config for model choice
            from helpers.plugins import get_plugin_config
            agent = context.agent0
            plugin_config = get_plugin_config("compaction", agent=agent) or {}
            use_chat_model = plugin_config.get("use_chat_model", True)

            # Start compaction as a deferred task
            context.run_task(_run_compaction_task, context, use_chat_model)

            return {"ok": True, "message": "Compaction started"}

        else:
            return Response(f"Unknown action: {action}", 400)


async def _run_compaction_task(context, use_chat_model: bool):
    """Wrapper to run compaction and handle errors."""
    try:
        import importlib
        import usr.plugins.compaction.helpers.compactor as _compactor_mod
        importlib.reload(_compactor_mod)
        await _compactor_mod.run_compaction(context, use_chat_model)
    except Exception as e:
        # Log error but don't crash the task
        context.log.log(
            type="error",
            heading="Compaction Failed",
            content=str(e),
        )
        from helpers.state_monitor_integration import mark_dirty_all
        mark_dirty_all(reason="plugins.compaction.compact_chat_error")
