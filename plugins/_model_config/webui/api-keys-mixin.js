const API_BASE = "/plugins/_model_config";

export const apiKeysState = {
  apiKeyStatus: {},
  apiKeyValues: {},
  apiKeyDirty: {},
  allProviders: [],
};

export const apiKeysMethods = {
  _setProviderHasKey(provider, hasKey) {
    if (!provider) return;
    this.apiKeyStatus = { ...this.apiKeyStatus, [provider]: !!hasKey };
    const normalized = provider.toLowerCase();
    this.allProviders = (this.allProviders || []).map((item) =>
      item.value?.toLowerCase() === normalized ? { ...item, has_key: !!hasKey } : item
    );
  },

  _ensureApiKeySlot(provider) {
    if (!provider) return;
    if (!(provider in this.apiKeyValues)) {
      this.apiKeyValues = { ...this.apiKeyValues, [provider]: '' };
    }
    if (!(provider in this.apiKeyDirty)) {
      this.apiKeyDirty = { ...this.apiKeyDirty, [provider]: false };
    }
  },

  _setApiKeyDirty(provider, isDirty) {
    if (!provider) return;
    this._ensureApiKeySlot(provider);
    this.apiKeyDirty = { ...this.apiKeyDirty, [provider]: !!isDirty };
  },

  touchApiKey(provider) {
    this._setApiKeyDirty(provider, true);
  },

  async refreshApiKeyStatus() {
    await this.ensureLoaded();
    const res = await fetchApi(`${API_BASE}/api_keys`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'get' })
    });
    const data = await res.json();
    const keys = data.keys || {};

    const nextStatus = { ...this.apiKeyStatus };
    const nextValues = { ...this.apiKeyValues };
    const nextDirty = { ...this.apiKeyDirty };

    for (const provider of this.allProviders) {
      const entry = keys[provider.value] || {};
      const hasKey = !!entry.has_key;
      nextStatus[provider.value] = hasKey;
      provider.has_key = hasKey;
      if (!(provider.value in nextDirty)) {
        nextDirty[provider.value] = false;
      }
      if (!hasKey && !nextDirty[provider.value]) {
        nextValues[provider.value] = '';
      }
    }

    this.apiKeyStatus = nextStatus;
    this.apiKeyValues = nextValues;
    this.apiKeyDirty = nextDirty;
    this.allProviders = [...this.allProviders];
    return keys;
  },

  resetApiKeyDrafts() {
    const nextValues = {};
    const nextDirty = {};
    for (const provider of this.allProviders || []) {
      if (!provider?.value) continue;
      nextValues[provider.value] = '';
      nextDirty[provider.value] = false;
    }
    this.apiKeyValues = nextValues;
    this.apiKeyDirty = nextDirty;
  },

  async saveApiKeys(updates) {
    const normalized = {};
    for (const [provider, value] of Object.entries(updates || {})) {
      if (!provider || typeof value !== 'string') continue;
      normalized[provider] = value.trim() ? value : '';
    }

    if (Object.keys(normalized).length === 0) {
      return { ok: true };
    }

    const res = await fetchApi(`${API_BASE}/api_keys`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'set', keys: normalized })
    });
    const data = await res.json();
    if (!data?.ok) {
      throw new Error(data?.error || 'Failed to save API keys.');
    }

    const nextValues = { ...this.apiKeyValues };
    const nextDirty = { ...this.apiKeyDirty };
    for (const [provider, value] of Object.entries(normalized)) {
      nextValues[provider] = value;
      nextDirty[provider] = false;
      this._setProviderHasKey(provider, !!value.trim());
    }
    this.apiKeyValues = nextValues;
    this.apiKeyDirty = nextDirty;
    return data;
  },

  async saveApiKey(provider, value) {
    return this.saveApiKeys({ [provider]: value });
  },

  saveApiKeyIfSet(provider) {
    if (provider in this.apiKeyValues) {
      return this.saveApiKey(provider, this.apiKeyValues[provider] || '');
    }
  },

  async revealApiKey(provider) {
    const res = await fetchApi(`${API_BASE}/api_keys`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'reveal', provider })
    });
    const data = await res.json();
    if (!data?.ok) {
      throw new Error(data?.error || 'Failed to load API key.');
    }
    const value = data.value || '';
    if (provider) {
      this._ensureApiKeySlot(provider);
      this.apiKeyValues = { ...this.apiKeyValues, [provider]: value };
      this._setApiKeyDirty(provider, false);
      this._setProviderHasKey(provider, !!value.trim());
    }
    return value;
  },

  async persistApiKeysForConfig(config) {
    const updates = {};
    const seen = new Set();
    for (const section of this.MODEL_SECTIONS) {
      const provider = config?.[section.key]?.provider;
      if (!provider || seen.has(provider) || !this.apiKeyDirty[provider]) continue;
      seen.add(provider);
      const value = this.apiKeyValues[provider];
      updates[provider] = typeof value === 'string' ? value : '';
    }
    return this.saveApiKeys(updates);
  },
};
