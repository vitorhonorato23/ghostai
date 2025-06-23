from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from services.character_service import CharacterService
from database import SessionLocal
from services.conversation_service import ConversationService
from services.message_service import MessageService
import requests

router = APIRouter()
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


@router.post("/newChat", response_class=HTMLResponse)
async def new_chat_entry(
    request: Request,
    name: str = Form(...),
    personality: str = Form(...),
    style: str = Form(...),
    context: str = Form(None),
    prompt: str = Form(...)
):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login")

    history = request.session.get("history", [])

    db = SessionLocal()
    user_id = request.session["user_id"]
    character_service = CharacterService(db)
    conversation_service = ConversationService(db)
    message_service = MessageService(db)

    # Reuse or create the character
    character = character_service.get_or_create(
        name=name,
        personality=personality,
        style=style,
        context=context,
        creator_id=user_id
    )

    conversation = conversation_service.create(
        user_id=user_id,
        character_id=character.id,
        title=f"Chat with {character.name}"
    )
    conversation_id = conversation.id
    request.session["conversation_id"] = conversation_id

    message_service.add_message(
        conversation_id=conversation_id,
        role="user",
        content=prompt
    )

    history.append({"role": "system", "content": generate_character_prompt(name, personality, style, context)})
    history.append({"role": "user", "content": prompt})

    try:
        response = requests.post(OLLAMA_URL, json={"model": OLLAMA_MODEL, "messages": history, "stream": False})
        response.raise_for_status()
        ai_message = response.json().get("message", {}).get("content", "").strip()
        message_service.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_message
        )
        history.append({"role": "assistant", "content": ai_message})

        request.session["history"] = history

    except Exception as e:
        ai_message = f"An error occurred: {e}"

    return templates.TemplateResponse("chat.html", {
        "request": request,
        "chat_response": ai_message,
        "user_prompt": "",
        "history": history,
        "character": request.session.get("character", {})
    })

@router.post("/chat", response_class=HTMLResponse)
async def chat_entry(
    request: Request,
    name: str = Form(...),
    personality: str = Form(...),
    style: str = Form(...),
    context: str = Form(None),
    prompt: str = Form(...)
):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login")
    
    history = request.session.get("history")

    db = SessionLocal()
    user_id = request.session["user_id"]
    conversation_id = request.session["conversation_id"]
    character_service = CharacterService(db)
    conversation_service = ConversationService(db)
    message_service = MessageService(db)

    message_service.add_message(
        conversation_id=conversation_id,
        role="user",
        content=prompt
    )
    history.append({"role": "user", "content": prompt})

    try:
        response = requests.post(OLLAMA_URL, json={"model": OLLAMA_MODEL, "messages": history, "stream": False})
        response.raise_for_status()
        ai_message = response.json().get("message", {}).get("content", "").strip()
        message_service.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_message
        )
        history.append({"role": "assistant", "content": ai_message})

        request.session["history"] = history

    except Exception as e:
        ai_message = f"An error occurred: {e}"

    return templates.TemplateResponse("chat.html", {
        "request": request,
        "chat_response": ai_message,
        "user_prompt": "",
        "history": history,
        "character": request.session.get("character", {})
    })


@router.post("/clear", response_class=HTMLResponse)
async def clear_conversation(request: Request):
    request.session.pop("history", None)
    return RedirectResponse(url="/", status_code=303)