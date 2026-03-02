from datetime import datetime, timezone
from python.helpers.extension import Extension
from agent import LoopData
from python.helpers.localization import Localization
from python.helpers.errors import RepairableException
from python.helpers import errors
from python.helpers.print_style import PrintStyle

DATA_NAME_COUNTER = "_plugin.error_retry.critical_exception_counter"

class ResetCriticalExceptionCounter(Extension):
    async def execute(self, exception_data: dict = {}, **kwargs):
        if not self.agent:
            return
        
        self.agent.set_data(DATA_NAME_COUNTER, 0)

        