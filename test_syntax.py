import ast
with open("api/mcp_servers_apply.py", "r") as f:
    source = f.read()
ast.parse(source)
print("Syntax OK")
