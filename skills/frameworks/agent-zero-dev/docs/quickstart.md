# Agent Zero Development Quickstart

Get started extending Agent Zero in 5 minutes.

## Prerequisites

- Agent Zero framework installed and running
- Basic understanding of Python async/await
- Familiarity with the framework structure

## 1. Create Your First Tool (2 minutes)

```bash
cd /a0/skills/frameworks/agent-zero-dev
python scripts/create_tool.py WeatherLookup "Get weather information for locations"
```

This creates `/a0/python/tools/weather_lookup.py` with full boilerplate.

Edit the file to implement your logic:

```python
async def _process(self, location: str, units: str) -> str:
    # Your weather API call here
    return f"Weather for {location}: 72°F, Sunny"
```

Restart Agent Zero to load the new tool.

## 2. Create Your First Extension (2 minutes)

```bash
python scripts/create_extension.py agent_init ConfigLoader "Load project configuration"
```

Edit the generated file to add initialization logic.

## 3. Create Your First Skill (3 minutes)

```bash
python scripts/create_skill.py my-skill "My custom skill description"
```

Edit `SKILL.md` to add instructions, then test with:
"Use my-skill to process data"

## 4. Create Your First API Endpoint (3 minutes)

```bash
python scripts/create_api.py DataApi "API for data operations"
```

Test with curl:
```bash
curl "http://localhost:5001/api/data_api?context=test&param=value"
```

## Next Steps

- Read the full [SKILL.md](../SKILL.md) for comprehensive documentation
- Explore existing tools in `/a0/python/tools/`
- Check out built-in skills in `/a0/skills/builtin/`
- Review the Superpowers framework for development workflows
