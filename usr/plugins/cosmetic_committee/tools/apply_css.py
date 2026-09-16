import json
from pathlib import Path
from helpers.tool import Tool, Response
from helpers.notification import AgentNotification
from helpers.messages import mq
from helpers import runtime

CSS_STORE_PATH = Path("usr/plugins/cosmetic_committee/current_theme.css")

class ApplyCssTool(Tool):
    async def execute(self, css="", **kwargs):
        # Save the CSS to file
        CSS_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CSS_STORE_PATH, "w") as f:
            f.write(css)

        # Notify user via toast Notification
        AgentNotification.success(
            self.agent.context.id,
            "Cosmetic CSS generated, reviewed, and applied successfully! Refreshing..."
        )

        # Broadcast the new CSS using mq.broadcast so the frontend JS store can catch it.
        # This allows the frontend to apply the changes without needing a full refresh.
        mq.broadcast("cosmetic_css_update", {"css": css})

        return Response(message="CSS applied successfully and broadcasted to clients.", break_loop=False)

    def get_log_object(self):
        return self.agent.context.log.log(
            type="tool",
            heading=f"icon://palette {self.agent.agent_name}: Applying Custom CSS",
            content=self.args.get("css", "No CSS provided"),
            kvps=self.args,
        )
