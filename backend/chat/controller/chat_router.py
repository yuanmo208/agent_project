import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from backend.chat.schema.chat_schema import ChatSchema
from backend.chat.service import chat_service

chat_router = APIRouter()


@chat_router.get("/chat")
async def chat(request: Request, chatschema: ChatSchema):
    # 取出用户问题
    question = chatschema.question
    # 取出用户ID
    user_id = chatschema.user_id
    # 取出会话ID
    session_id = chatschema.session_id
    print(f"用户问题:{question},用户ID:{user_id},会话ID:{session_id}")
    # 获取考试智能体
    exam_agent = request.app.state.exam_agent
    return chat_service.chat_service(exam_agent, question, user_id, session_id)