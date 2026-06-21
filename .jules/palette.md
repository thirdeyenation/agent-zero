## 2024-06-21 - Add ARIA Labels to Icon-Only Chat Navigation Buttons
**Learning:** Icon-only buttons that use Material Symbols ligatures (like `<span class="material-symbols-outlined">keyboard_arrow_up</span>`) will cause screen readers to read the raw ligature text (e.g., 'keyboard_arrow_up') if not properly hidden.
**Action:** Always add `aria-hidden="true"` to the inner `<span>` containing the ligature and explicitly set a descriptive `aria-label` on the parent `<button>` for all icon-only buttons to ensure clear screen reader announcements.
