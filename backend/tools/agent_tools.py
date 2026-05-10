from langchain_core.tools import StructuredTool
from lib import MongoLibrary
from tools.schemas import *
from tools.messaging import text

async def make_text_tool(phone_number: str, testing=False):
    # sent_this_invoke = False

    async def text_user(message: str):
        # nonlocal sent_this_invoke
        # if sent_this_invoke:
        #     return (
        #         "Already sent an SMS for this user message. Do not call text_user again. "
        #         "If you need to add something, put it in a normal assistant reply only (no tools)."
        #     )
        # sent_this_invoke = True
        if testing:
            print(f"===================== Texted: {message} to {phone_number} =====================================")
            return f"Texted: {message} to user!"
        mongo_db = MongoLibrary(phone_number)
        mongo_db.upload_message(message=message, role="system")
        await text(phone_number=phone_number, message=message)
        return f"Texted: {message} to user!"

    return StructuredTool.from_function(
        name="text_user",
        description=(
            "Send one SMS to the current user for this turn. Call at most once per user message; "
            "after success, answer with plain text only (no further tool calls)."
        ),
        args_schema=TextPhoneNumber,
        coroutine=text_user,
    )

async def fetch_conversations_from_database(phone_number: str):
    async def fetch_last_conversations(number_of_previous_conversations: int):
        mongo_db = MongoLibrary(phone_number=phone_number)
        return mongo_db.fetch_last_k(number_of_previous_conversations)

    return StructuredTool.from_function(
        name="fetch_conversations_from_database",
        description="Fetch user chats from the database",
        args_schema=GetUserInput,
        coroutine=fetch_last_conversations,
    )
