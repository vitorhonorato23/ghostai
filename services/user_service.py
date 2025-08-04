import bcrypt
from models import User

class UserService:
    def __init__(self, db_session):
        self.db = db_session

    def get_user_by_username(self, username: str):
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, username: str, password: str):
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = User(username=username, password_hash=hashed.decode('utf-8'))
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def verify_password(self, plain_password: str, hashed_password: str):
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def update_user(self, user_id: int, username: str, gpt_token: str | None):
        user = self.get_user_by_id(user_id)
        if user:
            user.username = username
            user.gpt_token = gpt_token
            self.db.commit()
            self.db.refresh(user)
        return user
