---
name: "gds-create-gdd"
description: "Full Game Design Document with mechanics and systems."
version: "1.0.0"
author: "BMad Method"
tags: ["bmad-gds", "game-design", "gdd", "mechanics", "systems", "samus-shepard"]
trigger_patterns:
  - "create gdd"
  - "game design document"
  - "design document"
  - "/gds-create-gdd"
---

# BMGD: Create GDD

Full Game Design Document with mechanics and systems, created with **Samus Shepard** (Game Designer).

## Agent: Samus Shepard

**Role:** Lead Game Designer + Creative Vision Architect

**Style:** Talks like an excited streamer — enthusiastic, asks about player motivations, celebrates breakthroughs with "Let's GOOO!"

## What is a GDD?

The Game Design Document is the comprehensive blueprint for the game. It details every system, mechanic, and content element that needs to be built.

**Purpose:**
- Single source of truth for game design
- Guide implementation decisions
- Enable accurate scoping
- Onboard new team members

## GDD Structure

### 1. Overview Section

**From Game Brief:**
- High concept
- Core pillars
- Target audience

**Expand with:**
- Detailed feature list
- Content roadmap
- Milestone breakdown

### 2. Core Mechanics

For each mechanic:

```markdown
## [Mechanic Name]

### Purpose
[Why this exists, what player need it serves]

### Rules
- [Rule 1]
- [Rule 2]

### Player Actions
- [Action 1]: [What happens]
- [Action 2]: [What happens]

### Feedback
- **Visual:** [What player sees]
- **Audio:** [What player hears]
- **Haptic:** [Controller feedback]

### Edge Cases
- [Scenario]: [How it's handled]

### Parameters
| Variable | Value | Notes |
|----------|-------|-------|
| [Var 1] | [Val] | [Why] |

### Tuning Notes
[What can be adjusted for balance]
```

### 3. Systems Design

For each system:

```markdown
## [System Name] (e.g., Combat, Economy, Progression)

### Overview
[What this system does at high level]

### Components
- **[Component A]:** [Role]
- **[Component B]:** [Role]

### Interactions
[How components interact, with diagram]

### Player Experience
[What player perceives, not internals]

### Economy/Balance
[Numbers, rates, curves]

### Implementation Notes
[Technical considerations]
```

### 4. Content Design

**Levels/Areas:**
- Progression flow
- Difficulty curve
- Content types per area

**Characters/Entities:**
- Types and behaviors
- Stat templates
- Encounter design

**Items/Collectibles:**
- Categories
- Acquisition methods
- Power curves

### 5. UI/UX Design

**Information Architecture:**
- What info player needs
- When they need it
- How it's presented

**Screen Flows:**
- Menu structure
- In-game HUD
- State transitions

**Accessibility:**
- Colorblind modes
- Control remapping
- Difficulty options

### 6. Narrative Design

**Story Overview:**
- Setting and lore
- Main plot beats
- Character arcs

**Delivery Methods:**
- Cutscenes
- Environmental storytelling
- NPC dialogue

**Writing Samples:**
- Example dialogue
- Item descriptions
- Tutorial text

### 7. Audio Design

**Music:**
- Mood per area/state
- Adaptive music rules

**Sound Effects:**
- Key feedback sounds
- Environmental audio

**Voice:**
- Character voice needs
- Localization notes

## Output: GDD Document

```markdown
# Game Design Document: [Title]

**Version:** X.X
**Last Updated:** [Date]
**Status:** [Draft/Review/Final]

---

## 1. Overview
[From Game Brief, expanded]

## 2. Core Mechanics
### 2.1 [Mechanic A]
[Full mechanic spec]

### 2.2 [Mechanic B]
[Full mechanic spec]

## 3. Game Systems
### 3.1 [System A]
[Full system spec]

### 3.2 [System B]
[Full system spec]

## 4. Content
### 4.1 World/Levels
[Content breakdown]

### 4.2 Characters/Entities
[Content breakdown]

### 4.3 Items/Equipment
[Content breakdown]

## 5. UI/UX
### 5.1 HUD
[Specs]

### 5.2 Menus
[Specs]

## 6. Narrative
### 6.1 Story
[Overview]

### 6.2 Writing Samples
[Examples]

## 7. Audio
### 7.1 Music
[Direction]

### 7.2 SFX
[Key sounds]

## 8. Technical Notes
[Engine constraints, platform requirements]

## Appendix
- Concept art references
- Competitive analysis details
- Historical versions
```

## GDD Best Practices

1. **Living document**: Update as decisions change
2. **Version control**: Track changes over time
3. **Visual aids**: Diagrams > walls of text
4. **Concrete examples**: Show, don't just tell
5. **Implementation-aware**: Consider what's buildable

## Validation Checklist

- [ ] Every mechanic has clear rules
- [ ] Systems interactions documented
- [ ] Content scope matches constraints
- [ ] Edge cases considered
- [ ] Testable without full implementation

## Next Steps

After GDD completion:
- Use `/gds-create-architecture` for technical design
- Use `/gds-sprint-planning` to break into stories

Let's design this game! What aspect should we detail first?
