import httpx
from helpers.api import ApiHandler, Request, Response
from helpers.providers import get_provider_config
import models

_CLOUD_ENDPOINTS: dict[str, str] = {
    "openai":     "https://api.openai.com/v1/models",
    "anthropic":  "https://api.anthropic.com/v1/models",
    "groq":       "https://api.groq.com/openai/v1/models",
    "deepseek":   "https://api.deepseek.com/models",
    "mistral":    "https://api.mistral.ai/v1/models",
    "openrouter": "https://openrouter.ai/api/v1/models",
    "xai":        "https://api.x.ai/v1/models",
    "sambanova":  "https://api.sambanova.ai/v1/models",
    "moonshot":   "https://api.moonshot.cn/v1/models",
    "google":     "https://generativelanguage.googleapis.com/v1beta/models",
    "a0_venice":  "https://api.venice.ai/api/v1/models",
    "venice":     "https://api.venice.ai/api/v1/models",
}

# Local providers with default base URLs (no auth required).
_LOCAL_DEFAULTS: dict[str, str] = {
    "ollama":    "http://host.docker.internal:11434",
    "lm_studio": "http://host.docker.internal:1234",
}

# Providers with hardcoded model lists (no listing API available).
_STATIC_MODELS: dict[str, list[str]] = {
    "github_copilot": [
        "gpt-4.1", "gpt-4o", "gpt-5-mini", "oswe-vscode-prime",
    ],
    "zai": [
        "glm-4-plus", "glm-4-air-250414", "glm-4-airx",
        "glm-4-long", "glm-4-flashx", "glm-4-flash-250414",
        "glm-4v-plus", "glm-4v", "glm-3-turbo",
    ],
    "zai_coding": [
        "codegeex-4",
        "glm-4-plus", "glm-4-air-250414", "glm-4-airx",
        "glm-4-flashx", "glm-4-flash-250414",
    ],
}

# Model name substrings to exclude from litellm fallback results
_LITELLM_EXCLUDE = frozenset({
    "dall-e", "gpt-image", "tts", "whisper", "audio",
    "realtime", "davinci", "babbage", "ada", "vision-preview",
})


class ModelSearch(ApiHandler):
    async def process(self, input: dict, request: Request) -> dict | Response:
        provider = input.get("provider", "")
        query = input.get("query", "").lower()
        model_type = input.get("model_type", "chat")
        user_api_base = input.get("api_base", "")

        if not provider:
            return {"models": []}

        if provider in _STATIC_MODELS:
            all_models = list(_STATIC_MODELS[provider])
        else:
            provider_cfg = get_provider_config(model_type, provider)
            all_models = await self._fetch_models(provider, provider_cfg, user_api_base) or []

            if not all_models:
                litellm_provider = (provider_cfg or {}).get("litellm_provider", provider)
                if litellm_provider == provider:
                    all_models = self._litellm_fallback(provider, provider_cfg)

        if query:
            all_models = [m for m in all_models if query in m.lower()]

        return {"models": sorted(all_models)[:50], "provider": provider}

    async def _fetch_models(self, provider: str, cfg: dict | None, user_api_base: str = "") -> list[str] | None:
        api_base = user_api_base or (cfg or {}).get("kwargs", {}).get("api_base", "")
        api_key = models.get_api_key(provider)

        url, fmt = self._resolve_url(provider, api_base)
        if not url:
            return None

        headers = self._build_headers(provider, api_key, cfg)
        params: dict[str, str] = {}
        if provider == "google":
            if api_key and api_key != "None":
                params["key"] = api_key
            params["pageSize"] = "1000"
        elif provider == "anthropic":
            params["limit"] = "1000"
        elif provider == "azure":
            params["api-version"] = "2024-10-21"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers, params=params)
                if resp.status_code == 200:
                    result = self._parse(resp.json(), fmt)
                    if result:
                        return result
        except Exception:
            pass

        return None

    def _resolve_url(self, provider: str, api_base: str) -> tuple[str | None, str]:
        if provider == "ollama":
            base = api_base or _LOCAL_DEFAULTS.get("ollama", "")
            return (base.rstrip("/") + "/api/tags" if base else None), "ollama"

        if provider == "google":
            if api_base:
                return api_base.rstrip("/") + "/models", "google"
            return _CLOUD_ENDPOINTS["google"], "google"

        if provider == "azure":
            if not api_base:
                return None, "openai"
            return api_base.rstrip("/") + "/openai/models", "openai"

        if provider in _CLOUD_ENDPOINTS:
            return _CLOUD_ENDPOINTS[provider], "openai"

        if api_base:
            return api_base.rstrip("/") + "/models", "openai"

        if provider in _LOCAL_DEFAULTS:
            return _LOCAL_DEFAULTS[provider] + "/v1/models", "openai"

        return None, "openai"

    def _build_headers(self, provider: str, api_key: str, cfg: dict | None) -> dict[str, str]:
        headers: dict[str, str] = {}
        has_key = api_key and api_key != "None"

        if provider == "anthropic":
            if has_key:
                headers["x-api-key"] = api_key
            headers["anthropic-version"] = "2023-06-01"
        elif provider == "google":
            pass
        elif provider == "azure":
            if has_key:
                headers["api-key"] = api_key
        elif provider not in ("ollama", "lm_studio"):
            if has_key:
                headers["Authorization"] = f"Bearer {api_key}"

        extra = (cfg or {}).get("kwargs", {}).get("extra_headers", {})
        if isinstance(extra, dict):
            for k, v in extra.items():
                if isinstance(v, str):
                    headers[k] = v

        return headers

    def _litellm_fallback(self, provider: str, cfg: dict | None) -> list[str]:
        try:
            import litellm
            registry = getattr(litellm, "models_by_provider", None)
            if not registry:
                return []

            litellm_provider = (cfg or {}).get("litellm_provider", provider)
            raw_models: set = registry.get(litellm_provider, set())
            if not raw_models:
                return []

            prefix = litellm_provider + "/"
            result: list[str] = []
            for name in raw_models:
                clean = name[len(prefix):] if name.startswith(prefix) else name
                low = clean.lower()
                if any(exc in low for exc in _LITELLM_EXCLUDE):
                    continue
                if clean:
                    result.append(clean)
            return result
        except Exception:
            return []

    def _parse(self, data: dict | list, fmt: str) -> list[str]:
        if fmt == "ollama":
            return [m.get("name", "") for m in data.get("models", []) if m.get("name")]

        if fmt == "google":
            result = []
            for m in data.get("models", []):
                name = m.get("name", "")
                if name.startswith("models/"):
                    name = name[7:]
                if name:
                    result.append(name)
            return result

        if isinstance(data, dict) and "data" in data:
            return [m.get("id", "") for m in data["data"] if m.get("id")]

        return []
