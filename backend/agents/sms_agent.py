import logging
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain.agents import create_agent

from agents.skills_loader import load_skill_prompt_safe
from config import settings
from tools.registry import AgentToolset, build_toolset

load_dotenv()
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SmsDecision:
    decision_type: str
    delegated_to: str | None = None


def classify_sms_decision(message: str) -> SmsDecision:
    normalized = message.strip().lower()
    if not normalized:
        return SmsDecision(decision_type="no_response")

    if "no need to reply" in normalized or "don't reply" in normalized:
        return SmsDecision(decision_type="defer_internal", delegated_to="extractor_agent")

    if any(term in normalized for term in ("summary", "weekly report", "recap")):
        return SmsDecision(decision_type="respond_now", delegated_to="reporter_agent")

    if any(term in normalized for term in ("remind me", "nudge me", "check in")):
        return SmsDecision(decision_type="respond_now", delegated_to="proactive_agent")

    return SmsDecision(decision_type="respond_now")


def should_send_sms(decision: SmsDecision, user_message: str) -> bool:
    normalized = user_message.strip().lower()
    if decision.decision_type == "no_response":
        return False
    if "silent:" in normalized:
        return False
    if decision.decision_type == "defer_internal":
        return False
    return True


async def run_sms_agent(phone_id: str, message: str, test: bool) -> None:
    decision = classify_sms_decision(message)
    send_sms = should_send_sms(decision, message)
    tools = await build_toolset(AgentToolset.SMS, phone_id, allow_texting=send_sms, testing=test)

    agent = create_agent(
        model=settings.model_name,
        tools=tools,
        # debug=True,
    )
    system_prompt = load_skill_prompt_safe(phone_number=phone_id, agent_name="sms_agent")
    policy_prompt = (
        "Communication policy:\n"
        "- SMS is the only external channel.\n"
        "- Only this sms_agent can send SMS.\n"
        "- Choose exactly one decision before action: respond_now, defer_internal, no_response.\n"
        "- For each inbound user message, call text_user at most once, unless allowed to do so by the user in the initial message; after it succeeds, respond with "
        "a short final message only (no more tools).\n"
        "- Use subagent delegation tools for internal help.\n"
        "- If texting tools are unavailable, do not attempt user messaging.\n"
        # f"- Active runtime decision: {decision.decision_type}.\n"
        # f"- Delegated target (if any): {decision.delegated_to or 'none'}."
    )
    response = await agent.ainvoke(
        {
            "messages": [
                {"role": "system", "content": f"{system_prompt}\n\n{policy_prompt}"},
                {"role": "user", "content": message},
            ]
        }
    )
    # logger.info(
    #     "sms_agent_decision decision_type=%s delegated_to=%s sms_sent=%s",
    #     decision.decision_type,
    #     decision.delegated_to,
    #     send_sms,
    # )
    print("================================== DONE ======================================")