# Quick Start
This guide provides a quick introduction to using Agent Zero. We'll cover launching the Web UI, starting a new chat, and running a simple task.

## Launching the Web UI (Docker)
1. Pull the latest image:

```bash
docker pull agent0ai/agent-zero:latest
```

Notes:
- HTTP binds to `--host/--port` (or `WEB_UI_HOST`/`WEB_UI_PORT`, default port 5000).

4. A message similar to this will appear in your terminal, indicating the Web UI is running:

```bash
docker run -p 0:80 agent0ai/agent-zero:latest
```

5. Open your web browser and navigate to the URL shown in the terminal (usually `http://127.0.0.1:5000`). You should see the Agent Zero Web UI.

![New Chat](res/ui_newchat1.png)

> [!TIP]
> As you can see, the Web UI has four distinct buttons for easy chat management:
> `New Chat`, `Reset Chat`, `Save Chat`, and `Load Chat`.
> Chats can be saved and loaded individually in `json` format and are stored in the
> `/tmp/chats` directory.

    ![Chat Management](res/ui_chat_management.png)

## Running a Simple Task
Let's ask Agent Zero to download a YouTube video. Here's how:

1. Type "Download a YouTube video for me" in the chat input field and press Enter or click the send button.
2. Agent Zero will process your request. You'll see its thoughts and tool calls in the UI.
3. The agent will ask you for the URL of the YouTube video you want to download.

## Example Interaction
Here's an example of what you might see in the Web UI at step 3:

![1](res/image-24.png)

## Next Steps
Now that you've run a simple task, you can experiment with more complex requests. Try asking Agent Zero to:

* Perform calculations
* Search the web for information
* Execute shell commands
* Explore web development tasks
* Create or modify files

> [!TIP]
> The [Usage Guide](usage.md) provides more in-depth information on tools, projects, tasks, and backup/restore.
