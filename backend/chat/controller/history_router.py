"""
聊天历史记录路由（最简实现：直接复用 summary_memory 的 PostgreSQL 连接池）
对应前端 chat.vue 的 history/* 请求
"""
import asyncio
from fastapi import APIRouter
from backend.chat.service.history_service import history_list_menu_service, select_history_service, \
    query_history_service, delete_history_service

history_router = APIRouter()


# ---------- 历史会话列表 ----------
@history_router.get("/historyListMenu")
async def history_list_menu(username: str):
    data = await asyncio.to_thread(history_list_menu_service, username)
    return {
        "code": 200,
        "data": data
    }


# ---------- 选择某历史会话（返回消息 + session_id 恢复后端会话上下文）----------
@history_router.get("/selectHistory")
async def select_history(historyId: int, username: str):
    msgs, sid = await asyncio.to_thread(select_history_service, historyId)
    return {
        "code": 200,
        "data": msgs,
        "session_id": sid
    }


# ---------- 模糊搜索 ----------
@history_router.get("/queryHistory")
async def query_history(username: str, keyword: str):
    data = await asyncio.to_thread(query_history_service, username, keyword)
    return {
        "code": 200,
        "data": data
    }


# ---------- 删除 ----------
@history_router.get("/deleteHistory")
async def delete_history(historyId: int, username: str):
    await asyncio.to_thread(delete_history_service, historyId, username)
    return {"code": 200, "data": "删除成功"}
