## 2024-07-06 - Improve accessibility for icon-only Material Symbol buttons
**Learning:** Screen readers will frustratingly read aloud raw ligature text (like 'vertical_align_top') when Material Symbols are used in icon-only buttons without proper ARIA attributes, causing user confusion.
**Action:** Always add an `aria-label` to the parent `<button>` and explicitly set `aria-hidden="true"` on the inner `<span>` when using ligature-based icons for icon-only interactive elements.
