---
name: "agent-zero-dev"
description: "Development framework for extending and building features for the Agent Zero AI framework. Provides patterns, templates, and best practices for creating tools, extensions, skills, API endpoints, subordinate profiles, and framework components."
version: "1.0.0"
author: "Agent Zero Team"
tags: ["development", "framework", "agent-zero", "extending", "tools", "extensions", "skills", "api"]
trigger_patterns:
  - "extend agent zero"
  - "agent zero development"
  - "build agent zero feature"
  - "create agent zero tool"
  - "add extension"
  - "framework development"
  - "agent zero skill"
---

# Agent Zero Development Framework

This framework provides comprehensive guidance for extending and building features for the Agent Zero AI framework. Use this skill when you need to:

- Create new **Tools** for agent capabilities
- Add **Extensions** to hook into framework lifecycle
- Build **Skills** following the SKILL.md standard
- Develop **API Endpoints** for the Web UI
- Create **Subordinate Profiles** for specialized agents
- Extend **Projects** with custom configuration
- Understand framework **Architecture** and patterns

## Quick Start

Choose your extension point:

| Component | Use Case | Location |
|-----------|----------|----------|
| **Tools** | Add agent capabilities (web search, code execution) | `python/tools/` |
| **Extensions** | Hook into lifecycle events | `python/extensions/<hook_point>/` |
| **Skills** | Create reusable instruction bundles | `skills/custom/<skill-name>/` |
| **API Endpoints** | Add Web UI functionality | `python/api/` |
| **Subordinates** | Create specialized agent profiles | `agents/<profile>/` |
| **Projects** | Project-specific configuration | `.a0proj/` |

---

## Architecture Overview

### Core Components

```
Agent Zero Framework Architecture
├── python/
│   ├── tools/          # Agent capabilities (inherit from Tool)
│   ├── extensions/     # Lifecycle hooks (numbered execution)
│   ├── api/            # FastAPI endpoints (inherit from ApiHandler)
│   └── helpers/        # Utility functions and base classes
├── skills/
│   ├── builtin/        # Built-in skills (system)
│   ├── custom/         # User-created skills
│   └── frameworks/     # Multi-phase framework skills
├── agents/
│   └── <profile>/      # Subordinate agent profiles
├── memory/             # FAISS-based vector memory
└── tmp/
    └── chats/          # Conversation storage
```

### Key Patterns

1. **Extensions execute in numeric order** (`_10_*.py`, `_20_*.py`, etc.)
2. **Tools inherit from `Tool` base class** with `execute()` method
3. **Skills use progressive disclosure** (metadata → content → scripts)
4. **Shared AgentContext** enables memory persistence across agents
5. **Async/await throughout** for non-blocking operations

---

## Creating Tools

Tools are the primary way agents interact with the world. Each tool inherits from the `Tool` base class.

### Tool Structure

```python
# python/tools/my_tool.py
from python.helpers.tool import Tool, Response

class MyTool(Tool):
    """
    Brief description of what this tool does.
    
    Arguments (tool_args):
        - arg1: Description of first argument
        - arg2: Description of second argument
    """

    async def execute(self, **kwargs) -> Response:
        # Get arguments from kwargs or self.args
        arg1 = kwargs.get("arg1") or self.args.get("arg1")
        arg2 = kwargs.get("arg2") or self.args.get("arg2")
        
        # Tool logic here
        result = await self.do_something(arg1, arg2)
        
        return Response(
            message=result,
            break_loop=False  # Set True to end agent loop
        )
    
    async def do_something(self, arg1, arg2):
        # Implement tool functionality
        pass
```

### Tool Best Practices

1. **Always document args** in the class docstring
2. **Use `Response` objects** for consistent return format
3. **Handle errors gracefully** - return error message, don't crash
4. **Access agent context** via `self.agent.context`
5. **Use kwargs fallback** to `self.args` for flexibility

### Example: Complete Tool

