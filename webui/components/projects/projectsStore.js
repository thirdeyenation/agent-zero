import { createStore } from "/js/AlpineStore.js";
import * as api from "/js/api.js";

// define the model object holding data and functions
const model = {
  projectList: [],
  selectedProject: null,

  async loadProjectsList() {
    this.loading = true;
    try {
      const response = await api.callJsonApi("projects", { action: "list" });
      this.projectList = response.data;
    } catch (error) {
      console.error("Error loading projects list:", error);
    } finally {
      this.loading = false;
    }
  },
};

// convert it to alpine store
const store = createStore("projects", model);

// export for use in other files
export { store };
