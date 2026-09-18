## 2025-06-11 - Adding Keyboard Accessibility to Alpine.js Action Cards
**Learning:** When using structural UI elements like `.welcome-action-card` `<div>`s in Alpine.js for interactive behaviors (`@click`), they must explicitly include `role="button"`, `tabindex="0"`, and keyboard event handlers (`@keydown.enter` and `@keydown.space.prevent`) to be accessible to keyboard and screen reader users. The application heavily relies on these custom div-based cards without inherent keyboard focusability.
**Action:** Always scan for `@click` handlers on non-native interactive elements (like `<div>` or `<span>`) across the codebase and ensure they are paired with appropriate ARIA roles, tabindex, and keydown listeners to guarantee WCAG compliance.

## 2024-10-24 - Add ARIA Labels and convert icon tags in UI

**Learning:** Legacy `<span class="material-symbols-outlined">` tags without screen-reader exclusion or wrapping `<button>` ARIA labels impair accessibility for icon-only buttons. The system prefers `<x-icon name="...">` custom tags with `aria-hidden="true"`, enclosed in `aria-label`ed buttons.
**Action:** Replaced lingering legacy `<span>` tags in progress and welcome screens with accessible `<x-icon>` tags and ensured appropriate parent container `aria-label` assignments.
