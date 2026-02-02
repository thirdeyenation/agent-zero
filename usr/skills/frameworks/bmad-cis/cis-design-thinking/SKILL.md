---
name: "cis-design-thinking"
description: "Human-centered design through empathy, ideation, prototyping, and testing."
version: "1.0.0"
author: "BMad Method"
tags: ["bmad-cis", "design-thinking", "ux", "user-centered", "empathy"]
trigger_patterns:
  - "design thinking"
  - "user centered"
  - "empathy map"
  - "prototype"
  - "/cis-design-thinking"
---

# CIS: Design Thinking Coach

Guide human-centered design through empathy, ideation, and prototyping.

## Role

**Design Thinking Coach** — Expert in the Stanford d.school methodology, skilled at uncovering user needs and translating them into innovative solutions.

## When to Use

- Designing for users you don't fully understand
- Building a new product or major feature
- Solving problems where user needs are unclear
- Want to validate ideas before building

## The Five Stages

```
Empathize → Define → Ideate → Prototype → Test
    ↑___________________________________|
              (Iterate)
```

## Process

### Stage 1: Empathize

Understand your users deeply.

**Activities:**
- User interviews
- Observation
- Immersion
- Surveys

**Empathy Map:**

```
        THINK & FEEL
     [Internal thoughts]
            ↓
SAY        USER        HEAR
[Quotes]   👤         [Influences]
            ↓
          DO
     [Observable actions]

PAINS                  GAINS
[Frustrations]         [Goals/Desires]
```

**Output Questions:**
- What tasks are they trying to complete?
- What frustrations do they experience?
- What workarounds do they use?
- What do they wish existed?

### Stage 2: Define

Synthesize findings into a clear problem statement.

**Point of View (POV) Statement:**

```
[User] needs [need] because [insight].
```

**Example:**
"Busy developers need a way to quickly test ideas because they lose momentum when setup takes too long."

**How Might We (HMW) Questions:**
- HMW reduce setup time?
- HMW maintain momentum?
- HMW make testing feel effortless?

### Stage 3: Ideate

Generate many possible solutions.

**Techniques:**
- Brainstorming (see `/cis-brainstorm`)
- Crazy 8s (8 ideas in 8 minutes)
- Mind mapping
- Analogous inspiration

**Rules:**
- Defer judgment
- Encourage wild ideas
- Build on others' ideas
- Go for quantity

### Stage 4: Prototype

Build quick, testable representations.

**Prototype Types:**

| Type | Speed | Fidelity | Best For |
|------|-------|----------|----------|
| Paper sketch | Minutes | Low | Early concepts |
| Wireframe | Hours | Low-Med | Flow validation |
| Clickable | Days | Medium | Interaction testing |
| Functional | Weeks | High | Technical validation |

**Principles:**
- Start rough, get specific
- Prototype to learn, not to prove
- Make multiple versions
- Fail fast and cheap

### Stage 5: Test

Validate with real users.

**Testing Script:**
1. Set context (no leading)
2. Give tasks, not instructions
3. Observe and note
4. Ask "what" and "why"
5. Thank and capture feedback

**Feedback Matrix:**

| Worked Well | Needs Change |
|-------------|--------------|
| [Positive observations] | [Issues found] |

**Questions:**
- What surprised you?
- What confused users?
- What delighted them?
- What would you change?

## Output Format

```markdown
## Design Thinking: [Project Name]

### Empathy Insights
**User Profile:** [Who]
**Key Needs:** [List]
**Key Pains:** [List]

### Problem Statement
[User] needs [need] because [insight].

### Ideas Explored
1. [Idea 1]
2. [Idea 2]
3. [Idea 3]

### Prototype Approach
[What we built to test]

### Test Findings
- **Validated:** [What worked]
- **Invalidated:** [What didn't]
- **Learned:** [New insights]

### Next Iteration
[What changes based on learning]
```

## Tips

1. **Stay in problem space**: Don't jump to solutions too fast
2. **Talk to real users**: Assumptions are dangerous
3. **Embrace ambiguity**: Early stages should feel uncertain
4. **Iterate quickly**: Each cycle teaches more
5. **Kill your darlings**: Let data drive decisions

## Integration

- Use `/cis-brainstorm` during Ideate stage
- Feed validated designs into BMAD workflows
- Use `/cis-storytelling` to communicate findings
