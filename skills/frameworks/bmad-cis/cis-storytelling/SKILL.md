---
name: "cis-storytelling"
description: "Craft compelling narratives for products and features."
version: "1.0.0"
author: "BMad Method"
tags: ["bmad-cis", "storytelling", "narrative", "communication", "pitch"]
trigger_patterns:
  - "storytelling"
  - "tell story"
  - "product story"
  - "narrative"
  - "/cis-storytelling"
---

# CIS: Storyteller

Craft compelling narratives for products and features.

## Role

**Storyteller** — Expert in narrative structure, persuasion, and translating technical concepts into stories that resonate with audiences.

## When to Use

- Communicating product vision
- Writing feature descriptions
- Creating launch narratives
- Pitching ideas to stakeholders
- Documentation that engages

## Story Structures

### The Hero's Journey (Product)

```
Ordinary World → Call to Adventure → Challenges → Transformation → Return
    (Pain)         (Discovery)        (Struggle)    (Success)      (Impact)
```

**Applied:**
1. User has a problem (ordinary world)
2. Discovers your product (call)
3. Learns and adopts (challenges)
4. Achieves goals (transformation)
5. Becomes advocate (return)

### Problem-Agitate-Solution (PAS)

Quick persuasion format:

1. **Problem**: State the pain clearly
2. **Agitate**: Make them feel it
3. **Solution**: Present your answer

**Example:**
- Problem: "Developers spend 40% of time on boilerplate"
- Agitate: "That's 2 days a week on code that adds zero value"
- Solution: "Our generator creates it in seconds"

### Before-After-Bridge (BAB)

Show transformation:

1. **Before**: Current state (struggle)
2. **After**: Desired state (success)
3. **Bridge**: How to get there (your solution)

### STAR Format

For specific examples:

- **Situation**: Set the context
- **Task**: What needed to be done
- **Action**: What was done
- **Result**: What happened (quantified)

## Process

### 1. Know Your Audience

**Questions:**
- Who are they?
- What do they care about?
- What do they already know?
- What objections might they have?

**Audience Map:**

| Audience | Cares About | Speaks In | Fears |
|----------|-------------|-----------|-------|
| Executives | ROI, risk | Business metrics | Failure |
| Developers | Efficiency | Technical terms | Maintenance |
| Users | Outcomes | Benefits | Complexity |

### 2. Define the Core Message

One sentence that captures everything:

"[Product] helps [audience] [achieve outcome] by [unique approach]."

**Test:** Can someone repeat it after hearing once?

### 3. Structure the Narrative

Choose framework based on goal:

| Goal | Use |
|------|-----|
| Sell/Persuade | PAS |
| Show transformation | BAB |
| Explain complex | Hero's Journey |
| Give example | STAR |

### 4. Add Emotional Hooks

Stories stick when they evoke emotion:

- **Surprise**: Unexpected stat or fact
- **Curiosity**: Unanswered question
- **Empathy**: Relatable character
- **Aspiration**: Vision of better future

### 5. Include Concrete Details

Abstract → Concrete:
- "Faster" → "3x faster"
- "Many users" → "10,000 developers"
- "Recently" → "Last Tuesday"

### 6. End with Call to Action

Every story should invite next step:
- "Try it now"
- "Let's discuss"
- "Sign up for beta"

## Output Formats

### Product Narrative

```markdown
## [Product Name]

### The Challenge
[Problem description with emotional hook]

### The Journey
[How users discover and adopt]

### The Transformation
[What changes for users]

### The Impact
[Results and outcomes with specifics]

### Join the Story
[Call to action]
```

### Feature Story

```markdown
## [Feature Name]: [Tagline]

**Before:** [Pain state]
**After:** [Success state]
**How:** [Feature description]

**Example:**
[STAR format example]

**Get Started:**
[Call to action]
```

### Pitch Deck Narrative

```markdown
Slide 1: Hook (Problem that grabs attention)
Slide 2: Pain (Agitate the problem)
Slide 3: Solution (Your answer)
Slide 4: How it works (Brief explanation)
Slide 5: Proof (Results, testimonials)
Slide 6: Vision (Where this goes)
Slide 7: Ask (What you want)
```

## Tips

1. **Start with conflict**: Stories need tension
2. **Show, don't tell**: Specific examples beat general claims
3. **Use "you"**: Direct address creates connection
4. **Keep it simple**: One main message, few supporting points
5. **End strong**: Last impression matters most

## Examples

**Weak:**
"Our platform improves developer productivity with various features."

**Strong:**
"Sarah spent 3 hours configuring her environment. Last Monday, she got a new laptop. This time? 12 minutes. That's what one command can do."

## Integration

- Use with `/cis-presentation` for full presentations
- Apply to BMAD product briefs and PRDs
- Use for release notes and documentation
