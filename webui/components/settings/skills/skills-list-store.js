import { createStore } from "/js/AlpineStore.js";
import { store as fileBrowserStore } from "/components/modals/file-browser/file-browser-store.js";
import { store as settingsStore } from "/components/settings/settings-store.js";
import { store as chatsStore } from "/components/sidebar/chats/chats-store.js";

const fetchApi = globalThis.fetchApi;

const model = {
  loading: false,
  error: "",
  skills: [],
  projects: [],
  projectName: "",
  profileName: "",

  async init() {
    this.resetState();
    await this.loadProjects();
    this.setDefaultProject();
    await this.loadSkills();
  },

  resetState() {
    this.loading = false;
    this.error = "";
    this.skills = [];
    this.projects = [];
    this.projectName = "";
    this.profileName = "";
  },

  onClose() {
    this.resetState();
  },

  setDefaultProject() {
    if (this.projectName) return;
    const active = chatsStore?.selectedContext?.project?.name;
    if (active) {
      this.projectName = active;
    }
  },

  refreshProfileName() {
    this.profileName = settingsStore?.settings?.agent_profile || "";
  },

  async loadProjects() {
    try {
      const response = await fetchApi("/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: "list" }),
      });
      const data = await response.json().catch(() => ({}));
      this.projects = data.ok ? (data.data || []) : [];
    } catch (e) {
      console.error("Failed to load projects:", e);
      this.projects = [];
    }
  },

  async loadSkills() {
    this.refreshProfileName();
    try {
      this.loading = true;
      this.error = "";
      const response = await fetchApi("/skills", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "list",
          project_name: this.projectName || null,
          profile_name: this.profileName || null,
        }),
      });
      const result = await response.json().catch(() => ({}));
      if (!result.ok) {
        this.error = result.error || "Failed to load skills";
        this.skills = [];
        return;
      }
      this.skills = Array.isArray(result.data) ? result.data : [];
    } catch (e) {
      this.error = e?.message || "Failed to load skills";
      this.skills = [];
    } finally {
      this.loading = false;
    }
  },

  async toggleSkill(skill, enabled) {
    if (!skill) return;
    const previous = skill.enabled;
    skill.enabled = enabled;
    try {
      const response = await fetchApi("/skills", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "toggle",
          skill_id: skill.skill_id,
          enabled,
          project_name: this.projectName || null,
          profile_name: this.profileName || null,
        }),
      });
      const result = await response.json().catch(() => ({}));
      if (!result.ok) {
        throw new Error(result.error || "Toggle failed");
      }
    } catch (e) {
      skill.enabled = previous;
      const msg = e?.message || "Toggle failed";
      if (window.toastFrontendError) {
        window.toastFrontendError(msg, "Skills");
      }
    }
  },

  async deleteSkill(skill) {
    if (!skill) return;
    try {
      const response = await fetchApi("/skills", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "delete",
          skill_id: skill.skill_id,
          project_name: this.projectName || null,
          profile_name: this.profileName || null,
        }),
      });
      const result = await response.json().catch(() => ({}));
      if (!result.ok) {
        throw new Error(result.error || "Delete failed");
      }
      if (window.toastFrontendSuccess) {
        window.toastFrontendSuccess("Skill deleted", "Skills");
      }
      await this.loadSkills();
    } catch (e) {
      const msg = e?.message || "Delete failed";
      if (window.toastFrontendError) {
        window.toastFrontendError(msg, "Skills");
      }
    }
  },

  async openSkill(skill) {
    if (!skill?.location) return;
    await fileBrowserStore.open(skill.location);
  },
};

const store = createStore("skillsListStore", model);
export { store };
