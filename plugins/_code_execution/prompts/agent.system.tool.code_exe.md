### code_execution_tool
run terminal, python, or nodejs commands
args:
- `runtime`: `terminal`, `python`, `nodejs`, or `output`
- `code`: command or script code
- `session`: terminal session id; default `0`
- `reset`: kill a session before running; `true` or `false`
rules:
- use `runtime=output` to poll running work
- use `input` for interactive terminal prompts
- do not interleave other tools while waiting
- ignore framework `[SYSTEM: ...]` info in output
example:
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