```python
# python/tools/data_processor.py
from python.helpers.tool import Tool, Response
import json

class DataProcessor(Tool):
    """
    Process and transform data structures.
    
    Arguments (tool_args):
        - operation: The operation to perform (filter, map, reduce)
        - data: JSON data to process
        - key: Key to filter/sort by (for filter/sort operations)
        - value: Value to filter by (for filter operation)
    """

    async def execute(self, **kwargs) -> Response:
        try:
            operation = kwargs.get("operation") or self.args.get("operation", "")
            data_str = kwargs.get("data") or self.args.get("data", "[]")
            key = kwargs.get("key") or self.args.get("key")
            value = kwargs.get("value") or self.args.get("value")
            
            data = json.loads(data_str)
            
            if operation == "filter":
                result = [item for item in data if item.get(key) == value]
            elif operation == "sort":
                result = sorted(data, key=lambda x: x.get(key))
            else:
                return Response(message=f"Unknown operation: {operation}", break_loop=False)
            
            return Response(
                message=json.dumps(result, indent=2),
                break_loop=False
            )
        except Exception as e:
            return Response(message=f"Error processing data: {e}", break_loop=False)
```

---

## Creating Extensions

Extensions hook into specific points in the agent lifecycle. They execute in numeric order.

### Extension Hook Points

| Hook Point | When It Fires | Use For |
|------------|---------------|---------|
| `agent_init` | Agent initialization | Loading configs, setting defaults |
| `message_loop_start` | Before message processing | Pre-processing, logging |
| `message_loop_end` | After message processing | Cleanup, post-processing |
| `before_main_llm_call` | Before LLM API call | Modifying prompts, adding context |
| `response_stream_start` | When response streaming begins | Initializing stream handlers |
| `response_stream_chunk` | Per response chunk | Transforming output |
| `response_stream_end` | When streaming ends | Finalizing, cleanup |
| `tool_execute_before` | Before tool execution | Validation, logging |
| `tool_execute_after` | After tool execution | Post-processing results |

### Extension Structure

```python
# python/extensions/<hook_point>/_10_my_extension.py
from python.helpers.extension import Extension
from python.helpers.print_style import PrintStyle

class MyExtension(Extension):
    """
    Brief description of extension purpose.
    """

    async def execute(self, **kwargs):
        # Access the agent
        agent = self.agent
        context = agent.context
        
        # Extension logic
        PrintStyle.hint("MyExtension executing...")
        
        # Modify data if needed (check kwargs for hook-specific data)
        data = kwargs.get("data", {})
        data["modified"] = True
        
        # Return modified data if applicable
        return data
```

### Extension Execution Order

Extensions execute in numeric order based on filename prefix:

```
_10_load_config.py    # Runs first
_20_validate.py       # Runs second  
_30_process.py        # Runs third
```

Use 10-number increments to leave room for future extensions.

### Example: Agent Init Extension

```python
# python/extensions/agent_init/_15_load_custom_config.py
from python.helpers.extension import Extension
from python.helpers import files
import json

class LoadCustomConfig(Extension):
    """
    Load custom configuration from .a0proj/config.json
    """

    async def execute(self, **kwargs):
        agent = self.agent
        context = agent.context
        
        config_path = files.get_abs_path(".a0proj/config.json")
        if files.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                context.data["custom_config"] = config
                
        return kwargs.get("data", {})
```

---

## Creating Skills

Skills are reusable instruction bundles following the SKILL.md standard.

### Skill Directory Structure

```
skills/custom/my-skill/
├── SKILL.md              # Required: Main skill file
├── scripts/              # Optional: Helper scripts
│   ├── helper.py
│   └── process.sh
├── templates/            # Optional: Templates
│   └── template.md
└── docs/                 # Optional: Additional docs
    └── examples.md
```

### SKILL.md Format

```yaml
---
name: "skill-name"
description: "Clear description of what this skill does and when to use it"
version: "1.0.0"
author: "Your Name"
tags: ["category1", "category2"]
trigger_patterns:
  - "keyword1"
  - "phrase that triggers this"
---

# Skill Title

## When to Use
Describe trigger conditions and use cases.

## The Process
Step-by-step instructions for the agent to follow.

### Step 1: First Action
Details...

### Step 2: Second Action
Details...

## Examples
Show sample interactions.

## Scripts
Reference any helper scripts:
- `scripts/helper.py` - Does X
- `scripts/process.sh` - Does Y

## Tips
Additional guidance and best practices.
```

