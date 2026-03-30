import json
from pathlib import Path
from helpers.api import ApiHandler, Request, Response

CSS_STORE_PATH = Path("usr/plugins/cosmetic_committee/current_theme.css")

class GetCssHandler(ApiHandler):
    async def process(self, input: dict, request: Request) -> dict | Response:
        css_content = ""
        if CSS_STORE_PATH.exists():
            with open(CSS_STORE_PATH, "r") as f:
                css_content = f.read()

        return {"ok": True, "css": css_content}
