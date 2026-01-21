// message actions and components
import { store as imageViewerStore } from "../components/modals/image-viewer/image-viewer-store.js";
import { marked } from "../vendor/marked/marked.esm.js";
import { store as _messageResizeStore } from "/components/messages/resize/message-resize-store.js"; // keep here, required in html
import { store as attachmentsStore } from "/components/chat/attachments/attachmentsStore.js";
import { addActionButtonsToElement } from "/components/messages/action-buttons/simple-action-buttons.js";
import { store as processGroupStore } from "/components/messages/process-group/process-group-store.js";
import { store as stepDetailStore } from "/components/modals/process-step-detail/step-detail-store.js";
import { store as preferencesStore } from "/components/sidebar/bottom/preferences/preferences-store.js";
import { formatDuration } from "./time-utils.js";

// ============================================
// Timing Constants
// ============================================
// Delay before collapsing previous steps when a new step is added
const STEP_COLLAPSE_DELAY_MS = 2000;
// Delay before collapsing the last step when processing completes
const FINAL_STEP_COLLAPSE_DELAY_MS = 2000;

// Track active collapse timeouts for steps (key: step DOM element, value: timeout ID)
const stepCollapseTimeouts = new Map();

const chatHistory = document.getElementById("chat-history");

let messageGroup = null;
let currentProcessGroup = null; // Track current process group for collapsible UI
let currentDelegationSteps = {}; // Track delegation steps by agent number for nesting
let activeProcessGroupId = null; // Only one process group should show "running" indicators at a time
let activeProcessGroupEl = null;
let activeStepTitleEl = null;

// Expose activeProcessGroupId for store access
window.activeProcessGroupId = null;

/**
 * Mark current process group as active and clear active badges.
 */
function setActiveProcessGroup(group) {
  if (!group || !group.id) return;
  if (activeProcessGroupId === group.id) return;

  // Clear shiny effect from the previous active step title if we moved to a new group
  if (activeStepTitleEl && activeProcessGroupEl && activeProcessGroupEl !== group && activeProcessGroupEl.contains(activeStepTitleEl)) {
    activeStepTitleEl.classList.remove("shiny-text");
    activeStepTitleEl = null;
  }

  activeProcessGroupId = group.id;
  activeProcessGroupEl = group;
  window.activeProcessGroupId = group.id; // Keep window copy in sync for store access

}

export function clearActiveStepShine() {
  if (activeStepTitleEl) {
    activeStepTitleEl.classList.remove("shiny-text");
    activeStepTitleEl = null;
  }
  // clear any lingering shine in process steps
  document.querySelectorAll(".process-step .step-title.shiny-text").forEach((el) => {
    el.classList.remove("shiny-text");
  });
}

/**
 * Resolve tool name from kvps, existing attribute, or previous siblings
 * For 'tool' type steps, inherits from preceding step if not directly available
 */
function resolveToolName(type, kvps, stepElement) {
  // Direct from kvps
  if (kvps?.tool_name) return kvps.tool_name;
  
  // Keep existing if present (for non-tool types during updates)
  if (type !== 'tool' && stepElement?.hasAttribute('data-tool-name')) {
    return stepElement.getAttribute('data-tool-name');
  }
  
  // Inherit from previous sibling (for tool steps)
  if (type === 'tool' && stepElement) {
    let prev = stepElement.previousElementSibling;
    while (prev) {
      if (prev.hasAttribute('data-tool-name')) {
        return prev.getAttribute('data-tool-name');
      }
      prev = prev.previousElementSibling;
    }
  }
  
  return null;
}

/**
 * Update status badge text content
 */
function updateBadgeText(badge, newCode) {
  if (!badge) return;
  badge.textContent = newCode;
}

// Process types that should be grouped into collapsible sections
const PROCESS_TYPES = ['agent', 'tool', 'code_exe', 'browser', 'progress', 'hint', 'util', 'warning', 'rate_limit'];
// Main types that should always be visible (not collapsed)
const MAIN_TYPES = ['user', 'response', 'error', 'info'];

/**
 * Helper to append a message container to the correct group in chat history
 */
function appendMessageToHistory(messageContainer, groupType, forceNewGroup, id) {
  // Check if current messageGroup is still in DOM, if not, reset it (context switch)
  if (messageGroup && !document.getElementById(messageGroup.id)) {
    messageGroup = null;
  }

  // Create new group if needed
  if (!messageGroup || forceNewGroup || groupType !== messageGroup.getAttribute("data-group-type")) {
    messageGroup = document.createElement("div");
    messageGroup.id = `message-group-${id}`;
    messageGroup.classList.add("message-group", `message-group-${groupType}`);
    messageGroup.setAttribute("data-group-type", groupType);
    chatHistory.appendChild(messageGroup);
  }

  // Append message to group
  messageGroup.appendChild(messageContainer);
}

export function setMessage(id, type, heading, content, temp, kvps = null, timestamp = null, durationMs = null, agentNumber = 0) {
  // Check if this is a process type message
  const isProcessType = PROCESS_TYPES.includes(type);
  
  // Search for the existing message container by id
  let messageContainer = document.getElementById(`message-${id}`);
  let processStepElement = document.getElementById(`process-step-${id}`);

  // For user messages, close current process group FIRST (start fresh for next interaction)
  if (type === "user") {
    currentProcessGroup = null;
    currentDelegationSteps = {}; // Clear delegation tracking
  }

  // For process types, check if we should add to process group
  if (isProcessType || (type === "response" && agentNumber !== 0)) {
    if (processStepElement) {
      // Update existing process step
      updateProcessStep(processStepElement, id, type, heading, content, kvps, durationMs, agentNumber);
      return processStepElement;
    }
    
    // Create or get process group for current interaction
    if (!currentProcessGroup || !document.getElementById(currentProcessGroup.id)) {
      // Create response container for this process group immediately (Option B)
      messageContainer = document.createElement("div");
      messageContainer.id = `message-${id}`;
      messageContainer.classList.add("message-container", "ai-container", "has-process-group");
      
      currentProcessGroup = createProcessGroup(id);
      currentProcessGroup.classList.add("embedded");
      messageContainer.appendChild(currentProcessGroup);
      
      // Handle DOM insertion immediately
      appendMessageToHistory(messageContainer, "left", false, id);
      
      setActiveProcessGroup(currentProcessGroup);
    }
    
    // Add step to current process group
    const stepType = (type === "response" && agentNumber !== 0) ? "response" : type;
    processStepElement = addProcessStep(currentProcessGroup, id, stepType, heading, content, kvps, timestamp, durationMs, agentNumber);
    return processStepElement;
  }

  // For main agent (A0) response, mark the current process group as complete
  if (type === "response" && currentProcessGroup) {
    // Mark process group as complete (END state)
    markProcessGroupComplete(currentProcessGroup, heading);
  }

  if (!messageContainer) {
    // Create a new container if not found
    const sender = type === "user" ? "user" : "ai";
    messageContainer = document.createElement("div");
    messageContainer.id = `message-${id}`;
    messageContainer.classList.add("message-container", `${sender}-container`);
  }

  const handler = getHandler(type);
  handler(messageContainer, id, type, heading, content, temp, kvps);

  // If this is a new message (not yet in DOM), handle DOM insertion
  if (!messageContainer.parentNode) {
    // message type visual grouping
    const groupTypeMap = {
      user: "right",
      info: "mid",
      warning: "mid",
      error: "mid",
      rate_limit: "mid",
      util: "mid",
      hint: "mid",
      // anything else is "left"
    };
    //force new group on these types
    const groupStart = {
      response: true, // response starts a new group
      user: true, // user message starts a new group (each user message should be separate)
      // anything else is false
    };

    const groupType = groupTypeMap[type] || "left";
    const forceNewGroup = groupStart[type] || false;

    appendMessageToHistory(messageContainer, groupType, forceNewGroup, id);
  }

  return messageContainer;
}

// Legacy copy button functions removed - now using action buttons component

export function getHandler(type) {
  switch (type) {
    case "user":
      return drawMessageUser;
    case "agent":
      return drawMessageAgent;
    case "response":
      return drawMessageResponse;
    case "tool":
      return drawMessageTool;
    case "code_exe":
      return drawMessageCodeExe;
    case "browser":
      return drawMessageBrowser;
    case "warning":
      return drawMessageWarning;
    case "rate_limit":
      return drawMessageWarning;
    case "error":
      return drawMessageError;
    case "info":
      return drawMessageInfo;
    case "util":
      return drawMessageUtil;
    case "hint":
      return drawMessageInfo;
    default:
      return drawMessageDefault;
  }
}

