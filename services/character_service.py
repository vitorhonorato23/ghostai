from models import Character

class CharacterService:
    def __init__(self, db_session):
        self.db = db_session

    def create_character(self, name, personality, style, context, creator_id):
        character = Character(
            name=name,
            personality=personality,
            style=style,
            context=context,
            creator_id=creator_id
        )
        self.db.add(character)
        self.db.commit()
        self.db.refresh(character)
        return character

    def get_or_create(self, name, personality, style, context, creator_id):
        existing = self.db.query(Character).filter_by(
            name=name,
            personality=personality,
            style=style,
            context=context
        ).first()

        if existing:
            return existing

        return self.create_character(name, personality, style, context, creator_id)

    def get_by_user(self, user_id):
        return self.db.query(Character).filter_by(creator_id=user_id).all()

    def get_by_id(self, character_id):
        return self.db.query(Character).filter_by(id=character_id).first()