from enum import Enum
from typing import List
from pydantic import BaseModel, EmailStr


class RSVPStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class RSVP(BaseModel):
    id: str
    email: EmailStr
    rsvp_status: RSVPStatus


class Event(BaseModel):
    id: str
    name: str
    description: str
    start: str
    end: str
    colour: str
    location: str
    rsvp_ids: List[str]
    public: bool = False


# Pass event_id through path
class GetEventRequest(BaseModel):
    pass


class GetEventResponse(BaseModel):
    event: Event


# For clubs to send email to event attendees
# Pass event_id through path
class SendRSVPEmailRequest(BaseModel):
    email: EmailStr


class SendRSVPEmailResponse(BaseModel):
    rsvp_id: str


# For event attendees to confirm or deny event attendance
# Pass rsvp_id through path
class ReplyRSVPRequest(BaseModel):
    rsvp_status: RSVPStatus


class ReplyRSVPResponse(BaseModel):
    pass


# Pass event_id through path
class GetEventRSVPsRequest(BaseModel):
    pass


class GetEventRSVPsResponse(BaseModel):
    rsvps: List[RSVP]


class UpdateEventDetailsRequest(BaseModel):
    name: str
    description: str
    start: str
    end: str
    colour: str
    location: str
    public: bool


class UpdateEventDetailsResponse(BaseModel):
    pass


class GetAllPublicEventsResponse(BaseModel):
    events: List[Event]
