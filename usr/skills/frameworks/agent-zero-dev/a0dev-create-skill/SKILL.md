---
name: "a0dev-create-skill"
description: "Build reusable instruction bundles following the SKILL.md standard."
version: "1.0.0"
author: "Agent Zero Team"
tags: ["agent-zero-dev", "skill", "instructions", "SKILL.md"]
trigger_patterns:
  - "create skill"
  - "new skill"
  - "add skill"
  - "build skill"
  - "/a0dev-create-skill"
---

# Agent Zero Dev: Create Skill

Skills are reusable instruction bundles that guide the agent through specific tasks. They follow the SKILL.md standard with YAML frontmatter and markdown content.

## Skill Location

```
usr/skills/
├── default/           # System skills (don't modify)
├── custom/            # Your skills go here
│   └── my-skill/
│       ├── SKILL.md   # Required: Main skill file
│       ├── scripts/   # Optional: Helper scripts
│       ├── templates/ # Optional: Templates
│       └── docs/      # Optional: Additional docs
└── frameworks/        # Multi-phase framework skills
```

## SKILL.md Format

```yaml
---
name: "skill-name"
description: "Clear description of what this skill does and when to use it"
version: "1.0.0"
author: "Your Name"
tags: ["category1", "category2"]
trigger_patterns:
  - "keyword that triggers"
  - "another trigger phrase"
  - "use skill-name"
---

# Skill Title

## When to Use
Describe the situations where this skill applies.

## The Process

### Step 1: First Action
Detailed instructions...

### Step 2: Second Action
More instructions...

## Examples
Show sample usage and expected outcomes.

## Tips
Additional guidance and best practices.
```

## Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique skill identifier (kebab-case) |
| `description` | Yes | One-line summary |
| `version` | No | Semantic version |
| `author` | No | Creator name |
| `tags` | No | Categorization tags |
| `trigger_patterns` | Yes | Phrases that activate this skill |

## Trigger Patterns

Trigger patterns are case-insensitive phrases that activate the skill:

```yaml
trigger_patterns:
  - "deploy to production"    # Exact phrase match
  - "ship it"                 # Short trigger
  - "production deploy"       # Alternative phrasing
  - "/deploy"                 # Command-style
```

**Best Practices:**
- Include 3-5 varied trigger phrases
- Mix formal and casual language
- Include command-style triggers (`/skill-name`)
- Avoid overly generic triggers

## Complete Example: Code Review Skill

```yaml
---
name: "code-review"
description: "Perform thorough code review with focus on quality and best practices"
version: "1.0.0"
author: "Agent Zero Team"
tags: ["development", "review", "quality"]
trigger_patterns:
  - "review code"
  - "code review"
  - "review this"
  - "check my code"
  - "/code-review"
---

# Code Review

Thorough code review focusing on quality, maintainability, and best practices.

## When to Use

- Before merging pull requests
- After completing a feature
- When refactoring existing code
- To learn from code patterns

## The Process

### Step 1: Understand Context

Before reviewing:
1. Identify the purpose of the code
2. Understand the broader system context
3. Note any constraints or requirements

### Step 2: Check Correctness

Review for:
- [ ] Logic errors
- [ ] Edge cases handled
- [ ] Error handling present
- [ ] Input validation

### Step 3: Assess Quality

Evaluate:
- [ ] Clear naming conventions
- [ ] Appropriate abstractions
- [ ] DRY (Don't Repeat Yourself)
- [ ] Single responsibility

### Step 4: Review Style

Check:
- [ ] Consistent formatting
- [ ] Meaningful comments
- [ ] Documentation updated
- [ ] Tests included

### Step 5: Provide Feedback

Structure feedback as:
- **Critical**: Must fix before merge
- **Important**: Should fix soon
- **Suggestion**: Nice to have improvements

## Output Format

```markdown
## Code Review: [File/Feature]

### Summary
[Brief overall assessment]

### Critical Issues
- [Issue 1]: [Location] - [Why it matters]

### Important Issues
- [Issue 1]: [Suggestion]

### Suggestions
- [Nice-to-have improvements]

### Strengths
- [What's done well]
```

## Tips

- Focus on the code, not the person
- Explain the "why" behind suggestions
- Acknowledge good patterns
- Be specific with line numbers/locations
```

## Adding Scripts

Skills can include helper scripts:

```
my-skill/
├── SKILL.md
└── scripts/
    ├── helper.py
    └── process.sh
```

Reference in SKILL.md:
```markdown
## Scripts

Run the helper script:
- `scripts/helper.py` - Processes input data
- `scripts/process.sh` - Sets up environment
```

## Adding Templates

Include reusable templates:

```
my-skill/
├── SKILL.md
└── templates/
    └── output.md
```

Reference in SKILL.md:
```markdown
## Templates

Use `templates/output.md` as the base for your output format.
```

## Using the Generator Script

```bash
python usr/skills/frameworks/agent-zero-dev/scripts/create_skill.py \
    code-review \
    "Perform thorough code review with focus on quality"
```

Generates: `usr/skills/custom/code-review/SKILL.md`

## Skill Best Practices

### DO

- ✅ Write clear, actionable instructions
- ✅ Include examples and expected outputs
- ✅ Use checklists for multi-step processes
- ✅ Provide output format templates
- ✅ Test with real scenarios

### DON'T

- ❌ Write vague or ambiguous instructions
- ❌ Assume context the agent won't have
- ❌ Use overly generic trigger patterns
- ❌ Skip the "When to Use" section
- ❌ Forget to version your skills

## Testing Skills

1. Create the skill in `usr/skills/custom/`
2. Ask the agent using a trigger phrase
3. Verify the skill loads correctly
4. Test with varied inputs
5. Refine based on results

## Next Steps

After creating a skill:
- Test with multiple trigger phrases
- Gather feedback on clarity
- Iterate on instructions
- Consider sharing with the community
