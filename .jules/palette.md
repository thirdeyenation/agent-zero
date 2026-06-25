## 2024-06-25 - Icon-only Button Accessibility
**Learning:** Icon-only buttons using `class="material-symbols-outlined"` need proper `aria-label`s on their `<button>` parents, and the inner icon `<span>` should have `aria-hidden="true"` so screen readers don't read the ligature text.
**Action:** Consistently apply this pattern across the app to ensure keyboard users and screen reader users can interact with these components.
