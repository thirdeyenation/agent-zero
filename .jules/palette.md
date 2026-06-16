## 2024-06-16 - Icon-Only Buttons Material Symbols Accessibility
**Learning:** Icon-only buttons in this app often rely on Material Symbol ligatures (which screen readers read as text if not hidden).
**Action:** Always add `aria-label`s on the button with `aria-hidden="true"` on the icon itself.
