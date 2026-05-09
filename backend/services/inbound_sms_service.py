from typing import Any

from fastapi import BackgroundTasks, Request

from services.message_buffer import MultipartMessageBuffer
from agents.orchestrator import run_orchestrator


class InboundSMSService:
    def __init__(self) -> None:
        self._buffer = MultipartMessageBuffer()

    async def parse_payload(self, request: Request) -> dict[str, Any]:
        content_type = request.headers.get("content-type", "")
        if "application/x-www-form-urlencoded" in content_type:
            form = await request.form()
            return dict(form)
        return {}

    async def handle_inbound(
        self, payload: dict[str, Any], background_task: BackgroundTasks
    ) -> dict[str, str]:
        phone_number = payload.get("msisdn")
        message = payload["text"] if isinstance(payload.get("text"), str) else ""
        if not isinstance(phone_number, str):
            return {"status": "ok"}

        concat_part = (
            payload["concat-part"] if isinstance(payload.get("concat-part"), str) else "1"
        )
        concat_total = (
            payload["concat-total"] if isinstance(payload.get("concat-total"), str) else "1"
        )
        concat_ref = (
            payload["concat-ref"] if isinstance(payload.get("concat-ref"), str) else "1"
        )

        self._buffer.add_part(phone_number, concat_ref, concat_part, message)
        if self._buffer.is_complete(phone_number, concat_ref, int(concat_total)):
            combined_message = self._buffer.consume(phone_number, concat_ref, int(concat_total))
            background_task.add_task(run_orchestrator, phone_number, combined_message)

        return {"status": "ok"}
