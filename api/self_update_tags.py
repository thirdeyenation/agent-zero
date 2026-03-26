from helpers.api import ApiHandler, Request, Response

from helpers import runtime
from helpers import self_update


class SelfUpdateTags(ApiHandler):
    async def process(self, input: dict, request: Request) -> dict | Response:
        branch = str(input.get("branch", "")).strip().lower()
        current_branch = self_update.get_repo_version_info().get("branch", "").strip().lower()
        default_branch = current_branch if current_branch in self_update.SUPPORTED_BRANCHES else "main"
        resolved_branch = branch or default_branch

        try:
            tags, higher_major_versions, error = self_update.get_selector_tag_options(
                resolved_branch,
            )
            return {
                "success": True,
                "supported": runtime.is_dockerized(),
                "branch": resolved_branch,
                "tags": tags,
                "higher_major_versions": higher_major_versions,
                "error": error,
            }
        except Exception as e:
            return {
                "success": False,
                "supported": runtime.is_dockerized(),
                "branch": resolved_branch,
                "tags": [],
                "higher_major_versions": [],
                "error": str(e),
            }
