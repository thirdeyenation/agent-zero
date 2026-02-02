---
name: "cis-presentation"
description: "Structure and deliver persuasive presentations."
version: "1.0.0"
author: "BMad Method"
tags: ["bmad-cis", "presentation", "slides", "pitch", "public-speaking"]
trigger_patterns:
  - "presentation"
  - "create slides"
  - "pitch deck"
  - "prepare talk"
  - "/cis-presentation"
---

# CIS: Presentation Master

Structure and deliver persuasive presentations.

## Role

**Presentation Master** — Expert in presentation design, slide structure, and delivery techniques that engage audiences and drive action.

## When to Use

- Preparing a pitch or proposal
- Creating a technical talk
- Building a demo presentation
- Planning a meeting deck

## Presentation Structures

### The McKinsey Structure

Pyramid principle: Answer first, then support.

```
          Answer/Recommendation
         /          |          \
   Support 1    Support 2    Support 3
   /    \       /    \       /    \
Evidence  Evidence  Evidence
```

**Flow:**
1. Start with conclusion/recommendation
2. Group supporting arguments
3. Back each with evidence

### The TED Structure

Engage, teach, inspire.

1. **Hook** (30 sec): Grab attention
2. **Context** (2 min): Why this matters
3. **Core Content** (10 min): 3 main points
4. **Climax** (2 min): Key insight
5. **Call to Action** (30 sec): What now

### The Demo Structure

For product demonstrations:

1. **Problem Hook**: Pain they feel
2. **Solution Overview**: What you built
3. **Live Demo**: Show don't tell
4. **Deep Dive**: Key features
5. **Results**: Proof it works
6. **Next Steps**: How to get it

### The Status Update

For regular meetings:

1. **Progress**: What's done
2. **Plans**: What's next
3. **Problems**: Blockers/risks
4. **Asks**: What you need

## Process

### 1. Define Success

**Questions:**
- What should the audience think after?
- What should they feel?
- What should they do?

**Success Statement:**
"After this presentation, [audience] will [action] because they understand [key point]."

### 2. Know Your Audience

| Factor | Details |
|--------|---------|
| Who | [Roles, backgrounds] |
| Knowledge | [What they know already] |
| Concerns | [What worries them] |
| Goals | [What they want] |

### 3. Structure Content

**The Rule of Three:**
- 3 main points maximum
- 3 supporting items per point
- Audiences remember thirds

**Time Allocation:**
- 10% Opening (hook + context)
- 80% Body (main content)
- 10% Close (summary + CTA)

### 4. Design Slides

**One Idea Per Slide:**
- Not: "Features and Benefits and Pricing"
- Yes: "Feature X", then "Why It Matters", then "What It Costs"

**Visual Guidelines:**
- Max 6 words per bullet
- Max 6 bullets per slide
- High contrast colors
- Large readable fonts (24pt minimum)

**Slide Types:**

| Type | Use For | Design |
|------|---------|--------|
| Title | Topic introduction | Big text, simple |
| Key Point | Main argument | Single statement |
| Evidence | Support | Chart or quote |
| Demo | Live showing | Minimal, focus on product |
| Transition | Shift topics | Visual break |
| Summary | Wrap up | Bullet recap |

### 5. Craft the Opening

**Hook Types:**
- **Question**: Engage thinking
- **Statistic**: Surprise with data
- **Story**: Create empathy
- **Problem**: Establish stakes
- **Vision**: Paint future

**Example Hooks:**

Bad: "Today I'll talk about our new feature"
Good: "What if I told you we could cut deploy time by 80%?"

### 6. Nail the Close

**Strong Close Elements:**
- Summarize key points (3 max)
- Reinforce main message
- Clear call to action
- Memorable last line

**Close Formula:**
"We've seen [point 1], [point 2], and [point 3]. The takeaway is [main message]. I'm asking you to [specific action]."

## Output Format

### Presentation Outline

```markdown
## [Presentation Title]
**Audience:** [Who]
**Duration:** [Time]
**Goal:** [Success statement]

### Opening (X min)
- Hook: [Type and content]
- Context: [Why this matters now]
- Preview: [What we'll cover]

### Body

#### Point 1: [Title] (X min)
- Key message: [One sentence]
- Evidence: [What supports it]
- Slide concept: [Visual description]

#### Point 2: [Title] (X min)
[Same structure]

#### Point 3: [Title] (X min)
[Same structure]

### Close (X min)
- Summary: [3 points recap]
- Message: [Core takeaway]
- CTA: [Specific ask]

### Appendix
- [Backup slides for Q&A]
```

### Slide Script

```markdown
## Slide 1: [Title]
**Visual:** [Description]
**Say:** [Spoken words]
**Time:** [Duration]

## Slide 2: [Title]
[Same structure]
```

## Delivery Tips

1. **Practice out loud**: Silent reading isn't practice
2. **Time yourself**: Always run shorter than slot
3. **Anticipate questions**: Prepare backup slides
4. **Start strong**: First 30 seconds set the tone
5. **Pause strategically**: Let key points land
6. **End on time**: Respect the audience

## Integration

- Use `/cis-storytelling` for narrative structure
- Apply BMAD data for evidence slides
- Use `/cis-brainstorm` when stuck on content
