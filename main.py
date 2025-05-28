from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import requests
from auth_setup import SessionLocal, UserService

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
templates = Jinja2Templates(directory="templates")

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama2"

def generate_character_prompt(name, personality, style, context=None):
    prompt = (
        f"You are {name}, {personality.strip()}\\n"
        f"You speak in a {style.strip()} style.\\n"
        f"Always stay in character and never reveal that you are an AI or language model.\\n"
        f"Respond with emotions, quirks, and personality consistent with your identity.\\n"
    )
    if context:
        prompt += f"You are currently in this situation: {context.strip()}\\n"
    return prompt.strip()

@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})

@app.post("/register", response_class=HTMLResponse)
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

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login", response_class=HTMLResponse)
async def login_user(request: Request, username: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    service = UserService(db)
    user = service.get_user_by_username(username)
    if not user or not service.verify_password(password, user.password_hash):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials."})

    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=302)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)

@app.get("/", response_class=HTMLResponse)
async def form(request: Request):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login")
    request.session.pop("history", None)
    return templates.TemplateResponse("form.html", {
        "request": request,
        "character": {},
        "character2": {}
    })

@app.post("/chat", response_class=HTMLResponse)
async def chat_entry(
    request: Request,
    name: str = Form(...),
    personality: str = Form(...),
    style: str = Form(...),
    context: str = Form(None),
    prompt: str = Form(...),
    name2: str = Form(None),
    personality2: str = Form(None),
    style2: str = Form(None),
    context2: str = Form(None),
):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login")

    history = request.session.get("history", [])
    is_duo = name2 and personality2 and style2

    if not history:
        history.append({"role": "system", "content": generate_character_prompt(name, personality, style, context)})
        if is_duo:
            history.append({"role": "system", "content": generate_character_prompt(name2, personality2, style2, context2)})

        request.session["character"] = {
            "name": name, "personality": personality, "style": style, "context": context
        }
        request.session["character2"] = {
            "name": name2, "personality": personality2, "style": style2, "context": context2
        }

    history.append({"role": "user", "content": prompt})

    try:
        response = requests.post(OLLAMA_URL, json={"model": OLLAMA_MODEL, "messages": history, "stream": False})
        response.raise_for_status()
        ai_message = response.json().get("message", {}).get("content", "").strip()
        history.append({"role": "assistant", "content": ai_message})

        if is_duo:
            response_2 = requests.post(OLLAMA_URL, json={"model": OLLAMA_MODEL, "messages": history, "stream": False})
            response_2.raise_for_status()
            ai_message_2 = response_2.json().get("message", {}).get("content", "").strip()
            history.append({"role": "assistant", "content": ai_message_2})

        request.session["history"] = history

    except Exception as e:
        ai_message = f"An error occurred: {e}"

    return templates.TemplateResponse("duo_chat.html" if is_duo else "chat.html", {
        "request": request,
        "chat_response": ai_message,
        "user_prompt": "",
        "history": history,
        "character": request.session.get("character", {}),
        "character2": request.session.get("character2", {})
    })

@app.post("/clear", response_class=HTMLResponse)
async def clear_conversation(request: Request):
    request.session.pop("history", None)
    return RedirectResponse(url="/", status_code=303)