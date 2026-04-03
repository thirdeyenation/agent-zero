## 2025-02-14 - Notification Icon Keyboard Accessibility
**Learning:** Found a custom UI component (`.notification-toggle` div) acting as a button but missing keyboard interaction and ARIA roles. Interactive `div` elements used as buttons must include `role="button"`, `tabindex="0"`, and keyboard event handlers (`keydown.enter` and `keydown.space`) to be accessible.
**Action:** Always verify custom interactive `div`s have proper ARIA attributes and keyboard handlers, or replace them with semantic `<button>` tags when possible.
