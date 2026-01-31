import { createStore } from "/js/AlpineStore.js";
import { store as navStore } from "/components/chat/navigation/chat-navigation-store.js";
import * as api from "/js/api.js";

const model = {
  items: [],
  pendingItems: [], // Local pending items (uploading to queue)

  get hasQueue() {
    return this.items.length > 0 || this.pendingItems.length > 0;
  },

  get count() {
    return this.items.length + this.pendingItems.length;
  },

  // Combined items for display: confirmed first, then pending at the end
  get allItems() {
    return [...this.items, ...this.pendingItems];
  },

  async addToQueue(text, attachments = []) {
    const context = globalThis.getContext?.();
    if (!context) return false;

    // Generate a temporary ID for pending item
    const tempId = `pending-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const pendingItem = {
      id: tempId,
      text: text || "(attachment only)",
      attachments: attachments.map(a => a.name || a.file?.name || "file"),
      pending: true,
    };

    // Add to pending immediately for UI feedback
    this.pendingItems = [...this.pendingItems, pendingItem];

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
      
      // Remove from pending (poll will add the confirmed item)
      this.pendingItems = this.pendingItems.filter(p => p.id !== tempId);
      return response?.ok || false;
    } catch (e) {
      console.error("Failed to queue message:", e);
      // Remove from pending on error
      this.pendingItems = this.pendingItems.filter(p => p.id !== tempId);
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
      navStore.scrollToBottom();
      await api.callJsonApi("/message_queue_send", { context, send_all: true });
    } catch (e) {
      console.error("Failed to send all queued:", e);
    }
  },

  updateFromPoll(queue) {
    this.items = queue || [];
  },

  getAttachmentUrl(filename) {
    return `/image_get?path=/a0/usr/uploads/${encodeURIComponent(filename)}`;
  },
};

const store = createStore("messageQueue", model);
export { store };
