---
name: "a0dev-create-tool"
description: "Create new agent capabilities (tools) for Agent Zero."
version: "1.0.0"
author: "Agent Zero Team"
tags: ["agent-zero-dev", "tool", "capability", "development"]
trigger_patterns:
  - "create tool"
  - "new tool"
  - "add tool"
  - "build tool"
  - "/a0dev-create-tool"
---

# Agent Zero Dev: Create Tool

Tools are the primary way agents interact with the world. Each tool inherits from the `Tool` base class and provides capabilities like web search, code execution, file manipulation, etc.

## Tool Location

```
python/tools/
├── code_execution_tool.py
├── search_engine.py
├── call_subordinate.py
├── memory_tool.py
└── your_tool.py  ← New tools go here
```

## Tool Structure

```python
# python/tools/my_tool.py
from python.helpers.tool import Tool, Response

class MyTool(Tool):
    """
    Brief description of what this tool does.

    Arguments (tool_args):
        - arg1: Description of first argument
        - arg2: Description of second argument (optional)
    """

    async def execute(self, **kwargs) -> Response:
        # Get arguments (kwargs takes priority, fallback to self.args)
        arg1 = kwargs.get("arg1") or self.args.get("arg1")
        arg2 = kwargs.get("arg2") or self.args.get("arg2", "default")

        try:
            # Tool logic here
            result = await self.do_work(arg1, arg2)

            return Response(
                message=result,
                break_loop=False  # True to end agent loop
            )
        except Exception as e:
            return Response(
                message=f"Error: {e}",
                break_loop=False
            )

    async def do_work(self, arg1, arg2):
        # Implementation
        return f"Processed {arg1} with {arg2}"
```

## Response Object

```python
Response(
    message: str,           # Result message shown to agent
    break_loop: bool,       # True = end agent loop (task complete)
    additional: dict = {}   # Extra data (hints, metadata)
)
```

## Accessing Agent Context

```python
async def execute(self, **kwargs) -> Response:
    # Access the agent
    agent = self.agent

    # Access shared context (persists across agents)
    context = agent.context

    # Store/retrieve data
    context.data["my_key"] = "my_value"
    value = context.data.get("my_key")

    # Access agent configuration
    config = agent.config
```

## Tool Best Practices

### DO

- ✅ Document arguments in class docstring
- ✅ Use `Response` for all returns
- ✅ Handle errors gracefully (return error message, don't crash)
- ✅ Use kwargs fallback to self.args
- ✅ Make operations async when possible
- ✅ Use type hints

### DON'T

- ❌ Raise unhandled exceptions
- ❌ Block the event loop (use async)
- ❌ Hardcode paths or values
- ❌ Ignore optional arguments
- ❌ Print directly (use Response or logging)

## Complete Example: Data Processor

```python
# python/tools/data_processor.py
from python.helpers.tool import Tool, Response
import json

class DataProcessor(Tool):
    """
    Process and transform JSON data structures.

    Arguments (tool_args):
        - operation: The operation (filter, sort, map)
        - data: JSON string to process
        - key: Key to operate on
        - value: Value for filter operation (optional)
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
                result = sorted(data, key=lambda x: x.get(key, ""))
            elif operation == "map":
                result = [item.get(key) for item in data]
            else:
                return Response(
                    message=f"Unknown operation: {operation}",
                    break_loop=False
                )

            return Response(
                message=json.dumps(result, indent=2),
                break_loop=False
            )

        except json.JSONDecodeError as e:
            return Response(message=f"Invalid JSON: {e}", break_loop=False)
        except Exception as e:
            return Response(message=f"Error: {e}", break_loop=False)
```

## Using the Generator Script

```bash
python skills/frameworks/agent-zero-dev/scripts/create_tool.py \
    DataProcessor \
    "Process and transform JSON data structures"
```

This generates boilerplate at `python/tools/data_processor.py`.

## Tool Registration

Tools are auto-discovered by filename convention:
- Filename: `snake_case.py` (e.g., `data_processor.py`)
- Class name: `PascalCase` (e.g., `DataProcessor`)
- Tool name (for agent): derived from class name

## Testing Your Tool

1. **Restart Agent Zero** (tools load at startup)
2. **Ask the agent** to use your tool:
   ```
   "Use the data_processor tool to sort this JSON by name: [{"name": "z"}, {"name": "a"}]"
   ```
3. **Check logs** for errors: `docker logs -f agent-zero`

## Common Patterns

### Async HTTP Request

```python
import aiohttp

async def fetch_data(self, url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
```

### File Operations

```python
from python.helpers import files

content = files.read_file("path/to/file")
files.write_file("path/to/file", content)
exists = files.exists("path/to/file")
```

### Logging

```python
from python.helpers.print_style import PrintStyle

PrintStyle.hint("Info message")
PrintStyle.warning("Warning message")
PrintStyle.error("Error message")
```

## Next Steps

After creating your tool:
- Test thoroughly with different inputs
- Document edge cases
- Consider error messages for users
- Add to project documentation if significant
