## 2025-02-23 - Add explicit aria-labels to icon-only sidebar buttons
**Learning:** Sidebar icon-only buttons for deleting, clearing, and viewing info had hover `title`s but lacked explicit `aria-label`s, rendering them partially inaccessible to screen readers that prioritize aria attributes or don't interpret titles effectively.
**Action:** Always add explicit `aria-label`s matching or expanding on the `title` attribute for icon-only action buttons across the UI.
