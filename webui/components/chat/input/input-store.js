import { createStore } from "/js/AlpineStore.js";
import * as shortcuts from "/js/shortcuts.js";
import { store as fileBrowserStore } from "/components/modals/file-browser/file-browser-store.js";
import { store as messageQueueStore } from "/components/chat/message-queue/message-queue-store.js";
import { store as chatTopStore } from "/components/chat/top-section/chat-top-store.js";
import { store as attachmentsStore } from "/components/chat/attachments/attachmentsStore.js";

const model = {
  paused: false,

  get inputPlaceholder() {
    const input = document.getElementById("chat-input");
    const hasTypedText = !!input?.value?.trim();
    const hasAttachments = (attachmentsStore?.attachments?.length || 0) > 0;
    const hasQueue = !!messageQueueStore?.hasQueue;

    if (hasQueue && !hasTypedText && !hasAttachments)
      return "Press Enter to send queued messages";
    return "Type your message here...";
  },

  // Computed: send button icon type
  get sendButtonIcon() {
    const input = document.getElementById("chat-input");
    const hasInput = input?.value?.trim() || attachmentsStore?.attachments?.length > 0;
    const hasQueue = messageQueueStore?.hasQueue;
    const running = chatTopStore?.running;

    if (hasQueue && !hasInput) return "send-all";
    if ((running || hasQueue) && hasInput) return "queue";
    return "send";
  },

  // Computed: send button CSS class
  get sendButtonClass() {
    const icon = this.sendButtonIcon;
    if (icon === "send-all") return "send-queue";
    if (icon === "queue") return "send-queue";
    return "";
  },

  // Computed: send button title
  get sendButtonTitle() {
    const icon = this.sendButtonIcon;
    if (icon === "send-all") return "Send all queued messages";
    if (icon === "queue") return "Add to queue";
    return "Send message";
  },

  init() {
    console.log("Input store initialized");
    // Event listeners are now handled via Alpine directives in the component
  },

  async sendMessage() {
    // Delegate to the global function
    if (globalThis.sendMessage) {
      await globalThis.sendMessage();
    }
  },

  adjustTextareaHeight() {
    const chatInput = document.getElementById("chat-input");
    if (chatInput) {
      chatInput.style.height = "auto";
      chatInput.style.height = chatInput.scrollHeight + "px";
    }
  },

  async pauseAgent(paused) {
    const prev = this.paused;
    this.paused = paused;
    try {
      const context = globalThis.getContext?.();
      if (!globalThis.sendJsonData)
        throw new Error("sendJsonData not available");
      await globalThis.sendJsonData("/pause", { paused, context });
    } catch (e) {
      this.paused = prev;
      if (globalThis.toastFetchError) {
        globalThis.toastFetchError("Error pausing agent", e);
      }
    }
  },

  async nudge() {
    try {
      const context = globalThis.getContext();
      await globalThis.sendJsonData("/nudge", { ctxid: context });
    } catch (e) {
      if (globalThis.toastFetchError) {
        globalThis.toastFetchError("Error nudging agent", e);
      }
    }
  },

  async loadKnowledge() {
    try {
      const resp = await shortcuts.callJsonApi("/knowledge_path_get", {
        ctxid: shortcuts.getCurrentContextId(),
      });
      if (!resp.ok) throw new Error("Error getting knowledge path");
      const path = resp.path;

      // open file browser and wait for it to close
      await fileBrowserStore.open(path);

      // progress notification
      shortcuts.frontendNotification({
        type: shortcuts.NotificationType.PROGRESS,
        message: "Loading knowledge...",
        priority: shortcuts.NotificationPriority.NORMAL,
        displayTime: 999,
        group: "knowledge_load",
        frontendOnly: true,
      });

      // then reindex knowledge
      await globalThis.sendJsonData("/knowledge_reindex", {
        ctxid: shortcuts.getCurrentContextId(),
      });

      // finished notification
      shortcuts.frontendNotification({
        type: shortcuts.NotificationType.SUCCESS,
        message: "Knowledge loaded successfully",
        priority: shortcuts.NotificationPriority.NORMAL,
        displayTime: 2,
        group: "knowledge_load",
        frontendOnly: true,
      });
    } catch (e) {
      // error notification
      shortcuts.frontendNotification({
        type: shortcuts.NotificationType.ERROR,
        message: "Error loading knowledge",
        priority: shortcuts.NotificationPriority.NORMAL,
        displayTime: 5,
        group: "knowledge_load",
        frontendOnly: true,
      });
    }
  },

  // previous implementation without projects
  async _loadKnowledge() {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".txt,.pdf,.csv,.html,.json,.md";
    input.multiple = true;

    input.onchange = async () => {
      try {
        const formData = new FormData();
        for (let file of input.files) {
          formData.append("files[]", file);
        }

        formData.append("ctxid", globalThis.getContext());

        const response = await globalThis.fetchApi("/import_knowledge", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          if (globalThis.toast)
            globalThis.toast(await response.text(), "error");
        } else {
          const data = await response.json();
          if (globalThis.toast) {
            globalThis.toast(
              "Knowledge files imported: " + data.filenames.join(", "),
              "success"
            );
          }
        }
      } catch (e) {
        if (globalThis.toastFetchError) {
          globalThis.toastFetchError("Error loading knowledge", e);
        }
      }
    };

    input.click();
  },

  async browseFiles(path) {
    if (!path) {
      try {
        const resp = await shortcuts.callJsonApi("/chat_files_path_get", {
          ctxid: shortcuts.getCurrentContextId(),
        });
        if (resp.ok) path = resp.path;
      } catch (_e) {
        console.error("Error getting chat files path", _e);
      }
    }
    await fileBrowserStore.open(path);
  },
};

const store = createStore("chatInput", model);

export { store };
