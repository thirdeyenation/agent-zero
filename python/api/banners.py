from python.helpers.api import ApiHandler, Request, Response
from python.helpers.extension import Extension
from python.helpers import files, extract_tools


class GetBanners(ApiHandler):
    """
    API endpoint for Welcome Screen banners.
    Add checks as extension scripts in python/extensions/banners/ or usr/extensions/banners/
    """

    async def process(self, input: dict, request: Request) -> dict | Response:
        frontend_banners = input.get("banners", [])
        frontend_context = input.get("context", {})
        backend_banners = await self._run_banner_extensions(frontend_context, frontend_banners)
        return {"banners": backend_banners}

    async def _run_banner_extensions(self, context: dict, frontend_banners: list) -> list[dict]:
        """Run all banner checks via extension point system."""
        banners = []
        for cls in self._get_banner_extensions():
            try:
                result = await cls(agent=None).execute(context=context, frontend_banners=frontend_banners)
                if result:
                    banners.extend(result if isinstance(result, list) else [result])
            except Exception as e:
                print(f"Banner check failed ({cls.__name__}): {e}")
        return banners

    def _get_banner_extensions(self) -> list[type[Extension]]:
        """Load banner extension classes from extensions folders."""
        all_exts = []
        for path in ["python/extensions/banners", "usr/extensions/banners"]:
            abs_path = files.get_abs_path(path)
            if files.exists(abs_path):
                all_exts.extend(extract_tools.load_classes_from_folder(abs_path, "*", Extension))
        
        # Deduplicate by filename (usr overrides default), sort by name
        unique = {}
        for cls in all_exts:
            file = cls.__module__.split(".")[-1]
            if file not in unique:
                unique[file] = cls
        return sorted(unique.values(), key=lambda c: c.__module__.split(".")[-1])

    @classmethod
    def get_methods(cls) -> list[str]:
        return ["POST"]