// draw a message with a specific type
export function _drawMessage(
  messageContainer,
  heading,
  content,
  temp,
  followUp,
  mainClass = "",
  kvps = null,
  messageClasses = [],
  contentClasses = [],
  latex = false,
  markdown = false,
  resizeBtns = true
) {
  // Find existing message div or create new one
  let messageDiv = messageContainer.querySelector(".message");
  if (!messageDiv) {
    messageDiv = document.createElement("div");
    messageDiv.classList.add("message");
    messageContainer.appendChild(messageDiv);
  }

  // Update message classes
  messageDiv.className = `message ${mainClass} ${messageClasses.join(" ")}`;

  // Handle heading (important for error/rate_limit messages that show context)
  if (heading) {
    let headingElement = messageDiv.querySelector(".msg-heading");
    if (!headingElement) {
      headingElement = document.createElement("div");
      headingElement.classList.add("msg-heading");
      messageDiv.insertBefore(headingElement, messageDiv.firstChild);
    }

    let headingH4 = headingElement.querySelector("h4");
    if (!headingH4) {
      headingH4 = document.createElement("h4");
      headingElement.appendChild(headingH4);
    }
    headingH4.innerHTML = convertIcons(escapeHTML(heading));

    // Remove heading if it exists but heading is null
    const existingHeading = messageDiv.querySelector(".msg-heading");
    if (existingHeading) {
      existingHeading.remove();
    }
  }

  // Find existing body div or create new one
  let bodyDiv = messageDiv.querySelector(".message-body");
  if (!bodyDiv) {
    bodyDiv = document.createElement("div");
    bodyDiv.classList.add("message-body");
    messageDiv.appendChild(bodyDiv);
  }

  // reapply scroll position or autoscroll
  const scroller = new Scroller(bodyDiv);

  // Handle KVPs incrementally
  drawKvpsIncremental(bodyDiv, kvps, false);

  // Handle content
  if (content && content.trim().length > 0) {
    if (markdown) {
      let contentDiv = bodyDiv.querySelector(".msg-content");
      if (!contentDiv) {
        contentDiv = document.createElement("div");
        bodyDiv.appendChild(contentDiv);
      }
      contentDiv.className = `msg-content ${contentClasses.join(" ")}`;

      let spanElement = contentDiv.querySelector("span");
      if (!spanElement) {
        spanElement = document.createElement("span");
        contentDiv.appendChild(spanElement);
      }

      let processedContent = content;
      processedContent = convertImageTags(processedContent);
      processedContent = convertImgFilePaths(processedContent);
      processedContent = convertFilePaths(processedContent);
      processedContent = marked.parse(processedContent, { breaks: true });
      processedContent = convertPathsToLinks(processedContent);
      processedContent = addBlankTargetsToLinks(processedContent);

      spanElement.innerHTML = processedContent;

      // KaTeX rendering for markdown
      if (latex) {
        spanElement.querySelectorAll("latex").forEach((element) => {
          katex.render(element.innerHTML, element, {
            throwOnError: false,
          });
        });
      }

      // Ensure action buttons exist
      addActionButtonsToElement(bodyDiv);
      adjustMarkdownRender(contentDiv);

    } else {
      let preElement = bodyDiv.querySelector(".msg-content");
      if (!preElement) {
        preElement = document.createElement("pre");
        preElement.classList.add("msg-content", ...contentClasses);
        preElement.style.whiteSpace = "pre-wrap";
        preElement.style.wordBreak = "break-word";
        bodyDiv.appendChild(preElement);
      } else {
        // Update classes
        preElement.className = `msg-content ${contentClasses.join(" ")}`;
      }

      let spanElement = preElement.querySelector("span");
      if (!spanElement) {
        spanElement = document.createElement("span");
        preElement.appendChild(spanElement);
      }

      spanElement.innerHTML = convertHTML(content);

      // Ensure action buttons exist
      addActionButtonsToElement(bodyDiv);

    }
  } else {
    // Remove content if it exists but content is empty
    const existingContent = bodyDiv.querySelector(".msg-content");
    if (existingContent) {
      existingContent.remove();
    }
  }

  // reapply scroll position or autoscroll
  scroller.reApplyScroll();

  if (followUp) {
    messageContainer.classList.add("message-followup");
  }

  return messageDiv;
}

export function addBlankTargetsToLinks(str) {
  const doc = new DOMParser().parseFromString(str, "text/html");

  doc.querySelectorAll("a").forEach((anchor) => {
    const href = anchor.getAttribute("href") || "";
    if (
      href.startsWith("#") ||
      href.trim().toLowerCase().startsWith("javascript")
    )
      return;
    if (
      !anchor.hasAttribute("target") ||
      anchor.getAttribute("target") === ""
    ) {
      anchor.setAttribute("target", "_blank");
    }

    const rel = (anchor.getAttribute("rel") || "").split(/\s+/).filter(Boolean);
    if (!rel.includes("noopener")) rel.push("noopener");
    if (!rel.includes("noreferrer")) rel.push("noreferrer");
    anchor.setAttribute("rel", rel.join(" "));
  });
  return doc.body.innerHTML;
}

export function drawMessageDefault(
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null
) {
  _drawMessage(
    messageContainer,
    heading,
    content,
    temp,
    false,
    "message-default",
    kvps,
    ["message-ai"],
    ["msg-json"],
    false,
    false
  );
}

export function drawMessageAgent(
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null
) {
  let kvpsFlat = null;
  if (kvps) {
    kvpsFlat = { ...kvps, ...(kvps["tool_args"] || {}) };
    delete kvpsFlat["tool_args"];
  }

  _drawMessage(
    messageContainer,
    heading,
    content,
    temp,
    false,
    "message-agent",
    kvpsFlat,
    ["message-ai"],
    ["msg-json"],
    false,
    false
  );
}

export function drawMessageResponse(
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null
) {
  _drawMessage(
    messageContainer,
    heading,
    content,
    temp,
    true,
    "message-agent-response",
    null,
    ["message-ai"],
    [],
    true,
    true
  );
}

export function drawMessageDelegation(
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null
) {
  _drawMessage(
    messageContainer,
    heading,
    content,
    temp,
    true,
    "message-agent-delegation",
    kvps,
    ["message-ai", "message-agent"],
    [],
    true,
    false
  );
}

export function drawMessageUser(
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null,
  latex = false
) {
  // Find existing message div or create new one
  let messageDiv = messageContainer.querySelector(".message");
  if (!messageDiv) {
    messageDiv = document.createElement("div");
    messageDiv.classList.add("message", "message-user");
    messageContainer.appendChild(messageDiv);
  } else {
    // Ensure it has the correct classes if it already exists
    messageDiv.className = "message message-user";
  }

  // Handle content
  let textDiv = messageDiv.querySelector(".message-text");
  if (content && content.trim().length > 0) {
    if (!textDiv) {
      textDiv = document.createElement("div");
      textDiv.classList.add("message-text");
      messageDiv.appendChild(textDiv);
    }
    let spanElement = textDiv.querySelector("pre");
    if (!spanElement) {
      spanElement = document.createElement("pre");
      textDiv.appendChild(spanElement);
    }
    spanElement.innerHTML = escapeHTML(content);
  } else {
    if (textDiv) textDiv.remove();
  }

  // Handle attachments
  let attachmentsContainer = messageDiv.querySelector(".attachments-container");
  if (kvps && kvps.attachments && kvps.attachments.length > 0) {
    if (!attachmentsContainer) {
      attachmentsContainer = document.createElement("div");
      attachmentsContainer.classList.add("attachments-container");
      messageDiv.appendChild(attachmentsContainer);
    }
    // Important: Clear existing attachments to re-render, preventing duplicates on update
    attachmentsContainer.innerHTML = ""; 

    kvps.attachments.forEach((attachment) => {
      const attachmentDiv = document.createElement("div");
      attachmentDiv.classList.add("attachment-item");

      const displayInfo = attachmentsStore.getAttachmentDisplayInfo(attachment);

      if (displayInfo.isImage) {
        attachmentDiv.classList.add("image-type");

        const img = document.createElement("img");
        img.src = displayInfo.previewUrl;
        img.alt = displayInfo.filename;
        img.classList.add("attachment-preview");
        img.style.cursor = "pointer";

        attachmentDiv.appendChild(img);
      } else {
        // Render as file tile with title and icon
        attachmentDiv.classList.add("file-type");

        // File icon
        if (
          displayInfo.previewUrl &&
          displayInfo.previewUrl !== displayInfo.filename
        ) {
          const iconImg = document.createElement("img");
          iconImg.src = displayInfo.previewUrl;
          iconImg.alt = `${displayInfo.extension} file`;
          iconImg.classList.add("file-icon");
          attachmentDiv.appendChild(iconImg);
        }

        // File title
        const fileTitle = document.createElement("div");
        fileTitle.classList.add("file-title");
        fileTitle.textContent = displayInfo.filename;

        attachmentDiv.appendChild(fileTitle);
      }

      attachmentDiv.addEventListener("click", displayInfo.clickHandler);

      attachmentsContainer.appendChild(attachmentDiv);
    });
  } else {
    if (attachmentsContainer) attachmentsContainer.remove();
  }

  // Render heading below message, if provided
  let headingElement = messageDiv.querySelector(".message-user-heading");
  if (heading && heading.trim() && heading.trim() !== "User message") {
    if (!headingElement) {
      headingElement = document.createElement("div");
      headingElement.className = "message-user-heading shiny-text";
    }
    headingElement.textContent = heading;
    messageDiv.appendChild(headingElement);
  } else if (headingElement) {
    headingElement.remove();
  }

  addActionButtonsToElement(messageDiv);

}

