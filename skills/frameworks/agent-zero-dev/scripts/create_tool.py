#!/usr/bin/env python3
"""
Create Tool Boilerplate
Generates a new Agent Zero tool with proper structure and patterns.

Usage:
    python create_tool.py ToolName "Description of what the tool does"
    python create_tool.py WeatherLookup "Get weather information for locations"

Output:
    Creates python/tools/tool_name.py with full boilerplate
"""

import sys
import re
from pathlib import Path


def to_snake_case(name: str) -> str:
    """Convert CamelCase or spaced name to snake_case."""
    # Handle spaces first
    name = name.replace(" ", "_")
    # Insert underscore before capital letters
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def to_class_name(name: str) -> str:
    """Convert snake_case or spaced name to CamelCase."""
    # Remove spaces and underscores, capitalize each word
    return ''.join(word.capitalize() for word in name.replace('_', ' ').split())


def generate_tool_code(class_name: str, tool_name: str, description: str) -> str:
    """Generate the tool boilerplate code."""
    return f'''from python.helpers.tool import Tool, Response


class {class_name}(Tool):
    """
    {description}
    
    Arguments (tool_args):
        - param1: Description of first parameter
        - param2: Description of second parameter
    
    Returns:
        Response object with result message
    """

    async def execute(self, **kwargs) -> Response:
        # Get arguments from kwargs with fallback to self.args
        param1 = kwargs.get("param1") or self.args.get("param1", "")
        param2 = kwargs.get("param2") or self.args.get("param2", "")
        
        try:
            # TODO: Implement your tool logic here
            result = await self._process(param1, param2)
            
            return Response(
                message=result,
                break_loop=False
            )
        except Exception as e:
            return Response(
                message=f"Error in {class_name}: {{e}}",
                break_loop=False
            )
    
    async def _process(self, param1: str, param2: str) -> str:
        """
        Implement your main tool logic here.
        
        Args:
            param1: First parameter
            param2: Second parameter
            
        Returns:
            Result string to return to agent
        """
        # TODO: Replace with actual implementation
        return f"Processed {{param1}} and {{param2}}"
'''


def main():
    if len(sys.argv) < 2:
        print("Usage: python create_tool.py ToolName [\"Description\"]")
        print("Example: python create_tool.py WeatherLookup \"Get weather for locations\"")
        sys.exit(1)
    
    tool_input = sys.argv[1]
    description = sys.argv[2] if len(sys.argv) > 2 else f"{tool_input} tool"
    
    class_name = to_class_name(tool_input)
    tool_name = to_snake_case(tool_input)
    
    # Generate code
    code = generate_tool_code(class_name, tool_name, description)
    
    # Determine output path
    output_dir = Path("/a0/python/tools")
    if not output_dir.exists():
        # Try relative path
        output_dir = Path("python/tools")
    
    output_file = output_dir / f"{tool_name}.py"
    
    # Check if file exists
    if output_file.exists():
        print(f"Error: File already exists: {output_file}")
        print("Use a different name or delete the existing file.")
        sys.exit(1)
    
    # Write file
    output_file.write_text(code)
    print(f"✅ Created tool: {output_file}")
    print(f"   Class: {class_name}")
    print(f"   Tool name (snake_case): {tool_name}")
    print(f"\nNext steps:")
    print(f"  1. Edit {output_file} to implement your logic")
    print(f"  2. Update the docstring with actual arguments")
    print(f"  3. Test your tool with the agent")
    print(f"  4. Restart Agent Zero to load the new tool")


if __name__ == "__main__":
    main()
