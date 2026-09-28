
import json

from sqlalchemy.orm import Session

from app.llm.factory import create_llm
from app.models.ride import TripRequest
from app.services.booking_service import booking_service
from app.services.geocoding_service import geocoding_service
from app.tools.ride_tools import search_cabs
from app.schemas.trip_state import (
    TripState,
    TripStatePatch,
)
from app.services.trip_state_service import merge_trip_state
from pydantic import ValidationError
from pydantic import BaseModel


class RideAgentResult(BaseModel):
    reply: str
    trip_state: TripState


SYSTEM_PROMPT = """
You are RidePilot, an AI cab search assistant.

Your responsibilities:
- Understand the user's pickup location, destination, passengers,
  budget, date and time.
- Ask for missing information when required.
- Call search_cabs when sufficient information is available.
- Never claim that a ride is booked unless booking has actually been confirmed.
- Never invent fares, providers or availability.
- Dont take broad location like Mumbai, Pune Delhi
- Always try to take exact location source and destination locations.

Before calling search_cabs:

- pickup must be a specific point, not merely a city/locality/area.
- destination must be a specific point, not merely a city/locality/area.
- If either is too broad, do not call the tool.
- Ask the user to provide the missing specific location.


Response style:
- Keep responses concise.
- Do NOT use Markdown tables.
- Do NOT use unnecessary bold or italic formatting.
- Do NOT repeat information unnecessarily.
- When presenting ride search results, show each option on one line.
- Mention the route and date/time only once.
- Avoid generic closing statements.

Example ride result format:

Ride options for 4 passengers:
Lakeshore Green Dombivali → Mumbai Airport T2
25 Sep 2026, 10:30 PM

1. ProviderA — ₹720 — 48 min
2. ProviderB — ₹650 — 52 min
3. ProviderC — ₹590 — 55 min

Then ask the user what they want to do next.
"""


TRIP_STATE_EXTRACTION_PROMPT = """
You extract updates to a cab trip.

You receive:
- The current structured trip state
- The latest user message
- Relevant conversation context

Return ONLY a JSON object containing fields
explicitly provided or corrected by the latest message.

Rules:
- Do not repeat unchanged fields.
- Do not set missing fields to null.
- Do not invent pickup, destination, date, time, passenger count, or fare.
- Interpret follow-up messages using the current state.
- If a date lacks a year and cannot be resolved safely,
  do not invent a year.
- Treat ambiguous locations as unresolved.
- Do not claim a cab is booked.
- Dont take broad location like Mumbai, Pune Delhi
- Take exact location for the source and destination

Allowed fields:
pickup, destination, passengers, pickup_date,
pickup_time, preferred_provider, max_fare.


Before calling search_cabs:
- pickup must be a specific point, not merely a city/locality/area.
- destination must be a specific point, not merely a city/locality/area.
- If either is too broad, do not call the tool.
- Ask the user to provide the missing specific location.


Date rules:
- pickup_date must be YYYY-MM-DD.
- Never return partial dates such as "25 Sep".
- Never invent a year.
- If the year is missing and cannot be resolved
  safely from the current date and context,
  take today date pickup_date.
- Do not set fields to null unless the user
  explicitly clears them.

Only return fields explicitly supplied or
corrected by the latest user message.
Do not repeat unchanged fields.
Do not invent trip details.
"""


SEARCH_CABS_TOOL = {
    "type": "function",
    "function": {
        "name": "search_cabs",
        "description": (
            "Search simulated cab providers for "
            "a pickup and destination."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "pickup": {
                    "type": "string",
                    "description": "Pickup location",
                },
                "destination": {
                    "type": "string",
                    "description": "Destination",
                },
                "max_fare": {
                    "type": ["number", "null"],
                    "description": (
                        "Maximum fare in INR, "
                        "or null if unspecified."
                    ),
                },
                "passengers": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 1,
                },
            },
            "required": [
                "pickup",
                "destination",
                "max_fare",
                "pickup_time",
                "passengers",
            ],
            "additionalProperties": False,
        },
    },
}


BOOK_CAB_TOOL = {
    "type": "function",
    "function": {
        "name": "book_cab",
        "description": "Book a specific cab provider from the search results.",
        "parameters": {
            "type": "object",
            "properties": {
                "provider_name": {
                    "type": "string",
                    "description": "The name of the provider chosen by the user (e.g., ProviderA)",
                },
                "quote_id": {
                    "type": "string",
                    "description": "The quote_id of the booking chosen by the user",
                },
                "fare": {
                    "type": "number",
                    "description": "The exact fare agreed upon for the booking",
                }
            },
            "required": ["provider_name", "quote_id", "fare"],
            "additionalProperties": False,
        },
    },
}


