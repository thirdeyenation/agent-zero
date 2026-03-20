# Telegram session behavior
user communicates via Telegram messenger
response tool = send message to user on Telegram
dont use code to send messages
break_loop true > stop working and wait for user reply
break_loop false > only for mid-task progress updates then keep working
include file paths in attachments array to send files/images
for multiple files zip first then attach single archive
optionally set keyboard array for inline buttons

usage:

~~~json
{
    ...
    "tool_name": "response",
    "tool_args": {
        "text": "working on it...",
        "break_loop": false
    }
}
~~~

~~~json
{
    ...
    "tool_name": "response",
    "tool_args": {
        "text": "Here is the result",
        "attachments": ["/path/to/file.zip"],
        "break_loop": true
    }
}
~~~

~~~json
{
    ...
    "tool_name": "response",
    "tool_args": {
        "text": "Choose an option:",
        "keyboard": [[{"text": "Option A", "callback_data": "a"}, {"text": "Option B", "callback_data": "b"}]],
        "break_loop": true
    }
}
~~~