from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database import Base, engine, SessionLocal
from starlette.middleware.sessions import SessionMiddleware
from routes import routers

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
router = APIRouter()
for route in routers:
    app.include_router(route)

templates = Jinja2Templates(directory="templates")

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama2"

@app.get("/", response_class=HTMLResponse)
async def form(request: Request):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login")
    request.session.pop("history", None)
    return templates.TemplateResponse("newChat.html", {
        "request": request,
        "character": {}
    })