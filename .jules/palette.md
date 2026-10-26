## 2024-05-24 - Missing Aria-Labels on Chat Nav Buttons
**Learning:** Icon-only buttons with tooltips (`title`) still need explicit `aria-label` for screen readers in the chat history view.
**Action:** Always ensure that any icon-only button, especially structural/navigation ones like the chat scroll buttons, have an `aria-label` equivalent to their visual tooltip.
