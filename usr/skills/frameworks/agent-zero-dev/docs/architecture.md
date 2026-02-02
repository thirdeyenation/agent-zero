# Agent Zero Architecture

This document provides an in-depth look at Agent Zero's architecture.

## Core Philosophy

Agent Zero is designed around the principle of **composable intelligence**:
- Small, focused components that work together
- Clear interfaces between layers
- Extensible at every level
- Async-first for responsiveness

## Component Layers

```
┌─────────────────────────────────────────────┐
│           Web UI (Alpine.js)                │
│  - Chat interface                           │
│  - File management                          │
│  - Memory dashboard                         │
└─────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────┐
│           API Layer (FastAPI)               │
│  - REST endpoints                           │
│  - WebSocket for streaming                  │
│  - File uploads/downloads                   │
└─────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────┐
│           Agent Core                        │
│  - Message loop                             │
│  - LLM interaction                          │
│  - Context management                       │
└─────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────┐
│           Extension Points                  │
│  - agent_init                               │
│  - message_loop_*                           │
│  - response_stream_*                        │
│  - tool_execute_*                           │
└─────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────┐
│           Tool Layer                        │
│  - Built-in tools                           │
│  - Custom tools                             │
│  - External tool calls                      │
└─────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────┐
│           Skill System                      │
│  - SKILL.md based                           │
│  - Progressive disclosure                   │
│  - Script execution                         │
└─────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────┐
│           Memory Layer                      │
│  - FAISS vector store                       │
│  - Shared AgentContext                      │
│  - Archive/recovery                         │
└─────────────────────────────────────────────┘
```

## Data Flow

### Message Processing Flow

1. **User Input** → API endpoint receives message
2. **Extension: message_loop_start** → Pre-processing
3. **Context Retrieval** → Get or create AgentContext
4. **Extension: before_main_llm_call** → Modify prompts
5. **LLM Call** → Send to language model
6. **Extension: response_stream_start** → Begin streaming
7. **Response Chunks** → Stream to UI via WebSocket
8. **Extension: response_stream_chunk** → Transform output
9. **Extension: response_stream_end** → Finalize
10. **Tool Execution** (if needed)
    - Extension: tool_execute_before
    - Tool.execute()
    - Extension: tool_execute_after
11. **Response to User** → Complete message

### Context Sharing

All agents in a conversation share the same `AgentContext`:

```python
# Main agent stores data
self.agent.context.data["user_preference"] = "dark_mode"

# Subordinate can access the same data
preference = self.agent.context.data.get("user_preference")
```

This enables:
- Persistent memory across agent switches
- Shared state between parent and subordinates
- Session-wide configuration

## Extension System

Extensions are Python classes that hook into specific lifecycle points.

### Execution Order

Extensions execute in numeric order based on filename prefix:

```
_10_first.py       # Runs first
_20_second.py      # Runs second
_30_third.py       # Runs third
```

### Hook Points

| Hook | Timing | Use Case |
|------|--------|----------|
| `agent_init` | Agent creation | Configuration loading |
| `message_loop_start` | Before processing | Input validation |
| `message_loop_end` | After processing | Cleanup |
| `before_main_llm_call` | Before LLM | Prompt modification |
| `response_stream_start` | Stream begins | Initialize handlers |
| `response_stream_chunk` | Per chunk | Transform output |
| `response_stream_end` | Stream complete | Finalize |
| `tool_execute_before` | Before tool | Validation |
| `tool_execute_after` | After tool | Post-processing |

## Memory System

### Vector Memory

FAISS-based vector storage for semantic search:

```python
# Save to memory
memory_save(text="Important information")

# Load from memory
results = memory_load(query="Find important info")
```

### Archive System

Soft-delete with recovery capability:

```python
# Delete (moves to archive)
memory_delete(ids=["id1", "id2"])

# Recover from archive
# (via memory dashboard or direct DB access)
```

## Skill System

Skills follow the SKILL.md standard:

### Progressive Disclosure

1. **Level 1: Metadata** - Always loaded (name, description, tags)
2. **Level 2: Full Content** - Loaded on demand (instructions)
3. **Level 3: Scripts** - Executed as needed

### Skill Loading

```
usr/skills/
├── builtin/      # System skills (loaded first)
├── custom/       # User-created skills
└── frameworks/   # Multi-phase framework skills
```

## Subordinate System

Specialized agents with custom profiles:

```
agents/
├── default/      # Default profile
├── developer/    # Coding specialist
├── researcher/   # Research specialist
└── [custom]/     # Your profiles
```

Each profile contains:
- `agent.json` - Configuration
- `prompts/system.md` - System prompt
- `prompts/subordinates.md` - Delegation prompts

## Security Considerations

### Sandboxing

- Tools run in isolated Python environment
- File system access limited to /a0 directory
- Network access controlled by tool permissions

### Secrets Management

Secrets stored in environment variables:

```python
# Access secrets
from python.helpers import secrets
api_key = secrets.get("API_KEY")
```

## Performance Optimization

### Async Patterns

All I/O is async to prevent blocking:

```python
# Concurrent execution
tasks = [fetch_data(url) for url in urls]
results = await asyncio.gather(*tasks)
```

### Caching

- Skill content cached after first load
- Context data persisted in memory
- Vector embeddings cached in FAISS

### Streaming

LLM responses stream to UI for perceived performance:

```python
for chunk in llm_stream(prompt):
    await send_to_ui(chunk)
```

## Extension Points Deep Dive

### Creating Custom Hooks

You can create custom hook points for your extensions:

```python
# Define hook in your extension
await extension.call_extensions("my_custom_hook", agent=agent, data=data)
```

### Inter-Extension Communication

Extensions can communicate via context data:

```python
# Extension A sets data
self.agent.context.data["ext_a_result"] = result

# Extension B reads it
result = self.agent.context.data.get("ext_a_result")
```

## Debugging and Development

### Logging

Use PrintStyle for consistent logging:

```python
PrintStyle.hint("Informational message")
PrintStyle.warning("Warning message")
PrintStyle.error("Error message")
PrintStyle.bold("Important message")
```

### Debugging Extensions

Add debug output to trace execution:

```python
async def execute(self, **kwargs):
    PrintStyle.hint(f"Extension {self.__class__.__name__} executing")
    PrintStyle.hint(f"Received kwargs: {kwargs}")
    # ... logic ...
```

### Testing Tools

Test tools in isolation:

```python
import asyncio
from python.tools.my_tool import MyTool

tool = MyTool()
result = asyncio.run(tool.execute(param="value"))
print(result.message)
```
