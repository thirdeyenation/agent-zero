from helpers.api import ApiHandler, Request, Response
from helpers import plugins
from plugins._model_config.helpers import model_config


class ModelPresets(ApiHandler):
    async def process(self, input: dict, request: Request) -> dict | Response:
        action = input.get("action", "get")
        project_name = input.get("project_name", "")
        agent_profile = input.get("agent_profile", "")

        if action == "get":
            presets = model_config.get_presets(
                project_name=project_name or None,
                agent_profile=agent_profile or None,
            )
            return {"ok": True, "presets": presets}

        elif action == "save":
            presets = input.get("presets")
            if not isinstance(presets, list):
                return Response(status=400, response="presets must be an array")

            # Load current config, update presets, save
            cfg = model_config.get_config(
                project_name=project_name or None,
                agent_profile=agent_profile or None,
            )
            if not cfg:
                cfg = plugins.get_default_plugin_config("_model_config") or {}

            cfg["model_presets"] = presets
            plugins.save_plugin_config(
                "_model_config", project_name, agent_profile, cfg
            )
            return {"ok": True, "presets": presets}

        return Response(status=400, response=f"Unknown action: {action}")
