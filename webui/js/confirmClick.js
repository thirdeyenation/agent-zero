// Inline button two-click confirmation for destructive actions.
// First click arms, second click confirms, timeout resets.

const CONFIRM_TIMEOUT = 2000;
const CONFIRM_CLASS = 'confirming';
const CONFIRM_ICON = 'check';

const buttonStates = new WeakMap();

// Handles inline two-click confirmation for a button.
export function confirmClick(event, action) {
  const button = event.currentTarget;
  if (!button) return;

  const state = buttonStates.get(button);

  if (state?.confirming) {
    clearTimeout(state.timeoutId);
    resetButton(button, state);
    buttonStates.delete(button);
    action();
  } else {
    const iconEl = button.querySelector('.material-symbols-outlined, .material-icons-outlined');
    const originalIcon = iconEl?.textContent?.trim();
    
    const newState = {
      confirming: true,
      originalIcon,
      timeoutId: setTimeout(() => {
        resetButton(button, newState);
        buttonStates.delete(button);
      }, CONFIRM_TIMEOUT)
    };
    
    buttonStates.set(button, newState);
    
    // Apply confirming state
    button.classList.add(CONFIRM_CLASS);
    if (iconEl) {
      iconEl.textContent = CONFIRM_ICON;
    }
  }
}

// Reset button to original state
function resetButton(button, state) {
  button.classList.remove(CONFIRM_CLASS);
  const iconEl = button.querySelector('.material-symbols-outlined, .material-icons-outlined');
  if (iconEl && state.originalIcon) {
    iconEl.textContent = state.originalIcon;
  }
}

// Register Alpine magic helper
export function registerAlpineMagic() {
  if (globalThis.Alpine) {
    Alpine.magic('confirmClick', () => confirmClick);
  }
}
