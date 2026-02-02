# Best Practices for Agent Zero Development

## Code Style

### Python Conventions

Follow PEP 8 with these specifics:

```python
# Use type hints
def process_data(data: dict) -> str:
    pass

# Async everywhere
async def fetch_data() -> dict:
    pass

# Clear variable names
user_input = ""  # Good
ui = ""         # Avoid
```

### Documentation

Every public class and method needs a docstring:

```python
class MyTool(Tool):
    """
    Brief description of tool purpose.
    
    Arguments (tool_args):
        - arg1: Description of first argument
        - arg2: Description of second argument
        
    Returns:
        Response object with result
    """
```

## Error Handling

### Graceful Degradation

Tools should never crash the agent:

```python
async def execute(self, **kwargs) -> Response:
    try:
        result = await self.risky_operation()
        return Response(message=result, break_loop=False)
    except Exception as e:
        # Log for debugging
        PrintStyle.error(f"Operation failed: {e}")
        # Return graceful error to user
        return Response(message=f"Error: {e}", break_loop=False)
```

### Specific Exceptions

Catch specific exceptions when possible:

```python
try:
    data = json.loads(json_str)
except json.JSONDecodeError as e:
    return Response(message=f"Invalid JSON: {e}", break_loop=False)
except Exception as e:
    return Response(message=f"Unexpected error: {e}", break_loop=False)
```

## Performance

### Avoid Blocking Operations

Never use synchronous I/O in async methods:

```python
# Bad - blocks event loop
data = requests.get(url).json()

# Good - async
import aiohttp
async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
        data = await response.json()
```

### Batch Operations

Process multiple items concurrently:

```python
# Process all at once
tasks = [process_item(item) for item in items]
results = await asyncio.gather(*tasks, return_exceptions=True)

# Handle errors individually
for item, result in zip(items, results):
    if isinstance(result, Exception):
        PrintStyle.error(f"Failed to process {item}: {result}")
    else:
        successes.append(result)
```

## Security

### Input Validation

Always validate user input:

```python
async def execute(self, **kwargs) -> Response:
    user_input = kwargs.get("input", "")
    
    # Validate
    if not user_input:
        return Response(message="Error: input is required", break_loop=False)
    
    if len(user_input) > 10000:
        return Response(message="Error: input too large", break_loop=False)
    
    # Process
    result = await self.process(user_input)
```

### Path Safety

Use secure paths:

```python
from werkzeug.utils import secure_filename
from python.helpers import files

# Sanitize filenames
filename = secure_filename(uploaded_file.filename)

# Use absolute paths
full_path = files.get_abs_path("tmp/uploads", filename)
```

### Secrets

Never hardcode credentials:

```python
# Bad
api_key = "sk-1234567890"

# Good
from python.helpers import secrets
api_key = secrets.get("API_KEY")
```

## Testing

### Unit Tests

Write tests for tools:

```python
import pytest
from python.tools.my_tool import MyTool

@pytest.mark.asyncio
async def test_my_tool_success():
    tool = MyTool()
    result = await tool.execute(param="valid_value")
    assert "success" in result.message

@pytest.mark.asyncio
async def test_my_tool_error():
    tool = MyTool()
    result = await tool.execute(param="")
    assert "error" in result.message.lower()
```

### Integration Tests

Test full workflows:

```python
@pytest.mark.asyncio
async def test_tool_integration():
    # Setup
    context = create_test_context()
    
    # Execute
    tool = MyTool()
    tool.agent = MockAgent(context)
    result = await tool.execute(data="test")
    
    # Verify
    assert result.break_loop is False
    assert "result" in context.data
```

## Memory Management

### Context Data

Use context for session-wide state:

```python
# Store data
self.agent.context.data["processed_items"] = items

# Retrieve with default
items = self.agent.context.data.get("processed_items", [])
```

### Memory Operations

Save important information:

```python
from python.helpers.memory import memory_save

# Save with metadata
memory_save(
    text="Important fact",
    metadata={"category": "user_preference", "timestamp": time.time()}
)
```

## Tool Design

### Single Responsibility

Each tool should do one thing well:

```python
# Good: WebSearch tool only searches
class WebSearch(Tool):
    async def execute(self, **kwargs):
        query = kwargs.get("query")
        results = await search_web(query)
        return Response(message=format_results(results))

# Bad: WebSearchAndSummarize does too much
```

### Composable Tools

Tools should work together:

```python
# SearchTool finds information
results = await search_tool.execute(query="Python async")

# SummaryTool summarizes it
summary = await summary_tool.execute(text=results.message)
```

## Extension Design

### Minimal Interference

Extensions should be lightweight:

```python
# Good: Quick check and return
async def execute(self, **kwargs):
    if not self.should_process(kwargs):
        return kwargs.get("data", {})
    # Process...

# Bad: Heavy processing in extension
async def execute(self, **kwargs):
    # Don't do this - slows down every message
    result = await heavy_computation()
```

### Data Preservation

Always return data unless modifying:

```python
# Good: Returns data even if not modified
async def execute(self, **kwargs):
    data = kwargs.get("data", {})
    # Do something...
    return data

# Bad: Returns None
async def execute(self, **kwargs):
    data = kwargs.get("data", {})
    # Do something...
    # Missing return!
```

## API Design

### RESTful Endpoints

Follow REST conventions:

```python
# GET for retrieval
async def _handle_get(self, input, context):
    item_id = input.get("id")
    item = await self.get_item(item_id)
    return {"data": item}

# POST for creation
async def _handle_post(self, input, request, context):
    data = input.get("data")
    created = await self.create_item(data)
    return {"data": created, "created": True}
```

### Consistent Responses

Return consistent structures:

```python
# Success
{
    "success": True,
    "data": {...},
    "context": "ctx-id"
}

# Error
{
    "success": False,
    "error": "Error message",
    "context": "ctx-id"
}
```

## Skill Design

### Clear Instructions

Skills should have actionable steps:

```markdown
## The Process

### Step 1: Analyze Input
- Check for required parameters
- Validate data format

### Step 2: Process Data
- Apply transformation X
- Verify intermediate result

### Step 3: Return Output
- Format as JSON
- Include metadata
```

### Trigger Patterns

Use specific trigger patterns:

```yaml
trigger_patterns:
  # Good: Specific
  - "analyze data"
  - "data analysis"
  - "process dataset"
  
  # Bad: Too generic
  - "do"
  - "make"
```

## Debugging

### Verbose Logging

Add detailed logging during development:

```python
PrintStyle.hint(f"Processing {len(items)} items")
PrintStyle.hint(f"First item: {items[0] if items else 'empty'}")
```

### Remove Before Commit

Clean up debug code:

```python
# Development
PrintStyle.hint(f"DEBUG: kwargs = {kwargs}")

# Production
# Remove or convert to proper logging
```

## Deployment

### Environment Variables

Use env vars for configuration:

```python
import os

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
```

### Feature Flags

Use flags for gradual rollout:

```python
ENABLE_NEW_FEATURE = os.getenv("ENABLE_NEW_FEATURE", "false") == "true"

async def execute(self, **kwargs):
    if ENABLE_NEW_FEATURE:
        return await self.new_implementation(kwargs)
    else:
        return await self.old_implementation(kwargs)
```

## Documentation

### README Files

Every component needs a README:

```markdown
# Component Name

## Purpose
What this component does

## Usage
How to use it

## Configuration
Configuration options

## Examples
Code examples
```

### Code Comments

Comment complex logic:

```python
# Use binary search for O(log n) performance
# instead of linear scan O(n)
index = binary_search(sorted_data, target)
```
