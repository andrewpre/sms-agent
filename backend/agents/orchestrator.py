from agents.sms_agent import run_sms_agent

def configured_agent_names() -> list[str]:
    # Keep historical names for startup prompt validation and backwards compatibility.
    return [
        "sms_agent",
        "reporter_agent",
        "proactive_agent",
        "extractor_agent",
        "router_agent",
    ]


async def run_orchestrator(phone_number: str, message: str, test: bool = False) -> None:
    """
    Here we will do all the processing before sending it to the sms_agent
    - Inserting into mongo
    - Extracting any important features and inserting that elsewhere
    Compatibility shim.
    The SMS agent is now always the primary controller.
    """
    await run_sms_agent(phone_number, message, test)
