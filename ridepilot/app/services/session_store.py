from dataclasses import dataclass, field
from typing import Any


@dataclass
class ChatSession:
    session_id: str
    user_id: str
    messages: list[dict[str, Any]] = field(default_factory=list)


class SessionStore:
    def __init__(self):
        self.sessions: dict[str, ChatSession] = {}

    def get_or_create(
        self,
        user_id: str,
        session_id: str,
    ) -> ChatSession:
        session = self.sessions.get(session_id)

        if session is None:
            session = ChatSession(
                session_id=session_id,
                user_id=user_id,
            )
            self.sessions[session_id] = session

        elif session.user_id != user_id:
            raise PermissionError(
                "Session belongs to another user"
            )

        return session


session_store = SessionStore()