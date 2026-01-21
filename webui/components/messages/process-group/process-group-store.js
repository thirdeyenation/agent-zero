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
  // Default collapsed state for new process groups
  defaultCollapsed: true,

  init() {
    try {
      // Load persisted default collapsed state only
      const stored = localStorage.getItem("processGroupState");
      if (stored) {
        const parsed = JSON.parse(stored);
        this.defaultCollapsed = parsed.defaultCollapsed ?? true;
      }
    } catch (e) {
      console.error("Failed to load process group state", e);
    }
  },

  _persist() {
    try {
      // Only persist the default collapsed preference
      // DOM is the source of truth for actual state
      localStorage.setItem("processGroupState", JSON.stringify({
        defaultCollapsed: this.defaultCollapsed
      }));
    } catch (e) {
      console.error("Failed to persist process group state", e);
    }
  },

  // Check if a process group is expanded
  isGroupExpanded(groupId) {
    const groupElement = document.getElementById(groupId);
    if (groupElement) {
      return groupElement.classList.contains("expanded");
    }
    return !this.defaultCollapsed;
  },

  // Toggle process group expansion
  toggleGroup(groupId) {
    const groupElement = document.getElementById(groupId);
    if (!groupElement) return;
    
    const currentState = groupElement.classList.contains("expanded");
    groupElement.classList.toggle("expanded", !currentState);
  },

  // Expand a specific group
  expandGroup(groupId) {
    const groupElement = document.getElementById(groupId);
    if (groupElement) {
      groupElement.classList.add("expanded");
    }
  },

  // Collapse a specific group
  collapseGroup(groupId) {
    const groupElement = document.getElementById(groupId);
    if (groupElement) {
      groupElement.classList.remove("expanded");
    }
  },

  // Check if a step within a group is expanded
  isStepExpanded(groupId, stepId) {
    const stepElement = document.getElementById(`process-step-${stepId}`);
    if (stepElement) {
      return stepElement.classList.contains("step-expanded");
    }
    return false;
  },

  // Toggle step expansion
  toggleStep(groupId, stepId) {
    const stepElement = document.getElementById(`process-step-${stepId}`);
    if (!stepElement) return;
    
    const currentState = stepElement.classList.contains("step-expanded");
    stepElement.classList.toggle("step-expanded", !currentState);
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
  },

  // Get current detail mode from preferences
  _getDetailMode() {
    return preferencesStore.detailMode || "current";
  },

  shouldExpandGroup(groupId, isActiveAndGenerating = false) {
    const mode = this._getDetailMode();
    if (mode === "collapsed") {
      return false;
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
    
    // Find the last visible step in an active (not completed) group only
    const stepSelector = showUtils 
      ? ".process-group:not(.process-group-completed) .process-step" 
      : ".process-group:not(.process-group-completed) .process-step:not(.message-util)";
    const visibleSteps = document.querySelectorAll(stepSelector);
    const lastActiveStep = visibleSteps.length > 0 ? visibleSteps[visibleSteps.length - 1] : null;
    
    // Get all steps for applying expansion
    const allSteps = document.querySelectorAll(".process-step");
    
    // Apply to groups
    allGroups.forEach(group => {
      const shouldExpandGroup = mode !== "collapsed";
      group.classList.toggle("expanded", shouldExpandGroup);
    });
    
    // Apply to steps
    allSteps.forEach(step => {
      let shouldExpand = false;
      if (mode === "expanded") {
        shouldExpand = true;
      } else if (mode === "current") {
        // Only expand the last step in an active group
        shouldExpand = step === lastActiveStep || step.contains(lastActiveStep);
      }
      step.classList.toggle("step-expanded", shouldExpand);
      
      // Clear user-pinned flag when mode changes
      if (!shouldExpand) {
        step.removeAttribute("data-user-pinned");
      }
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
