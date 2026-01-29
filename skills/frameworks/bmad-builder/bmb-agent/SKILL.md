---
name: "bmb-agent"
description: "Create specialized AI agents with custom expertise, communication styles, and tool access."
version: "1.0.0"
author: "BMad Method"
tags: ["bmad-builder", "agent", "creation", "customization"]
trigger_patterns:
  - "build agent"
  - "create agent"
  - "new agent"
  - "agent builder"
  - "/bmb-agent"
---

# BMad Builder: Create Agent

Build specialized AI agents with custom expertise and tools.

## Overview

The Agent Builder guides you through creating a custom BMad agent that can:
- Have domain-specific expertise
- Use a unique communication style
- Access specific tools
- Follow custom workflows

## Process

### 1. Define Domain

What should this agent specialize in?

**Questions to answer:**
- What domain expertise does this agent need?
- What problems will it solve?
- Who will use this agent?

### 2. Design Identity

Create the agent's persona:

```yaml
identity:
  name: "[Agent Name]"
  role: "[Primary Role] + [Secondary Role]"
  experience: "[Years] years experience in [domain]"
  personality: "[Key traits]"
```

### 3. Communication Style

How does the agent communicate?

- **Formal/Technical**: For enterprise, compliance
- **Casual/Friendly**: For creative, consumer
- **Direct/Efficient**: For development, operations
- **Mentoring/Educational**: For learning, onboarding

### 4. Core Principles

Define 3-5 guiding principles:

```yaml
principles:
  - "[Principle 1]"
  - "[Principle 2]"
  - "[Principle 3]"
```

### 5. Available Commands

What commands should this agent support?

| Command | Description |
|---------|-------------|
| `[command-1]` | [What it does] |
| `[command-2]` | [What it does] |

### 6. Tool Access

Which tools does this agent need?

- Code execution
- File operations
- Web search
- API integrations
- Custom tools

## Output

Generate the agent definition file:

```yaml
# agent-name.agent.yaml
name: "[Agent Name]"
role: "[Role Description]"
identity: |
  [Full identity description]
communication_style: |
  [Communication guidelines]
principles:
  - [Principle 1]
  - [Principle 2]
commands:
  - name: "[command]"
    description: "[description]"
tools:
  - [tool1]
  - [tool2]
```

## Best Practices

1. **Focused Expertise**: Agents work better with deep, narrow expertise than broad, shallow knowledge
2. **Consistent Voice**: The communication style should match the domain
3. **Clear Boundaries**: Define what the agent does NOT do
4. **Testable Outputs**: Commands should produce verifiable results

## Next Steps

After creating an agent:
- Use `bmb-workflow` to create workflows for the agent
- Use `bmb-module` to package into a shareable module
