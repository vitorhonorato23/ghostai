from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from services import UserService
from database import SessionLocal

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})

@router.post("/register", response_class=HTMLResponse)
async def register_user(request: Request, username: str = Form(...), password: str = Form(...), confirm: str = Form(...)):
    if password != confirm:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Passwords do not match."})

    db = SessionLocal()
    service = UserService(db)
    existing = service.get_user_by_username(username)
    if existing:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already taken."})

    user = service.create_user(username, password)
    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=302)