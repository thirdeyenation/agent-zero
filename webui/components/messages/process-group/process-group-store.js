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
  init() {},

  // Toggle process group expansion (called from click handler in messages.js)
  toggleGroup(groupId) {
    const groupElement = document.getElementById(groupId);
    if (!groupElement) return;
    groupElement.classList.toggle("expanded");
  },

  // Toggle step expansion (called from click handler in messages.js)
  toggleStep(groupId, stepId) {
    const stepElement = document.getElementById(`process-step-${stepId}`);
    if (!stepElement) return;
    stepElement.classList.toggle("step-expanded");
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

  // Get current detail mode from preferences
  _getDetailMode() {
    return preferencesStore.detailMode || "current";
  },

  shouldExpandGroup() {
    const mode = this._getDetailMode();
    // Groups expand in "current" and "expanded" modes, collapse only in "collapsed" mode
    return mode !== "collapsed";
  },

  // Apply current mode to all existing DOM elements
  applyModeSteps() {
    const mode = this._getDetailMode();
    const showUtils = preferencesStore.showUtils || false;
    const allGroups = document.querySelectorAll(".process-group");
    
    // Find the active group (currently streaming) - DOM is source of truth
    const activeGroup = document.querySelector(".process-group.active");
    
    // Find the last visible step in the ACTIVE group only (for "current" mode)
    let lastActiveStep = null;
    if (activeGroup && !activeGroup.classList.contains("process-group-completed")) {
      const stepSelector = showUtils 
        ? ".process-step" 
        : ".process-step:not(.message-util)";
      const stepsInActiveGroup = activeGroup.querySelectorAll(stepSelector);
      lastActiveStep = stepsInActiveGroup.length > 0 ? stepsInActiveGroup[stepsInActiveGroup.length - 1] : null;
    }
    
    // Apply to groups
    allGroups.forEach(group => {
      const shouldExpandGroup = mode !== "collapsed";
      group.classList.toggle("expanded", shouldExpandGroup);
    });
    
    // Apply to steps - different logic for active vs non-active groups
    allGroups.forEach(group => {
      const isActiveGroup = group.classList.contains("active");
      const steps = group.querySelectorAll(".process-step");
      
      steps.forEach(step => {
        let shouldExpand = false;
        
        if (mode === "expanded") {
          shouldExpand = true;
        } else if (mode === "current") {
          if (isActiveGroup) {
            // Active group: only expand the last step
            shouldExpand = step === lastActiveStep;
          }
          // Non-active groups: shouldExpand stays false → all steps collapsed
        }
        // In "collapsed" mode: shouldExpand stays false
        
        if (shouldExpand) {
          step.classList.add("step-expanded");
        } else {
          // For non-active groups or collapsed mode, immediately collapse
          // Only defer to timeout for active group in "current" mode when there's an active step
          // (lastActiveStep is null if group is completed - no deferral needed)
          const shouldDefer = mode === "current" && isActiveGroup && lastActiveStep && step !== lastActiveStep;
          if (!shouldDefer) {
            step.classList.remove("step-expanded");
            step.removeAttribute("data-user-pinned");
          }
        }
      });
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
