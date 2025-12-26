import { createStore } from "/js/AlpineStore.js";
import { store as schedulerStore } from "/components/modals/scheduler/scheduler-store.js";

const model = {
  closePromise: null,

  async open(options = {}) {
    // Open modal
    this.closePromise = window.openModal("modals/scheduler/scheduler-modal.html");

    // Setup cleanup on modal close
    if (this.closePromise?.then) {
      this.closePromise.then(() => this.cleanup());
    }

    // Notify scheduler store that modal opened
    schedulerStore.onTabActivated?.();

    // If taskId provided, show detail after load
    if (options.taskId) {
      setTimeout(async () => {
        await schedulerStore.fetchTasks({ manual: true });
        schedulerStore.showTaskDetail(options.taskId);
      }, 200);
    }
  },

  cleanup() {
    schedulerStore.onModalClosed?.();
    this.closePromise = null;
  },
};

export const store = createStore("schedulerModal", model);

