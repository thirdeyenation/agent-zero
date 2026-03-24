import { createStore } from "/js/AlpineStore.js";
import * as API from "/js/api.js";
import { store as notificationStore } from "/components/notifications/notification-store.js";

const HEALTH_POLL_INTERVAL_MS = 2000;
const HEALTH_WAIT_BUFFER_MS = 30000;

const model = {
  loading: false,
  saving: false,
  restarting: false,
  error: "",
  info: null,
  form: {
    branch: "main",
    tag: "",
    backup_usr: true,
    backup_path: "",
    backup_name: "",
    backup_conflict_policy: "rename",
  },
  _reconnectTimer: null,

  get isBusy() {
    return this.loading || this.saving || this.restarting;
  },

  get isSupported() {
    return Boolean(this.info?.supported);
  },

  get currentVersion() {
    return this.info?.current?.short_tag || "unknown";
  },

  get availableTags() {
    return Array.isArray(this.info?.available_tags) ? this.info.available_tags : [];
  },

  async init() {
    await this.refresh();
  },

  cleanup() {
    this.clearReconnectTimer();
    this.error = "";
    this.loading = false;
    this.saving = false;
    this.restarting = false;
  },

  clearReconnectTimer() {
    if (this._reconnectTimer) {
      clearTimeout(this._reconnectTimer);
      this._reconnectTimer = null;
    }
  },

  formatTimestamp(value) {
    if (!value) return "";
    try {
      return new Date(value).toLocaleString();
    } catch {
      return value;
    }
  },

  formatBranchTag(branch, tag) {
    return `${branch || "main"} / ${tag || "None"}`;
  },

  async refresh() {
    this.loading = true;
    this.error = "";
    try {
      const response = await API.callJsonApi("self_update_get", {});
      if (!response?.success) {
        throw new Error(response?.error || "Failed to load self-update info.");
      }
      this.info = response;
      this.applyFormState(response.pending || response.defaults || {});
    } catch (error) {
      console.error("Failed to load self-update info:", error);
      this.error = error.message || "Failed to load self-update info.";
    } finally {
      this.loading = false;
    }
  },

  applyFormState(source) {
    this.form.branch = source?.branch || "main";
    this.form.tag = source?.tag || this.currentVersion;
    this.form.backup_usr =
      typeof source?.backup_usr === "boolean" ? source.backup_usr : true;
    this.form.backup_path = source?.backup_path || "";
    this.form.backup_name = source?.backup_name || "";
    this.form.backup_conflict_policy =
      source?.backup_conflict_policy || "rename";
  },

  async scheduleUpdate() {
    if (!this.form.branch?.trim()) {
      this.error = "Choose a branch.";
      return;
    }

    if (!this.form.tag?.trim()) {
      this.error = "Enter a release tag to schedule.";
      return;
    }

    this.saving = true;
    this.error = "";
    try {
      const response = await API.callJsonApi("self_update_schedule", {
        branch: this.form.branch,
        tag: this.form.tag,
        backup_usr: this.form.backup_usr,
        backup_path: this.form.backup_path,
        backup_name: this.form.backup_name,
        backup_conflict_policy: this.form.backup_conflict_policy,
      });
      if (!response?.success) {
        throw new Error(response?.error || "Failed to schedule the self-update.");
      }

      if (this.info) {
        this.info.pending = response.pending;
      }
      await notificationStore.frontendWarning(
        "Agent Zero is restarting to apply the requested branch and release tag.",
        "Self Update",
        10,
        "self-update-restart",
        undefined,
        true,
      );
      await this.restartAndReload();
    } catch (error) {
      console.error("Failed to schedule self-update:", error);
      this.error = error.message || "Failed to schedule the self-update.";
    } finally {
      this.saving = false;
    }
  },

  async restartAndReload() {
    this.restarting = true;
    this.clearReconnectTimer();

    try {
      await API.fetchApi("/restart", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
      });
    } catch (_error) {
      // The restart request often terminates the backend mid-flight.
    }

    const maxWaitMs =
      ((this.info?.pending?.health_timeout_seconds ||
        this.info?.defaults?.health_timeout_seconds ||
        120) *
        1000) +
      HEALTH_WAIT_BUFFER_MS;
    const deadline = Date.now() + maxWaitMs;
    let lastError = "";

    while (Date.now() < deadline) {
      try {
        const response = await fetch("/api/health", {
          method: "GET",
          credentials: "same-origin",
          cache: "no-store",
        });
        if (response.ok) {
          window.location.reload();
          return;
        }
        lastError = `Health check returned HTTP ${response.status}.`;
      } catch (error) {
        lastError = error?.message || String(error);
      }

      await new Promise((resolve) => {
        this._reconnectTimer = setTimeout(() => {
          this._reconnectTimer = null;
          resolve();
        }, HEALTH_POLL_INTERVAL_MS);
      });
    }

    this.restarting = false;
    this.error =
      "Agent Zero did not come back within the expected window. It may still be rolling back. " +
      (lastError ? `Last health check error: ${lastError}` : "");
    await this.refresh();
  },

  close() {
    window.closeModal("settings/external/self-update-modal.html");
  },
};

const store = createStore("selfUpdateStore", model);

export { store };
