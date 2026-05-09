from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import JSONResponse

from services.inbound_sms_service import InboundSMSService


router = APIRouter()
inbound_service = InboundSMSService()


@router.api_route("/webhooks/inbound", methods=["POST"])
async def inbound_sms(background_task: BackgroundTasks, request: Request):
    payload = await inbound_service.parse_payload(request)
    result = await inbound_service.handle_inbound(payload, background_task)
    return JSONResponse(content=result)
