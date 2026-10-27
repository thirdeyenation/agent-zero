## 2024-10-27 - Icon Accessibility
**Learning:** Custom `<x-icon>` tags in icon-only buttons often lack screen-reader context if `aria-hidden="true"` isn't applied to the icon, and the wrapper button lacks an `aria-label`.
**Action:** Ensure icon-only buttons have an `aria-label` and internal icons are hidden from screen readers.
