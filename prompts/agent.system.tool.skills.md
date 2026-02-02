### skills_tool

manage and use agent skills for specialized capabilities
skills are composable bundles of instructions context and executable code
use progressive disclosure: metadata → full content → referenced files
use "method" arg to specify operation: "list" "load" "read_file" "search"

## Overview

Skills system provides three-level progressive disclosure:
- Level 1: Metadata (name + description) loaded in system prompt at startup
- Level 2: Full SKILL.md content loaded when relevant to task
- Level 3+: Referenced files loaded on-demand

When to use skills:
- Task matches skill description from available skills list
- Need specialized procedures or domain knowledge
- Task requires bundled scripts or automation
- Need step-by-step guidance for complex operations

Progressive workflow:
1. Check available skills metadata already in your context
2. Use "search" if looking for specific capability
3. Use "load" to get full skill instructions and context
4. Use "read_file" to load additional reference documents
5. Use code_execution_tool to run any scripts referenced by the skill

## Operations

### 1. list available skills

Lists all available skills with metadata
Shows name, version, description, tags, and author
Use when: exploring available capabilities or confirming skill exists

~~~json
{
    "thoughts": [
        "Need to see what skills are available",
        "User asked about available capabilities"
    ],
    "headline": "Listing all available skills",
    "tool_name": "skills_tool",
    "tool_args": {
        "method": "list"
    }
}
~~~

Response format:
- Skill name and version
- Brief description
- Tags for categorization
- Author attribution

### 2. load full skill content

Loads complete SKILL.md content with instructions and procedures
Returns metadata, full content, and list of referenced files
Use when: identified relevant skill and need detailed instructions

~~~json
{
    "thoughts": [
        "User needs PDF form extraction",
        "pdf_editing skill will provide procedures",
        "Loading full skill content"
    ],
    "headline": "Loading PDF editing skill",
    "tool_name": "skills_tool",
    "tool_args": {
        "method": "load",
        "skill_name": "pdf_editing"
    }
}
~~~

Required args:
- skill_name: exact name from metadata or list

Response includes:
- Skill metadata (name, version, description, tags)
- Full markdown content with instructions
- List of referenced files available to load
- Code examples and procedures

### 3. read skill reference file

Reads additional reference files from skill directory
Files referenced in SKILL.md can be loaded progressively
Use when: need detailed documentation or examples from skill references

~~~json
{
    "thoughts": [
        "Skill mentioned forms.md for form filling details",
        "Need specific form field handling instructions",
        "Loading reference file"
    ],
    "headline": "Reading PDF forms reference documentation",
    "tool_name": "skills_tool",
    "tool_args": {
        "method": "read_file",
        "skill_name": "pdf_editing",
        "file_path": "forms.md"
    }
}
~~~

Required args:
- skill_name: name of skill containing file
- file_path: relative path within skill directory (e.g. "reference.md" or "examples/example1.md")

Security:
- Path validation prevents directory traversal
- Only files within skill directory accessible
- Supports markdown, text, code files

### 4. search skills by query

Searches skills by text matching in name, description, and tags
Returns ranked results by relevance score
Use when: looking for skills without knowing exact name

~~~json
{
    "thoughts": [
        "User needs web scraping capability",
        "Not sure of exact skill name",
        "Searching for web-related skills"
    ],
    "headline": "Searching for web scraping skills",
    "tool_name": "skills_tool",
    "tool_args": {
        "method": "search",
        "query": "web scraping html parsing"
    }
}
~~~

Required args:
- query: search text (searches name, description, tags)

Scoring:
- Name match: +3 points
- Description match: +2 points
- Tag match: +1 point per tag
- Results sorted by descending score

## Running skill scripts

When a skill includes scripts (listed under its files), use code_execution_tool directly to run them.
The skill's "load" output shows the skill directory path and lists available scripts.
Use read_file to inspect a script before running it if needed.

Example: running a Python script from a skill
1. Load the skill to get its path and script list
2. Use code_execution_tool with runtime="python" to run the script

~~~json
{
    "thoughts": [
        "Need to convert PDF to images",
        "Skill provides convert_pdf_to_images.py at scripts/convert_pdf_to_images.py",
        "Using code_execution_tool to run it directly"
    ],
    "headline": "Converting PDF to images",
    "tool_name": "code_execution_tool",
    "tool_args": {
        "runtime": "python",
        "code": "import subprocess\nsubprocess.run(['python', '/path/to/skill/scripts/convert_pdf_to_images.py', '/path/to/document.pdf', '/tmp/images'], check=True)"
    }
}
~~~

Example: running a shell script from a skill
~~~json
{
    "thoughts": [
        "Skill provides a shell script for data processing",
        "Running it via terminal runtime"
    ],
    "headline": "Running data processing script",
    "tool_name": "code_execution_tool",
    "tool_args": {
        "runtime": "terminal",
        "code": "cd /path/to/skill && bash scripts/process.sh /data/input.csv /tmp/output"
    }
}
~~~

## Best Practices

### When to use skills vs other tools

Use skills when:
- Task requires specialized domain knowledge
- Need structured procedures or step-by-step guidance
- Complex multi-step operations with best practices

Use code_execution_tool directly when:
- Running skill scripts (load skill first to get paths)
- Simple file operations
- General computation

Use other tools when:
- Web search (use search_engine)
- Memory operations (use memory tools)

### Progressive disclosure workflow

1. Start with metadata (already in context)
   - Check available skills list in system prompt
   - Match task to skill description

2. Load full content when relevant
   - Use "load" to get complete instructions
   - Review procedures and examples

3. Load references as needed
   - Use "read_file" for detailed documentation
   - Load only files relevant to current subtask

4. Execute scripts via code_execution_tool
   - Use skill path from "load" output
   - Run scripts directly with code_execution_tool

### Common patterns

Pattern: Using a skill for first time
1. Identify skill from metadata
2. Load full skill content
3. Follow instructions in content
4. Load reference files if mentioned
5. Run scripts via code_execution_tool using paths from load output

Pattern: Exploring capabilities
1. Search with query terms
2. Review matches
3. Load most relevant skill

## Error Handling

Common errors:
- "Skill not found": Check spelling, use list or search to find correct name
- "File not found": Verify file_path matches referenced files from load output

When skill loading fails:
- Verify skill exists using list method
- Check for typos in skill_name
- Ensure skill system is enabled in settings

## Notes

- Skills metadata already loaded in your system prompt
- Skills cache after first load for efficiency
- Referenced files listed in load response
- Use code_execution_tool to run any scripts provided by skills
- All operations return formatted text responses
- Skills follow the open SKILL.md standard (cross-platform compatible)
- Use skills for structured procedures and contextual expertise
