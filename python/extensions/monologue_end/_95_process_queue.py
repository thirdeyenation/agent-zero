import asyncio
from python.helpers.extension import Extension
from python.helpers import message_queue as mq
from agent import LoopData


class ProcessQueue(Extension):
    """Process queued messages after monologue ends."""

    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        # Only process for agent0 (main agent)
        if self.agent.number != 0:
            return

        context = self.agent.context

        # Check if there are queued messages
        if mq.has_queue(context):
            # Schedule delayed task to send next queued message
            # This allows current monologue to fully complete first
            asyncio.create_task(self._delayed_send(context))

    async def _delayed_send(self, context):
        """Wait for task to complete, then send next queued message."""
        # Small delay to ensure monologue fully completes
        await asyncio.sleep(0.1)
        
        # Wait for current task to finish
        while context.task and context.task.is_alive():
            await asyncio.sleep(0.1)
        
        # Send next queued message
        mq.send_next(context)
