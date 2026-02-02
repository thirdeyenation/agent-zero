---
name: "a0dev-quickstart"
description: "5-minute quickstart guide to extending Agent Zero."
version: "1.0.0"
author: "Agent Zero Team"
tags: ["agent-zero-dev", "quickstart", "getting-started", "tutorial"]
trigger_patterns:
  - "quickstart"
  - "getting started"
  - "start extending"
  - "how to extend"
  - "/a0dev-quickstart"
---

# Agent Zero Dev: Quickstart

Get started extending Agent Zero in 5 minutes.

## Choose Your Extension Point

| Want To | Use | Location |
|---------|-----|----------|
| Add agent capability | **Tool** | `python/tools/` |
| Hook lifecycle events | **Extension** | `python/extensions/<hook>/` |
| Create instruction bundle | **Skill** | `usr/skills/custom/<name>/` |
| Add Web UI endpoint | **API** | `python/api/` |
| Create specialized agent | **Subordinate** | `agents/<profile>/` |
| Configure project | **Project** | `.a0proj/` |

## Quick Commands

```bash
# Create a new tool
python usr/skills/frameworks/agent-zero-dev/scripts/create_tool.py MyTool "Description"

# Create an extension
python usr/skills/frameworks/agent-zero-dev/scripts/create_extension.py agent_init MyExt "Description"

# Create a skill
python usr/skills/frameworks/agent-zero-dev/scripts/create_skill.py my-skill "Description"

# Create an API endpoint
python usr/skills/frameworks/agent-zero-dev/scripts/create_api.py MyEndpoint "Description"
```

## Framework Architecture

```
Agent Zero Framework
├── python/
│   ├── tools/          # Agent capabilities (inherit from Tool)
│   ├── extensions/     # Lifecycle hooks (numbered execution)
│   ├── api/            # FastAPI endpoints (inherit from ApiHandler)
│   └── helpers/        # Utility functions and base classes
├── usr/skills/
│   ├── default/        # Default skills
│   ├── custom/         # Your skills go here
│   └── frameworks/     # Multi-phase framework skills
├── agents/             # Subordinate profiles
└── memory/             # FAISS vector memory
```

## Key Patterns

1. **Extensions execute in numeric order** (`_10_*.py`, `_20_*.py`)
2. **Tools inherit from `Tool`** with async `execute()` method
3. **Skills use YAML frontmatter** + markdown content
4. **APIs inherit from `ApiHandler`** with `process()` method
5. **Everything is async/await** for non-blocking operations

## Minimal Examples

### Minimal Tool

```python
# python/tools/hello_tool.py
from python.helpers.tool import Tool, Response

class HelloTool(Tool):
    async def execute(self, name="World", **kwargs) -> Response:
        return Response(message=f"Hello, {name}!", break_loop=False)
```

### Minimal Extension

```python
# python/extensions/agent_init/_99_my_ext.py
from python.helpers.extension import Extension

class MyExtension(Extension):
    async def execute(self, **kwargs):
        print("Agent initialized!")
        return kwargs.get("data", {})
```

### Minimal Skill

```yaml
---
name: "my-skill"
description: "What this skill does"
trigger_patterns:
  - "trigger phrase"
---

# My Skill

Instructions for the agent to follow.
```

### Minimal API

```python
# python/api/my_endpoint.py
from python.helpers.api import ApiHandler, Request

class MyEndpoint(ApiHandler):
    async def process(self, input: dict, request: Request) -> dict:
        return {"message": "Hello from API!"}
```

## Development Workflow

```
1. Choose extension point → Tool, Extension, Skill, API, etc.
2. Generate boilerplate → Use scripts/ generators
3. Implement logic → Fill in your code
4. Test → Restart Agent Zero and verify
5. Iterate → Refine based on results
```

## Next Steps

- `/a0dev-create-tool` — Deep dive into tools
- `/a0dev-create-extension` — Deep dive into extensions
- `/a0dev-create-skill` — Deep dive into skills
- `/a0dev-create-api` — Deep dive into APIs
- `/a0dev-workflow` — Full development workflow

## Need Help?

Say "help me create a [tool/extension/skill/api]" and I'll guide you through it!
