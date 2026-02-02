---
name: "bmb-workflow"
description: "Design structured workflows with steps, menus, and cross-workflow communication."
version: "1.0.0"
author: "BMad Method"
tags: ["bmad-builder", "workflow", "design", "process"]
trigger_patterns:
  - "build workflow"
  - "create workflow"
  - "new workflow"
  - "workflow builder"
  - "/bmb-workflow"
---

# BMad Builder: Create Workflow

Design structured workflows with steps and cross-workflow communication.

## Overview

Workflows are structured processes that guide agents through complex tasks with:
- Sequential or branching steps
- Decision points and menus
- Cross-workflow communication
- Output artifacts

## Process

### 1. Define Purpose

What does this workflow accomplish?

**Questions:**
- What is the end goal?
- What inputs does it need?
- What outputs does it produce?
- Who triggers this workflow?

### 2. Map the Steps

Break the workflow into discrete steps:

```
Step 1: [Action]
    ↓
Step 2: [Action]
    ↓
Decision Point: [Condition]
    ├── Option A → Step 3a
    └── Option B → Step 3b
    ↓
Step 4: [Final Action]
```

### 3. Design Each Step

For each step, define:

```yaml
steps:
  - id: "step-1"
    name: "[Step Name]"
    description: "[What happens]"
    inputs:
      - "[input 1]"
    outputs:
      - "[output 1]"
    next: "step-2"  # or decision
```

### 4. Add Decision Points

For branching logic:

```yaml
decisions:
  - id: "decision-1"
    question: "[What determines the path?]"
    options:
      - label: "[Option A]"
        condition: "[When to choose]"
        next: "step-3a"
      - label: "[Option B]"
        condition: "[When to choose]"
        next: "step-3b"
```

### 5. Define Artifacts

What does the workflow produce?

```yaml
artifacts:
  - name: "[Artifact Name]"
    type: "document|code|data"
    template: "[Template reference]"
    location: "[Where it's saved]"
```

### 6. Cross-Workflow Communication

How does this workflow connect to others?

```yaml
triggers:
  incoming:
    - from: "[workflow-name]"
      event: "[trigger event]"
  outgoing:
    - to: "[workflow-name]"
      event: "[event to trigger]"
```

## Output

Generate the workflow definition:

```yaml
# workflow-name.workflow.yaml
name: "[Workflow Name]"
description: "[Purpose]"
trigger_command: "/[command-name]"

steps:
  - id: "step-1"
    # ... step definition

decisions:
  - id: "decision-1"
    # ... decision definition

artifacts:
  - name: "[Output]"
    # ... artifact definition
```

## Best Practices

1. **Single Purpose**: Each workflow should accomplish one clear goal
2. **Clear Entry/Exit**: Define explicit start conditions and completion criteria
3. **Recoverable**: Allow resuming from any step
4. **Documented**: Each step should explain what and why

## Next Steps

After creating a workflow:
- Test with real scenarios
- Use `bmb-module` to package with agents into a module