class RideAgent:
    def __init__(self):
        self.llm = create_llm()

    def chat(
            self,
            user_message: str,
            db: Session,
            history: list[dict] | None = None,
            user_id: str = "",
            session_id: str = "",
            current_state: TripState | None = None,
    ) -> RideAgentResult:
        if history is None:
            history = []

        history.append({
            "role": "user",
            "content": user_message,
        })

        if current_state is None:
            current_state = TripState()

        patch = self.extract_trip_state(
            user_message=user_message,
            current_state=current_state,
        )

        updated_state = merge_trip_state(
            current=current_state,
            patch=patch,
        )

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "system",
                "content": (
                        "Current structured trip state:\n"
                        + json.dumps( updated_state.model_dump(mode="json"))
                        + "\nUse this state when interpreting "
                          "follow-up messages. Do not ask again "
                          "for fields already known unless they "
                          "need clarification."
                ),
            },
            *history,
        ]

        max_iterations = 5

        for _ in range(max_iterations):
            response = self.llm.chat(
                messages=messages,
                tools=[SEARCH_CABS_TOOL, BOOK_CAB_TOOL],
            )

            assistant_message = response.choices[0].message

            if not assistant_message.tool_calls:
                answer = assistant_message.content or ""

                history.append({
                    "role": "assistant",
                    "content": answer,
                })

                return RideAgentResult(
                    reply=answer,
                    trip_state=updated_state,
                )

            assistant_dict = assistant_message.model_dump(
                exclude_none=True
            )

            messages.append(assistant_dict)
            history.append(assistant_dict)

            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name

                if tool_name == "search_cabs":
                    try:
                        arguments = json.loads(
                            tool_call.function.arguments
                        )

                        tool_patch = TripStatePatch.model_validate(arguments)
                        search_state = merge_trip_state(
                            current=updated_state,
                            patch=tool_patch,
                        )
                        pickup_latitude, pickup_longitude = (geocoding_service.geocode(search_state.pickup))
                        destination_latitude, destination_longitude = (geocoding_service.geocode(search_state.destination))

                        print(pickup_latitude, pickup_longitude )
                        print(destination_latitude, destination_longitude)

                        trip = TripRequest(
                            pickup=search_state.pickup,
                            destination=search_state.destination,
                            pickup_latitude=pickup_latitude,
                            pickup_longitude=pickup_longitude,
                            destination_latitude=destination_latitude,
                            destination_longitude=destination_longitude,
                            passengers=search_state.passengers or 1,
                            max_fare=search_state.max_fare,
                            preferred_provider=search_state.preferred_provider,
                        )
                        quotes = search_cabs(
                            trip,
                            user_id=user_id,
                            session_id=session_id,
                            db=db,
                        )

                        tool_result = json.dumps([quote.model_dump(mode="json") for quote in quotes])

                    except Exception as e:
                        # Capture the error instead of throwing an ASGI crash
                        print(f"Booking Service Exception: {str(e)}")  # Visible in terminal
                        tool_result = json.dumps({
                            "status": "failed",
                            "error": str(e)
                        })
                    tool_message = {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result,
                    }
                    messages.append(tool_message)
                    history.append(tool_message)

                elif tool_name == "book_cab":  #  ADD THIS NEW BLOCK
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                        provider = arguments.get("provider_name")
                        fare = arguments.get("fare")
                        quote_id = arguments.get("quote_id")

                        #  CALL YOUR ACTUAL BOOKING CODE HERE
                        # Example database/service execution:
                        # booking = booking_service.create_booking(db, user_id=user_id, provider=provider, fare=fare)
                        booking = booking_service.create_booking(
                            db=db,
                            quote_id=quote_id,
                            user_id=user_id,
                            session_id=session_id,
                            idempotency_key=quote_id,
                        )

                        tool_result = booking.model_dump_json()

                    except Exception as e:
                        # Capture the error instead of throwing an ASGI crash
                        print(f"Booking Service Exception: {str(e)}")  # Visible in terminal
                        tool_result = json.dumps({
                            "status": "failed",
                            "error": str(e)
                        })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": tool_result,
                    })

                else:
                    raise ValueError(f"Unknown tool: {tool_name}")

        return RideAgentResult(
            reply="I couldn't complete the search within the allowed number of steps. Please try again.",
            trip_state=updated_state,
        )




    def extract_trip_state(
            self,
            user_message: str,
            current_state: TripState,
    ) -> TripStatePatch:

        base_payload = {
            "current_trip_state": (
                current_state.model_dump(mode="json")
            ),
            "latest_user_message": user_message,
        }

        messages = [
            {
                "role": "system",
                "content": TRIP_STATE_EXTRACTION_PROMPT,
            },
            {
                "role": "user",
                "content": json.dumps(base_payload),
            },
        ]

        for attempt in range(2):
            response = self.llm.chat(messages=messages)

            content = (
                    response.choices[0].message.content or "{}"
            )

            try:
                extracted = json.loads(content)
                return TripStatePatch.model_validate(extracted)

            except (json.JSONDecodeError, ValidationError) as exc:
                if attempt == 1:
                    # Do not apply unvalidated data.
                    # Log this failure in your application.
                    return TripStatePatch()

                messages.append({
                    "role": "assistant",
                    "content": content,
                })

                messages.append({
                    "role": "user",
                    "content": (
                        "Your previous output was invalid. "
                        "Return only corrected JSON. "
                        "pickup_date must be YYYY-MM-DD. "
                        "Do not guess a missing year. "
                        f"Validation error: {str(exc)}"
                    ),
                })

        return TripStatePatch()
