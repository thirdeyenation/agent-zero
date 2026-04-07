## 2026-04-07 - Action Card Keyboard Accessibility
**Learning:** Custom interactive `div` elements used as buttons (like the action cards on the welcome screen) were missing core keyboard accessibility attributes, leaving them unusable for keyboard navigation.
**Action:** Always ensure custom UI buttons use `role="button"`, `tabindex="0"`, have `@keydown.enter` and `@keydown.space.prevent` handlers to match click behaviors, and include `:focus-visible` CSS mirroring the `:hover` state for visual clarity.
