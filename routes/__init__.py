from .login import router as login_router
from .chat import router as chat_router
from .register import router as register_router
from .character import router as character_router
from .conversation import router as conversation_router

routers = [login_router, chat_router, register_router, character_router, conversation_router]