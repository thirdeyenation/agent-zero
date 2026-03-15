export const MODEL_SECTIONS = [
  { key: 'chat_model', title: 'Main Model', desc: 'Primary model for chat, reasoning, and browser tasks.' },
  { key: 'utility_model', title: 'Utility Model', desc: 'Lightweight model for background tasks: memory management, prompt preparation, summarization.' },
  { key: 'embedding_model', title: 'Embedding Model', desc: 'Model for generating vector embeddings used in knowledge retrieval.' }
];

export function kwargsToText(obj) {
  if (!obj || typeof obj !== 'object') return '';
  return Object.entries(obj).map(([k, v]) => {
    if (typeof v === 'string') return k + '=' + JSON.stringify(v);
    return k + '=' + (typeof v === 'object' ? JSON.stringify(v) : String(v));
  }).join('\n');
}

export function textToKwargs(text) {
  const d = {};
  (text || '').split('\n').forEach(l => {
    l = l.trim();
    if (!l || l.startsWith('#')) return;
    const i = l.indexOf('=');
    if (i > 0) {
      const key = l.substring(0, i).trim();
      let val = l.substring(i + 1).trim();
      try { val = JSON.parse(val); } catch {}
      d[key] = val;
    }
  });
  return d;
}

export function textToHeaders(text) {
  const d = {};
  (text || '').split('\n').forEach(l => {
    l = l.trim();
    if (!l || l.startsWith('#')) return;
    const i = l.indexOf('=');
    if (i > 0) d[l.substring(0, i).trim()] = l.substring(i + 1).trim();
  });
  return d;
}

export async function loadConfigData() {
  const res = await fetchApi('/plugins/_model_config/model_config_get', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({})
  });
  return await res.json();
}

export async function saveApiKey(provider, value) {
  await fetchApi('/plugins/_model_config/api_keys', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'set', keys: { [provider]: value } })
  });
}

export async function revealApiKey(provider) {
  const res = await fetchApi('/plugins/_model_config/api_keys', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action: 'reveal', provider })
  });
  const data = await res.json();
  return data.value || '';
}

export async function searchModels(provider, query, modelType, apiBase) {
  if (!provider) return [];
  try {
    const res = await fetchApi('/plugins/_model_config/model_search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider, query: query || '', model_type: modelType || 'chat', api_base: apiBase || '' })
    });
    const data = await res.json();
    return data.models || [];
  } catch (e) {
    console.error('Model search failed:', e);
    return [];
  }
}

export function initConfigFields(config) {
  if (config?.chat_model) config.chat_model._kwargs_text = kwargsToText(config.chat_model.kwargs);
  if (config?.utility_model) config.utility_model._kwargs_text = kwargsToText(config.utility_model.kwargs);
  if (config?.embedding_model) config.embedding_model._kwargs_text = kwargsToText(config.embedding_model.kwargs);
  if (config) config._browser_headers_text = Object.entries(config.browser_http_headers || {}).map(([k, v]) => k + '=' + v).join('\n');
  if (config) {
    if (!config.model_presets) config.model_presets = [];
    config.model_presets = config.model_presets.map(p => ({
      name: p.name || '',
      chat: { provider: '', name: '', api_key: '', api_base: '', ...(p.chat || {}) },
      utility: { provider: '', name: '', api_key: '', api_base: '', ...(p.utility || {}) },
    }));
  }
}

export async function initConfigComponent(comp, config) {
  const data = await loadConfigData();
  comp.chatProviders = data.chat_providers || [];
  comp.embeddingProviders = data.embedding_providers || [];
  comp.apiKeyStatus = data.api_key_status || {};
  const allProviders = [...comp.chatProviders, ...comp.embeddingProviders];
  const newKeys = { ...comp.apiKeyValues };
  const seen = new Set();
  for (const p of allProviders) {
    if (!p.value || seen.has(p.value)) continue;
    seen.add(p.value);
    if (!(p.value in newKeys)) newKeys[p.value] = '';
  }
  comp.apiKeyValues = newKeys;
  initConfigFields(config);
}