export function drawMessageTool(
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null
) {
  _drawMessage(
    messageContainer,
    heading,
    content,
    temp,
    true,
    "message-tool",
    kvps,
    ["message-ai"],
    ["msg-output"],
    false,
    false
  );
}

export function drawMessageCodeExe(
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null
) {
  _drawMessage(
    messageContainer,
    heading,
    content,
    temp,
    true,
    "message-code-exe",
    null,
    ["message-ai"],
    [],
    false,
    false
  );
}

export function drawMessageBrowser(
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null
) {
  _drawMessage(
    messageContainer,
    heading,
    content,
    temp,
    true,
    "message-browser",
    kvps,
    ["message-ai"],
    ["msg-json"],
    false,
    false
  );
}

export function drawMessageAgentPlain(
  mainClass,
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null
) {
  _drawMessage(
    messageContainer,
    heading,
    content,
    temp,
    false,
    mainClass,
    kvps,
    [],
    [],
    false,
    false
  );
  messageContainer.classList.add("center-container");
}

export function drawMessageInfo(
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null
) {
  return drawMessageAgentPlain(
    "message-info",
    messageContainer,
    id,
    type,
    heading,
    content,
    temp,
    kvps
  );
}

export function drawMessageUtil(
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null
) {
  _drawMessage(
    messageContainer,
    heading,
    content,
    temp,
    false,
    "message-util",
    kvps,
    [],
    ["msg-json"],
    false,
    false
  );
  messageContainer.classList.add("center-container");
}

export function drawMessageWarning(
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null
) {
  return drawMessageAgentPlain(
    "message-warning",
    messageContainer,
    id,
    type,
    heading,
    content,
    temp,
    kvps
  );
}

export function drawMessageError(
  messageContainer,
  id,
  type,
  heading,
  content,
  temp,
  kvps = null
) {
  // Create or get the message div
  let messageDiv = messageContainer.querySelector(".message");
  if (!messageDiv) {
    messageDiv = document.createElement("div");
    messageDiv.classList.add("message", "message-error-group");
    messageContainer.appendChild(messageDiv);
  }

  // Check if error group already exists
  let errorGroup = messageDiv.querySelector(".error-group");
  if (!errorGroup) {
    errorGroup = document.createElement("div");
    errorGroup.classList.add("error-group");
    errorGroup.setAttribute("data-error-id", id);
    
    // Create header (clickable for expand/collapse)
    const header = document.createElement("div");
    header.classList.add("error-group-header");
    
    // Expand icon (triangle)
    const expandIcon = document.createElement("span");
    expandIcon.classList.add("expand-icon");
    header.appendChild(expandIcon);
    
    // Status badge (before title)
    const badge = document.createElement("span");
    badge.classList.add("status-badge", "status-err");
    badge.textContent = "ERR";
    header.appendChild(badge);
    
    // Title
    const title = document.createElement("span");
    title.classList.add("error-title");
    title.textContent = "Error";
    header.appendChild(title);
    
    // Subtitle (short error description)
    const subtitle = document.createElement("span");
    subtitle.classList.add("error-subtitle");
    header.appendChild(subtitle);
    
    // Click handler for expand/collapse
    header.addEventListener("click", () => {
      errorGroup.classList.toggle("expanded");
    });
    
    errorGroup.appendChild(header);
    
    // Create content container (collapsible)
    const contentWrapper = document.createElement("div");
    contentWrapper.classList.add("error-group-content");
    
    const contentInner = document.createElement("div");
    contentInner.classList.add("error-content-inner");
    contentWrapper.appendChild(contentInner);
    
    errorGroup.appendChild(contentWrapper);
    messageDiv.appendChild(errorGroup);
    
    // Check detail mode and expand if needed
    const detailMode = window.Alpine?.store("preferences")?.detailMode || "current";
    if (detailMode === "current" || detailMode === "expanded") {
      errorGroup.classList.add("expanded");
    }
  }
  
  // Update subtitle with short error description
  const subtitle = errorGroup.querySelector(".error-subtitle");
  if (subtitle) {
    // Extract short description from heading or content
    let shortDesc = "";
    // Skip if heading is just "Error" (redundant with title)
    if (heading && heading.trim() && heading.trim().toLowerCase() !== "error") {
      shortDesc = heading.trim();
    } 
    // If no useful heading, try to extract from content
    if (!shortDesc && content && content.trim()) {
      const lines = content.trim().split("\n");
      // Look for the error line (usually last meaningful line or one matching ErrorType: pattern)
      for (let i = lines.length - 1; i >= 0; i--) {
        const line = lines[i].trim();
        if (line && /^[\w\.]+Error[:\s]/.test(line)) {
          shortDesc = line;
          break;
        }
      }
      // Fallback to first non-empty line if no error pattern found
      if (!shortDesc) {
        for (const line of lines) {
          if (line.trim() && !line.startsWith("Traceback")) {
            shortDesc = line.trim();
            break;
          }
        }
      }
    }
    // Truncate if too long
    if (shortDesc.length > 100) {
      shortDesc = shortDesc.substring(0, 97) + "...";
    }
    subtitle.textContent = shortDesc;
    subtitle.title = shortDesc; // Full text on hover
  }
  
  // Update content (full callstack)
  const contentInner = errorGroup.querySelector(".error-content-inner");
  if (contentInner && content) {
    contentInner.innerHTML = "";
    
    // Create pre element for callstack/content
    const pre = document.createElement("pre");
    pre.classList.add("error-callstack");
    pre.textContent = content;
    contentInner.appendChild(pre);
    
    // Add action buttons for copy functionality
    addActionButtonsToElement(contentInner);
  }
  
  messageContainer.classList.add("center-container");
}

function drawKvps(container, kvps, latex) {
  if (kvps) {
    const table = document.createElement("table");
    table.classList.add("msg-kvps");
    for (let [key, value] of Object.entries(kvps)) {
      const row = table.insertRow();
      row.classList.add("kvps-row");
      // Skip reasoning
      if (key === "reasoning") continue;
      if (key === "thoughts")
        // TODO: find a better way to determine special class assignment
        row.classList.add("msg-thoughts");

      const th = row.insertCell();
      th.textContent = convertToTitleCase(key);
      th.classList.add("kvps-key");

      const td = row.insertCell();
      const tdiv = document.createElement("div");
      tdiv.classList.add("kvps-val");
      td.appendChild(tdiv);

      if (Array.isArray(value)) {
        for (const item of value) {
          addValue(item);
        }
      } else {
        addValue(value);
      }

      // addActionButtonsToElement(tdiv);

      // autoscroll the KVP value if needed
      // if (getAutoScroll()) #TODO needs a better redraw system
      setTimeout(() => {
        tdiv.scrollTop = tdiv.scrollHeight;
      }, 0);

      function addValue(value) {
        if (typeof value === "object") value = JSON.stringify(value, null, 2);

        if (typeof value === "string" && value.startsWith("img://")) {
          const imgElement = document.createElement("img");
          imgElement.classList.add("kvps-img");
          imgElement.src = value.replace("img://", "/image_get?path=");
          imgElement.alt = "Image Attachment";
          tdiv.appendChild(imgElement);

          // Add click handler and cursor change
          imgElement.style.cursor = "pointer";
          imgElement.addEventListener("click", () => {
            openImageModal(imgElement.src, 1000);
          });
        } else {
          const pre = document.createElement("pre");
          const span = document.createElement("span");
          span.innerHTML = convertHTML(value);
          pre.appendChild(span);
          tdiv.appendChild(pre);

          // KaTeX rendering for markdown
          if (latex) {
            span.querySelectorAll("latex").forEach((element) => {
              katex.render(element.innerHTML, element, {
                throwOnError: false,
              });
            });
          }
        }
      }
    }
    container.appendChild(table);
  }
}

