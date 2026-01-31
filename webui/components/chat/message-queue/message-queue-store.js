import { createStore } from "/js/AlpineStore.js";
import { store as navStore } from "/components/chat/navigation/chat-navigation-store.js";
import * as api from "/js/api.js";
import { toastFrontendInfo, NotificationPriority } from "/components/notifications/notification-store.js";
import { sleep } from "/js/sleep.js";

const model = {
  items: [],
  pendingItems: [], // Local pending items (uploading to queue)

  _getQueueScrollerEl() {
    return document.querySelector(".queue-preview .queue-items");
  },

  scrollQueueToBottom() {
    const el = this._getQueueScrollerEl();
    if (!el) return;

    const scroll = () => {
      el.scrollTop = el.scrollHeight;
    };

    requestAnimationFrame(() => {
      scroll();
      requestAnimationFrame(scroll);
    });
  },

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
    this.scrollQueueToBottom();

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

      const serverId = response?.item_id;
      if (serverId) {
        this.pendingItems = this.pendingItems.map((p) =>
          p.id === tempId ? { ...p, serverId } : p,
        );
      }
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

    // check for pending uploads and notify user
    if (this.pendingItems.length > 0) {
      await sleep(1000);
      if (this.pendingItems.length > 0) {
        toastFrontendInfo(
          "There are pending uploads in the queue. You can wait for them to finish or remove them.",
          "Pending uploads",
          3,
          "pending-uploads",
          NotificationPriority.NORMAL,
          true,
        );
        return;
      }
    }

    if (!this.hasQueue) return;
    try {
      navStore.scrollToBottom();
      await api.callJsonApi("/message_queue_send", { context, send_all: true });
    } catch (e) {
      console.error("Failed to send all queued:", e);
    }
  },

  updateFromPoll(queue) {
    this.items = queue || [];

    if (this.pendingItems.length > 0) {
      const hasPendingWithServerId = this.pendingItems.some((p) => p.serverId);
      if (hasPendingWithServerId) {
        const serverIds = new Set(this.items.map((i) => i.id).filter(Boolean));
        this.pendingItems = this.pendingItems.filter((p) => {
          if (!p.serverId) return true;
          return !serverIds.has(p.serverId);
        });
      }
    }
    // this.scrollQueueToBottom();
  },

  getAttachmentUrl(filename) {
    return `/image_get?path=/a0/usr/uploads/${encodeURIComponent(filename)}`;
  },
};

const store = createStore("messageQueue", model);
export { store };
