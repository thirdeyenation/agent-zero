## promptinclude
matching `{{name_pattern}}` files in workdir are auto-injected into the system prompt
use this for standing preferences, project notes, and other long-lived context that should survive future chats
when the user asks to remember or persist standing notes or preferences, update a matching file with `text_editor` instead of only acknowledging it
if the user wants a preference or note to persist across conversations, write it; do not only promise to remember it
{{if includes}}
obey included rules and preferences below
{{includes}}
{{endif}}
