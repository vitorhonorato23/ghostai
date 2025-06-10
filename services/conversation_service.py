# services/conversation_service.py
from sqlalchemy.orm import Session
from models import Conversation

class ConversationService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, character_id: int, title: str = "Untitled"):
        conversation = Conversation(user_id=user_id, character_id=character_id, title=title)
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get(self, conversation_id: int):
        return self.db.query(Conversation).filter_by(id=conversation_id).first()

    def get_all_for_user(self, user_id: int):
        return self.db.query(Conversation).filter_by(user_id=user_id).order_by(Conversation.created_at.desc()).all()
