## 2024-05-24 - Screen Reader Compatibility for Material Symbol Ligatures
**Learning:** Screen readers announce the raw text of Material Symbol ligatures (like "vertical_align_top") if they are not explicitly hidden, which is confusing for users.
**Action:** When adding or updating icon-only buttons that rely on Material Symbol ligatures (e.g., `<span class="material-symbols-outlined">`), always add an `aria-label` to the parent `<button>` and explicitly set `aria-hidden="true"` on the inner `<span>`.
