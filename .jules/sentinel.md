## 2024-05-24 - Cross-Site Scripting (XSS) in UI Modals
**Vulnerability:** The confirm dialog component used `innerHTML` with string interpolation for dynamic arguments like `title`, `message`, `confirmText`, and `cancelText`, introducing a Cross-Site Scripting (XSS) vulnerability.
**Learning:** Reusable UI components that accept arbitrary text arguments are prone to XSS if they construct DOM elements using template literals and `innerHTML` instead of dynamically setting properties like `textContent` after DOM construction.
**Prevention:** Avoid `innerHTML` when rendering user-provided or dynamically constructed text variables in frontend modules. Render the skeleton HTML first, select the nodes, and populate their content using `textContent`.
