from langchain_mcp_adapters.client import MultiServerMCPClient

async def load_mcp_tools():
    client = MultiServerMCPClient(
        {
            # "filesystem": {
            #     "command": "npx",
            #     "args": [
            #         "-y",
            #         "@modelcontextprotocol/server-filesystem",
            #         "./"
            #     ],
            #     "transport": "stdio",
            # },

            "playwright": {
            "command": "npx",
            "args": [
                "@playwright/mcp@latest"
            ]
            }
        }
    )

    tools = await client.get_tools()
    for tool in tools:
        print(tool.name)

    return tools