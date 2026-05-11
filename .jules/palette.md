## 2024-05-11 - Add ARIA labels and hide ligature text for icon-only buttons
**Learning:** Icon-only buttons using ligature fonts (like Material Symbols) need both `aria-label` on the button and `aria-hidden="true"` on the inner ligature icon, otherwise screen readers read the raw ligature text instead of the button's intended purpose.
**Action:** Always add `aria-hidden="true"` to `<span class="material-symbols-outlined">` and ensure the parent button has an `aria-label` when the button is icon-only.