### Using Skills

```python
# Load skill metadata
await skills_tool.execute(method="list")

# Load full skill content
await skills_tool.execute(method="load", skill_name="my-skill")

# Execute skill script
await skills_tool.execute(
    method="execute_script",
    skill_name="my-skill",
    script_path="scripts/helper.py",
    script_args={"input": "value"},
    arg_style="positional"  # or "named" or "env"
)
```

---

## Creating API Endpoints

API endpoints serve the Web UI and external clients using FastAPI.

### API Endpoint Structure

```python
# python/api/my_endpoint.py
from python.helpers.api import ApiHandler, Request, Response
from agent import AgentContext

class MyEndpoint(ApiHandler):
    """
    Handle requests for /api/my-endpoint
    """

    async def process(self, input: dict, request: Request) -> dict | Response:
        # Get query params or JSON body
        param = input.get("param", "default")
        
        # Get or create agent context
        ctxid = input.get("context", "")
        context = self.use_context(ctxid)
        
        # Process request
        result = await self.process_request(param, context)
        
        return {
            "result": result,
            "context": context.id,
        }
    
    async def process_request(self, param, context):
        # Implement endpoint logic
        return {"processed": param}
```

### API Best Practices

1. **Use `ApiHandler` base class** for consistent request/response handling
2. **Get context with `self.use_context(ctxid)`** - creates if not exists
3. **Return dict or Response** objects
4. **Handle both GET and POST** if applicable
5. **Use `Request` object** for accessing headers, files, etc.

### Example: File Upload Endpoint

```python
# python/api/upload_processor.py
from python.helpers.api import ApiHandler, Request
from werkzeug.utils import secure_filename
import os

class UploadProcessor(ApiHandler):
    async def process(self, input: dict, request: Request) -> dict:
        if request.method == "POST":
            uploaded_file = request.files.get("file")
            if uploaded_file:
                filename = secure_filename(uploaded_file.filename)
                save_path = f"/tmp/uploads/{filename}"
                uploaded_file.save(save_path)
                
                return {
                    "success": True,
                    "filename": filename,
                    "path": save_path
                }
        
        return {"success": False, "error": "No file provided"}
```

---

## Creating Subordinate Profiles

Subordinates are specialized agents with custom prompts and configurations.

### Profile Directory Structure

```
agents/<profile-name>/
├── agent.json           # Profile configuration
└── prompts/
    ├── system.md        # System prompt
    └── subordinates.md  # Subordinate delegation prompts
```

### agent.json Configuration

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
    "call_subordinate"
  ],
  "prompts": {
    "system": "prompts/system.md",
    "subordinates": "prompts/subordinates.md"
  }
}
```

### System Prompt Template

```markdown
# System Prompt for Specialized Agent

## Your Role
You are a specialized agent focused on [domain].

## Capabilities
- Expertise in [specific area]
- Use tools: code_execution_tool, search_engine

## Process
1. Analyze the request
2. Choose appropriate tools
3. Execute and verify results
4. Return structured response

## Output Format
Always respond with valid JSON:
```json
{
  "result": "your result here",
  "confidence": 0.95
}
```
```

### Using Subordinates

```python
# Call from main agent
call_subordinate(
    profile="developer",
    message="Implement a Python function to calculate Fibonacci",
    reset="true"
)
```

---

## Creating Projects

Projects provide isolated workspaces with custom configuration.

### Project Structure

```
/usr/projects/<project-name>/
├── .a0proj/
│   ├── config.json      # Project configuration
│   ├── instructions.md  # Project-specific instructions
│   └── skills/          # Project-specific skills
└── <project-files>/     # Your project files
```

### config.json

```json
{
  "name": "My Project",
  "description": "Project description",
  "default_model": "anthropic/claude-sonnet-4-20250514",
  "allowed_tools": ["*"],
  "extensions": {
    "enabled": ["custom_extension"]
  },
 "skills": {
    "auto_load": ["project-specific-skill"]
  }
}
```

### instructions.md

```markdown
# Project: My Project

## Overview
This project does X, Y, Z.

## Coding Standards
- Use Python 3.12+ features
- Follow PEP 8
- Write tests for all functions

