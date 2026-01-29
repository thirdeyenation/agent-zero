---
name: "a0dev-create-project"
description: "Set up project-specific configuration for Agent Zero workspaces."
version: "1.0.0"
author: "Agent Zero Team"
tags: ["agent-zero-dev", "project", "configuration", "workspace"]
trigger_patterns:
  - "create project"
  - "new project"
  - "setup project"
  - "project config"
  - "/a0dev-create-project"
---

# Agent Zero Dev: Create Project

Projects provide isolated workspaces with custom configuration, instructions, and skills specific to a codebase or task.

## Project Location

```
/path/to/your/project/
├── .a0proj/                    # Agent Zero project config
│   ├── config.json             # Project configuration
│   ├── instructions.md         # Project-specific instructions
│   └── skills/                 # Project-specific skills
│       └── custom-skill/
│           └── SKILL.md
└── <your-project-files>/       # Your actual project
```

## Configuration Files

### .a0proj/config.json

```json
{
  "name": "My Project",
  "description": "Brief project description",
  "version": "1.0.0",

  "agent": {
    "model": "anthropic/claude-sonnet-4-20250514",
    "temperature": 0.7
  },

  "tools": {
    "allowed": ["*"],
    "disabled": []
  },

  "skills": {
    "auto_load": ["project-specific-skill"],
    "disabled": []
  },

  "extensions": {
    "enabled": [],
    "disabled": []
  },

  "paths": {
    "work_dir": ".",
    "output_dir": "./output"
  }
}
```

### Configuration Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Project display name |
| `description` | string | Brief description |
| `agent.model` | string | Default LLM model |
| `agent.temperature` | float | Response randomness |
| `tools.allowed` | array | Allowed tools (`["*"]` for all) |
| `tools.disabled` | array | Explicitly disabled tools |
| `skills.auto_load` | array | Skills to load automatically |
| `paths.work_dir` | string | Working directory |

### .a0proj/instructions.md

```markdown
# Project: [Project Name]

## Overview
[What this project does and its purpose]

## Tech Stack
- Language: [Python 3.12+]
- Framework: [FastAPI]
- Database: [PostgreSQL]
- Other: [Docker, Redis]

## Architecture
[Brief architecture description]

```
project/
├── api/           # API endpoints
├── services/      # Business logic
├── models/        # Data models
└── tests/         # Test files
```

## Coding Standards
- Follow [PEP 8 / Standard Style]
- Write tests for all functions
- Use type hints
- Document public APIs

## Important Files
- `api/main.py` - Entry point
- `services/core.py` - Core logic
- `config.py` - Configuration

## Commands
- `make dev` - Start development server
- `make test` - Run tests
- `make lint` - Run linter

## Notes
[Any special considerations or warnings]
```

## Complete Example: Python API Project

### .a0proj/config.json

```json
{
  "name": "User API Service",
  "description": "REST API for user management",
  "version": "1.0.0",

  "agent": {
    "model": "anthropic/claude-sonnet-4-20250514",
    "temperature": 0.3
  },

  "tools": {
    "allowed": ["*"],
    "disabled": ["browser_tool"]
  },

  "skills": {
    "auto_load": ["api-development", "testing"],
    "disabled": []
  },

  "paths": {
    "work_dir": ".",
    "output_dir": "./generated"
  },

  "custom": {
    "test_command": "pytest -v",
    "lint_command": "ruff check .",
    "database": "postgresql://localhost/userdb"
  }
}
```

### .a0proj/instructions.md

```markdown
# Project: User API Service

## Overview
REST API service for user management with authentication, profiles, and permissions.

## Tech Stack
- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy (async)
- Pydantic v2
- pytest

## Architecture

```
src/
├── api/
│   ├── routes/        # API endpoints
│   ├── deps.py        # Dependencies
│   └── main.py        # FastAPI app
├── models/
│   ├── user.py        # User model
│   └── base.py        # Base model
├── services/
│   ├── auth.py        # Authentication
│   └── user.py        # User service
├── schemas/
│   └── user.py        # Pydantic schemas
└── tests/
    ├── conftest.py    # Test fixtures
    └── test_user.py   # User tests
```

## Coding Standards
- PEP 8 compliance (enforced by ruff)
- Type hints on all functions
- Docstrings for public APIs
- 80%+ test coverage
- Async/await for I/O operations

## API Conventions
- RESTful endpoints
- JSON request/response
- Standard error format: `{"detail": "message"}`
- Auth via Bearer token

## Commands
```bash
# Development
uvicorn src.api.main:app --reload

# Testing
pytest -v --cov=src

# Linting
ruff check src/
ruff format src/
```

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing key
- `DEBUG` - Enable debug mode

## Important Notes
- Never commit `.env` files
- Run migrations before testing
- Use dependency injection for services
```

## Project-Specific Skills

Create skills that only apply to this project:

```
.a0proj/skills/
└── deploy-staging/
    └── SKILL.md
```

```yaml
---
name: "deploy-staging"
description: "Deploy this project to staging environment"
trigger_patterns:
  - "deploy to staging"
  - "staging deploy"
---

# Deploy to Staging

## Steps
1. Run tests: `pytest -v`
2. Build image: `docker build -t userapi:staging .`
3. Push: `docker push registry.example.com/userapi:staging`
4. Deploy: `kubectl apply -f k8s/staging/`

## Verification
- Check pods: `kubectl get pods -n staging`
- Check logs: `kubectl logs -n staging -l app=userapi`
- Test endpoint: `curl https://staging.example.com/health`
```

## Setting Up a New Project

### Quick Setup

1. **Create the config directory**:
   ```bash
   mkdir -p .a0proj/skills
   ```

2. **Create config.json**:
   ```bash
   cat > .a0proj/config.json << 'EOF'
   {
     "name": "My Project",
     "description": "Project description"
   }
   EOF
   ```

3. **Create instructions.md**:
   ```bash
   cat > .a0proj/instructions.md << 'EOF'
   # Project: My Project

   ## Overview
   [Describe your project]

   ## Tech Stack
   [List technologies]

   ## Commands
   [List common commands]
   EOF
   ```

4. **Open project in Agent Zero**:
   - Navigate to project directory
   - Agent will auto-detect `.a0proj/`

## Best Practices

### DO

- ✅ Keep instructions concise but complete
- ✅ Document important file locations
- ✅ Include common commands
- ✅ List coding standards
- ✅ Update as project evolves

### DON'T

- ❌ Include sensitive data (secrets, keys)
- ❌ Write overly detailed instructions
- ❌ Forget to update after changes
- ❌ Create conflicting tool configurations

## Project Detection

Agent Zero detects projects by:
1. Looking for `.a0proj/` directory
2. Loading `config.json` for settings
3. Loading `instructions.md` for context
4. Discovering project-specific skills

## Next Steps

After setting up a project:
- Test that instructions are helpful
- Add project-specific skills as needed
- Refine configuration based on usage
- Keep documentation current
