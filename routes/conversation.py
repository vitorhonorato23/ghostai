from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import SessionLocal
from services.conversation_service import ConversationService
from services.message_service import MessageService

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/conversations", response_class=HTMLResponse)
async def view_conversations(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login")

    db = SessionLocal()
    conversations = ConversationService(db).get_all_for_user(user_id)

    return templates.TemplateResponse("conversations.html", {
        "request": request,
        "conversations": conversations
    })

@router.get("/resume/{conversation_id}", response_class=HTMLResponse)
async def resume_conversation(conversation_id: int, request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login")

    db = SessionLocal()
    convo_service = ConversationService(db)
    msg_service = MessageService(db)

    conversation = convo_service.get(conversation_id)
    if not conversation or conversation.user_id != user_id:
        return RedirectResponse("/conversations")

    # Store context in session
    request.session["conversation_id"] = conversation.id
    request.session["character"] = {
        "name": conversation.character.name,
        "personality": conversation.character.personality,
        "style": conversation.character.style,
        "context": conversation.character.context
    }

    # Rebuild chat history for LLM input
    messages = msg_service.get_by_conversation(conversation.id)
    history = [{"role": m.role, "content": m.content} for m in messages]
    request.session["history"] = history

    edit_index = request.session.pop("edit_index", None)

    return templates.TemplateResponse("chat.html", {
        "request": request,
        "chat_response": "",
        "user_prompt": "",
        "history": history,
        "character": request.session["character"],
        "edit_index": edit_index,
        "session_conversation_id": conversation_id
    })