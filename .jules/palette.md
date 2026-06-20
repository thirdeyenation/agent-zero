## 2024-06-20 - Ensure screen readers handle Material Symbols correctly
**Learning:** Screen readers may read the raw ligature text (like 'vertical_align_top') of Material Symbols in icon-only buttons if aria-hidden="true" is omitted.
**Action:** Always add aria-hidden="true" to inner <span> icons and an explicit aria-label to the parent <button> for icon-only components.
