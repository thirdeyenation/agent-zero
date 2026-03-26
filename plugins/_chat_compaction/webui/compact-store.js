import { createStore } from "/js/AlpineStore.js";
import { callJsonApi } from "/js/api.js";
import {
  toastFrontendSuccess,
  toastFrontendError,
} from "/components/notifications/notification-store.js";

export const store = createStore("compactStore", {
  compacting: false,
  stats: null,
  showModal: false,

  async fetchStats() {
    try {
      const ctxid = globalThis.getContext?.();
      if (!ctxid) {
        toastFrontendError("No active chat", "Compaction");
        return;
      }

      const res = await callJsonApi("/plugins/_chat_compaction/compact_chat", {
        context: ctxid,
        action: "stats",
      });

      if (!res?.ok) {
        throw new Error(res?.message || "Failed to fetch stats");
      }

      this.stats = res.stats;
      this.showModal = true;
    } catch (e) {
      toastFrontendError(e.message, "Compaction");
    }
  },

  async compact() {
    this.compacting = true;
    try {
      const ctxid = globalThis.getContext?.();
      if (!ctxid) {
        throw new Error("No active chat");
      }

      const res = await callJsonApi("/plugins/_chat_compaction/compact_chat", {
        context: ctxid,
        action: "compact",
      });

      if (!res?.ok) {
        throw new Error(res?.message || "Compaction failed");
      }

      toastFrontendSuccess("Compaction started", "Compaction");
      this.showModal = false;
    } catch (e) {
      toastFrontendError(e.message, "Compaction");
    } finally {
      this.compacting = false;
    }
  },

  closeModal() {
    this.showModal = false;
    this.stats = null;
  },
});
