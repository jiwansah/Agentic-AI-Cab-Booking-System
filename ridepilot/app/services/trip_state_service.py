
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.orm_models import Conversation
from app.schemas.trip_state import TripState, TripStatePatch


def load_trip_state(conversation: Conversation) -> TripState:
    return TripState.model_validate(
        conversation.trip_state or {}
    )


def merge_trip_state(
    current: TripState,
    patch: TripStatePatch,
) -> TripState:
    updates = patch.model_dump(exclude_unset=True)

    # Do not overwrite an existing value with null.
    updates = {
        key: value
        for key, value in updates.items()
        if value is not None
    }

    return current.model_copy(update=updates)


def save_trip_state(
    db: Session,
    conversation: Conversation,
    state: TripState,
) -> None:
    # Convert date/time and other Pydantic values to
    # JSON-compatible values.
    conversation.trip_state = state.model_dump(mode="json")
    conversation.updated_at = datetime.now(timezone.utc)

    db.add(conversation)
