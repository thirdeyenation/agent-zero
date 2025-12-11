import { createStore } from "/js/AlpineStore.js";
import * as API from "/js/api.js";
import { store as notificationStore } from "/components/notifications/notification-store.js";
import { store as schedulerStore } from "/components/settings/scheduler/scheduler-store.js";

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
  sectionsById: {},
  
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
        this.rebuildSectionsIndex();
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
    // Notify scheduler if it was active
    if (this._activeTab === "scheduler") {
      schedulerStore.onTabDeactivated?.();
    }
    schedulerStore.onModalClosed?.();
    
    this.settings = null;
    this.sectionsById = {};
    this.error = null;
    this.isLoading = false;
  },

  // Tab management
  applyActiveTab(previous, current) {
    // Persist
    try {
      localStorage.setItem(VIEW_MODE_STORAGE_KEY, current);
    } catch {}

    // Scheduler lifecycle
    if (previous === "scheduler" && current !== "scheduler") {
      schedulerStore.onTabDeactivated?.();
    }
    if (current === "scheduler" && previous !== "scheduler") {
      schedulerStore.onTabActivated?.();
    }
  },

  switchTab(tabName) {
    this.activeTab = tabName;
  },

  // Computed: sections for current tab
  get filteredSections() {
    if (!this.settings || !this.settings.sections) return [];
    const sections = this.settings.sections.filter(
      (section) => section.tab === this._activeTab
    );
    return sections;
  },

  rebuildSectionsIndex() {
    const map = {};
    if (this.settings && Array.isArray(this.settings.sections)) {
      for (const section of this.settings.sections) {
        if (section && section.id) {
          map[section.id] = section;
        }
      }
    }
    this.sectionsById = map;
  },

  getSectionById(sectionId) {
    if (!sectionId) return null;
    return this.sectionsById[sectionId] || null;
  },

  // Save settings
  async saveSettings() {
    if (!this.settings) {
      toast("No settings to save", "warning");
      return false;
    }

    this.isLoading = true;
    try {
      const response = await API.callJsonApi("settings_set", this.settings);
      if (response && response.settings) {
        this.settings = response.settings;
        this.rebuildSectionsIndex();
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
  getField(sectionId, fieldId) {
    if (!this.settings || !this.settings.sections) return null;
    for (const section of this.settings.sections) {
      if (section.id === sectionId) {
        for (const field of section.fields) {
          if (field.id === fieldId) {
            return field;
          }
        }
      }
    }
    return null;
  },

  setFieldValue(sectionId, fieldId, value) {
    const field = this.getField(sectionId, fieldId);
    if (field) {
      field.value = value;
      return true;
    }
    return false;
  },

  findFieldValue(fieldId) {
    if (!this.settings || !this.settings.sections) return null;
    for (const section of this.settings.sections) {
      for (const field of section.fields) {
        if (field.id === fieldId) {
          return field.value;
        }
      }
    }
    return null;
  },

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

  // Scheduler integration: open Settings modal, switch to scheduler tab, show task detail
  async openSchedulerTaskDetail(taskId) {
    // Set tab to scheduler before opening
    this._activeTab = "scheduler";
    
    // Open the modal (do NOT await - openModal resolves on close)
    window.openModal("settings/settings.html");

    // Ensure scheduler tasks are loaded, then show the detail modal
    setTimeout(async () => {
      try {
        if (typeof schedulerStore.fetchTasks === "function") {
          await schedulerStore.fetchTasks({ manual: true });
        }
        schedulerStore.showTaskDetail?.(taskId);
      } catch (error) {
        console.warn("[settings-store] openSchedulerTaskDetail failed", error);
      }
    }, 200);
  },
};

const store = createStore("settingsStore", model);

export { store };

