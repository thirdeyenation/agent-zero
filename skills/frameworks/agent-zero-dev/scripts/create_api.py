#!/usr/bin/env python3
"""
Create API Endpoint Boilerplate
Generates a new Agent Zero API endpoint with proper structure and patterns.

Usage:
    python create_api.py EndpointName "Description"
    python create_api.py TaskManager "Manage async tasks"

Output:
    Creates python/api/endpoint_name.py with full boilerplate
"""

import sys
import re
from pathlib import Path


def to_snake_case(name: str) -> str:
    """Convert CamelCase or spaced name to snake_case."""
    name = name.replace(" ", "_")
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def to_class_name(name: str) -> str:
    """Convert snake_case or spaced name to CamelCase."""
    return ''.join(word.capitalize() for word in name.replace('_', ' ').split())


def generate_api_code(class_name: str, endpoint_name: str, description: str) -> str:
    """Generate the API endpoint boilerplate code."""
    return f'''from python.helpers.api import ApiHandler, Request, Response
from agent import AgentContext
from python.helpers.print_style import PrintStyle


class {class_name}(ApiHandler):
    """
    {description}
    
    Endpoint: /api/{endpoint_name}
    Methods: GET, POST (as needed)
    """

    async def process(self, input: dict, request: Request) -> dict | Response:
        """
        Process the API request.
        
        Args:
            input: Parsed JSON body or query parameters
            request: Werkzeug Request object
            
        Returns:
            dict response or Response object
        """
        # Get context (creates new if ctxid is empty)
        ctxid = input.get("context", "")
        context = self.use_context(ctxid)
        
        # Handle different HTTP methods
        if request.method == "GET":
            return await self._handle_get(input, context)
        elif request.method == "POST":
            return await self._handle_post(input, request, context)
        else:
            return {{
                "success": False,
                "error": f"Method {{request.method}} not supported"
            }}
    
    async def _handle_get(self, input: dict, context: AgentContext) -> dict:
        """Handle GET requests."""
        # TODO: Implement GET logic
        param = input.get("param", "default")
        
        return {{
            "success": True,
            "data": {{
                "message": f"GET request processed with param: {{param}}",
                "context": context.id
            }}
        }}
    
    async def _handle_post(self, input: dict, request: Request, context: AgentContext) -> dict:
        """Handle POST requests."""
        # TODO: Implement POST logic
        # Access JSON body: input.get("field")
        # Access form data: request.form.get("field")
        # Access files: request.files.get("file")
        
        data = input.get("data", {{}})
        
        PrintStyle.hint(f"{class_name} processing POST request")
        
        return {{
            "success": True,
            "data": {{
                "message": "POST request processed",
                "received": data,
                "context": context.id
            }}
        }}
'''


def main():
    if len(sys.argv) < 2:
        print("Usage: python create_api.py EndpointName [\"Description\"]")
        print("Example: python create_api.py TaskManager \"Manage async tasks\"")
        print("\nThe endpoint will be accessible at /api/endpoint-name")
        sys.exit(1)
    
    endpoint_input = sys.argv[1]
    description = sys.argv[2] if len(sys.argv) > 2 else f"{endpoint_input} API endpoint"
    
    class_name = to_class_name(endpoint_input)
    endpoint_name = to_snake_case(endpoint_input)
    
    # Generate code
    code = generate_api_code(class_name, endpoint_name, description)
    
    # Determine output path
    output_dir = Path("/a0/python/api")
    if not output_dir.exists():
        output_dir = Path("python/api")
    
    output_file = output_dir / f"{endpoint_name}.py"
    
    # Check if file exists
    if output_file.exists():
        print(f"Error: File already exists: {output_file}")
        print("Use a different name or delete the existing file.")
        sys.exit(1)
    
    # Write file
    output_file.write_text(code)
    
    print(f"✅ Created API endpoint: {output_file}")
    print(f"   Class: {class_name}")
    print(f"   Endpoint: /api/{endpoint_name}")
    print(f"   URL: http://localhost:5001/api/{endpoint_name}")
    print(f"\nNext steps:")
    print(f"  1. Edit {output_file} to implement your logic")
    print(f"  2. Add route registration if needed (check python/api/__init__.py)")
    print(f"  3. Test with curl or the Web UI")
    print(f"  4. Restart Agent Zero to load the new endpoint")
    print(f"\nExample curl commands:")
    print(f'  GET:  curl "http://localhost:5001/api/{endpoint_name}?context=test&param=value"')
    print(f'  POST: curl -X POST "http://localhost:5001/api/{endpoint_name}" -H "Content-Type: application/json" -d \'{{"context":"test","data":{{"key":"value"}}}}\'')


if __name__ == "__main__":
    main()
