import sys
import helpers.guids as guids
print("Guids generate_id:", guids.generate_id(8))

import agent
print("Agent short id:", agent.AgentContext.generate_id())
