import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from backend.chat.schema.chat_schema import ChatSchema, CreateSessionSchema, SaveConversationSchema
from backend.chat.service import chat_service
from backend.ai.agent.memory.save.summary_memory import pool
import asyncio

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
    def _save():
        with pool.connection() as con:
            with con.cursor() as cur:
                if req.parentId == 0:
                    title = req.question[:30] + ("..." if len(req.question) > 30 else "")
                    cur.execute(
                        "INSERT INTO chat_history(username, session_id, title) VALUES(%s,%s,%s) RETURNING history_id",
                        (req.username, req.sessionId, title)
                    )
                    hid = cur.fetchone()[0]
                else:
                    hid = req.parentId
                    # 若传了新 sessionId 则同步更新
                    if req.sessionId:
                        cur.execute(
                            "UPDATE chat_history SET session_id=%s WHERE history_id=%s",
                            (req.sessionId, hid)
                        )
                cur.execute(
                    "INSERT INTO chat_message(history_id, role, content) VALUES(%s,%s,%s)",
                    (hid, "user", req.question)
                )
                cur.execute(
                    "INSERT INTO chat_message(history_id, role, content) VALUES(%s,%s,%s)",
                    (hid, "ai", req.answer)
                )
                con.commit()
                return hid
    hid = await asyncio.to_thread(_save)
    return {"code": 200, "data": hid}
