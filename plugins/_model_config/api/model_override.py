from helpers.api import ApiHandler, Request, Response
from helpers.persist_chat import save_tmp_chat
from agent import AgentContext
from plugins._model_config.helpers import model_config


def _sync_override_to_project(ctx: AgentContext, override_value) -> int:
    """Apply the same override to all other contexts sharing the same project.
    Returns the number of synced contexts."""
    current_project = ctx.get_data("project")  # str or None
    synced = 0
    for other in AgentContext.all():
        if other.id == ctx.id:
            continue
        if other.get_data("project") == current_project:
            other.set_data("chat_model_override", override_value)
            save_tmp_chat(other)
            synced += 1
    if synced:
        from helpers.state_monitor_integration import mark_dirty_all
        mark_dirty_all(reason="model_override.sync_project")
    return synced


class ModelOverride(ApiHandler):
    async def process(self, input: dict, request: Request) -> dict | Response:
        context_id = input.get("context_id", "")
        action = input.get("action", "get")  # get | set | set_preset | clear

        if not context_id:
            return Response(status=400, response="Missing context_id")

        ctx = AgentContext.get(context_id)
        if not ctx:
            return Response(status=404, response="Context not found")

        if action == "get":
            override = ctx.get_data("chat_model_override")
            allowed = model_config.is_chat_override_allowed(ctx.agent0)
            return {"override": override, "allowed": allowed}

        elif action == "set":
            if not model_config.is_chat_override_allowed(ctx.agent0):
                return Response(status=403, response="Per-chat override is disabled")
            override_config = input.get("override")
            if not override_config or not isinstance(override_config, dict):
                return Response(status=400, response="Missing or invalid override config")
            ctx.set_data("chat_model_override", override_config)
            save_tmp_chat(ctx)
            synced = _sync_override_to_project(ctx, override_config)
            return {"ok": True, "override": override_config, "synced_count": synced}

        elif action == "set_preset":
            if not model_config.is_chat_override_allowed(ctx.agent0):
                return Response(status=403, response="Per-chat override is disabled")
            preset_name = input.get("preset_name", "")
            if not preset_name:
                return Response(status=400, response="Missing preset_name")
            # Verify preset exists
            preset = model_config.get_preset_by_name(preset_name)
            if not preset:
                return Response(status=404, response=f"Preset '{preset_name}' not found")
            # Store as a preset reference
            override_value = {"preset_name": preset_name}
            ctx.set_data("chat_model_override", override_value)
            save_tmp_chat(ctx)
            synced = _sync_override_to_project(ctx, override_value)
            return {"ok": True, "preset_name": preset_name, "synced_count": synced}

        elif action == "clear":
            ctx.set_data("chat_model_override", None)
            save_tmp_chat(ctx)
            synced = _sync_override_to_project(ctx, None)
            return {"ok": True, "override": None, "synced_count": synced}

        return Response(status=400, response=f"Unknown action: {action}")
