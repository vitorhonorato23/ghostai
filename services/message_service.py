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
    
    def update_content(self, message_id: int, new_content: str):
        message = self.db.query(Message).filter_by(id=message_id).first()
        if message:
            message.content = new_content
            self.db.commit()
        return message

    def delete(self, message_id: int):
        message = self.db.query(Message).filter_by(id=message_id).first()
        if message:
            self.db.delete(message)
            self.db.commit()