function drawKvpsIncremental(container, kvps, latex) {
  if (kvps) {
    // Find existing table or create new one
    let table = container.querySelector(".msg-kvps");
    if (!table) {
      table = document.createElement("table");
      table.classList.add("msg-kvps");
      container.appendChild(table);
    }

    // Get all current rows for comparison
    let existingRows = table.querySelectorAll(".kvps-row");
    // Filter out reasoning
    const kvpEntries = Object.entries(kvps).filter(([key]) => key !== "reasoning");

    // Update or create rows as needed
    kvpEntries.forEach(([key, value], index) => {
      let row = existingRows[index];

      if (!row) {
        // Create new row if it doesn't exist
        row = table.insertRow();
        row.classList.add("kvps-row");
      }

      // Update row classes
      row.className = "kvps-row";
      if (key === "thoughts") {
        row.classList.add("msg-thoughts");
      }

      // Handle key cell
      let th = row.querySelector(".kvps-key");
      if (!th) {
        th = row.insertCell(0);
        th.classList.add("kvps-key");
      }
      th.textContent = convertToTitleCase(key);

      // Handle value cell
      let td = row.cells[1];
      if (!td) {
        td = row.insertCell(1);
      }

      let tdiv = td.querySelector(".kvps-val");
      if (!tdiv) {
        tdiv = document.createElement("div");
        tdiv.classList.add("kvps-val");
        td.appendChild(tdiv);
      }

      // reapply scroll position or autoscroll
      const scroller = new Scroller(tdiv);

      // Clear and rebuild content (for now - could be optimized further)
      tdiv.innerHTML = "";

      // addActionButtonsToElement(tdiv);

      if (Array.isArray(value)) {
        for (const item of value) {
          addValue(item, tdiv);
        }
      } else {
        addValue(value, tdiv);
      }

      // reapply scroll position or autoscroll
      scroller.reApplyScroll();
    });

    // Remove extra rows if we have fewer kvps now
    while (existingRows.length > kvpEntries.length) {
      const lastRow = existingRows[existingRows.length - 1];
      lastRow.remove();
      existingRows = table.querySelectorAll(".kvps-row");
    }

    function addValue(value, tdiv) {
      if (typeof value === "object") value = JSON.stringify(value, null, 2);

      if (typeof value === "string" && value.startsWith("img://")) {
        const imgElement = document.createElement("img");
        imgElement.classList.add("kvps-img");
        imgElement.src = value.replace("img://", "/image_get?path=");
        imgElement.alt = "Image Attachment";
        tdiv.appendChild(imgElement);

        // Add click handler and cursor change
        imgElement.style.cursor = "pointer";
        imgElement.addEventListener("click", () => {
          imageViewerStore.open(imgElement.src, { refreshInterval: 1000 });
        });
      } else {
        const pre = document.createElement("pre");
        const span = document.createElement("span");
        span.innerHTML = convertHTML(value);
        pre.appendChild(span);
        tdiv.appendChild(pre);

        // Add action buttons to the row
        // const row = tdiv.closest(".kvps-row");
        // if (row) {
          // addActionButtonsToElement(pre);
        // }

        // KaTeX rendering for markdown
        if (latex) {
          span.querySelectorAll("latex").forEach((element) => {
            katex.render(element.innerHTML, element, {
              throwOnError: false,
            });
          });
        }
      }
    }
  } else {
    // Remove table if kvps is null/empty
    const existingTable = container.querySelector(".msg-kvps");
    if (existingTable) {
      existingTable.remove();
    }
  }
}

function convertToTitleCase(str) {
  return str
    .replace(/_/g, " ") // Replace underscores with spaces
    .toLowerCase() // Convert the entire string to lowercase
    .replace(/\b\w/g, function (match) {
      return match.toUpperCase(); // Capitalize the first letter of each word
    });
}

/**
 * Clean text value by removing standalone bracket lines and trimming
 * Handles both strings and arrays (filters out bracket-only items)
 */
function cleanTextValue(value) {
  if (Array.isArray(value)) {
    return value
      .filter(item => item && String(item).trim() && !/^[\[\]]$/.test(String(item).trim()))
      .join("\n");
  }
  if (typeof value === "object" && value !== null) {
    return JSON.stringify(value, null, 2);
  }
  return String(value).replace(/^\s*[\[\]]\s*$/gm, "").trim();
}

function convertImageTags(content) {
  // Regular expression to match <image> tags and extract base64 content
  const imageTagRegex = /<image>(.*?)<\/image>/g;

  // Replace <image> tags with <img> tags with base64 source
  const updatedContent = content.replace(
    imageTagRegex,
    (match, base64Content) => {
      return `<img src="data:image/jpeg;base64,${base64Content}" alt="Image Attachment" style="max-width: 250px !important;"/>`;
    }
  );

  return updatedContent;
}

function convertHTML(str) {
  if (typeof str !== "string") str = JSON.stringify(str, null, 2);

  let result = escapeHTML(str);
  result = convertImageTags(result);
  result = convertPathsToLinks(result);
  return result;
}

