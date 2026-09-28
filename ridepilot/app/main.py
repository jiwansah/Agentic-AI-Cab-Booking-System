# app/main.py
from urllib.request import Request

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.agent.ride_agent import RideAgent
from app.models.ride import TripRequest
from app.models.booking import BookingRequest
from app.services.booking_service import booking_service
from app.services.geocoding_service import geocoding_service
from app.tools.ride_tools import search_cabs
import logging
from app.models.chat import ChatRequest, ChatHistoryResponse, ChatHistoryMessage
from sqlalchemy import text
from app.db.database import engine
from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.db.orm_models import AccountType, AuthSession
from app.services.auth_service import auth_service
from fastapi import Header
from app.models.auth import (
    GuestResumeRequest,
    GuestForgetRequest,
    RegisterRequest,
    LoginRequest,
)
from app.services.chat_history_service import chat_history_service
from app.services.trip_state_service import save_trip_state, load_trip_state
from app.services.quote_service import quote_service

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RidePilot",
    version="0.3.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.29.7:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = RideAgent()


class SearchRideRequest(TripRequest):
    pass


class SelectQuoteRequest(BaseModel):
    quote_id: str


class ConfirmBookingRequest(BookingRequest):
    pass


@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
    modified_details = []

    for error in exc.errors():
        # Copy the original error structure
        new_error = dict(error)

        # Check if the error is due to min_length (string_too_short)
        if error.get("type") == "string_too_short":
            # Extract the field name from the location tuple (e.g., 'phone' or 'password')
            field_name = error["loc"][-1] if error.get("loc") else "field"
            min_len = error.get("ctx", {}).get("min_length", 0)

            # Dynamically overwrite the generic message with your preferred text
            new_error["msg"] = f"{field_name} should have at least {min_len} characters"

        modified_details.append(new_error)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": modified_details},
    )


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "ridepilot",
    }


@app.get("/health/db")
def database_health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "database": "postgresql",
        }

    except Exception:
        logger.exception("Database health check failed")

        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        )



security = HTTPBearer(auto_error=False)


def get_current_session(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(security),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> AuthSession:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    auth_session = auth_service.authenticate(
        db,
        credentials.credentials,
    )

    if auth_session is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid, expired, or revoked session",
        )

    return auth_session



@app.post("/auth/guest", status_code=201)
def create_guest(
    db: Annotated[Session, Depends(get_db)],
):
    return auth_service.create_guest(db)


@app.post("/auth/guest/resume")
def resume_guest(
    request: GuestResumeRequest,
    db: Annotated[Session, Depends(get_db)],
):
    result = auth_service.resume_guest(
        db,
        request.credential,
    )

    if result is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid guest recovery credential",
        )

    return result


@app.post("/auth/guest/forget")
def forget_guest(
    request: GuestForgetRequest,
    auth_session: Annotated[
        AuthSession,
        Depends(get_current_session),
    ],
    db: Annotated[Session, Depends(get_db)],
):
    if not request.confirm:
        raise HTTPException(
            status_code=400,
            detail="Explicit confirmation is required",
        )

    if auth_session.user.account_type != AccountType.GUEST:
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only for guest accounts",
        )

    deleted = auth_service.forget_guest(
        db,
        auth_session.user_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Guest identity not found",
        )

    return {"status": "guest_identity_deleted"}


@app.post("/auth/register", status_code=201)
def register_user(
    request: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
):
    try:
        return auth_service.register(
            db=db,
            phone=request.phone,
            email=str(request.email) if request.email else None,
            password=request.password,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc


@app.post("/auth/login")
def login_user(
    request: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
):
    result = auth_service.login(
        db=db,
        identifier=request.identifier,
        password=request.password,
    )

    if result is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid identifier or password",
        )

    return result


@app.get("/auth/me")
def get_me(
    auth_session: Annotated[
        AuthSession,
        Depends(get_current_session),
    ],
    db: Annotated[Session, Depends(get_db)],
):
    user = auth_service.get_user_details( db=db, user_id=auth_session.user_id)
    return {
        "phone": user.phone_number,
        "email": user.email,
        "user_id": user.user_id,
        "account_type": user.account_type,
        "session_id": auth_session.session_id,
        "expires_at": auth_session.expires_at,
    }


@app.post("/auth/logout")
def logout(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(security),
    ],
    db: Annotated[Session, Depends(get_db)],
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    auth_service.logout(db, credentials.credentials)

    return {"status": "signed_out"}



