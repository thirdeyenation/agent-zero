import { createStore } from "/js/AlpineStore.js";
import * as css from "/js/css.js";
import { store as speechStore } from "/components/chat/speech/speech-store.js";
import { store as processGroupStore } from "/components/messages/process-group/process-group-store.js";

// Preferences store centralizes user preference toggles and side-effects
const model = {
  // UI toggles (initialized with safe defaults, loaded from localStorage in init)
  get autoScroll() {
    return this._autoScroll;
  },
  set autoScroll(value) {
    this._autoScroll = value;
    this._applyAutoScroll(value);
  },
  _autoScroll: true,

  get darkMode() {
    return this._darkMode;
  },
  set darkMode(value) {
    this._darkMode = value;
    this._applyDarkMode(value);
  },
  _darkMode: true,

  get speech() {
    return this._speech;
  },
  set speech(value) {
    this._speech = value;
    this._applySpeech(value);
  },
  _speech: false,

  get showUtils() {
    return this._showUtils;
  },
  set showUtils(value) {
    this._showUtils = value;
    this._applyShowUtils(value);
  },
  _showUtils: false,

  // Process group collapse preference
  get collapseProcessGroups() {
    return this._collapseProcessGroups;
  },
  set collapseProcessGroups(value) {
    this._collapseProcessGroups = value;
    this._applyCollapseProcessGroups(value);
  },
  _collapseProcessGroups: true, // Default to collapsed

  // Chat container width preference for HiDPI/large screens
  get chatWidth() {
    return this._chatWidth;
  },
  set chatWidth(value) {
    this._chatWidth = value;
    this._applyChatWidth(value);
  },
  _chatWidth: "55", // Default width in em (standard)

  // Width presets: { label, value in em }
  chatWidthOptions: [
    { label: "STD", value: "55" },
    { label: "X-WIDE", value: "90" },
    { label: "FULL", value: "full" },
  ],

  // Detail mode for process groups/steps expansion
  get detailMode() {
    return this._detailMode;
  },
  set detailMode(value) {
    this._detailMode = value;
    this._applyDetailMode(value);
  },
  _detailMode: "current", // Default: show current step only

  // Detail mode options for UI sidebar
  detailModeOptions: [
    { label: "MIN", value: "collapsed", icon: "unfold_less", title: "All collapsed" },
    { label: "CUR", value: "current", icon: "step", title: "Current step only" },
    { label: "ALL", value: "expanded", icon: "unfold_more", title: "All expanded" },
  ],

  // Initialize preferences and apply current state
  init() {
    try {
      // Load persisted preferences with safe fallbacks
      try {
        const storedDarkMode = localStorage.getItem("darkMode");
        this._darkMode = storedDarkMode !== "false";
      } catch {
        this._darkMode = true; // Default to dark mode if localStorage is unavailable
      }

      try {
        const storedSpeech = localStorage.getItem("speech");
        this._speech = storedSpeech === "true";
      } catch {
        this._speech = false; // Default to speech off if localStorage is unavailable
      }

      // Load collapse process groups preference
      try {
        const storedCollapse = localStorage.getItem("collapseProcessGroups");
        this._collapseProcessGroups = storedCollapse !== "false"; // Default true
      } catch {
        this._collapseProcessGroups = true;
      }

      // Load chat width preference
      try {
        const storedChatWidth = localStorage.getItem("chatWidth");
        if (storedChatWidth && this.chatWidthOptions.some(opt => opt.value === storedChatWidth)) {
          this._chatWidth = storedChatWidth;
        }
      } catch {
        this._chatWidth = "55"; // Default to standard
      }

      // Load detail mode preference
      try {
        const storedDetailMode = localStorage.getItem("detailMode");
        if (storedDetailMode && this.detailModeOptions.some(opt => opt.value === storedDetailMode)) {
          this._detailMode = storedDetailMode;
        }
      } catch {
        this._detailMode = "current"; // Default
      }

      // Apply all preferences
      this._applyDarkMode(this._darkMode);
      this._applyAutoScroll(this._autoScroll);
      this._applySpeech(this._speech);
      this._applyShowUtils(this._showUtils);
      this._applyCollapseProcessGroups(this._collapseProcessGroups);
      this._applyChatWidth(this._chatWidth);
      this._applyDetailMode(this._detailMode);
    } catch (e) {
      console.error("Failed to initialize preferences store", e);
    }
  },

  _applyAutoScroll(value) {
    // nothing for now
  },

  _applyDarkMode(value) {
    if (value) {
      document.body.classList.remove("light-mode");
      document.body.classList.add("dark-mode");
    } else {
      document.body.classList.remove("dark-mode");
      document.body.classList.add("light-mode");
    }
    localStorage.setItem("darkMode", value);
  },

  _applySpeech(value) {
    localStorage.setItem("speech", value);
    if (!value) speechStore.stopAudio();
  },


  _applyShowUtils(value) {
    // For original messages
    css.toggleCssProperty(
      ".message-util",
      "display",
      value ? undefined : "none"
    );
    // For process steps - toggle class on all existing elements
    document.querySelectorAll(".process-step.message-util").forEach((el) => {
      el.classList.toggle("show-util", value);
    });
    // Re-apply detail mode to reset current visible step
    processGroupStore.applyModeSteps();
  },

  _applyCollapseProcessGroups(value) {
    localStorage.setItem("collapseProcessGroups", value);
    // Update process group store default
    processGroupStore.defaultCollapsed = value;
  },

  _applyChatWidth(value) {
    localStorage.setItem("chatWidth", value);
    // Set CSS custom property for chat max-width
    const root = document.documentElement;
    if (value === "full") {
      root.style.setProperty("--chat-max-width", "100%");
    } else {
      root.style.setProperty("--chat-max-width", `${value}em`);
    }
  },

  _applyDetailMode(value) {
    localStorage.setItem("detailMode", value);
    // Sync defaultCollapsed based on mode
    processGroupStore.defaultCollapsed = value === "collapsed";
    // Apply mode to all existing DOM elements
    processGroupStore.applyModeSteps();
  },
};

export const store = createStore("preferences", model);
