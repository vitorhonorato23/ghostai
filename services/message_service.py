# services/message_service.py
from sqlalchemy.orm import Session
from models import Message

class MessageService:
    def __init__(self, db: Session):
        self.db = db

    def add_message(self, conversation_id: int, role: str, content: str):
        message = Message(conversation_id=conversation_id, role=role, content=content)
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_by_conversation(self, conversation_id: int):
        return self.db.query(Message).filter_by(conversation_id=conversation_id).order_by(Message.timestamp).all()
