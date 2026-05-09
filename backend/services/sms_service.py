from dotenv import load_dotenv
from vonage import Auth, Vonage
from vonage_messages import Sms

from config import settings

load_dotenv()


class SMSClient:
    def __init__(self) -> None:
        self._client = Vonage(
            Auth(
                api_key=settings.vonage_api_key,
                api_secret=settings.vonage_api_secret,
            )
        )

    def send(self, phone_number: str, message: str) -> str:
        response = self._client.messages.send(
            Sms(
                to=phone_number,
                from_=settings.vonage_from_number,
                text=message,
            )
        )
        return str(response)


sms_client = SMSClient()


def text_phone_message(phone_number: str, message: str) -> str:
    print("CURRENT_PHONE_NUMER:", phone_number)
    print("CURRENT_MESSAGE:", message)
    if not settings.vonage_from_number:
        return "Missing VONAGE_FROM_NUMBER"
    return sms_client.send(phone_number=phone_number, message=message)
