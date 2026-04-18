
## 2024-05-18 - Added ARIA labels to queue, attachment, and task list icon-only buttons
**Learning:** Found several icon-only buttons across components (Message Queue, Input Preview, and Tasks List) lacking ARIA labels (`aria-label`), which hindered screen reader accessibility. Also noticed `bottom-actions.html` had icon buttons with visible text inside (`<span>Clear Chat</span>`), confirming these correctly did *not* need `aria-label`s to avoid screen reader redundancy.
**Action:** When auditing or implementing UI components, rigorously check all `btn-icon-action`, `queue-action-btn`, and similar icon-only functional buttons to ensure they have an explicit `aria-label` or `aria-labelledby` attribute for accessibility. Skip this only if the button visibly contains its descriptive text.
