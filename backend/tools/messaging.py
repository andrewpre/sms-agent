from services.sms_service import text_phone_message


async def text_user_cut(phone_number: str, message: str):
    # Message cannot exceed 150 characters per SMS part.
    for i in range(0, len(message), 150):
        await text(phone_number, message[i : i + 150])


async def text(phone_number: str, message: str):
    print(f"Texted '{message}' to {phone_number}")
    text_phone_message(phone_number=phone_number, message=message)

def text_weekly_summary(phone_number: str, message: str):
    _ = (phone_number, message)
    return
