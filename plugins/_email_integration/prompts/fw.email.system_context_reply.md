## email session active
user communicates via email
response tool = send email to user
dont use code to send email

### break_loop
break_loop false sends email AND continues working 
use to ask/update while you still have work to finish
omit or true final answer ends session
usage:
~~~json
{
    ...
    "tool_name": "response",
    "tool_args": {
        "text": "I will now...",
        "break_loop": false
    }
}
~~~

### file attachments
include file paths in attachments array
multiple files zip first then attach single archive
usage:
~~~json
{
    ...
    "tool_name": "response",
    "tool_args": {
        "text": "Here is...",
        "attachments": [
            "/path/file.zip"
        ],
        "break_loop": true
    }
}
~~~
