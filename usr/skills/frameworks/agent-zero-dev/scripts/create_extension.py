#!/usr/bin/env python3
"""
Create Extension Boilerplate
Generates a new Agent Zero extension with proper structure and patterns.

Usage:
    python create_extension.py hook_point ExtensionName "Description"
    python create_extension.py agent_init ConfigLoader "Load custom configuration"

Hook Points:
    - agent_init
    - message_loop_start
    - message_loop_end
    - before_main_llm_call
    - response_stream_start
    - response_stream_chunk
    - response_stream_end
    - tool_execute_before
    - tool_execute_after

Output:
    Creates python/extensions/<hook_point>/_XX_extension_name.py
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


def get_next_number(extension_dir: Path) -> int:
    """Get the next available extension number."""
    if not extension_dir.exists():
        return 10
    
    existing = [f for f in extension_dir.iterdir() if f.suffix == '.py' and f.stem.startswith('_')]
    numbers = []
    for f in existing:
        match = re.match(r'_(\d+)_.*', f.stem)
        if match:
            numbers.append(int(match.group(1)))
    
    if numbers:
        # Round up to next 10
        max_num = max(numbers)
        return ((max_num // 10) + 1) * 10
    return 10


def generate_extension_code(class_name: str, description: str, hook_point: str) -> str:
    """Generate the extension boilerplate code."""
    return f'''from python.helpers.extension import Extension
from python.helpers.print_style import PrintStyle


class {class_name}(Extension):
    """
    {description}
    
    Hook Point: {hook_point}
    """

    async def execute(self, **kwargs):
        """
        Execute the extension logic.
        
        Common kwargs by hook point:
        - agent_init: {{}}
        - message_loop_start: {{"message": str}}
        - before_main_llm_call: {{"prompts": list}}
        - response_stream_chunk: {{"chunk": str}}
        - tool_execute_before: {{"tool_name": str, "arguments": dict}}
        - tool_execute_after: {{"tool_name": str, "result": any}}
        """
        agent = self.agent
        context = agent.context
        
        # Access hook-specific data
        data = kwargs.get("data", {{}})
        
        try:
            # TODO: Implement your extension logic
            PrintStyle.hint(f"{class_name} executing for {hook_point}")
            
            # Example: Modify data if applicable
            # data["modified"] = True
            
            return data
            
        except Exception as e:
            PrintStyle.error(f"Error in {class_name}: {{e}}")
            return data
'''


def main():
    valid_hooks = [
        "agent_init", "message_loop_start", "message_loop_end",
        "before_main_llm_call", "response_stream_start", "response_stream_chunk",
        "response_stream_end", "tool_execute_before", "tool_execute_after"
    ]
    
    if len(sys.argv) < 3:
        print("Usage: python create_extension.py hook_point ExtensionName [\"Description\"]")
        print("\nValid hook points: " + ", ".join(valid_hooks))
        print("\nExample: python create_extension.py agent_init ConfigLoader")
        sys.exit(1)
    
    hook_point = sys.argv[1]
    ext_name = sys.argv[2]
    description = sys.argv[3] if len(sys.argv) > 3 else f"{ext_name} extension"
    
    if hook_point not in valid_hooks:
        print(f"Error: Invalid hook point '{hook_point}'")
        print(f"Valid hook points: {', '.join(valid_hooks)}")
        sys.exit(1)
    
    class_name = to_class_name(ext_name)
    ext_file_name = to_snake_case(ext_name)
    
    # Determine output path
    base_dir = Path("/a0/python/extensions")
    if not base_dir.exists():
        base_dir = Path("python/extensions")
    
    extension_dir = base_dir / hook_point
    
    # Get next number
    number = get_next_number(extension_dir)
    
    # Create directory if needed
    extension_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = extension_dir / f"_{number}_{ext_file_name}.py"
    
    # Check if file exists
    if output_file.exists():
        print(f"Error: File already exists: {output_file}")
        sys.exit(1)
    
    # Generate and write code
    code = generate_extension_code(class_name, description, hook_point)
    output_file.write_text(code)
    
    print(f"✅ Created extension: {output_file}")
    print(f"   Class: {class_name}")
    print(f"   Hook Point: {hook_point}")
    print(f"\nNext steps:")
    print(f"  1. Edit {output_file} to implement your logic")
    print(f"  2. Check kwargs for your specific hook point")
    print(f"  3. Test by running the framework")
    print(f"  4. Restart Agent Zero to load the extension")


if __name__ == "__main__":
    main()
