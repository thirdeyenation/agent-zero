---
name: "bmb-module"
description: "Package agents and workflows into shareable BMad modules."
version: "1.0.0"
author: "BMad Method"
tags: ["bmad-builder", "module", "package", "distribution"]
trigger_patterns:
  - "build module"
  - "create module"
  - "package module"
  - "module builder"
  - "/bmb-module"
---

# BMad Builder: Create Module

Package agents and workflows into shareable BMad modules.

## Overview

Modules bundle related agents and workflows into distributable packages that can be:
- Installed via `npx bmad-method install`
- Shared on npm or GitHub
- Versioned and maintained

## Module Structure

```
your-module/
├── src/
│   ├── module.yaml      # Module metadata and install config
│   ├── agents/          # Agent definitions (.agent.yaml)
│   ├── workflows/       # Workflow files
│   └── tools/           # Small reusable tools
├── docs/
│   └── README.md        # Module documentation
├── package.json         # NPM package info
└── LICENSE
```

## Process

### 1. Define Module Scope

**Questions:**
- What domain does this module serve?
- What agents and workflows does it include?
- Who is the target user?

### 2. Create module.yaml

```yaml
# src/module.yaml
name: "your-module-name"
version: "1.0.0"
description: "[Module purpose]"
author: "[Your name/org]"

# What gets installed
agents:
  - agents/agent-one.agent.yaml
  - agents/agent-two.agent.yaml

workflows:
  - workflows/workflow-one.yaml
  - workflows/workflow-two.yaml

# Installation options
install:
  required: []  # Always install these
  optional:     # Let user choose
    - name: "[Feature Set]"
      description: "[What it adds]"
      includes:
        - agents/optional-agent.agent.yaml

# Dependencies on other modules
dependencies:
  - bmad-method@^1.0.0
```

### 3. Create package.json

```json
{
  "name": "bmad-module-your-name",
  "version": "1.0.0",
  "description": "BMad module for [domain]",
  "keywords": ["bmad", "bmad-method", "your-domain"],
  "repository": {
    "type": "git",
    "url": "https://github.com/your-org/your-module"
  },
  "files": ["src/"],
  "scripts": {
    "release": "npm version patch && git push --follow-tags"
  },
  "license": "MIT"
}
```

### 4. Write Documentation

Create `docs/README.md` with:
- What the module does
- Installation instructions
- Quick start guide
- Agent and workflow reference
- Examples

### 5. Test Locally

Before publishing:

```bash
# Test installation
npx bmad-method install --local ./path/to/module

# Verify agents work
# Run workflows
# Check documentation renders
```

### 6. Publish

```bash
# Tag release
git tag v1.0.0
git push origin v1.0.0

# Publish to npm (optional)
npm publish
```

## Best Practices

1. **Focused Scope**: One module = one domain
2. **Complete Package**: Include docs, examples, and tests
3. **Semantic Versioning**: Follow semver for updates
4. **Clear Dependencies**: List required BMad version
5. **License**: Include appropriate license

## Module Naming

Convention: `bmad-module-[domain]`

Examples:
- `bmad-module-game-dev-studio`
- `bmad-module-creative-intelligence`
- `bmad-module-security-audit`

## Distribution Options

| Method | Best For |
|--------|----------|
| npm | Public modules, easy installation |
| GitHub | Private/org modules, version control |
| Local | Development, testing |

## Next Steps

After creating a module:
- Test with fresh installation
- Write comprehensive docs
- Share with the community
- Maintain and update based on feedback
