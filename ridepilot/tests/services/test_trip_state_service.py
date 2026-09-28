
from datetime import date, time

from app.schemas.trip_state import TripState, TripStatePatch
from app.services.trip_state_service import merge_trip_state


def test_followup_date_preserves_existing_trip_fields():
    current = TripState(
        pickup="Kalyan",
        destination="Airport",
        passengers=4,
        pickup_time=time(23, 30),
    )

    patch = TripStatePatch(
        pickup_date=date(2027, 4, 25)
    )

    updated = merge_trip_state(current, patch)

    assert updated.pickup == "Kalyan"
    assert updated.destination == "Airport"
    assert updated.passengers == 4
    assert updated.pickup_time == time(23, 30)
    assert updated.pickup_date == date(2027, 4, 25)


def test_patch_does_not_clear_existing_values():
    current = TripState(
        pickup="Kalyan",
        destination="Airport",
        passengers=4,
    )

    patch = TripStatePatch(
        pickup=None,
        passengers=2,
    )

    updated = merge_trip_state(current, patch)

    assert updated.pickup == "Kalyan"
    assert updated.destination == "Airport"
    assert updated.passengers == 2


def test_explicit_pickup_correction_replaces_old_value():
    current = TripState(pickup="Kalyan")

    patch = TripStatePatch(pickup="Thane")

    updated = merge_trip_state(current, patch)

    assert updated.pickup == "Thane"
