from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from pymongo.asynchronous.database import AsyncDatabase
from pathlib import Path

from app.db.client import get_db
from app.schemas.event import (
    GetAllPublicEventsResponse,
    GetEventRSVPsResponse,
    GetEventResponse,
    RSVPStatus,
    SendRSVPEmailRequest,
    SendRSVPEmailResponse,
    UpdateEventDetailsRequest,
    UpdateEventDetailsResponse,
)
from app.service.event import (
    get_all_public_events_service,
    get_event_rsvps_service,
    get_event_service,
    reply_rsvp_service,
    send_rsvp_email_service,
    update_event_details_service,
)

router = APIRouter()


@router.get("/public/all")
async def get_all_public_events(
    db: AsyncDatabase = Depends(get_db)
) -> GetAllPublicEventsResponse:
    return GetAllPublicEventsResponse(events=await get_all_public_events_service(db))


@router.get("/get-event/{event_id}")
async def get_event(
    event_id: str, db: AsyncDatabase = Depends(get_db)
) -> GetEventResponse:
    return GetEventResponse(event=await get_event_service(event_id, db))


@router.post("/send-rsvp-email/{event_id}")
async def send_rsvp_email(
    event_id: str,
    send_rsvp_email_request: SendRSVPEmailRequest,
    db: AsyncDatabase = Depends(get_db),
) -> SendRSVPEmailResponse:

    return SendRSVPEmailResponse(
        rsvp_id=await send_rsvp_email_service(
            event_id, send_rsvp_email_request.email, db
        )
    )


def get_rsvp_response_html():
    html_file = Path("app/templates/rsvp_response_page.html")
    return html_file.read_text(encoding="utf-8")


@router.get("/reply-rsvp/{rsvp_id}/{rsvp_status}")
async def reply_rsvp(
    rsvp_id: str,
    rsvp_status: RSVPStatus,
    db: AsyncDatabase = Depends(get_db),
) -> HTMLResponse:

    await reply_rsvp_service(rsvp_id, rsvp_status, db)

    return HTMLResponse(content=get_rsvp_response_html(), status_code=200)


@router.get("/get-event-rsvps/{event_id}")
async def get_event_rsvps(
    event_id: str, db: AsyncDatabase = Depends(get_db)
) -> GetEventRSVPsResponse:

    return GetEventRSVPsResponse(rsvps=await get_event_rsvps_service(event_id, db))


@router.post("/update-event-details/{event_id}")
async def update_event_details(
    event_id: str,
    update_event_details_request: UpdateEventDetailsRequest,
    db: AsyncDatabase = Depends(get_db),
):

    await update_event_details_service(event_id, update_event_details_request, db)

    return UpdateEventDetailsResponse()
