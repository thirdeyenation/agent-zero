## 2024-06-10 - Native button styling regression on semantic replacement
**Learning:** Replacing an interactive `<div @click="..">` with a `<button>` inherently applies the browser's native button styles (e.g., appearance, borders, hardcoded text colors), overriding custom CSS even if some properties were inherited correctly.
**Action:** When converting custom `<div>` controls to `<button>` elements, always explicitly apply `appearance: none;` (and `-webkit-appearance: none;`) and explicitly specify `color` and `font-family` fallbacks in the CSS to preserve the original visual design.
