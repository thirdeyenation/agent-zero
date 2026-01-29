---
name: "a0dev-workflow"
description: "Full development workflow for building Agent Zero features."
version: "1.0.0"
author: "Agent Zero Team"
tags: ["agent-zero-dev", "workflow", "development", "process"]
trigger_patterns:
  - "development workflow"
  - "dev workflow"
  - "build feature"
  - "extend agent zero"
  - "/a0dev-workflow"
---

# Agent Zero Dev: Development Workflow

Complete workflow for building features for Agent Zero framework.

## Workflow Phases

```
1. Brainstorm → 2. Plan → 3. Scaffold → 4. Implement → 5. Test → 6. Refine
```

## Phase 1: Brainstorm

### Define the Problem

**Questions to answer:**
- What problem does this solve?
- Who benefits from this feature?
- What's the expected outcome?

### Identify Extension Point

| If you need to... | Use |
|-------------------|-----|
| Add agent capability | Tool |
| Hook into lifecycle | Extension |
| Create instruction bundle | Skill |
| Add Web UI endpoint | API |
| Create specialized agent | Subordinate |
| Configure workspace | Project |

### Review Existing Patterns

Before building, examine similar code:
- `python/tools/` — Tool patterns
- `python/extensions/` — Extension patterns
- `skills/` — Skill patterns
- `python/api/` — API patterns

## Phase 2: Plan

### Break Into Tasks

Each task should be:
- Small (2-5 minutes to complete)
- Testable (clear verification)
- Independent (minimal dependencies)

### Example Task Breakdown

**Feature:** "Add weather lookup tool"

```markdown
## Tasks

1. [ ] Create tool file structure
   - File: python/tools/weather_tool.py
   - Verify: File exists with boilerplate

2. [ ] Implement weather API integration
   - Use aiohttp for async requests
   - Verify: Can fetch weather data

3. [ ] Add error handling
   - Handle API errors, invalid locations
   - Verify: Graceful error messages

4. [ ] Test with agent
   - Ask agent to get weather
   - Verify: Correct response format

5. [ ] Document the tool
   - Add docstring with args
   - Verify: Documentation complete
```

### Identify Dependencies

```
What must exist first?
├── API keys configured?
├── Dependencies installed?
├── Related code ready?
└── Test data available?
```

## Phase 3: Scaffold

### Use Generator Scripts

```bash
# Generate boilerplate
python skills/frameworks/agent-zero-dev/scripts/create_tool.py WeatherTool "Look up weather for a location"
```

### Available Generators

| Script | Creates |
|--------|---------|
| `create_tool.py` | Tool in `python/tools/` |
| `create_extension.py` | Extension in `python/extensions/` |
| `create_skill.py` | Skill in `skills/custom/` |
| `create_api.py` | API in `python/api/` |

### Review Generated Code

After generation:
1. Open the created file
2. Review the boilerplate
3. Identify what to fill in
4. Note the patterns used

## Phase 4: Implement

### Follow Test-Driven Development

```
1. Write test (what should happen)
2. Run test (should fail)
3. Write code (minimal to pass)
4. Run test (should pass)
5. Refactor (improve quality)
```

### Implementation Checklist

- [ ] Follow existing code patterns
- [ ] Add proper error handling
- [ ] Use type hints
- [ ] Write clear docstrings
- [ ] Keep functions focused
- [ ] Use async where appropriate

### Common Patterns

**Accessing Context:**
```python
context = self.agent.context
data = context.data
```

**Error Handling:**
```python
try:
    result = await risky_operation()
except Exception as e:
    return Response(message=f"Error: {e}", break_loop=False)
```

**Async Operations:**
```python
async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
        return await response.json()
```

## Phase 5: Test

### Manual Testing

1. **Restart Agent Zero** (code loads at startup)
2. **Trigger your feature**:
   ```
   "Use the weather tool to check weather in Seattle"
   ```
3. **Verify behavior**:
   - Correct response?
   - Errors handled?
   - Performance acceptable?

### Check Logs

```bash
# Docker logs
docker logs -f agent-zero

# Or check log files
tail -f logs/agent.log
```

### Test Edge Cases

- Invalid inputs
- Missing data
- Network failures
- Concurrent access

## Phase 6: Refine

### Code Review Checklist

- [ ] Follows project conventions?
- [ ] Error handling complete?
- [ ] Documentation updated?
- [ ] No hardcoded values?
- [ ] Performance acceptable?

### Refactoring

After it works:
- Simplify complex logic
- Extract reusable functions
- Improve naming
- Add missing tests

### Documentation

Update as needed:
- Code docstrings
- Skill instructions
- README files
- API documentation

## Complete Example: Weather Tool

### Phase 1: Brainstorm
- **Problem:** Agent can't check weather
- **Extension Point:** Tool
- **Similar Code:** `search_engine.py`

### Phase 2: Plan
```markdown
1. [ ] Generate tool boilerplate
2. [ ] Add weather API integration
3. [ ] Implement execute() method
4. [ ] Add error handling
5. [ ] Test with agent
```

### Phase 3: Scaffold
```bash
python scripts/create_tool.py WeatherLookup "Get weather for a location"
```

### Phase 4: Implement
```python
# python/tools/weather_lookup.py
from python.helpers.tool import Tool, Response
import aiohttp

class WeatherLookup(Tool):
    """
    Look up current weather for a location.

    Arguments:
        - location: City name or coordinates
    """

    async def execute(self, location="", **kwargs) -> Response:
        location = location or kwargs.get("location") or self.args.get("location", "")

        if not location:
            return Response(message="Please provide a location", break_loop=False)

        try:
            weather = await self.fetch_weather(location)
            return Response(
                message=f"Weather in {location}: {weather['description']}, {weather['temp']}°F",
                break_loop=False
            )
        except Exception as e:
            return Response(message=f"Could not fetch weather: {e}", break_loop=False)

    async def fetch_weather(self, location):
        # Implementation using weather API
        async with aiohttp.ClientSession() as session:
            url = f"https://api.weather.example/v1?q={location}"
            async with session.get(url) as response:
                return await response.json()
```

### Phase 5: Test
```
User: "What's the weather in Seattle?"
Agent: Uses weather_lookup tool
Result: "Weather in Seattle: Partly cloudy, 58°F"
```

### Phase 6: Refine
- Add caching for repeated lookups
- Support metric/imperial units
- Add forecast option

## Quick Reference

### Extension Points
- **Tools:** `python/tools/`
- **Extensions:** `python/extensions/<hook>/`
- **Skills:** `skills/custom/`
- **APIs:** `python/api/`
- **Subordinates:** `agents/<profile>/`
- **Projects:** `.a0proj/`

### Key Files
- `python/helpers/tool.py` — Tool base class
- `python/helpers/extension.py` — Extension base class
- `python/helpers/api.py` — API base class

### Commands
- Restart to reload code
- Check logs for errors
- Test with real interactions

## Next Steps

Ready to build? Start with:
1. `/a0dev-quickstart` — Quick overview
2. `/a0dev-create-tool` — Build a tool
3. `/a0dev-create-skill` — Create a skill