function convertImgFilePaths(str) {
  return str.replace(/img:\/\//g, "/image_get?path=");
}

function convertFilePaths(str) {
  return str.replace(/file:\/\//g, "/download_work_dir_file?path=");
}

export function convertIcons(str) {
  return str.replace(
    /icon:\/\/([a-zA-Z0-9_]+)/g,
    '<span class="icon material-symbols-outlined">$1</span>'
  );
}

function escapeHTML(str) {
  const escapeChars = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "'": "&#39;",
    '"': "&quot;",
  };
  return str.replace(/[&<>'"]/g, (char) => escapeChars[char]);
}

function convertPathsToLinks(str) {
  function generateLinks(match) {
    const parts = match.split("/");
    if (!parts[0]) parts.shift(); // drop empty element left of first "
    let conc = "";
    let html = "";
    for (const part of parts) {
      conc += "/" + part;
      html += `/<a href="#" class="path-link" onclick="openFileLink('${conc}');">${part}</a>`;
    }
    return html;
  }

  const prefix = `(?:^|[> \`'"\\n]|&#39;|&quot;)`;
  const folder = `[a-zA-Z0-9_\\/.\\-]`;
  const file = `[a-zA-Z0-9_\\-\\/]`;
  const suffix = `(?<!\\.)`;
  const pathRegex = new RegExp(
    `(?<=${prefix})\\/${folder}*${file}${suffix}`,
    "g"
  );

  // skip paths inside html tags, like <img src="/path/to/image">
  const tagRegex = /(<(?:[^<>"']+|"[^"]*"|'[^']*')*>)/g;

  return str
    .split(tagRegex) // keep tags & text separate
    .map((chunk) => {
      // if it *starts* with '<', it's a tag -> leave untouched
      if (chunk.startsWith("<")) return chunk;
      // otherwise run your link-generation
      return chunk.replace(pathRegex, generateLinks);
    })
    .join("");
}

function adjustMarkdownRender(element) {
  // find all tables in the element
  const elements = element.querySelectorAll("table");

  // wrap each with a div with class message-markdown-table-wrap
  elements.forEach((el) => {
    const wrapper = document.createElement("div");
    wrapper.className = "message-markdown-table-wrap";
    el.parentNode.insertBefore(wrapper, el);
    wrapper.appendChild(el);
  });

  // find all images
  const images = element.querySelectorAll("img");

  // wrap each image in <a>
  images.forEach((img) => {
    if (img.parentNode?.tagName === "A") return;
    const link = document.createElement("a");
    link.className = "message-markdown-image-wrap";
    link.href = img.src;
    img.parentNode.insertBefore(link, img);
    link.appendChild(img);
    link.onclick = (e) => (e.preventDefault(), imageViewerStore.open(img.src, { name: img.alt || "Image" }));
  });
}

class Scroller {
  constructor(element) {
    this.element = element;
    this.wasAtBottom = this.isAtBottom();
  }

  isAtBottom(tolerance = 10) {
    const scrollHeight = this.element.scrollHeight;
    const clientHeight = this.element.clientHeight;
    const distanceFromBottom =
      scrollHeight - this.element.scrollTop - clientHeight;
    return distanceFromBottom <= tolerance;
  }

  reApplyScroll() {
    if (this.wasAtBottom) this.element.scrollTop = this.element.scrollHeight;
  }
}

// ============================================
// Process Group Embedding Functions
// ============================================

// ============================================
// Process Group Functions
// ============================================

/**
 * Create a new collapsible process group
 */
function createProcessGroup(id) {
  const groupId = `process-group-${id}`;
  const group = document.createElement("div");
  group.id = groupId;
  group.classList.add("process-group");
  group.setAttribute("data-group-id", groupId);
  
  // Determine initial expansion state from current detail mode
  const initiallyExpanded = processGroupStore.shouldExpandGroup(groupId, true); // true = is active
  if (initiallyExpanded) {
    group.classList.add('expanded');
  }
  
  // Create header
  const header = document.createElement("div");
  header.classList.add("process-group-header");
  header.innerHTML = `
    <span class="expand-icon"></span>
    <span class="group-title">Processing...</span>
    <span class="status-badge status-gen group-status">GEN</span>
    <span class="group-metrics">
      <span class="metric-time" title="Start time"><span class="material-symbols-outlined">schedule</span><span class="metric-value">--:--</span></span>
      <span class="metric-steps" title="Steps"><span class="material-symbols-outlined">footprint</span><span class="metric-value">0</span></span>
      <span class="metric-notifications" title="Warnings/Info/Hint" hidden><span class="material-symbols-outlined">priority_high</span><span class="metric-value">0</span></span>
      <span class="metric-duration" title="Duration"><span class="material-symbols-outlined">timer</span><span class="metric-value">0s</span></span>
    </span>
  `;
  
  // Add click handler for expansion
  header.addEventListener("click", (e) => {
    // Toggle group (store directly modifies DOM - single source of truth)
    processGroupStore.toggleGroup(groupId);
  });
  
  group.appendChild(header);
  
  // Create content container
  const content = document.createElement("div");
  content.classList.add("process-group-content");
  
  // Create steps container
  const steps = document.createElement("div");
  steps.classList.add("process-steps");
  content.appendChild(steps);
  
  group.appendChild(content);
  
  return group;
}

/**
 * Create or get nested container within a parent step
 */
function getNestedContainer(parentStep) {
  let nestedContainer = parentStep.querySelector(".process-nested-container");
  
  if (!nestedContainer) {
    // Create new container
    nestedContainer = document.createElement("div");
    nestedContainer.classList.add("process-nested-container");
    
    // Create inner wrapper for animation support
    const innerWrapper = document.createElement("div");
    innerWrapper.classList.add("process-nested-inner");
    nestedContainer.appendChild(innerWrapper);
    
    parentStep.appendChild(nestedContainer);
    parentStep.classList.add("has-nested-steps");
  }
  
  // Return the inner wrapper for appending steps
  const innerWrapper = nestedContainer.querySelector(".process-nested-inner");
  return innerWrapper || nestedContainer; // Fallback to container if wrapper missing
}

/**
 * Schedule a step to collapse after a delay
 * Automatically handles cancellation on click and reset on hover
 */
function scheduleStepCollapse(stepElement, delayMs) {
  // Cancel any existing timeout for this step
  cancelStepCollapse(stepElement);
  
  // Schedule the collapse
  const timeoutId = setTimeout(() => {
    stepElement.classList.remove("step-expanded");
    stepCollapseTimeouts.delete(stepElement);
    // Clear user-pinned flag when auto-collapsing
    stepElement.removeAttribute("data-user-pinned");
  }, delayMs);
  
  // Store the timeout ID
  stepCollapseTimeouts.set(stepElement, timeoutId);
}

/**
 * Cancel a scheduled collapse for a step
 */
function cancelStepCollapse(stepElement) {
  const timeoutId = stepCollapseTimeouts.get(stepElement);
  if (timeoutId) {
    clearTimeout(timeoutId);
    stepCollapseTimeouts.delete(stepElement);
  }
}

/**
 * Add interaction handlers to prevent fighting with user
 * - Hover: cancels the collapse timeout (keeps step open while reading)
 * - Leave: starts a new timeout ONLY if user hasn't clicked (no explicit interaction)
 * - Click anywhere on step: permanently cancels auto-collapse (user wants it open)
 */
function addStepCollapseInteractionHandlers(stepElement) {
  // On hover, cancel the timeout to keep it open while user is reading
  stepElement.addEventListener("mouseenter", () => {
    if (stepElement.classList.contains("step-expanded")) {
      cancelStepCollapse(stepElement);
    }
  });
  
  // On leave, start a new timeout ONLY if user hasn't explicitly clicked
  stepElement.addEventListener("mouseleave", () => {
    // Don't restart timeout if user has explicitly interacted (clicked)
    if (stepElement.classList.contains("step-expanded") && 
        !stepElement.hasAttribute("data-user-pinned")) {
      scheduleStepCollapse(stepElement, STEP_COLLAPSE_DELAY_MS);
    }
  });
  
  // On click anywhere on step, permanently cancel auto-collapse
  stepElement.addEventListener("click", () => {
    if (stepElement.classList.contains("step-expanded")) {
      cancelStepCollapse(stepElement);
      // Mark as user-pinned so mouseleave won't restart timeout
      stepElement.setAttribute("data-user-pinned", "true");
    }
  });
}

/**
 * Add a step to a process group
 */
function addProcessStep(group, id, type, heading, content, kvps, timestamp = null, durationMs = null, agentNumber = 0) {
  // group with newest step becomes the active one
  setActiveProcessGroup(group);

  const groupId = group.getAttribute("data-group-id");
  let stepsContainer = group.querySelector(".process-steps");
  const isGroupCompleted = group.classList.contains("process-group-completed");
  
  // Create step element
  const step = document.createElement("div");
  step.id = `process-step-${id}`;
  step.classList.add("process-step");
  step.setAttribute("data-type", type);
  step.setAttribute("data-step-id", id);
  step.setAttribute("data-agent-number", agentNumber);
  
  // Resolve tool name (direct, inherited, or null)
  // For new steps, pass null as stepElement - inheritance uses stepsContainer query
  let toolNameToUse = kvps?.tool_name;
  if (type === 'tool' && !toolNameToUse) {
    const existingSteps = stepsContainer.querySelectorAll('.process-step[data-tool-name]');
    if (existingSteps.length > 0) {
      toolNameToUse = existingSteps[existingSteps.length - 1].getAttribute("data-tool-name");
    }
  }
  if (toolNameToUse) {
    step.setAttribute("data-tool-name", toolNameToUse);
  }
  
  // Store timestamp for duration calculation
  if (timestamp) {
    step.setAttribute("data-timestamp", timestamp);
    
    // Set group start time from first log item
    if (!group.getAttribute("data-start-timestamp")) {
      group.setAttribute("data-start-timestamp", timestamp);
      // Update header time metric immediately
      const timeMetricEl = group.querySelector(".metric-time .metric-value");
      if (timeMetricEl) {
        const date = new Date(parseFloat(timestamp) * 1000);
        const hours = String(date.getHours()).padStart(2, "0");
        const minutes = String(date.getMinutes()).padStart(2, "0");
        timeMetricEl.textContent = `${hours}:${minutes}`;
      }
    }
  }
  
  // Store duration from backend (used for final duration calculation)
  if (durationMs != null) {
    step.setAttribute("data-duration-ms", durationMs);
  }
  
  // Add message-util class for utility/info types (controlled by showUtils preference)
  if (type === "util" || type === "info" || type === "hint") {
    step.classList.add("message-util");
    // Apply current preference state
    if (preferencesStore.showUtils) {
      step.classList.add("show-util");
    }
  }
  
  // Get step info from heading (single source of truth: backend)
  const title = getStepTitle(heading, kvps, type);
  
  // Determine if this new step should be expanded
  const detailMode = preferencesStore.detailMode;
  let shouldExpand = false;
  
  if (detailMode === "expanded") {
    shouldExpand = true;
  } else if (detailMode === "current" && !isGroupCompleted) {
    // In "current" mode: expand new step, delay-collapse all previous steps
    shouldExpand = true;
    
    // Schedule collapse for ALL previously expanded steps
    const allExpandedSteps = stepsContainer.querySelectorAll(".process-step.step-expanded");
    allExpandedSteps.forEach(expandedStep => {
      // Don't schedule collapse for the newly added step (the current one)
      if (expandedStep.id !== `process-step-${id}`) {
        scheduleStepCollapse(expandedStep, STEP_COLLAPSE_DELAY_MS);
      }
    });
  }
  // In "collapsed" mode: shouldExpand stays false
  
  if (shouldExpand) {
    step.classList.add("step-expanded");
  }
  
  // Create step header
  const stepHeader = document.createElement("div");
  stepHeader.classList.add("process-step-header");
  
  // Status code and color class from store (maps backend types)
  const statusCode = processGroupStore.getStepCode(type, toolNameToUse);
  const statusColorClass = processGroupStore.getStatusColorClass(type, toolNameToUse);
  
  // Add status color class to step for cascading --step-accent to internal icons
  step.classList.add(statusColorClass);
  
  stepHeader.innerHTML = `
    <span class="step-expand-icon"></span>
    <span class="status-badge ${statusColorClass}">${statusCode}</span>
    <span class="step-title">${escapeHTML(title)}</span>
  `;
  
  // Add click handler for step expansion
  stepHeader.addEventListener("click", (e) => {
    e.stopPropagation();
    
    // Cancel any scheduled auto-collapse (user is manually toggling)
    cancelStepCollapse(step);
    
    // Toggle step (store directly modifies DOM - single source of truth)
    processGroupStore.toggleStep(groupId, id);
    
    // Clear user-pinned flag when manually toggling
    // (allows auto-collapse to work again on next expansion)
    step.removeAttribute("data-user-pinned");
  });
  
  step.appendChild(stepHeader);
  
  // Create step detail container
  const detail = document.createElement("div");
  detail.classList.add("process-step-detail");
  
  const detailContent = document.createElement("div");
  detailContent.classList.add("process-step-detail-content");
  
  // Add content to detail
  renderStepDetailContent(detailContent, content, kvps, type);
  
  detail.appendChild(detailContent);
  
  // Store step data on the element for fresh access on modal open
  step._stepData = {
    type,
    heading,
    content,
    kvps,
    timestamp,
    durationMs,
    agentNumber,
    toolName: toolNameToUse
  };
  
  // Add "View Details" button for full modal view (reads fresh data from step._stepData)
  const viewDetailsBtn = createViewDetailsButton(step);
  detail.appendChild(viewDetailsBtn);
  
  step.appendChild(detail);
  
  // Track delegation steps for nesting
  if (toolNameToUse === "call_subordinate") {
    currentDelegationSteps[agentNumber] = step;
  }
  
  // Determine where to append the step (main list or nested in parent)
  let appendTarget = stepsContainer;
  
  // Check if this step belongs to a subordinate agent
  if (agentNumber > 0 && currentDelegationSteps[agentNumber - 1]) {
    const parentStep = currentDelegationSteps[agentNumber - 1];
    appendTarget = getNestedContainer(parentStep);
    step.classList.add("nested-step");
  }
  
  // Remove shiny effect from the previously active step title (O(1))
  if (activeStepTitleEl) {
    activeStepTitleEl.classList.remove("shiny-text");
    activeStepTitleEl = null;
  }
  
  appendTarget.appendChild(step);
  
  // Add interaction handlers to prevent fighting with user during auto-collapse
  addStepCollapseInteractionHandlers(step);
  
  // Scroll terminal to bottom on initial render (including page refresh)
  const initialTerminal = step.querySelector(".terminal-output");
  if (initialTerminal) {
    initialTerminal.scrollTop = initialTerminal.scrollHeight;
  }
  
  // Update group header
  updateProcessGroupHeader(group);

  // Apply shiny effect to the active step title
  if (!isGroupCompleted && group.id === activeProcessGroupId) {
    const titleEl = step.querySelector(".process-step-header .step-title");
    if (titleEl) {
      titleEl.classList.add("shiny-text");
      activeStepTitleEl = titleEl;
    }
  }
  
  return step;
}

/**
 * Update an existing process step
 */
function updateProcessStep(stepElement, id, type, heading, content, kvps, durationMs = null, agentNumber = 0) {
  // Update title
  const titleEl = stepElement.querySelector(".step-title");
  if (titleEl) {
    const title = getStepTitle(heading, kvps, type);
    titleEl.textContent = title;
  }
  
  // Update duration from backend
  if (durationMs != null) {
    stepElement.setAttribute("data-duration-ms", durationMs);
  }
  
  // Update agent number if provided
  if (agentNumber !== undefined) {
    stepElement.setAttribute("data-agent-number", agentNumber);
  }
  
  // Resolve and update tool name + badge
  const toolNameToUse = resolveToolName(type, kvps, stepElement);
  if (toolNameToUse) {
    stepElement.setAttribute("data-tool-name", toolNameToUse);
    const newCode = processGroupStore.getStepCode(type, toolNameToUse);
    updateBadgeText(stepElement.querySelector(".status-badge"), newCode);
  }
  
  // Update detail content
  const detailContent = stepElement.querySelector(".process-step-detail-content");
  let skipFullRender = false;
  
  if (detailContent) {
    // Capture scroll state before re-render (uses existing Scroller pattern)
    const terminal = detailContent.querySelector(".terminal-output");
    const scroller = terminal ? new Scroller(terminal) : null;
    
    // For browser, update image src incrementally to avoid flashing
    if (type === "browser" && kvps?.screenshot) {
      const existingImg = detailContent.querySelector(".screenshot-img");
      const newSrc = kvps.screenshot.replace("img://", "/image_get?path=");
      if (existingImg) {
        // Only update if src actually changed
        if (!existingImg.src.endsWith(newSrc.split("?path=")[1])) {
          existingImg.src = newSrc;
        }
        // Skip full re-render to avoid flashing, but still update group header
        skipFullRender = true;
      }
    }
    
    if (!skipFullRender) {
      renderStepDetailContent(detailContent, content, kvps, type);
      
      // Re-apply scroll (stays at bottom if was at bottom)
      const newTerminal = detailContent.querySelector(".terminal-output");
      if (newTerminal && scroller?.wasAtBottom) {
        newTerminal.scrollTop = newTerminal.scrollHeight;
      }
    }
  }
  
  // Update stored step data for fresh access by modal
  const timestamp = stepElement._stepData?.timestamp; // preserve original timestamp
  stepElement._stepData = {
    type,
    heading,
    content,
    kvps,
    timestamp,
    durationMs,
    agentNumber,
    toolName: toolNameToUse
  };
  
  // Update parent group header
  const group = stepElement.closest(".process-group");
  if (group) {
    updateProcessGroupHeader(group);
  }
}

/**
 * Get a concise title for a process step
 */
function getStepTitle(heading, kvps, type) {
  // code_exe: show command when finished
  const showCommand = type === "code_exe" && kvps?.code && 
    /done_all|code_execution_tool/.test(heading || "");
  if (showCommand) {
    const s = kvps.session ?? kvps.Session;
    return `${s != null ? `[${s}] ` : ""}${kvps.runtime || "bash"}> ${kvps.code.trim()}`;
  }

  // Try to get a meaningful title from heading or kvps
  if (heading && heading.trim()) {
    return cleanStepTitle(heading, 100);
  }
  
  // For warnings/errors without heading, use content preview as title
  if ((type === "warning" || type === "error")) {
    // We'll show full content in detail, so just use type as title
    return type === "warning" ? "Warning" : "Error";
  }
  
  if (kvps) {
    // Try common fields for title
    if (kvps.tool_name) {
      const headline = kvps.headline ? cleanStepTitle(kvps.headline, 60) : '';
      return `${kvps.tool_name}${headline ? ': ' + headline : ''}`;
    }
    if (kvps.headline) {
      return cleanStepTitle(kvps.headline, 100);
    }
    if (kvps.query) {
      return truncateText(kvps.query, 100);
    }
    if (kvps.thoughts) {
      return truncateText(String(kvps.thoughts), 100);
    }
  }
  
  // Fallback: capitalize type (backend is source of truth)
  return type ? type.charAt(0).toUpperCase() + type.slice(1).replace(/_/g, ' ') : 'Process';
}

/**
 * Extract icon name from heading with icon:// prefix
 * Returns the icon name (e.g., "terminal") or null if no prefix found
 */
function extractIconFromHeading(heading) {
  if (!heading) return null;
  const match = String(heading).match(/^icon:\/\/([a-zA-Z0-9_]+)/);
  return match ? match[1] : null;
}

/**
 * Clean step title by removing icon:// prefixes and status phrases
 * Preserves agent markers (A1:, A2:, etc.) so users can see which subordinate agent is executing
 */
function cleanStepTitle(text, maxLength) {
  if (!text) return "";
  let cleaned = String(text);
  
  // Remove icon:// patterns (e.g., "icon://network_intelligence")
  cleaned = cleaned.replace(/icon:\/\/[a-zA-Z0-9_]+\s*/g, "");
  
  // Trim whitespace
  cleaned = cleaned.trim();
  
  return truncateText(cleaned, maxLength);
}

/**
 * Render content for step detail panel
 */
function renderStepDetailContent(container, content, kvps, type = null) {
  container.innerHTML = "";
  
  // Special handling for response type - show content as markdown (for subordinate responses)
  if (type === "response" && content && content.trim()) {
    const responseDiv = document.createElement("div");
    responseDiv.classList.add("step-response-content");
    
    // Parse markdown
    let processedContent = content;
    processedContent = convertImageTags(processedContent);
    processedContent = convertImgFilePaths(processedContent);
    processedContent = convertFilePaths(processedContent);
    processedContent = marked.parse(processedContent, { breaks: true });
    processedContent = convertPathsToLinks(processedContent);
    processedContent = addBlankTargetsToLinks(processedContent);
    
    responseDiv.innerHTML = processedContent;
    container.appendChild(responseDiv);
    return;
  }
  
  // Special handling for warning/error types - always show content prominently
  if ((type === "warning" || type === "error") && content && content.trim()) {
    const warningDiv = document.createElement("div");
    warningDiv.classList.add("step-warning-content");
    warningDiv.textContent = content;
    container.appendChild(warningDiv);
    // Don't return - also show kvps if present
  }
  
  // Special handling for code_exe type - render as terminal-style output
  if (type === "code_exe" && kvps) {
    const runtime = kvps.runtime || kvps.Runtime || "bash";
    const code = kvps.code || kvps.Code || "";
    const output = content || "";
    
    if (code || output) {
      const terminalDiv = document.createElement("div");
      terminalDiv.classList.add("step-terminal");
  
      // Show output if present (no truncation - CSS handles max-height)
      if (output && output.trim()) {
        const outputPre = document.createElement("pre");
        outputPre.classList.add("terminal-output");
        // Escape HTML first, then convert paths to clickable links
        let processedOutput = escapeHTML(output);
        processedOutput = convertPathsToLinks(processedOutput);
        outputPre.innerHTML = processedOutput;
        terminalDiv.appendChild(outputPre);
      }
      
      container.appendChild(terminalDiv);
    }
    
    // Still render thoughts if present (but not reasoning - that's native model thinking, not structured output)
    if (kvps.thoughts || kvps.thinking) {
      const thoughtKey = kvps.thoughts ? "thoughts" : "thinking";
      const thoughtValue = kvps[thoughtKey];
      renderThoughts(container, thoughtValue);
    }
    
    return;
  }
  
  // Add KVPs if present
  if (kvps && Object.keys(kvps).length > 0) {
    const kvpsDiv = document.createElement("div");
    kvpsDiv.classList.add("step-kvps");
    
    for (const [key, value] of Object.entries(kvps)) {
      // Skip internal/display keys
      if (key === "finished" || key === "attachments") continue;
      
      // Skip code_exe specific keys that we handle specially above
      if (type === "code_exe" && (key.toLowerCase() === "runtime" || key.toLowerCase() === "session" || key.toLowerCase() === "code")) {
        continue;
      }
      
      const lowerKey = key.toLowerCase();
      
      // Skip headline and tool_name - they're shown elsewhere
      if (lowerKey === "headline" || lowerKey === "tool_name") continue;
      
      // Skip query in agent steps - it's shown in the tool call step
      if (type === "agent" && lowerKey === "query") continue;
      
      // Special handling for thoughts - render with single lightbulb icon
      // Skip reasoning
      if (lowerKey === "reasoning") continue;
      if (lowerKey === "thoughts" || lowerKey === "thinking" || lowerKey === "reflection") {
        renderThoughts(kvpsDiv, value);
        continue;
      }
      
      // Special handling for tool_args - render only for tool/mcp types (skip for agent)
      if (lowerKey === "tool_args") {
        // Skip tool_args for agent steps - it's shown in the tool call step
        if (type === "agent") continue;
        
        if (typeof value !== "object" || value === null) continue;
        const argsDiv = document.createElement("div");
        argsDiv.classList.add("step-tool-args");
        
        // Icon mapping for common tool arguments
        const argIcons = {
          'query': 'search',
          'url': 'link',
          'path': 'folder',
          'file': 'description',
          'code': 'code',
          'command': 'terminal',
          'message': 'chat',
          'text': 'notes',
          'content': 'article',
          'name': 'label',
          'id': 'tag',
          'type': 'category',
          'document': 'description',
          'documents': 'folder_open',
          'queries': 'search'
        };
        
        for (const [argKey, argValue] of Object.entries(value)) {
          const argRow = document.createElement("div");
          argRow.classList.add("tool-arg-row");
          
          const argLabel = document.createElement("span");
          argLabel.classList.add("tool-arg-label");
          
          // Use icon if available, otherwise use text label
          const lowerArgKey = argKey.toLowerCase();
          if (argIcons[lowerArgKey]) {
            argLabel.innerHTML = `<span class="material-symbols-outlined">${argIcons[lowerArgKey]}</span>`;
          } else {
            argLabel.textContent = convertToTitleCase(argKey) + ":";
          }
          
          const argVal = document.createElement("span");
          argVal.classList.add("tool-arg-value");
          
          const argText = cleanTextValue(argValue);
          
          argVal.textContent = truncateText(argText, 300);
          
          argRow.appendChild(argLabel);
          argRow.appendChild(argVal);
          argsDiv.appendChild(argRow);
        }
        
        kvpsDiv.appendChild(argsDiv);
        continue;
      }
      
      const kvpDiv = document.createElement("div");
      kvpDiv.classList.add("step-kvp");
      
      const keySpan = document.createElement("span");
      keySpan.classList.add("step-kvp-key");
      
      // Icon mapping for common kvp keys
      const kvpIcons = {
        'query': 'search',
        'url': 'link',
        'path': 'folder',
        'file': 'description',
        'code': 'code',
        'command': 'terminal',
        'message': 'chat',
        'text': 'notes',
        'content': 'article',
        'name': 'label',
        'id': 'tag',
        'type': 'category',
        'runtime': 'memory',
        'result': 'output',
        'progress': 'pending',
        'document': 'description',
        'documents': 'folder_open',
        'queries': 'search',
        'screenshot': 'image'
      };
      
      // lowerKey already defined above
      if (kvpIcons[lowerKey]) {
        keySpan.innerHTML = `<span class="material-symbols-outlined">${kvpIcons[lowerKey]}</span>`;
      } else {
        keySpan.textContent = convertToTitleCase(key) + ":";
      }
      
      const valueSpan = document.createElement("div");
      valueSpan.classList.add("step-kvp-value");
      
      if (typeof value === "string" && value.startsWith("img://")) {
        const imgElement = document.createElement("img");
        imgElement.classList.add("screenshot-img");
        imgElement.src = value.replace("img://", "/image_get?path=");
        imgElement.alt = "Image Attachment";
        imgElement.style.cursor = "pointer";
        imgElement.style.maxWidth = "100%";
        imgElement.style.display = "block";
        imgElement.style.marginTop = "4px";
        
        // Add click handler and cursor change
        imgElement.addEventListener("click", () => {
          imageViewerStore.open(imgElement.src, { name: "Image Attachment" });
        });
        
        valueSpan.appendChild(imgElement);
      } else {
        const valueText = cleanTextValue(value);
        valueSpan.textContent = truncateText(valueText, 1000);
      }
      
      kvpDiv.appendChild(keySpan);
      kvpDiv.appendChild(valueSpan);
      kvpsDiv.appendChild(kvpDiv);
    }
    
    container.appendChild(kvpsDiv);
  }
  
  // Add main content if present (JSON content)
  if (content && content.trim()) {
    const pre = document.createElement("pre");
    pre.classList.add("msg-json");
    pre.textContent = truncateText(content, 1000);
    container.appendChild(pre);
  }
}

/**
 * Helper to render thoughts/reasoning with lightbulb icon
 */
function renderThoughts(container, value) {
  const thoughtsDiv = document.createElement("div");
  thoughtsDiv.classList.add("step-thoughts", "msg-thoughts");
  
  const thoughtText = cleanTextValue(value);
  
  if (thoughtText) {
    thoughtsDiv.innerHTML = `<span class="thought-icon material-symbols-outlined">lightbulb</span><span class="thought-text">${escapeHTML(thoughtText)}</span>`;
    container.appendChild(thoughtsDiv);
  }
}

/**
 * Create "View Details" button for opening step detail modal
 * @param {HTMLElement} stepElement - The step DOM element containing _stepData property
 */
function createViewDetailsButton(stepElement) {
  const btnContainer = document.createElement("div");
  btnContainer.classList.add("step-detail-actions");
  
  const btn = document.createElement("button");
  btn.classList.add("btn", "text-button");
  btn.innerHTML = '<span class="material-symbols-outlined">open_in_full</span> View Details';
  btn.title = "Open full step details in modal";
  
  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    // Read fresh data from the step element at click time
    const freshData = stepElement._stepData || {};
    stepDetailStore.showStepDetail(freshData);
  });
  
  btnContainer.appendChild(btn);
  return btnContainer;
}

/**
 * Update process group header with step count, status, and metrics
 */
function updateProcessGroupHeader(group) {
  const steps = group.querySelectorAll(".process-step");
  const titleEl = group.querySelector(".group-title");
  const statusEl = group.querySelector(".group-status");
  const metricsEl = group.querySelector(".group-metrics");
  const isCompleted = group.classList.contains("process-group-completed");
  
  const notificationsEl = metricsEl?.querySelector(".metric-notifications");
  if (notificationsEl) {
    const counts = { warning: 0, info: 0, hint: 0 };
    steps.forEach((step) => {
      const stepType = step.getAttribute("data-type");
      if (Object.prototype.hasOwnProperty.call(counts, stepType)) {
        counts[stepType] += 1;
      }
    });

    const totalNotifications = counts.warning + counts.info + counts.hint;
    const countEl = notificationsEl.querySelector(".metric-value");
    notificationsEl.classList.remove("status-wrn", "status-inf", "status-hnt");

    if (totalNotifications > 0) {
      if (countEl) {
        countEl.textContent = totalNotifications.toString();
      }
      if (counts.warning > 0) {
        notificationsEl.classList.add("status-wrn");
      } else if (counts.info > 0) {
        notificationsEl.classList.add("status-inf");
      } else {
        notificationsEl.classList.add("status-hnt");
      }
      notificationsEl.hidden = false;
      notificationsEl.title = `Warnings: ${counts.warning}, Info: ${counts.info}, Hints: ${counts.hint}`;
    } else {
      notificationsEl.hidden = true;
    }
  }
  
  // If completed, don't update metrics
  if (isCompleted) {
    return;
  }
  
  // Update group title with the latest agent step heading
  if (titleEl) {
    // Find the last "agent" type step
    const agentSteps = Array.from(steps).filter(step => step.getAttribute("data-type") === "agent");
    if (agentSteps.length > 0) {
      const lastAgentStep = agentSteps[agentSteps.length - 1];
      const lastHeading = lastAgentStep.querySelector(".step-title")?.textContent;
      if (lastHeading) {
        const cleanTitle = cleanStepTitle(lastHeading, 50);
        if (cleanTitle) {
          titleEl.textContent = cleanTitle;
        }
      }
    }
  }
  
  // Update step count in metrics - All GEN steps from all agents per process group
  const stepsMetricEl = metricsEl?.querySelector(".metric-steps .metric-value");
  if (stepsMetricEl) {
    const genSteps = group.querySelectorAll('.process-step[data-type="agent"]');
    stepsMetricEl.textContent = genSteps.length.toString();
  }
  
  // Update time metric
  const timeMetricEl = metricsEl?.querySelector(".metric-time .metric-value");
  const startTimestamp = group.getAttribute("data-start-timestamp");
  if (timeMetricEl && startTimestamp) {
    const date = new Date(parseFloat(startTimestamp) * 1000);
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    timeMetricEl.textContent = `${hours}:${minutes}`;
  }
  
  // Update duration metric
  const durationMetricEl = metricsEl?.querySelector(".metric-duration .metric-value");
  if (durationMetricEl && steps.length > 0) {
    // Calculate accumulated duration from backend data
    let accumulatedMs = 0;
    steps.forEach(step => {
      accumulatedMs += parseInt(step.getAttribute("data-duration-ms") || "0", 10);
    });
    
    // Check if last step is still in progress (no duration_ms set yet)
    const lastStep = steps[steps.length - 1];
    const lastStepDuration = lastStep.getAttribute("data-duration-ms");
    const lastStepTimestamp = lastStep.getAttribute("data-timestamp");
    
    if (lastStepDuration == null && lastStepTimestamp) {
      // Last step is in progress - add live elapsed time for this step only
      const lastStepStartMs = parseFloat(lastStepTimestamp) * 1000;
      const liveElapsedMs = Math.max(0, Date.now() - lastStepStartMs);
      accumulatedMs += liveElapsedMs;
    }
    
    durationMetricEl.textContent = formatDuration(accumulatedMs);
  }
  
  if (steps.length > 0) {
    // Get the last step's type for status
    const lastStep = steps[steps.length - 1];
    const lastType = lastStep.getAttribute("data-type");
    const lastToolName = lastStep.getAttribute("data-tool-name");
    const lastTitle = lastStep.querySelector(".step-title")?.textContent || "";
    
    // Update status badge
    if (statusEl) {
      // Status code and color class from store (maps backend types)
      const statusCode = processGroupStore.getStepCode(lastType, lastToolName);
      const statusColorClass = processGroupStore.getStatusColorClass(lastType, lastToolName);
      
      statusEl.textContent = statusCode;
      statusEl.className = `status-badge ${statusColorClass} group-status`;
    }
    
    // Update title
    if (titleEl) {
      // Prefer agent type steps for the group title as they contain thinking/planning info
      if (lastType === "agent" && lastTitle) {
        titleEl.textContent = cleanStepTitle(lastTitle, 50);
      } else {
        // Try to find the most recent agent step for a better title
        const agentSteps = group.querySelectorAll('.process-step[data-type="agent"]');
        if (agentSteps.length > 0) {
          const lastAgentStep = agentSteps[agentSteps.length - 1];
          const agentTitle = lastAgentStep.querySelector(".step-title")?.textContent || "";
          if (agentTitle) {
            titleEl.textContent = cleanStepTitle(agentTitle, 50);
            return;
          }
        }
        titleEl.textContent = cleanStepTitle(lastTitle, 50) || `Processing...`;
      }
    }
  }
}

/**
 * Truncate text to a maximum length
 */
function truncateText(text, maxLength) {
  if (!text) return "";
  text = String(text).trim();
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength - 3) + "...";
}

/**
 * Mark a process group as complete (END state)
 */
function markProcessGroupComplete(group, responseTitle) {
  if (!group) return;
  
  // Update status badge to END
  const statusEl = group.querySelector(".group-status");
  if (statusEl) {
    // statusEl.innerHTML = '<span class="badge-icon material-symbols-outlined">check</span>END';
    statusEl.innerHTML = 'END';
    statusEl.className = "status-badge status-end group-status";
  }
  
  // Update title if response title is available
  const titleEl = group.querySelector(".group-title");
  if (titleEl && responseTitle) {
    const cleanTitle = cleanStepTitle(responseTitle, 50);
    if (cleanTitle) {
      titleEl.textContent = cleanTitle;
    }
  }
  
  // Add completed class to group
  group.classList.add("process-group-completed");
  
  // Collapse all expanded steps when processing is done (in "current" mode) with delay
  const detailMode = preferencesStore.detailMode;
  if (detailMode === "current") {
    // Schedule collapse for all expanded steps (deterministic)
    const allExpandedSteps = group.querySelectorAll(".process-step.step-expanded");
    allExpandedSteps.forEach(expandedStep => {
      scheduleStepCollapse(expandedStep, FINAL_STEP_COLLAPSE_DELAY_MS);
    });
  }
  
  // Calculate final duration from backend data (sum of all step durations)
  const steps = group.querySelectorAll(".process-step");
  let totalDurationMs = 0;
  steps.forEach(step => {
    const durationMs = parseInt(step.getAttribute("data-duration-ms") || "0", 10);
    totalDurationMs += durationMs;
  });
  
  // Update duration metric with final value from backend
  const metricsEl = group.querySelector(".group-metrics");
  const durationMetricEl = metricsEl?.querySelector(".metric-duration .metric-value");
  if (durationMetricEl && totalDurationMs > 0) {
    durationMetricEl.textContent = formatDuration(totalDurationMs);
  }
}

/**
 * Reset process group state (called on context switch)
 */
export function resetProcessGroups() {
  currentProcessGroup = null;
  currentDelegationSteps = {};
  messageGroup = null;
  activeProcessGroupId = null;
  activeProcessGroupEl = null;
  window.activeProcessGroupId = null; // Keep window copy in sync
  if (activeStepTitleEl) {
    activeStepTitleEl.classList.remove("shiny-text");
  }
  activeStepTitleEl = null;
  
  // Clear all pending collapse timeouts
  stepCollapseTimeouts.forEach(timeoutId => clearTimeout(timeoutId));
  stepCollapseTimeouts.clear();
}

/**
 * Format Unix timestamp as date-time string (YYYY-MM-DD HH:MM:SS)
 */
function formatDateTime(timestamp) {
  const date = new Date(timestamp * 1000); // Convert seconds to milliseconds
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  const seconds = String(date.getSeconds()).padStart(2, "0");
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}
