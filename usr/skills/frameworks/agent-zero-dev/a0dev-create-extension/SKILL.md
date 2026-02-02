---
name: "a0dev-create-extension"
description: "Hook into Agent Zero lifecycle events with extensions."
version: "1.0.0"
author: "Agent Zero Team"
tags: ["agent-zero-dev", "extension", "lifecycle", "hooks"]
trigger_patterns:
  - "create extension"
  - "new extension"
  - "add extension"
  - "lifecycle hook"
  - "/a0dev-create-extension"
---

# Agent Zero Dev: Create Extension

Extensions hook into specific points in the agent lifecycle. They execute in numeric order based on filename prefix.

## Extension Hook Points

| Hook Point | When It Fires | Use For |
|------------|---------------|---------|
| `agent_init` | Agent initialization | Loading configs, setting defaults |
| `message_loop_start` | Before message processing | Pre-processing, logging |
| `message_loop_end` | After message processing | Cleanup, post-processing |
| `message_loop_prompts_after` | After prompts assembled | Adding context to prompts |
| `before_main_llm_call` | Before LLM API call | Modifying prompts |
| `response_stream_start` | Response streaming begins | Initializing handlers |
| `response_stream_chunk` | Per response chunk | Transforming output |
| `response_stream_end` | Streaming ends | Finalizing |
| `tool_execute_before` | Before tool execution | Validation, logging |
| `tool_execute_after` | After tool execution | Post-processing |
| `hist_add_user_message` | User message added | Message interception |
| `system_prompt` | System prompt assembly | Injecting context |

## Extension Location

```
python/extensions/
├── agent_init/
│   ├── _10_load_settings.py
│   └── _20_your_extension.py
├── message_loop_start/
├── message_loop_end/
├── before_main_llm_call/
└── <hook_point>/
    └── _NN_extension_name.py
```

## Extension Structure

```python
# python/extensions/<hook_point>/_NN_my_extension.py
from python.helpers.extension import Extension
from python.helpers.print_style import PrintStyle

class MyExtension(Extension):
    """
    Brief description of what this extension does.
    """

    async def execute(self, **kwargs):
        # Access the agent
        agent = self.agent
        context = agent.context

        # Extension logic
        PrintStyle.hint("MyExtension executing...")

        # Get/modify hook-specific data
        data = kwargs.get("data", {})

        # Return data (some hooks expect modified data back)
        return data
```

## Execution Order

Extensions execute in numeric order based on filename prefix:

```
_10_first.py      # Runs first
_20_second.py     # Runs second
_30_third.py      # Runs third
_55_yours.py      # Your extension
_90_last.py       # Runs last
```

**Convention:** Use 10-number increments to leave room for future extensions.

## Hook-Specific Examples

### Agent Init (Load Configuration)

```python
# python/extensions/agent_init/_15_load_custom_config.py
from python.helpers.extension import Extension
from python.helpers import files
import json

class LoadCustomConfig(Extension):
    """Load custom configuration from .a0proj/config.json"""

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

### Message Loop Start (Logging)

```python
# python/extensions/message_loop_start/_10_log_message.py
from python.helpers.extension import Extension
import logging

class LogMessage(Extension):
    """Log incoming messages for debugging"""

    async def execute(self, **kwargs):
        agent = self.agent
        message = kwargs.get("message", "")

        logging.info(f"Agent {agent.number} received: {message[:100]}...")

        return kwargs.get("data", {})
```

### System Prompt (Inject Context)

```python
# python/extensions/system_prompt/_50_inject_project_context.py
from python.helpers.extension import Extension

class InjectProjectContext(Extension):
    """Add project-specific context to system prompt"""

    async def execute(self, **kwargs):
        agent = self.agent
        context = agent.context

        # Get the prompt being built
        prompt_parts = kwargs.get("data", [])

        # Add project context if available
        project_info = context.data.get("project_info")
        if project_info:
            prompt_parts.append(f"\n## Project Context\n{project_info}\n")

        return prompt_parts
```

### Before LLM Call (Modify Prompt)

```python
# python/extensions/before_main_llm_call/_40_add_instructions.py
from python.helpers.extension import Extension

class AddInstructions(Extension):
    """Add dynamic instructions before LLM call"""

    async def execute(self, **kwargs):
        # Access messages being sent
        messages = kwargs.get("messages", [])

        # Modify or add messages
        custom_instruction = {
            "role": "system",
            "content": "Remember to be concise."
        }

        # Return modified data
        return {"messages": messages + [custom_instruction]}
```

### Tool Execute After (Post-Process)

```python
# python/extensions/tool_execute_after/_30_log_tool_result.py
from python.helpers.extension import Extension
from python.helpers.print_style import PrintStyle

class LogToolResult(Extension):
    """Log tool execution results"""

    async def execute(self, **kwargs):
        tool_name = kwargs.get("tool_name", "unknown")
        result = kwargs.get("result", {})

        PrintStyle.hint(f"Tool {tool_name} returned: {str(result)[:100]}...")

        return kwargs.get("data", {})
```

## Using the Generator Script

```bash
python usr/skills/frameworks/agent-zero-dev/scripts/create_extension.py \
    agent_init \
    LoadProjectSettings \
    "Load project-specific settings on agent init"
```

Generates: `python/extensions/agent_init/_50_load_project_settings.py`

## Extension Best Practices

### DO

- ✅ Use numeric prefixes (10, 20, 30...)
- ✅ Return the data dict (even if unmodified)
- ✅ Document what the extension does
- ✅ Keep extensions focused (single responsibility)
- ✅ Handle errors gracefully
- ✅ Use PrintStyle for logging

### DON'T

- ❌ Block the event loop
- ❌ Modify global state carelessly
- ❌ Ignore the return value
- ❌ Use conflicting numeric prefixes
- ❌ Create circular dependencies

## Accessing Context

```python
# Agent and context
agent = self.agent
context = agent.context

# Shared data (persists across agents)
context.data["key"] = value
value = context.data.get("key")

# Agent-specific data
agent.set_data("key", value)
value = agent.get_data("key")

# Configuration
config = agent.config
model = config.chat_model
```

## Testing Extensions

1. **Add your extension** to the appropriate hook point
2. **Restart Agent Zero** (extensions load at startup)
3. **Trigger the hook** by performing the related action
4. **Check logs** for your output or errors

## Next Steps

- Identify which hook point fits your use case
- Start with logging to understand data flow
- Keep extensions small and composable
