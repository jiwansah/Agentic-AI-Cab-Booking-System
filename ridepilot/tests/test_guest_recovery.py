
from app.services.auth_service import auth_service


def test_guest_can_resume_with_device_credential(db):
    created = auth_service.create_guest(db)

    resumed = auth_service.resume_guest(
        db,
        created["device_credential"],
    )

    assert resumed is not None
    assert resumed["user_id"] == created["user_id"]
    assert resumed["access_token"] != created["access_token"]


def test_guest_can_resume_with_recovery_code(db):
    created = auth_service.create_guest(db)

    resumed = auth_service.resume_guest(
        db,
        created["recovery_code"],
    )

    assert resumed is not None
    assert resumed["user_id"] == created["user_id"]


def test_invalid_credential_is_rejected(db):
    result = auth_service.resume_guest(
        db,
        "this-is-not-a-valid-guest-credential",
    )

    assert result is None


def test_logout_does_not_destroy_guest_recovery(db):
    created = auth_service.create_guest(db)

    auth_service.logout(
        db,
        created["access_token"],
    )

    resumed = auth_service.resume_guest(
        db,
        created["device_credential"],
    )

    assert resumed is not None
    assert resumed["user_id"] == created["user_id"]
