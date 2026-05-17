## 2026-05-17 - Prevent XSS in generic UI components
**Vulnerability:** XSS vulnerability in `showConfirmDialog` via unsafe `innerHTML` interpolation of `title` and `message`.
**Learning:** Generic UI components that accept parameters often construct DOM elements using template literals and `innerHTML`, making them vulnerable if untrusted input is passed.
**Prevention:** Always use `textContent` for text-only inputs, or sanitize HTML inputs using `DOMPurify` (e.g., `sanitizeHtml`) before injecting them into the DOM.
