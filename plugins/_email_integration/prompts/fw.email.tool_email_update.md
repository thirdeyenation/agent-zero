### email_update
send progress or status email to user without ending your task
use when working on long tasks keep user informed while continuing work
does NOT end your agentic loop use "response" tool for final answer
usage:
~~~json
{
    ...
    "tool_name": "email_update",
    "tool_args": {
        "text": "... Completed step 1 of 3..."
    }
}
~~~

optional attach files with attachments
~~~json
{
    ...
    "tool_name": "email_update",
    "tool_args": {
        "text": "... preliminary results ...",
        "attachments": [
            "/path/report.csv"
        ]
    }
}
~~~
