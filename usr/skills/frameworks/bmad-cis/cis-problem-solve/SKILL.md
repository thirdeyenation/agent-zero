---
name: "cis-problem-solve"
description: "Systematic problem diagnosis and root cause analysis."
version: "1.0.0"
author: "BMad Method"
tags: ["bmad-cis", "problem-solving", "root-cause", "analysis", "5-whys"]
trigger_patterns:
  - "problem solve"
  - "root cause"
  - "diagnose"
  - "5 whys"
  - "/cis-problem-solve"
---

# CIS: Problem Solver

Systematic problem diagnosis and root cause analysis.

## Role

**Problem Solver** — Expert in structured analysis techniques that diagnose issues, identify root causes, and generate effective solutions.

## When to Use

- Facing a complex problem without clear cause
- Bug or issue keeps recurring
- Need to understand why something failed
- Want to prevent future problems

## Techniques

### 5 Whys

Drill down to root cause by asking "why" repeatedly.

**Process:**
1. State the problem clearly
2. Ask: "Why did this happen?"
3. For each answer, ask "Why?" again
4. Continue until you reach the root cause (usually 5 levels)

**Example:**
```
Problem: Users abandon checkout

Why? → Cart page is confusing
Why? → Too many options displayed
Why? → We show every upsell possibility
Why? → PM wanted to maximize revenue
Why? → No data on conversion impact
        ↓
Root: Lack of conversion metrics driving decisions
```

### Fishbone Diagram (Ishikawa)

Categorize potential causes visually.

```
        People    Process    Technology
            \        |        /
             \       |       /
              Problem Statement
             /       |       \
            /        |        \
     Environment  Materials   Measurement
```

**Categories to explore:**
- **People**: Skills, training, communication
- **Process**: Procedures, workflows, handoffs
- **Technology**: Tools, systems, integrations
- **Environment**: Context, constraints, resources
- **Materials**: Inputs, dependencies, data
- **Measurement**: Metrics, feedback, visibility

### Problem Framing

Ensure you're solving the right problem.

**Questions:**
1. What is the problem? (Observable symptoms)
2. Who is affected? (Stakeholders)
3. When does it occur? (Timing, triggers)
4. Where does it happen? (Context, scope)
5. What is the impact? (Severity, frequency)
6. What have we tried? (Previous attempts)

### MECE Analysis

Mutually Exclusive, Collectively Exhaustive breakdown.

**Rules:**
- Categories don't overlap (ME)
- Categories cover everything (CE)

**Example for "Low conversion":**
- Traffic problems (getting visitors)
- Engagement problems (keeping visitors)
- Conversion problems (converting visitors)
- Retention problems (keeping customers)

### Pareto Analysis (80/20)

Focus on the vital few causes.

1. List all potential causes
2. Estimate impact of each
3. Sort by impact
4. Focus on top 20% that cause 80% of problems

## Process

### 1. Define the Problem

Write a clear problem statement:
- **Vague**: "The app is slow"
- **Clear**: "Page load time exceeds 3s for 40% of users, causing 25% abandonment"

### 2. Gather Data

What evidence do we have?
- Logs and metrics
- User feedback
- Timeline of events
- Related changes

### 3. Generate Hypotheses

List possible causes without judgment:
- Technical factors
- Human factors
- Process factors
- External factors

### 4. Analyze Root Cause

Apply techniques:
- Use 5 Whys for linear causation
- Use Fishbone for complex causation
- Use MECE for comprehensive coverage

### 5. Validate

Test your hypothesis:
- Can you reproduce the issue?
- Does fixing the cause fix the problem?
- Do the data support your conclusion?

### 6. Recommend Solutions

For each root cause:
- Immediate fix (stop the bleeding)
- Permanent fix (prevent recurrence)
- Systemic fix (prevent similar issues)

## Output Format

```markdown
## Problem Analysis: [Title]

### Problem Statement
[Clear, measurable description]

### Impact
- **Users affected:** [Number/percentage]
- **Severity:** [High/Medium/Low]
- **Frequency:** [How often]

### Root Cause Analysis

#### 5 Whys
1. Why? → [Answer]
2. Why? → [Answer]
3. Why? → [Answer]
4. Why? → [Answer]
5. Why? → [Root cause]

#### Contributing Factors
- [Factor 1]
- [Factor 2]

### Root Cause
[Primary root cause statement]

### Recommendations

| Action | Type | Effort | Impact |
|--------|------|--------|--------|
| [Fix 1] | Immediate | Low | High |
| [Fix 2] | Permanent | Med | High |
| [Fix 3] | Systemic | High | Med |

### Prevention
[How to prevent similar problems]
```

## Tips

1. **Don't stop at symptoms**: "Server crashed" isn't root cause
2. **Verify each "why"**: Use data, not assumptions
3. **Consider multiple roots**: Complex problems often have several
4. **Focus on systems**: People make mistakes; systems allow them
5. **Document for future**: Root cause analysis is organizational learning

## Integration

- After analysis, use BMAD workflows to implement fixes
- Use `/cis-brainstorm` to generate solution options
- Feed prevention items into backlog
