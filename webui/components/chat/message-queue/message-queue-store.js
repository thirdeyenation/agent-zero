import { createStore } from "/js/AlpineStore.js";
import * as api from "/js/api.js";

const model = {
  items: [],

  get hasQueue() {
    return this.items.length > 0;
  },

  get count() {
    return this.items.length;
  },

  async addToQueue(text, attachments = []) {
    const context = globalThis.getContext?.();
    if (!context) return false;

    try {
      let filenames = [];
      if (attachments.length > 0) {
        const formData = new FormData();
        for (const att of attachments) {
          formData.append("file", att.file || att);
        }
        const resp = await api.fetchApi("/upload", { method: "POST", body: formData });
        if (resp.ok) {
          const result = await resp.json();
          filenames = result.filenames || [];
        }
      }
      const response = await api.callJsonApi("/message_queue_add", { context, text, attachments: filenames });
      return response?.ok || false;
    } catch (e) {
      console.error("Failed to queue message:", e);
      return false;
    }
  },

  async removeItem(itemId) {
    const context = globalThis.getContext?.();
    if (!context) return;
    try {
      await api.callJsonApi("/message_queue_remove", { context, item_id: itemId });
    } catch (e) {
      console.error("Failed to remove from queue:", e);
    }
  },

  async clearQueue() {
    const context = globalThis.getContext?.();
    if (!context) return;
    try {
      await api.callJsonApi("/message_queue_remove", { context });
    } catch (e) {
      console.error("Failed to clear queue:", e);
    }
  },

  async sendItem(itemId) {
    const context = globalThis.getContext?.();
    if (!context) return;
    try {
      await api.callJsonApi("/message_queue_send", { context, item_id: itemId });
    } catch (e) {
      console.error("Failed to send queued message:", e);
    }
  },

  async sendAll() {
    const context = globalThis.getContext?.();
    if (!context || !this.hasQueue) return;
    try {
      await api.callJsonApi("/message_queue_send", { context, send_all: true });
    } catch (e) {
      console.error("Failed to send all queued:", e);
    }
  },

  updateFromPoll(queue) {
    this.items = queue || [];
  },

  getAttachmentUrl(filename) {
    return `/image_get?path=/a0/tmp/uploads/${encodeURIComponent(filename)}`;
  },
};

const store = createStore("messageQueue", model);
export { store };
