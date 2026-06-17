## 2026-06-17 - Icon-only ligatures need parent aria-labels
**Learning:** In Material Symbol setups like `<span class="material-symbols-outlined">vertical_align_top</span>`, the screen reader can read out the raw ligature text ("vertical align top") instead of the intent. It causes duplicate or confusing reads when buttons only have a title attribute.
**Action:** Always place `aria-hidden="true"` on the `<span>` ligature and a clear `aria-label` on the parent `<button>` so the screen reader interprets it as a single accessible control.
