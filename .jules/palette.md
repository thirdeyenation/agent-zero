## 2024-04-16 - Make custom div buttons accessible
**Learning:** Found custom interactive `div` elements used as buttons (`.welcome-action-card`) that lacked accessibility attributes and keyboard support.
**Action:** Always ensure that custom interactive elements used as buttons have `role="button"`, `tabindex="0"`, keyboard event handlers (`@keydown.enter`, `@keydown.space.prevent`), and `:focus-visible` styles paired with their hover styles.
