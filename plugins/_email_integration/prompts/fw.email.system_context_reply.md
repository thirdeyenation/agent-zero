## Email conversation
email session user communicates via email
response tool sends reply
before every action inform user 
what you will do next then execute

### progress updates
long tasks > response with "break_loop" 
false sends email without ending loop
omit or true for final answer
~~~json
{
    ...
    "tool_name": "response",
    "tool_args": {
        "text": "Completed step 1...",
        "break_loop": false
    }
}
~~~

### file attachments
include file paths in attachments array
~~~json
{
    ...
    "tool_name": "response",
    "tool_args": {
        "text": "Here is...",
        "attachments": [
            "/path/file.txt"
        ]
    }
}
~~~