## Architecture
- API layer in `api/`
- Business logic in `services/`
- Models in `models/`
```

---

## Framework Development Workflow

When building features for Agent Zero itself, follow this workflow:

### Phase 1: Brainstorming
- Define the problem and solution
- Identify extension points (tool, extension, skill, API)
- Review existing patterns for consistency

### Phase 2: Planning
- Break work into small tasks (2-5 min each)
- Identify dependencies and order
- Write verification criteria for each task

### Phase 3: Implementation
- Create feature branch (use git worktrees)
- Follow TDD: test first, then implement
- Match existing code patterns

### Phase 4: Code Review
- Review against plan
- Check pattern consistency
- Verify tests pass

### Phase 5: Integration
- Merge to main
- Update documentation
- Test in production context

---

## Common Patterns Reference

### Accessing Context Data

```python
# Shared across all agents in conversation
context = self.agent.context
data = context.data  # dict-like shared memory

# Store data
data["my_key"] = my_value

# Retrieve data
value = data.get("my_key", default)
```

### Using Helpers

```python
from python.helpers import files, extension, print_style

# File operations
content = files.read_file("path/to/file")
files.write_file("path/to/file", content)
exists = files.exists("path/to/file")

# Extensions
await extension.call_extensions("hook_point", agent=agent, data=data)

# Printing
PrintStyle.hint("Hint message")
PrintStyle.warning("Warning message")
PrintStyle.error("Error message")
```

### Error Handling

```python
try:
    result = await risky_operation()
except Exception as e:
    # Log for debugging
    PrintStyle.error(f"Operation failed: {e}")
    # Return graceful error to user
    return Response(message=f"Error: {e}", break_loop=False)
```

### Async Patterns

```python
# Concurrent execution
tasks = [process_item(item) for item in items]
results = await asyncio.gather(*tasks)

# Timeouts
try:
    result = await asyncio.wait_for(operation(), timeout=30)
except asyncio.TimeoutError:
    return Response(message="Operation timed out", break_loop=False)
```

---

## Testing Your Extensions

### Manual Testing

1. **Restart the framework** after code changes
2. **Test with minimal input** first
3. **Check logs** for errors: `docker logs -f agent-zero`
4. **Verify in UI** that changes appear correctly

### Unit Testing (when available)

```python
# tests/tools/test_my_tool.py
import pytest
from python.tools.my_tool import MyTool

@pytest.mark.asyncio
async def test_my_tool():
    tool = MyTool()
    result = await tool.execute(operation="test", data="{}")
    assert "success" in result.message
```

---

## Scripts and Templates

This skill includes helper scripts and templates:

### Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/create_tool.py` | Generate tool boilerplate | `python scripts/create_tool.py ToolName` |
| `scripts/create_extension.py` | Generate extension boilerplate | `python scripts/create_extension.py HookPoint ExtensionName` |
| `scripts/create_skill.py` | Generate skill boilerplate | `python scripts/create_skill.py skill-name` |
| `scripts/create_api.py` | Generate API endpoint boilerplate | `python scripts/create_api.py EndpointName` |

### Templates

| Template | Purpose |
|----------|---------|
| `templates/tool.py` | Tool boilerplate |
| `templates/extension.py` | Extension boilerplate |
| `templates/SKILL.md` | Skill boilerplate |
| `templates/api.py` | API endpoint boilerplate |

---

## Best Practices Summary

### DO
- ✅ Follow existing patterns and conventions
- ✅ Write clear docstrings and comments
- ✅ Handle errors gracefully
- ✅ Use type hints where applicable
- ✅ Test your changes thoroughly
- ✅ Update documentation
- ✅ Use meaningful names

### DON'T
- ❌ Break existing functionality
- ❌ Ignore error cases
- ❌ Hardcode paths or values
- ❌ Skip documentation
- ❌ Mix sync and async code carelessly
- ❌ Access internal structures directly when helpers exist

---

## Need Help?

Use this skill by saying:
- "Help me create a new tool for..."
- "I want to add an extension that..."
- "Create a skill for..."
- "Build an API endpoint for..."
- "How do I extend Agent Zero to..."

I'll guide you through the appropriate patterns and generate boilerplate code!
