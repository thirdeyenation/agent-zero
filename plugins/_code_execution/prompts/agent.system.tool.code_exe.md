### code_execution_tool
run terminal, python, or nodejs commands
args:
- `runtime`: `terminal`, `python`, `nodejs`, or `output`
- `code`: command or script code
- `session`: terminal session id; default `0`
- `reset`: kill a session before running; `true` or `false`
rules:
- place the command or script in `code`
- use `runtime=output` to poll running work
- use `input` for interactive terminal prompts
- if a session is stuck, call again with the same `session` and `reset=true`
- check dependencies before running code
- replace placeholder or demo data with real values before execution
- use `print()` or `console.log()` when you need explicit output
- do not interleave other tools while waiting
- ignore framework `[SYSTEM: ...]` info in output
examples:
1 terminal command
~~~json
{
  "thoughts": ["I should run a terminal command in the default session."],
  "headline": "Running terminal command",
  "tool_name": "code_execution_tool",
  "tool_args": {
    "runtime": "terminal",
    "session": 0,
    "reset": false,
    "code": "pwd"
  }
}
~~~

2 python snippet
~~~json
{
  "thoughts": ["A short Python check is faster than using the shell."],
  "headline": "Running Python snippet",
  "tool_name": "code_execution_tool",
  "tool_args": {
    "runtime": "python",
    "session": 0,
    "reset": false,
    "code": "import os\nprint(os.getcwd())"
  }
}
~~~

3 wait for running output
~~~json
{
  "thoughts": ["The previous command is still running, so I should poll for output."],
  "headline": "Waiting for command output",
  "tool_name": "code_execution_tool",
  "tool_args": {
    "runtime": "output",
    "session": 0
  }
}
~~~
