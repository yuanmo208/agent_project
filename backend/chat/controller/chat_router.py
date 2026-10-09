from fastapi import APIRouter, Request
from backend.chat.schema.chat_schema import SaveConversationSchema
from backend.chat.service import chat_service
import asyncio

from backend.chat.service.chat_service import save_conversation_service


chat_router = APIRouter()


@chat_router.get("/create_session")
async def create_session(request: Request, user_id: str):
    print(f"创建会话,用户ID:{user_id}")
    # 获取考试智能体
    exam_agent = request.app.state.exam_agent
    return await chat_service.create_session_service(exam_agent, user_id)


@chat_router.get("/chat")
async def chat(request: Request, question: str, user_id: str, session_id: str):
    print(f"用户问题:{question},用户ID:{user_id},会话ID:{session_id}")
    # 获取考试智能体
    exam_agent = request.app.state.exam_agent
    return await chat_service.chat_service(exam_agent, question, user_id, session_id)


@chat_router.post("/saveConversation")
async def save_conversation(req: SaveConversationSchema):
    """保存一轮对话到 PostgreSQL，供前端历史记录查询"""
    # 将数据库操作放入线程池执行，避免阻塞主线程
    hid = await asyncio.to_thread(
        save_conversation_service,
        username=req.username,
        session_id=req.sessionId,
        question=req.question,
        answer=req.answer,
        parent_id=req.parentId
    )

    return {
        "code": 200,
        "data": hid
    }

