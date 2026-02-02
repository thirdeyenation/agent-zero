from dataclasses import asdict
from python.helpers.api import ApiHandler, Input, Output, Request
from python.helpers import frameworks


class Frameworks(ApiHandler):
    """API handler for framework operations."""

    async def process(self, input: Input, request: Request) -> Output:
        action = input.get("action", "list")
        try:
            if action == "list":
                return {"ok": True, "data": self.list_frameworks()}
            if action == "get":
                framework_id = input.get("id", "")
                data = self.get_framework(framework_id)
                if data is None:
                    return {"ok": False, "error": "Framework not found"}
                return {"ok": True, "data": data}
            return {"ok": False, "error": "Invalid action"}
        except Exception:
            return {"ok": False, "error": "Internal error"}

    def list_frameworks(self) -> list[dict]:
        """List all available frameworks."""
        return [asdict(fw) for fw in frameworks.list_frameworks()]

    def get_framework(self, framework_id: str) -> dict | None:
        """Get a specific framework by ID."""
        fw = frameworks.get_framework(framework_id)
        if fw is None:
            return None
        return asdict(fw)
