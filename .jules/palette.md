## 2025-05-07 - Add ARIA labels to task action buttons
**Learning:** Found missing ARIA labels on icon-only buttons in the task list components (`webui/components/sidebar/tasks/tasks-list.html`). The buttons only had `title` attributes and contained visible ligature text which is problematic for screen readers.
**Action:** When adding `aria-label` to icon-only buttons, always ensure to add `aria-hidden="true"` to the inner element containing ligature text (e.g., `<span class="material-symbols-outlined">`) to prevent garbled readouts.
