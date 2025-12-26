import { createStore } from "/js/AlpineStore.js";
import * as API from "/js/api.js";
import { store as notificationStore } from "/components/notifications/notification-store.js";

// Constants
const VIEW_MODE_STORAGE_KEY = "settingsActiveTab";
const DEFAULT_TAB = "agent";

// Helper for toasts
function toast(text, type = "info", timeout = 5000) {
  notificationStore.addFrontendToastOnly(type, text, "", timeout / 1000);
}

// Settings Store
const model = {
  // State
  isLoading: false,
  error: null,
  settings: null,
  additional: null,
  
  // Tab state
  _activeTab: DEFAULT_TAB,
  get activeTab() {
    return this._activeTab;
  },
  set activeTab(value) {
    const previous = this._activeTab;
    this._activeTab = value;
    this.applyActiveTab(previous, value);
  },

  // Lifecycle
  init() {
    // Restore persisted tab
    try {
      const saved = localStorage.getItem(VIEW_MODE_STORAGE_KEY);
      if (saved) this._activeTab = saved;
    } catch {}
  },

  async onOpen() {
    this.error = null;
    this.isLoading = true;
    
    try {
      const response = await API.callJsonApi("settings_get", null);
      if (response && response.settings) {
        this.settings = response.settings;
        this.additional = response.additional || null;
      } else {
        throw new Error("Invalid settings response");
      }
    } catch (e) {
      console.error("Failed to load settings:", e);
      this.error = e.message || "Failed to load settings";
      toast("Failed to load settings", "error");
    } finally {
      this.isLoading = false;
    }

    // Trigger tab activation for current tab
    this.applyActiveTab(null, this._activeTab);
  },

  cleanup() {
    this.settings = null;
    this.additional = null;
    this.error = null;
    this.isLoading = false;
  },

  // Tab management
  applyActiveTab(previous, current) {
    // Persist
    try {
      localStorage.setItem(VIEW_MODE_STORAGE_KEY, current);
    } catch {}
  },

  switchTab(tabName) {
    this.activeTab = tabName;
  },



  get apiKeyProviders() {
    const seen = new Set();
    const options = [];
    const addProvider = (prov) => {
      if (!prov?.value) return;
      const key = prov.value.toLowerCase();
      if (seen.has(key)) return;
      seen.add(key);
      options.push({ value: prov.value, label: prov.label || prov.value });
    };
    (this.additional?.chat_providers || []).forEach(addProvider);
    (this.additional?.embedding_providers || []).forEach(addProvider);
    options.sort((a, b) => a.label.localeCompare(b.label));
    return options;
  },

  // Save settings
  async saveSettings() {
    if (!this.settings) {
      toast("No settings to save", "warning");
      return false;
    }

    this.isLoading = true;
    try {
      const response = await API.callJsonApi("settings_set", { settings: this.settings });
      if (response && response.settings) {
        this.settings = response.settings;
        this.additional = response.additional || this.additional;
        toast("Settings saved successfully", "success");
        document.dispatchEvent(
          new CustomEvent("settings-updated", { detail: response.settings })
        );
        return true;
      } else {
        throw new Error("Failed to save settings");
      }
    } catch (e) {
      console.error("Failed to save settings:", e);
      toast("Failed to save settings: " + e.message, "error");
      return false;
    } finally {
      this.isLoading = false;
    }
  },

  // Close the modal
  closeSettings() {
    window.closeModal("settings/settings.html");
  },

  // Save and close
  async saveAndClose() {
    const success = await this.saveSettings();
    if (success) {
      this.closeSettings();
    }
  },

  // Field helpers for external components
  // Handle button field clicks (opens sub-modals)
  async handleFieldButton(field) {
    if (field.id === "mcp_servers_config") {
      window.openModal("settings/mcp/client/mcp-servers.html");
    } else if (field.id === "backup_create") {
      window.openModal("settings/backup/backup.html");
    } else if (field.id === "backup_restore") {
      window.openModal("settings/backup/restore.html");
    } else if (field.id === "show_a2a_connection") {
      window.openModal("settings/a2a/a2a-connection.html");
    } else if (field.id === "external_api_examples") {
      window.openModal("settings/external/api-examples.html");
    } else if (field.id === "memory_dashboard") {
      window.openModal("settings/memory/memory-dashboard.html");
    }
  },

  // Open settings modal from external callers
  async open(initialTab = null) {
    if (initialTab) {
      this._activeTab = initialTab;
    }
    await window.openModal("settings/settings.html");
  },
};

const store = createStore("settingsStore", model);

export { store };

