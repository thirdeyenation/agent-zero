## 2024-05-24 - Accessibility improvements for icon-only buttons
**Learning:** Found several icon-only buttons missing aria-labels (e.g. in the message queue, attachments preview, and chat model setup). Screen readers require aria-labels or visually hidden text for icon-only buttons to convey their purpose.
**Action:** Always verify if an icon-only button has an `aria-label` attribute. If not, add one matching its `title` or tooltip.
