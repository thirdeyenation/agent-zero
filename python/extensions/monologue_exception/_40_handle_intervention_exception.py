from datetime import datetime, timezone
from python.helpers.extension import Extension
from agent import LoopData
from python.helpers.localization import Localization
from python.helpers.errors import InterventionException
from python.helpers import errors
from python.helpers.print_style import PrintStyle


class HandleInterventionException(Extension):
    async def execute(self, exception_data: dict = {}, **kwargs):
        if not self.agent:
            return

        if not exception_data.get("exception"):
            return

        if isinstance(exception_data["exception"], InterventionException):
            exception_data["exception"] = None # skip the exception and continue message loop

        
