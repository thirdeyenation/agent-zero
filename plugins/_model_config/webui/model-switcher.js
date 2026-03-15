const API_BASE = "/plugins/_model_config";

export async function loadSwitcherState(contextId) {
  const result = {
    allowed: false,
    presets: [],
    chatProviders: [],
    override: null,
  };

  try {
    const cfgRes = await fetchApi(`${API_BASE}/model_config_get`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    const cfgData = await cfgRes.json();
    const chatCfg = cfgData.config?.chat_model || {};

    result.allowed = !!chatCfg.allow_chat_override;
    result.chatProviders = cfgData.chat_providers || [];
    result.presets = cfgData.config?.model_presets || [];

    if (!result.allowed) return result;

    // Fetch current override status
    if (contextId) {
      const overRes = await fetchApi(`${API_BASE}/model_override`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "get", context_id: contextId }),
      });
      const overData = await overRes.json();
      result.override = overData.override || null;
    }
  } catch (e) {
    console.error("Model switcher load failed:", e);
  }

  return result;
}

export async function setPresetOverride(contextId, presetName) {
  try {
    const res = await fetchApi(`${API_BASE}/model_override`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: "set_preset",
        context_id: contextId,
        preset_name: presetName,
      }),
    });
    const data = await res.json();
    return !!data.ok;
  } catch (e) {
    console.error("Failed to set preset override:", e);
    return false;
  }
}

export async function clearOverride(contextId) {
  try {
    const res = await fetchApi(`${API_BASE}/model_override`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "clear", context_id: contextId }),
    });
    const data = await res.json();
    return !!data.ok;
  } catch (e) {
    console.error("Failed to clear override:", e);
    return false;
  }
}

export function getPresetLabel(preset) {
  return preset?.name || "Unnamed";
}

export function getPresetSummary(preset) {
  if (!preset) return "";
  const parts = [];
  if (preset.chat?.name) parts.push(preset.chat.name);
  if (preset.utility?.name) parts.push(preset.utility.name);
  return parts.join(" / ");
}
