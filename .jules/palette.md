
## 2024-05-18 - Chat Navigation Accessibility
**Learning:** Icon-only navigation buttons in the chat area relied solely on `title` attributes, which can be inconsistent for screen reader users and often lead to raw icon ligature text (e.g., "vertical align top") being announced if the inner icon span isn't explicitly hidden from the accessibility tree.
**Action:** Consistently apply `aria-label`s to the parent button element and `aria-hidden="true"` to inner icon spans (like `material-symbols-outlined`) across all similar floating action button groups.
