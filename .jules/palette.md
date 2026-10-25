## 2025-10-25 - Missing aria-labels on icon buttons
**Learning:** Icon-only buttons using the `btn-icon-action` class with title attributes were missing the `aria-label` attribute, preventing proper screen reader compatibility.
**Action:** When adding icon-only actions, ensure an `aria-label` is always included alongside the `title` attribute for accessibility, and add `aria-hidden="true"` to child icons.
