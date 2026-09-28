#import datetime
from typing import Sequence
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.orm_models import Conversation, ChatMessage


class ChatHistoryService:

    def get_or_create_conversation(
        self,
        db: Session,
        user_id: str,
        conversation_id: str | None = None,
    ) -> Conversation:
        """
        Return an existing conversation owned by this user,
        or create a new one.
        """

        if conversation_id:
            conversation = db.scalar(
                select(Conversation).where(
                    Conversation.conversation_id == conversation_id,
                    Conversation.user_id == user_id,
                )
            )

            if conversation is None:
                raise PermissionError(
                    "Conversation not found for this user"
                )

            return conversation

        conversation = Conversation(
            user_id=user_id,
        )

        db.add(conversation)
        db.flush()

        return conversation

    def get_messages(
        self,
        db: Session,
        conversation_id: str,
        user_id: str,
    ) -> list[dict]:
        """
        Retrieve the conversation's complete agent history.
        """

        conversation = db.scalar(
            select(Conversation).where(
                Conversation.conversation_id == conversation_id,
                Conversation.user_id == user_id,
            )
        )

        if conversation is None:
            raise PermissionError(
                "Conversation not found for this user"
            )

        rows = db.scalars(
            select(ChatMessage)
            .where(
                ChatMessage.conversation_id == conversation_id
            )
            .order_by(ChatMessage.created_at, ChatMessage.message_id)
        ).all()

        history = []

        for row in rows:
            if row.message_data:
                history.append(row.message_data)
            else:
                history.append({
                    "role": row.role,
                    "content": row.content,
                })

        return history



    def get_chat_messages(
        self,
        db: Session,
        conversation_id: str,
        roles: list[str],
        user_id: str,
    ) -> list[dict]:
        """
        Retrieve the conversation's complete agent history.
        """

        conversation = db.scalar(
            select(Conversation).where(
                Conversation.conversation_id == conversation_id,
                Conversation.user_id == user_id,
            )
        )

        if conversation is None:
            raise PermissionError(
                "Conversation not found for this user"
            )

        rows = db.scalars(
            select(ChatMessage)
            .where(
                ChatMessage.conversation_id == conversation_id,
                ChatMessage.role.in_(roles),
            )
            .order_by(ChatMessage.created_at, ChatMessage.message_id)
        ).all()

        history = []

        for row in rows:
            if row.message_data:
                history.append(row.message_data)
            else:
                history.append({
                    "role": row.role,
                    "content": row.content,
                })

        return history



    def save_messages(self, db: Session, conversation: Conversation, messages: list[dict]):
        for message in messages:
            db.add(
                ChatMessage(
                    conversation_id=conversation.conversation_id,
                    role=message.get("role", "assistant"),
                    content=str(message.get("content") or ""),
                    message_data=message,
                )
            )

        conversation.updated_at = datetime.now(timezone.utc)



    def get_messages_per_role(
        self,
        db: Session,
        conversation_id: str,
        user_id: str,
        role: str,
    ) -> list[dict]:
        """
        Retrieve the conversation's complete agent history.
        """

        conversation = db.scalar(
            select(Conversation).where(
                Conversation.conversation_id == conversation_id,
                Conversation.user_id == user_id,
            )
        )

        if conversation is None:
            raise PermissionError(
                "Conversation not found for this user"
            )

        rows = db.scalars(
            select(ChatMessage)
            .where(
                ChatMessage.conversation_id == conversation_id,
                ChatMessage.role == role,
            )
            .order_by(ChatMessage.created_at, ChatMessage.message_id)
        ).all()

        history = []

        for row in rows:
            if row.message_data:
                history.append(row.message_data)
            else:
                history.append({
                    "role": row.role,
                    "content": row.content,
                })

        return history


    def list_conversations(
        self,
        db: Session,
        user_id: str,
    ) -> Sequence[Conversation]:
        """
        Return conversations belonging to this user.
        """
        return db.scalars(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        ).all()


'''    def save_messages(
        self,
        db: Session,
        conversation: Conversation,
        messages: list[dict],
    ) -> None:
        """
        Save a batch of messages to the conversation.
        """

        for message in messages:
            role = message.get("role", "unknown")
            content = message.get("content")

            if content is None:
                content = ""

            if not isinstance(content, str):
                content = str(content)

            db.add(
                ChatMessage(
                    conversation_id=conversation.conversation_id,
                    role=role,
                    content=content,
                    message_data=message,
                )
            )

        db.flush()'''




chat_history_service = ChatHistoryService()
