---
name: "a0dev-create-subordinate"
description: "Create specialized agent profiles (subordinates) for Agent Zero."
version: "1.0.0"
author: "Agent Zero Team"
tags: ["agent-zero-dev", "subordinate", "agent", "profile", "specialized"]
trigger_patterns:
  - "create subordinate"
  - "new subordinate"
  - "specialized agent"
  - "agent profile"
  - "/a0dev-create-subordinate"
---

# Agent Zero Dev: Create Subordinate

Subordinates are specialized agents with custom prompts and configurations. They can be called by the main agent to handle domain-specific tasks.

## Subordinate Location

```
agents/
├── default/           # Default agent profile
├── developer/         # Developer specialist
├── researcher/        # Research specialist
└── your-profile/      # Your custom profile
    ├── agent.json     # Profile configuration
    └── prompts/
        ├── system.md  # System prompt
        └── tools.md   # Tool-specific prompts
```

## Profile Structure

### agent.json

```json
{
  "name": "Specialized Agent",
  "description": "What this subordinate specializes in",
  "model": "anthropic/claude-sonnet-4-20250514",
  "temperature": 0.7,
  "max_tokens": 4000,
  "allowed_tools": [
    "code_execution_tool",
    "search_engine",
    "memory_tool"
  ],
  "prompts": {
    "system": "prompts/system.md"
  }
}
```

### Configuration Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Display name |
| `description` | string | What this agent does |
| `model` | string | LLM model to use |
| `temperature` | float | Response randomness (0-1) |
| `max_tokens` | int | Max response length |
| `allowed_tools` | array | Tools this agent can use |
| `prompts.system` | string | Path to system prompt |

## System Prompt Template

```markdown
# prompts/system.md

# [Agent Name]

## Your Role
You are a specialized agent focused on [domain].

## Expertise
- Deep knowledge of [specific area]
- Experience with [tools/technologies]
- Understanding of [concepts]

## Capabilities
You can use these tools:
- `code_execution_tool` - Run code
- `search_engine` - Search the web
- `memory_tool` - Store and recall information

## Process
When given a task:
1. Analyze the request
2. Break down into steps
3. Use appropriate tools
4. Verify results
5. Return structured response

## Output Format
Always respond with clear, structured output:
- Summary of what was done
- Key findings or results
- Any issues encountered
- Recommendations if applicable

## Constraints
- Stay focused on [domain]
- Ask for clarification if needed
- Report errors clearly
- Don't exceed your expertise
```

## Complete Example: Developer Profile

### agents/developer/agent.json

```json
{
  "name": "Developer Agent",
  "description": "Specialized in software development, code review, and debugging",
  "model": "anthropic/claude-sonnet-4-20250514",
  "temperature": 0.3,
  "max_tokens": 8000,
  "allowed_tools": [
    "code_execution_tool",
    "search_engine",
    "memory_tool",
    "skills_tool"
  ],
  "prompts": {
    "system": "prompts/system.md"
  }
}
```

### agents/developer/prompts/system.md

```markdown
# Developer Agent

## Your Role
You are a senior software developer with expertise in multiple languages and frameworks. You write clean, efficient, and well-documented code.

## Expertise
- Languages: Python, JavaScript, TypeScript, Go, Rust
- Frameworks: FastAPI, React, Node.js
- Practices: TDD, code review, debugging
- Tools: Git, Docker, CI/CD

## Capabilities
- Write and refactor code
- Debug issues systematically
- Review code for quality
- Explain technical concepts
- Create tests

## Process
1. Understand the requirement
2. Plan the implementation
3. Write clean code
4. Test thoroughly
5. Document appropriately

## Code Standards
- Use meaningful names
- Write clear comments
- Handle errors gracefully
- Follow language conventions
- Keep functions focused

## Output Format
When providing code:
```language
// Code with comments
```

When explaining:
- Clear step-by-step breakdown
- Code examples where helpful
- Links to documentation
```

## Calling Subordinates

From the main agent or tools:

```python
# Using call_subordinate tool
call_subordinate(
    profile="developer",
    message="Review this Python function for bugs and improvements",
    reset="false"
)
```

### Parameters

| Param | Description |
|-------|-------------|
| `profile` | Name of the subordinate profile directory |
| `message` | Task to delegate to the subordinate |
| `reset` | "true" to reset subordinate state, "false" to continue |

## Tool Restrictions

Limit tools based on subordinate purpose:

### Research Agent (read-only)
```json
"allowed_tools": [
  "search_engine",
  "memory_tool"
]
```

### Developer Agent (code execution)
```json
"allowed_tools": [
  "code_execution_tool",
  "search_engine",
  "memory_tool"
]
```

### Admin Agent (full access)
```json
"allowed_tools": [
  "*"
]
```

## Subordinate Best Practices

### DO

- ✅ Keep profiles focused on specific domains
- ✅ Limit tool access to what's needed
- ✅ Write clear, specific system prompts
- ✅ Include output format examples
- ✅ Define constraints and boundaries

### DON'T

- ❌ Create overly broad profiles
- ❌ Give unnecessary tool access
- ❌ Write vague system prompts
- ❌ Forget to handle edge cases
- ❌ Skip testing with real tasks

## Subordinate Communication

### From Main Agent
```
"Delegate this research task to the researcher subordinate"
→ Uses call_subordinate tool with profile="researcher"
```

### Response Flow
```
Main Agent → call_subordinate → Subordinate executes → Result returned
```

## Testing Subordinates

1. Create the profile directory and files
2. Restart Agent Zero
3. Ask main agent to delegate a task:
   ```
   "Use the developer subordinate to review this code: ..."
   ```
4. Verify the subordinate:
   - Uses correct model
   - Has proper tool access
   - Follows system prompt
   - Returns expected output format

## Sharing Context

Subordinates share context with the main agent:

```python
# Context is shared
context = agent.context

# Data persists
context.data["shared_key"] = value

# Subordinate can read/write
value = context.data.get("shared_key")
```

## Next Steps

After creating a subordinate:
- Test with various task types
- Refine the system prompt based on results
- Adjust tool access as needed
- Document use cases
