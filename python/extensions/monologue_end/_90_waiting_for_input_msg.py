from python.helpers.extension import Extension
from agent import LoopData

class WaitingForInputMsg(Extension):

    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        # show temp info message
        if self.agent.number == 0:
            self.agent.context.log.set_initial_progress()

        self.agent.context.log.log(
            type="hint", heading="Waiting for input...", content="test content", dumy_kvp1=3, dumy_kvp2="test test"
        )
