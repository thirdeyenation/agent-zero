---
name: "a0dev-create-api"
description: "Add Web UI and REST API endpoints for Agent Zero."
version: "1.0.0"
author: "Agent Zero Team"
tags: ["agent-zero-dev", "api", "endpoint", "fastapi", "webui"]
trigger_patterns:
  - "create api"
  - "new endpoint"
  - "add api"
  - "api endpoint"
  - "/a0dev-create-api"
---

# Agent Zero Dev: Create API

API endpoints serve the Web UI and external clients using FastAPI. Each endpoint inherits from `ApiHandler`.

## API Location

```
python/api/
├── poll.py           # Long-polling for updates
├── chat.py           # Chat message handling
├── frameworks.py     # Framework management
├── settings.py       # Settings management
└── your_endpoint.py  # New endpoints go here
```

## API Endpoint Structure

```python
# python/api/my_endpoint.py
from python.helpers.api import ApiHandler, Request, Input, Output

class MyEndpoint(ApiHandler):
    """
    Handle requests for /api/my-endpoint

    Query params / JSON body:
        - param1: Description of param1
        - param2: Description of param2
    """

    async def process(self, input: Input, request: Request) -> Output:
        # Get parameters from input (works for both GET params and POST body)
        param1 = input.get("param1", "default")
        param2 = input.get("param2")

        try:
            # Process the request
            result = await self.do_work(param1, param2)

            return {
                "ok": True,
                "data": result,
            }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
            }

    async def do_work(self, param1, param2):
        # Implementation
        return {"processed": param1}
```

## Type Definitions

```python
Input = dict          # Request parameters (query or body)
Output = dict | Response  # Return dict or FastAPI Response
Request = fastapi.Request  # Full request object
```

## URL Routing

Endpoints are auto-routed based on filename:
- `my_endpoint.py` → `/api/my_endpoint` or `/api/my-endpoint`
- Class name doesn't affect routing

## Getting Agent Context

```python
async def process(self, input: Input, request: Request) -> Output:
    # Get context ID from request
    ctxid = input.get("context", "")

    # Get or create context (creates if doesn't exist)
    context = self.use_context(ctxid)

    # Access context data
    data = context.data

    # Get the agent for this context
    agent = self.get_context_agent(context)

    return {
        "ok": True,
        "context": context.id,
    }
```

## Complete Example: Data Query Endpoint

```python
# python/api/data_query.py
from python.helpers.api import ApiHandler, Request, Input, Output
from dataclasses import asdict

class DataQuery(ApiHandler):
    """
    Query and manipulate stored data.

    Actions:
        - get: Retrieve data by key
        - set: Store data with key
        - list: List all keys
        - delete: Remove data by key

    Query params / JSON body:
        - action: The action to perform
        - context: Agent context ID
        - key: Data key (for get/set/delete)
        - value: Data value (for set)
    """

    async def process(self, input: Input, request: Request) -> Output:
        action = input.get("action", "list")
        ctxid = input.get("context", "")
        key = input.get("key")
        value = input.get("value")

        try:
            context = self.use_context(ctxid)

            if action == "list":
                keys = list(context.data.keys())
                return {"ok": True, "keys": keys}

            elif action == "get":
                if not key:
                    return {"ok": False, "error": "Key required"}
                data = context.data.get(key)
                return {"ok": True, "key": key, "value": data}

            elif action == "set":
                if not key:
                    return {"ok": False, "error": "Key required"}
                context.data[key] = value
                return {"ok": True, "key": key, "stored": True}

            elif action == "delete":
                if not key:
                    return {"ok": False, "error": "Key required"}
                if key in context.data:
                    del context.data[key]
                return {"ok": True, "key": key, "deleted": True}

            else:
                return {"ok": False, "error": f"Unknown action: {action}"}

        except Exception as e:
            return {"ok": False, "error": str(e)}
```

## Handling File Uploads

```python
# python/api/file_upload.py
from python.helpers.api import ApiHandler, Request, Input, Output
from fastapi import UploadFile
from python.helpers import files

class FileUpload(ApiHandler):
    """Handle file uploads"""

    async def process(self, input: Input, request: Request) -> Output:
        # Access uploaded file from request
        form = await request.form()
        uploaded_file: UploadFile = form.get("file")

        if not uploaded_file:
            return {"ok": False, "error": "No file provided"}

        # Read file content
        content = await uploaded_file.read()
        filename = uploaded_file.filename

        # Save file
        save_path = f"/tmp/uploads/{filename}"
        files.write_file(save_path, content.decode())

        return {
            "ok": True,
            "filename": filename,
            "size": len(content),
            "path": save_path,
        }
```

## Streaming Responses

```python
# python/api/stream_data.py
from python.helpers.api import ApiHandler, Request, Input, Output
from fastapi.responses import StreamingResponse
import asyncio

class StreamData(ApiHandler):
    """Stream data to client"""

    async def process(self, input: Input, request: Request) -> Output:
        async def generate():
            for i in range(10):
                yield f"data: {i}\n\n"
                await asyncio.sleep(0.5)

        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
```

## Using the Generator Script

```bash
python skills/frameworks/agent-zero-dev/scripts/create_api.py \
    DataQuery \
    "Query and manipulate stored data"
```

Generates: `python/api/data_query.py`

## API Best Practices

### DO

- ✅ Use `ApiHandler` base class
- ✅ Return consistent response format (`{ok, data/error}`)
- ✅ Document params in docstring
- ✅ Handle errors gracefully
- ✅ Use `self.use_context()` for context management
- ✅ Support both GET and POST where appropriate

### DON'T

- ❌ Expose sensitive data
- ❌ Skip input validation
- ❌ Block the event loop
- ❌ Return inconsistent response formats
- ❌ Forget error handling

## Testing Your API

1. **Restart Agent Zero** (APIs load at startup)
2. **Test with curl**:
   ```bash
   curl "http://localhost:8080/api/my_endpoint?param1=value"
   ```
3. **Test with browser** (for GET endpoints)
4. **Check logs** for errors

## Frontend Integration

APIs are called from the Web UI using:

```javascript
// webui/js/api.js
import { callJsonApi, fetchApi } from "/js/api.js";

// JSON POST with CSRF
const result = await callJsonApi("/my_endpoint", { param1: "value" });

// Raw fetch with CSRF
const response = await fetchApi("/my_endpoint", { method: "GET" });
```

## Next Steps

After creating an API:
- Test all actions/parameters
- Add frontend integration if needed
- Document the endpoint
- Consider rate limiting for public APIs
