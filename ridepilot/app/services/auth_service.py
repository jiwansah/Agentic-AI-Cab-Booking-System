
# app/services/auth_service.py

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from pwdlib import PasswordHash
from sqlalchemy.exc import IntegrityError
from app.db.orm_models import (
    AccountType,
    AuthSession,
    GuestRecoveryCredential,
    User,
)


GUEST_SESSION_HOURS = 24
password_hasher = PasswordHash.recommended()

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def hash_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def new_secret() -> str:
    return secrets.token_urlsafe(32)



def generate_recovery_code() -> str:
    """Generate a 96-bit guest recovery code."""
    raw = secrets.token_hex(12)  # 24 hex characters

    return "-".join([
        raw[0:8],
        raw[8:16],
        raw[16:24],
    ])



class AuthService:

    def _create_access_session(
        self,
        db: Session,
        user: User,
    ) -> tuple[AuthSession, str]:
        raw_token = new_secret()

        auth_session = AuthSession(
            session_id=str(uuid4()),
            user_id=user.user_id,
            token_hash=hash_secret(raw_token),
            expires_at=utc_now()
            + timedelta(hours=GUEST_SESSION_HOURS),
        )

        db.add(auth_session)
        return auth_session, raw_token



    def create_guest(self, db: Session):
        try:
            # 1. Create the guest user
            user = User(
                user_id=str(uuid4()),
                account_type=AccountType.GUEST,
                is_active=True,
            )
            db.add(user)

            # 2. Flush parent row first (without committing)
            db.flush()

            # 3. Generate guest credentials
            device_credential = new_secret()
            recovery_code = generate_recovery_code()
            # Human-readable, saveable recovery code.
            '''recovery_code = (
                    secrets.token_hex(4).upper()
                    + "-"
                    + secrets.token_hex(4).upper()
                    + "-"
                    + secrets.token_hex(4).upper()
            )'''

            # 4. Add recovery credentials linked to this user
            device_record = GuestRecoveryCredential(
                credential_id=str(uuid4()),
                user_id=user.user_id,
                credential_type="device",
                secret_hash=hash_secret(device_credential),
            )

            recovery_record = GuestRecoveryCredential(
                credential_id=str(uuid4()),
                user_id=user.user_id,
                credential_type="recovery",
                secret_hash=hash_secret(recovery_code),
            )

            # 5. Create the access session
            access_token = new_secret()

            auth_session = AuthSession(
                session_id=str(uuid4()),
                user_id=user.user_id,
                token_hash=hash_secret(access_token),
                expires_at=datetime.now(timezone.utc)
                           + timedelta(hours=24),
            )

            db.add_all([
                device_record,
                recovery_record,
                auth_session,
            ])

            # 6. Commit everything together
            db.commit()

            return {
                "user_id": user.user_id,
                "session_id": auth_session.session_id,
                "access_token": access_token,
                "device_credential": device_credential,
                "recovery_code": recovery_code,
            }

        except Exception:
            db.rollback()
            raise



    def resume_guest(
        self,
        db: Session,
        credential: str,
    ) -> dict | None:
        credential_hash = hash_secret(credential.strip())

        saved_credential = db.scalar(
            select(GuestRecoveryCredential).where(
                GuestRecoveryCredential.secret_hash
                == credential_hash,
                GuestRecoveryCredential.revoked_at.is_(None),
            )
        )

        if saved_credential is None:
            return None

        user = db.get(User, saved_credential.user_id)

        if (
            user is None
            or not user.is_active
            or user.account_type != AccountType.GUEST
        ):
            return None

        auth_session, access_token = self._create_access_session(
            db,
            user,
        )

        db.commit()
        db.refresh(auth_session)

        return {
            "user_id": user.user_id,
            "session_id": auth_session.session_id,
            "access_token": access_token,
            "token_type": "bearer",
            "expires_at": auth_session.expires_at,
            "account_type": "guest",
        }

    def authenticate(
        self,
        db: Session,
        token: str,
    ) -> AuthSession | None:
        auth_session = db.scalar(
            select(AuthSession).where(
                AuthSession.token_hash == hash_secret(token),
                AuthSession.revoked_at.is_(None),
                AuthSession.expires_at > utc_now(),
            )
        )

        if auth_session is None:
            return None

        if not auth_session.user.is_active:
            return None

        return auth_session

    def logout(self, db: Session, token: str) -> bool:
        auth_session = db.scalar(
            select(AuthSession).where(
                AuthSession.token_hash == hash_secret(token),
                AuthSession.revoked_at.is_(None),
            )
        )

        if auth_session is None:
            return False

        auth_session.revoked_at = utc_now()
        db.commit()
        return True

    def forget_guest(
        self,
        db: Session,
        user_id: str,
    ) -> bool:
        user = db.get(User, user_id)

        if (
            user is None
            or user.account_type != AccountType.GUEST
        ):
            return False

        # Deleting the user cascades to auth sessions and
        # guest recovery credentials through their FKs.
        db.delete(user)
        db.commit()
        return True



    def get_user_details(
        self,
        db: Session,
        user_id: str,
    ) -> User:
        user = db.get(User, user_id)

        if (
            user is None
        ):
            return User()

        return user


    def register(
        self,
        db: Session,
        phone: str | None,
        email: str | None,
        password: str,
    ) -> dict:
        phone = phone.strip() if phone else None
        email = email.strip().lower() if email else None

        if not phone and not email:
            raise ValueError("Phone or email is required")

        try:
            user = User(
                user_id=str(uuid4()),
                account_type=AccountType.REGISTERED,
                phone_number=phone,
                email=email,
                password_hash=password_hasher.hash(password),
                is_active=True,
            )

            db.add(user)
            db.flush()

            auth_session, access_token = (
                self._create_access_session(db, user)
            )

            db.commit()
            db.refresh(auth_session)

            return {
                "user_id": user.user_id,
                "session_id": auth_session.session_id,
                "access_token": access_token,
                "token_type": "bearer",
                "expires_at": auth_session.expires_at,
                "account_type": "registered",
            }

        except IntegrityError as exc:
            db.rollback()
            raise ValueError(
                "Phone number or email is already registered"
            ) from exc

        except Exception:
            db.rollback()
            raise

    def login(
        self,
        db: Session,
        identifier: str,
        password: str,
    ) -> dict | None:
        identifier = identifier.strip()

        # Match by email (case-insensitive) or phone.
        user = db.scalar(
            select(User).where(
                User.account_type == AccountType.REGISTERED,
                or_(
                    User.email == identifier.lower(),
                    User.phone_number == identifier,
                ),
            )
        )

        if (
            user is None
            or not user.is_active
            or not user.password_hash
        ):
            return None

        if not password_hasher.verify(
            password,
            user.password_hash,
        ):
            return None

        try:
            auth_session, access_token = (
                self._create_access_session(db, user)
            )

            db.commit()
            db.refresh(auth_session)

            return {
                "user_id": user.user_id,
                "session_id": auth_session.session_id,
                "access_token": access_token,
                "token_type": "bearer",
                "expires_at": auth_session.expires_at,
                "account_type": "registered",
            }

        except Exception:
            db.rollback()
            raise






auth_service = AuthService()