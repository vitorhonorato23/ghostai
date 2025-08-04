from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from services import UserService
from database import SessionLocal

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/settings", response_class=HTMLResponse)
async def settings_form(request: Request):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login", status_code=302)
    db = SessionLocal()
    service = UserService(db)
    user = service.get_user_by_id(request.session["user_id"])
    return templates.TemplateResponse("settings.html", {"request": request, "user": user, "message": None})

@router.post("/settings", response_class=HTMLResponse)
async def update_settings(request: Request, username: str = Form(...), gpt_token: str = Form(None)):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login", status_code=302)
    db = SessionLocal()
    service = UserService(db)
    service.update_user(request.session["user_id"], username, gpt_token)
    user = service.get_user_by_id(request.session["user_id"])
    return templates.TemplateResponse(
        "settings.html",
        {"request": request, "user": user, "message": "Settings updated."},
    )
