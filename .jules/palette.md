## 2024-04-04 - Interactive Alpine.js div elements require explicit keyboard accessibility
**Learning:** When using `div` elements as interactive buttons (like action cards on the welcome screen), they are not natively accessible to keyboard users or screen readers. This pattern is common when wrapping Alpine.js `@click` handlers.
**Action:** Always add `role="button"`, `tabindex="0"`, `@keydown.enter="$el.click()"`, and `@keydown.space.prevent="$el.click()"` to interactive `div` elements, and ensure focus styles are visible (e.g., matching `:hover` styles with `:focus-visible`).
