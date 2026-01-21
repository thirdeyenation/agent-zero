// Message Action Buttons - Copy and Speak functionality
import { store as speechStore } from "/components/chat/speech/speech-store.js";

/**
 * Copy text to clipboard with fallback for non-secure contexts
 */
async function copyToClipboard(text) {
  if (navigator.clipboard && window.isSecureContext) {
    await navigator.clipboard.writeText(text);
  } else {
    // Fallback for local dev / non-secure contexts
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.style.cssText = "position:fixed;left:-9999px";
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
  }
}

/**
 * Show visual feedback on a button (success/error state)
 */
function showButtonFeedback(button, success, originalIcon) {
  const icon = button.querySelector(".material-symbols-outlined");
  if (!icon) return;
  
  icon.textContent = success ? "check" : "error";
  button.classList.add(success ? "success" : "error");
  
  setTimeout(() => {
    icon.textContent = originalIcon;
    button.classList.remove("success", "error");
  }, 2000);
}

/**
 * Create action button element
 */
function createButton(iconName, label, className) {
  const btn = document.createElement("button");
  btn.className = `action-button ${className}`;
  btn.setAttribute("aria-label", label);
  btn.setAttribute("title", label);
  btn.innerHTML = `<span class="material-symbols-outlined">${iconName}</span>`;
  return btn;
}

/**
 * Add action buttons (copy, speak, optionally view details) to an element
 * 
 * @param {HTMLElement} container - Element to append buttons to
 * @param {Object} options - Configuration
 * @param {string|Function|HTMLElement} options.contentRef - Text content source:
 *   - string: Use directly
 *   - Function: Call to get text
 *   - HTMLElement: Get innerText from element
 * @param {Function} [options.onViewDetails] - If provided, adds view details button
 */
export function addActionButtonsToElement(container, options = {}) {
  const { contentRef, onViewDetails } = options;
  
  // Skip if buttons already exist
  if (container.querySelector(".step-action-buttons")) return;
  
  // Create buttons container
  const buttonsDiv = document.createElement("div");
  buttonsDiv.className = "step-action-buttons";
  
  // Helper to resolve content from contentRef
  const getContent = () => {
    if (typeof contentRef === "string") return contentRef;
    if (typeof contentRef === "function") return contentRef();
    if (contentRef instanceof HTMLElement) return contentRef.innerText || "";
    return "";
  };
  
  // View Details button (optional)
  if (onViewDetails) {
    const viewBtn = createButton("open_in_full", "View details", "view-details-action");
    viewBtn.onclick = (e) => {
      e.stopPropagation();
      onViewDetails();
    };
    buttonsDiv.appendChild(viewBtn);
  }
  
  // Copy button
  const copyBtn = createButton("content_copy", "Copy text", "copy-action");
  copyBtn.onclick = async (e) => {
    e.stopPropagation();
    const text = getContent();
    if (!text) return;
    
    try {
      await copyToClipboard(text);
      showButtonFeedback(copyBtn, true, "content_copy");
    } catch (err) {
      console.error("Copy failed:", err);
      showButtonFeedback(copyBtn, false, "content_copy");
    }
  };
  buttonsDiv.appendChild(copyBtn);
  
  // Speak button
  const speakBtn = createButton("volume_up", "Speak text", "speak-action");
  speakBtn.onclick = async (e) => {
    e.stopPropagation();
    const text = getContent();
    if (!text?.trim()) return;
    
    try {
      showButtonFeedback(speakBtn, true, "volume_up");
      await speechStore.speak(text);
    } catch (err) {
      console.error("Speech failed:", err);
      showButtonFeedback(speakBtn, false, "volume_up");
    }
  };
  buttonsDiv.appendChild(speakBtn);
  
  container.appendChild(buttonsDiv);
}
