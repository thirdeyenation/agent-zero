#!/usr/bin/env python3
"""
Create Skill Boilerplate
Generates a new Agent Zero skill with SKILL.md and directory structure.

Usage:
    python create_skill.py skill-name "Description of the skill"
    python create_skill.py web-scraper "Scrape web pages for data extraction"

Output:
    Creates skills/custom/<skill-name>/ directory with SKILL.md
"""

import sys
import re
from pathlib import Path
from datetime import datetime


def validate_skill_name(name: str) -> str:
    """Validate and normalize skill name."""
    # Remove leading/trailing whitespace
    name = name.strip()
    # Replace spaces with hyphens
    name = name.replace(" ", "-")
    # Ensure only lowercase letters, numbers, and hyphens
    if not re.match(r'^[a-z0-9-]+$', name):
        raise ValueError(f"Invalid skill name: {name}. Use only lowercase letters, numbers, and hyphens.")
    return name


def generate_skill_md(name: str, description: str, author: str) -> str:
    """Generate the SKILL.md content."""
    # Generate trigger patterns based on name and description
    words = name.replace("-", " ").split()
    trigger_patterns = [
        f'"{name}"',
        f'"{" ".join(words)}"',
    ]
    
    # Add description words as triggers
    desc_words = description.lower().split()[:3]
    if desc_words:
        trigger_patterns.append(f'"{" ".join(desc_words)}"')
    
    triggers_str = "\n  - ".join(trigger_patterns)
    
    return f'''---
name: "{name}"
description: "{description}"
version: "1.0.0"
author: "{author}"
tags: ["custom", "helper"]
trigger_patterns:
  - {triggers_str}
---

# {name.replace("-", " ").title()}

## When to Use

This skill activates when users mention:
- Keywords: {name}
- Related concepts: {description}

Use this skill to:
1. First use case
2. Second use case
3. Third use case

## The Process

### Step 1: Preparation
Describe initial setup or validation steps.

### Step 2: Main Processing
Detail the core functionality.

### Step 3: Finalization
Explain output formatting and delivery.

## Examples

### Example 1: Basic Usage

**User**: "Use {name} to..."

**Agent**: 
> I'll help you with that. Here's what I'll do:
> 1. Step one
> 2. Step two
> 3. Step three

### Example 2: Advanced Usage

**User**: "Complex {name} task with parameters"

**Agent**:
> Processing with custom parameters...
> - Parameter A: value
> - Parameter B: value
> Result: success

## Scripts and Resources

This skill includes optional helper scripts:

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/helper.py` | Description | `python scripts/helper.py arg1 arg2` |

To use scripts:
```json
{{
  "method": "execute_script",
  "skill_name": "{name}",
  "script_path": "scripts/helper.py",
  "script_args": {{"arg1": "value"}},
  "arg_style": "positional"
}}
```

## Best Practices

### DO
- ✅ Best practice 1
- ✅ Best practice 2
- ✅ Best practice 3

### DON'T
- ❌ Anti-pattern 1
- ❌ Anti-pattern 2

## Tips and Tricks

- Tip 1
- Tip 2
- Tip 3

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Problem | Root cause | How to fix |

## Related Skills

- `related-skill-1` - Related functionality
- `related-skill-2` - Complementary feature
'''


def main():
    if len(sys.argv) < 2:
        print("Usage: python create_skill.py skill-name [\"Description\"]")
        print("Example: python create_skill.py data-processor \"Process and transform data\"")
        print("\nSkill name rules:")
        print("  - Use lowercase letters, numbers, and hyphens only")
        print("  - No spaces (use hyphens)")
        print("  - Example: web-scraper, data-processor, api-client")
        sys.exit(1)
    
    try:
        skill_name = validate_skill_name(sys.argv[1])
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    description = sys.argv[2] if len(sys.argv) > 2 else f"Skill for {skill_name}"
    author = "Agent Zero User"
    
    # Determine output path
    base_dir = Path("/a0/skills/custom")
    if not base_dir.exists():
        base_dir = Path("skills/custom")
    
    skill_dir = base_dir / skill_name
    
    # Check if skill already exists
    if skill_dir.exists():
        print(f"Error: Skill already exists: {skill_dir}")
        print("Use a different name or delete the existing skill.")
        sys.exit(1)
    
    # Create directory structure
    skill_dir.mkdir(parents=True)
    (skill_dir / "scripts").mkdir()
    (skill_dir / "templates").mkdir()
    (skill_dir / "docs").mkdir()
    
    # Create SKILL.md
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(generate_skill_md(skill_name, description, author))
    
    # Create placeholder files
    (skill_dir / "scripts" / "helper.py").write_text("""#!/usr/bin/env python3
# Helper script for skill

def main():
    print("Helper script placeholder")
    # TODO: Implement script logic

if __name__ == "__main__":
    main()
""")
    
    (skill_dir / "templates" / "template.md").write_text("# Template placeholder\n\nEdit this template as needed.")
    (skill_dir / "docs" / "examples.md").write_text("# Examples\n\nAdd usage examples here.")
    
    print(f"✅ Created skill: {skill_dir}")
    print(f"   Name: {skill_name}")
    print(f"   Description: {description}")
    print(f"\nStructure:")
    print(f"  {skill_dir}/")
    print(f"  ├── SKILL.md         # Main skill file (EDIT THIS)")
    print(f"  ├── scripts/")
    print(f"  │   └── helper.py    # Helper script")
    print(f"  ├── templates/")
    print(f"  │   └── template.md  # Template file")
    print(f"  └── docs/")
    print(f"      └── examples.md  # Documentation")
    print(f"\nNext steps:")
    print(f"  1. Edit {skill_dir}/SKILL.md to add your instructions")
    print(f"  2. Update trigger_patterns for activation")
    print(f"  3. Implement scripts in scripts/")
    print(f"  4. Test the skill by using trigger words")
    print(f"  5. Skills load automatically on agent initialization")


if __name__ == "__main__":
    main()
