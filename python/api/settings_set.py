from python.helpers.api import ApiHandler, Request, Response

from python.helpers import settings

from typing import Any


class SetSettings(ApiHandler):
    async def process(self, input: dict[Any, Any], request: Request) -> dict[Any, Any] | Response:
        # Convert SettingsOutput (sections/fields) into internal flat Settings,
        # persist it, then return the updated SettingsOutput back to the UI.
        internal = settings.convert_in(input)
        settings.set_settings(internal)
        return {"settings": settings.convert_out(settings.get_settings())}
