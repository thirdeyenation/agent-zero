## 2026-03-25 - Improve Project List Accessibility
**Learning:** Icon-only action buttons relying on Google Material Symbols ligatures (e.g. "close", "edit", "delete") are read literally by screen readers unless `aria-hidden="true"` is applied to the symbol `<span/>` wrapper. Additionally, an `aria-label` is needed on the parent `<button>` for correct semantic meaning.
**Action:** When adding new icon buttons in the UI, apply `aria-label` to the `<button>` and add `aria-hidden="true"` to the inner material symbol span to prevent screen readers from reading the ligature.
