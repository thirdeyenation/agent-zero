from python.helpers.api import ApiHandler, Input, Output, Request, Response
from python.helpers import skills


def _coerce_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on")
    return bool(value)


class Skills(ApiHandler):
    async def process(self, input: Input, request: Request) -> Output:
        action = input.get("action", "")

        try:
            if action == "list":
                data = self.list_skills(input)
            elif action == "toggle":
                data = self.toggle_skill(input)
            elif action == "delete":
                data = self.delete_skill(input)
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

    def list_skills(self, input: Input):
        project_name = (input.get("project_name") or "").strip() or None
        profile_name = (input.get("profile_name") or "").strip() or None
        return skills.get_skills_list(
            project_name=project_name,
            profile_name=profile_name
        )

    def toggle_skill(self, input: Input):
        skill_id = str(input.get("skill_id") or "").strip()
        if not skill_id:
            raise Exception("skill_id is required")

        enabled = _coerce_bool(input.get("enabled", True))
        project_name = (input.get("project_name") or "").strip() or None
        profile_name = (input.get("profile_name") or "").strip() or None

        skills.set_skill_activation(
            skill_id,
            enabled=enabled,
            project_name=project_name,
            profile_name=profile_name,
        )
        return {"enabled": enabled}

    def delete_skill(self, input: Input):
        skill_id = str(input.get("skill_id") or "").strip()
        if not skill_id:
            raise Exception("skill_id is required")

        project_name = (input.get("project_name") or "").strip() or None
        profile_name = (input.get("profile_name") or "").strip() or None

        skills.delete_skill(
            skill_id,
            project_name=project_name,
            profile_name=profile_name,
        )
        return {"skill_id": skill_id}
