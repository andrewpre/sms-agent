from enum import Enum
from tools.agent_tools import *
from tools.mcp_tools import load_mcp_tools

class AgentToolset(str, Enum):
    SMS = "sms"
    REPORTER = "reporter"
    PROACTIVE = "proactive"
    EXTRACTOR = "extractor"


async def build_toolset(
    agent_toolset: AgentToolset, phone_number: str, allow_texting: bool = True, testing: bool = False
):
    tools = [
        await make_text_tool(phone_number, testing),
        await fetch_conversations_from_database(phone_number),
        await load_mcp_tools()
    ]
    return tools
