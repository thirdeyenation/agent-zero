# Agent Zero Development Framework

A comprehensive development framework for extending and building features for the Agent Zero AI framework.

## Overview

This framework provides everything you need to extend Agent Zero:

- 🛠️ **Code Generators** - Scaffold tools, extensions, skills, and APIs
- 📚 **Documentation** - Architecture guides, best practices, and quickstart
- 🧩 **Templates** - Boilerplate code following framework patterns
- 🎯 **Examples** - Real-world patterns and use cases

## Quick Start

```bash
# Create a new tool
python scripts/create_tool.py MyTool "Description of what it does"

# Create an extension
python scripts/create_extension.py agent_init MyExtension "What it does"

# Create a skill
python scripts/create_skill.py my-skill "Skill description"

# Create an API endpoint
python scripts/create_api.py MyEndpoint "What it does"
```

## What's Included

### Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `create_tool.py` | Generate tool boilerplate | `python create_tool.py ToolName "Description"` |
| `create_extension.py` | Generate extension boilerplate | `python create_extension.py hook_point ExtName` |
| `create_skill.py` | Generate skill boilerplate | `python create_skill.py skill-name "Description"` |
| `create_api.py` | Generate API endpoint boilerplate | `python create_api.py EndpointName "Description"` |

### Documentation

| Document | Contents |
|----------|----------|
| [SKILL.md](SKILL.md) | Main framework documentation |
| [docs/quickstart.md](docs/quickstart.md) | 5-minute quickstart guide |
| [docs/architecture.md](docs/architecture.md) | Deep dive into architecture |
| [docs/best-practices.md](docs/best-practices.md) | Coding standards and patterns |

### Directory Structure

```
agent-zero-dev/
├── SKILL.md              # Main skill documentation
├── README.md             # This file
├── scripts/              # Code generator scripts
│   ├── create_tool.py
│   ├── create_extension.py
│   ├── create_skill.py
│   └── create_api.py
├── templates/            # Placeholder for templates
└── docs/                 # Additional documentation
    ├── quickstart.md
    ├── architecture.md
    └── best-practices.md
```

## Usage

### Activating This Skill

This skill activates automatically when you mention:
- "extend agent zero"
- "create a tool"
- "build agent zero feature"
- "agent zero development"

### Example Workflows

#### Creating a Weather Tool

```bash
# 1. Generate the tool
python scripts/create_tool.py WeatherLookup "Get weather for a location"

# 2. Edit /a0/python/tools/weather_lookup.py
#    - Add your weather API logic
#    - Update docstrings

# 3. Restart Agent Zero
#    - The tool loads automatically
```

#### Creating a Custom Skill

```bash
# 1. Generate the skill
python scripts/create_skill.py data-processor "Process CSV and JSON data"

# 2. Edit /a0/skills/custom/data-processor/SKILL.md
#    - Add trigger patterns
#    - Write step-by-step instructions

# 3. Test it
#    "Use data-processor to analyze my CSV"
```

## Architecture Overview

Agent Zero is built on these extension points:

1. **Tools** - Agent capabilities (web search, code execution)
2. **Extensions** - Lifecycle hooks (initialization, message processing)
3. **Skills** - Reusable instruction bundles (SKILL.md standard)
4. **APIs** - Web UI endpoints (FastAPI)
5. **Subordinates** - Specialized agent profiles
6. **Projects** - Isolated workspaces with custom config

## Development Workflow

```
1. Brainstorm → Identify what to build
2. Plan → Choose the right extension point
3. Scaffold → Use scripts to generate boilerplate
4. Implement → Fill in your logic
5. Test → Verify with the agent
6. Refine → Iterate based on results
```

## Best Practices

- ✅ Follow existing patterns in the codebase
- ✅ Write clear docstrings and comments
- ✅ Handle errors gracefully
- ✅ Test thoroughly before deploying
- ✅ Update documentation

## Contributing

When adding to this framework:

1. Follow the SKILL.md standard
2. Include examples in documentation
3. Test scripts before committing
4. Update this README

## Resources

- [Agent Zero Main Documentation](https://github.com/frdel/agent-zero)
- [SKILL.md Standard](https://github.com/anthropics/skills/blob/main/SKILL.md)
- [Python Async/Await Guide](https://docs.python.org/3/library/asyncio.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## License

Part of the Agent Zero framework - follow the same license terms.

## Support

- Check [docs/troubleshooting.md](docs/troubleshooting.md) (if exists)
- Review [docs/best-practices.md](docs/best-practices.md)
- Examine existing code in `/a0/python/`

---

**Ready to extend Agent Zero?** Start with [docs/quickstart.md](docs/quickstart.md)!
