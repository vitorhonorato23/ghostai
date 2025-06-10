from .login import router as login_router
from .chat import router as chat_router
from .register import router as register_router
from .character import router as character_router

routers = [login_router, chat_router, register_router, character_router]