@app.post("/rides/search")
def search_rides(
    request: SearchRideRequest,
    auth_session: Annotated[
        AuthSession,
        Depends(get_current_session),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):
    try:
        pickup_latitude, pickup_longitude = ( geocoding_service.geocode(request.pickup))
        destination_latitude, destination_longitude = (geocoding_service.geocode(request.destination))

        quotes = search_cabs(
            TripRequest(
                pickup=request.pickup,
                destination=request.destination,

                pickup_latitude=pickup_latitude,
                pickup_longitude=pickup_longitude,
                destination_latitude=destination_latitude,
                destination_longitude=destination_longitude,

                passengers=request.passengers,
                max_fare=request.max_fare,
                preferred_provider=(
                    request.preferred_provider
                ),
            ),
            user_id=auth_session.user_id,
            session_id=auth_session.session_id,
        )


        return {
            "pickup": request.pickup,
            "destination": request.destination,
            "quotes": quotes,
        }

    except Exception:
        db.rollback()
        logger.exception(
            "Failed to search and save cabs"
        )
        raise




@app.post("/cab_booking_chat")
def cab_booking_chat(
    request: ChatRequest,
    auth_session: AuthSession = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    user_id = auth_session.user_id

    try:
        conversation = chat_history_service.get_or_create_conversation(
            db=db,
            user_id=user_id,
            conversation_id=request.conversation_id,
        )
        current_state = load_trip_state(conversation)

        # Load persisted history from PostgreSQL
        history = chat_history_service.get_messages(
            db=db,
            conversation_id=conversation.conversation_id,
            user_id=user_id,
        )

        # Remember where this turn starts
        previous_count = len(history)

        # The agent mutates history with this turn's messages
        result = agent.chat(
            user_message=request.message,
            history=history,
            user_id=user_id,
            session_id=auth_session.session_id,
            current_state=current_state,
            db=db,
        )

        # Persist only newly appended messages
        new_messages = history[previous_count:]

        chat_history_service.save_messages(
            db=db,
            conversation=conversation,
            messages=new_messages,
        )

        save_trip_state(
            db=db,
            conversation=conversation,
            state=result.trip_state,
        )
        db.commit()

        return {
            "conversation_id": conversation.conversation_id,
            "reply": result.reply,
            "trip_state": result.trip_state.model_dump(mode="json"),
        }

    except PermissionError as exc:
        db.rollback()
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )
    except Exception:
        db.rollback()
        raise




@app.post("/bookings/preview")
def preview_booking(
    request: SelectQuoteRequest,
    auth_session: Annotated[
        AuthSession,
        Depends(get_current_session),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
):

    quote = quote_service.get_quote(
        db=db,
        quote_id=request.quote_id,
        user_id=auth_session.user_id,
        session_id=auth_session.session_id,
    )

    if quote is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Quote not found, expired, "
                "or no longer available"
            ),
        )

    if (
        quote.fare is None
        or not quote.pickup
        or not quote.destination
    ):
        raise HTTPException(
            status_code=422,
            detail="Quote is missing required booking information",
        )

    return {
        "quote_id": quote.quote_id,
        "provider": quote.provider,
        "vehicle_type": quote.vehicle_type,
        "fare": quote.fare,
        "currency": quote.currency,
        "pickup": quote.pickup,
        "destination": quote.destination,
        "estimated_arrival_minutes": (
            quote.estimated_arrival_minutes
        ),
        "requires_confirmation": True,
    }



@app.get("/conversations")
def get_chat_history(
    auth_session=Depends(get_current_session),
    db: Session = Depends(get_db),
):
    try:
        return chat_history_service.list_conversations(
            db=db,
            user_id=auth_session.user_id,
        )

    except PermissionError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


@app.get("/conversations/{conversation_id}/chatmessages")
def get_chat_messages(
    conversation_id: str,
    auth_session=Depends(get_current_session),
    db: Session = Depends(get_db),
):
    try:
        messages = chat_history_service.get_chat_messages(
            db=db,
            conversation_id=conversation_id,
            user_id=auth_session.user_id,
            roles=["user", "assistant"],
        )

        return {
            "conversation_id": conversation_id,
            "messages": messages,
        }

    except PermissionError as e:
        print(f"CRITICAL CHAT ERROR: {str(e)}")  # This prints to your backend terminal
        raise HTTPException(status_code=500, detail=f"Internal agent crash: {str(e)}")


@app.get("/conversations/{conversation_id}/messages")
def get_all_chat_messages(
    conversation_id: str,
    auth_session=Depends(get_current_session),
    db: Session = Depends(get_db),
):
    try:
        messages = chat_history_service.get_messages(
            db=db,
            conversation_id=conversation_id,
            user_id=auth_session.user_id,
        )

        return {
            "conversation_id": conversation_id,
            "messages": messages,
        }

    except PermissionError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )


@app.post("/bookings/confirm")
def confirm_booking(
    request: ConfirmBookingRequest,
    auth_session: Annotated[
        AuthSession,
        Depends(get_current_session),
    ],
    db: Annotated[
        Session,
        Depends(get_db),
    ],
    idempotency_key: str = Header(
        ...,
        alias="Idempotency-Key",
    ),
):

    if not request.confirmed:
        raise HTTPException(
            status_code=400,
            detail="Explicit confirmation is required",
        )

    idempotency_key = idempotency_key.strip()

    if not idempotency_key:
        raise HTTPException(
            status_code=400,
            detail="Idempotency-Key cannot be empty",
        )

    try:

        booking = booking_service.create_booking(
            db=db,
            quote_id=request.quote_id,
            user_id=auth_session.user_id,
            session_id=auth_session.session_id,
            idempotency_key=idempotency_key,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    return booking

