import { createStore } from "/js/AlpineStore.js";
import { store as preferencesStore } from "/components/sidebar/bottom/preferences/preferences-store.js";

// Process Group Store - manages collapsible process groups in chat

// Unified mapping for both Tool Names and Step Types
// Specific tool names (keys) take precedence over generic types
const DISPLAY_CODES = {
  // --- Specific Tools ---
  'call_subordinate': 'SUB',
  'search_engine': 'WEB',
  'a2a_chat': 'A2A',
  'behaviour_adjustment': 'ADJ',
  'document_query': 'DOC',
  'vision_load': 'EYE',
  'notify_user': 'NTF',
  'scheduler': 'SCH',
  'unknown': 'UNK',
  // Memory operations group
  'memory_save': 'MEM',
  'memory_load': 'MEM',
  'memory_forget': 'MEM',
  'memory_delete': 'MEM',

  // --- Step Types ---
  'agent': 'GEN',
  'response': 'END',
  'tool': 'USE',       // Generic fallback for tools
  'code_exe': 'EXE',
  'browser': 'WWW',
  'progress': 'HLD',
  'subagent': 'SUB',   // Type fallback if tool name missing
  'mcp': 'MCP',
  'info': 'INF',
  'hint': 'HNT',
  'warning': 'WRN',
  'error': 'ERR',
  'util': 'UTL',
  'done': 'END'
};

const model = {
  // Track which process groups are expanded (by group ID)
  expandedGroups: {},
  
  // Track which individual steps are expanded within a group
  expandedSteps: {},
  
  // Default collapsed state for new process groups
  defaultCollapsed: true,

  init() {
    try {
      // Load persisted state
      const stored = localStorage.getItem("processGroupState");
      if (stored) {
        const parsed = JSON.parse(stored);
        this.expandedGroups = parsed.expandedGroups || {};
        this.expandedSteps = parsed.expandedSteps || {};
        this.defaultCollapsed = parsed.defaultCollapsed ?? true;
      }
    } catch (e) {
      console.error("Failed to load process group state", e);
    }
  },

  _persist() {
    try {
      localStorage.setItem("processGroupState", JSON.stringify({
        expandedGroups: this.expandedGroups,
        expandedSteps: this.expandedSteps,
        defaultCollapsed: this.defaultCollapsed
      }));
    } catch (e) {
      console.error("Failed to persist process group state", e);
    }
  },

  // Check if a process group is expanded
  isGroupExpanded(groupId) {
    if (groupId in this.expandedGroups) {
      return this.expandedGroups[groupId];
    }
    return !this.defaultCollapsed;
  },

  // Toggle process group expansion
  toggleGroup(groupId) {
    const current = this.isGroupExpanded(groupId);
    this.expandedGroups[groupId] = !current;
    this._persist();
  },

  // Expand a specific group
  expandGroup(groupId) {
    this.expandedGroups[groupId] = true;
    this._persist();
  },

  // Collapse a specific group
  collapseGroup(groupId) {
    this.expandedGroups[groupId] = false;
    this._persist();
  },

  // Check if a step within a group is expanded
  isStepExpanded(groupId, stepId) {
    const key = `${groupId}:${stepId}`;
    return this.expandedSteps[key] || false;
  },

  // Toggle step expansion
  toggleStep(groupId, stepId) {
    const key = `${groupId}:${stepId}`;
    const currentState = this.expandedSteps[key] || false;
    this.expandedSteps[key] = !currentState;
    this._persist();
  },

  // Status code (3-4 letter) for backend log types
  // Looks up tool name first (specific), then falls back to type (generic)
  getStepCode(type, toolName = null) {
    // Specific tool codes only apply to generic 'tool' steps
    if (type === 'tool' && toolName && DISPLAY_CODES[toolName]) {
      return DISPLAY_CODES[toolName];
    }

    return DISPLAY_CODES[type] || 
           type?.toUpperCase()?.slice(0, 4) || 
           'GEN';
  },

  // CSS color class for backend log types
  // Looks up tool name first (specific), then falls back to type (generic)
  getStatusColorClass(type, toolName = null) {
    // Specific tool name mappings for 'tool' steps
    if (type === 'tool' && toolName) {
      // call_subordinate gets teal (SUB color)
      if (toolName === 'call_subordinate') {
        return 'status-sub';
      }
      // Add other specific tool mappings here if needed in the future
    }
    
    const colors = {
      'agent': 'status-gen',
      'response': 'status-end',
      'tool': 'status-tool',
      'mcp': 'status-mcp',
      'subagent': 'status-sub',
      'code_exe': 'status-exe',
      'browser': 'status-www',
      'progress': 'status-wait',
      'info': 'status-inf',
      'hint': 'status-hnt',
      'warning': 'status-wrn',
      'error': 'status-err',
      'util': 'status-utl',
      'done': 'status-end'
    };
    return colors[type] || 'status-gen';
  },

  // Clear state for a specific context (when chat is reset)
  clearContext(contextPrefix) {
    // Clear groups matching the context
    for (const key of Object.keys(this.expandedGroups)) {
      if (key.startsWith(contextPrefix)) {
        delete this.expandedGroups[key];
      }
    }
    // Clear steps matching the context
    for (const key of Object.keys(this.expandedSteps)) {
      if (key.startsWith(contextPrefix)) {
        delete this.expandedSteps[key];
      }
    }
    this._persist();
  },

  // Get current detail mode from preferences
  _getDetailMode() {
    return preferencesStore.detailMode || "current";
  },

  expandGroup(groupId, isActiveAndGenerating = false) {
    const mode = this._getDetailMode();
    if (mode === "collapsed") {
      // Only expand if generating, not for completed groups
      return isActiveAndGenerating;
    }
    if (mode === "current" || mode === "expanded") return true;
    return !this.defaultCollapsed;
  },

  expandStep(groupId, stepId, isActive = false) {
    const mode = this._getDetailMode();
    if (mode === "collapsed") return false;
    if (mode === "expanded") return true;
    if (mode === "current") return isActive;
    return this.isStepExpanded(groupId, stepId);
  },

  // Apply current mode to all existing DOM elements
  applyModeSteps() {
    const mode = this._getDetailMode();
    const showUtils = preferencesStore.showUtils || false;
    const allGroups = document.querySelectorAll(".process-group");
    
    // Find the last VISIBLE step using targeted selector
    const stepSelector = showUtils ? ".process-step" : ".process-step:not(.message-util)";
    const visibleSteps = document.querySelectorAll(stepSelector);
    const lastStep = visibleSteps.length > 0 ? visibleSteps[visibleSteps.length - 1] : null;
    
    // Get all steps for applying expansion
    const allSteps = document.querySelectorAll(".process-step");
    
    // Apply to groups
    allGroups.forEach(group => {
      group.classList.toggle("expanded", mode !== "collapsed");
    });
    
    // Apply to steps
    allSteps.forEach(step => {
      let shouldExpand = false;
      if (mode === "expanded") {
        shouldExpand = true;
      } else if (mode === "current") {
        // Expand the last step and any parent steps containing it (for nested subordinate steps)
        shouldExpand = step === lastStep || step.contains(lastStep);
      }
      step.classList.toggle("step-expanded", shouldExpand);
    });
    
    // Apply to error groups
    const allErrorGroups = document.querySelectorAll(".error-group");
    allErrorGroups.forEach(errorGroup => {
      const shouldExpand = mode === "current" || mode === "expanded";
      errorGroup.classList.toggle("expanded", shouldExpand);
    });
  }
};

export const store = createStore("processGroup", model);
