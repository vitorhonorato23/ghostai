from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.character_service import CharacterService
from database import SessionLocal

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/characters", response_class=HTMLResponse)
async def character_list(request: Request):
    db = SessionLocal()
    user_id = request.session.get("user_id")

    if not user_id:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login")

    characters = CharacterService(db).get_by_user(user_id)
    return templates.TemplateResponse("characters.html", {
        "request": request,
        "characters": characters
    })
