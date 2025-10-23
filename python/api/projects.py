from python.helpers.api import ApiHandler, Input, Output, Request, Response
from python.helpers import projects


class Projects(ApiHandler):
    async def process(self, input: Input, request: Request) -> Output:
        action = input.get("action", "")

        try:
            if action == "list":
                data = self.get_projects_list()
            else:
                raise Exception("Invalid action")

            return {
                "ok": True,
                "data": data,
            }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
            }

    async def get_projects_list(self):
        return await projects.get_projects_list()
