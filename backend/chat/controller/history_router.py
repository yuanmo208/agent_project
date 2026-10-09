"""
聊天历史记录路由（最简实现：直接复用 summary_memory 的 PostgreSQL 连接池）
对应前端 chat.vue 的 history/* 请求
"""
import asyncio
from fastapi import APIRouter
from backend.ai.agent.memory.save.summary_memory import pool

history_router = APIRouter()


# 建表（首次启动自动创建）
def _init_tables():
    try:
        with pool.connection() as con:
            with con.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS chat_history (
                        history_id SERIAL PRIMARY KEY,
                        username VARCHAR(100) NOT NULL,
                        session_id VARCHAR(100),
                        title VARCHAR(255),
                        create_time TIMESTAMP DEFAULT NOW()
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS chat_message (
                        msg_id SERIAL PRIMARY KEY,
                        history_id INTEGER NOT NULL,
                        role VARCHAR(20) NOT NULL,
                        content TEXT,
                        create_time TIMESTAMP DEFAULT NOW()
                    )
                """)
                con.commit()
    except Exception as e:
        print(f"chat 历史表建表失败:{e}")


_init_tables()


# ---------- 历史会话列表 ----------
@history_router.get("/historyListMenu")
async def history_list_menu(username: str):
    def _q():
        with pool.connection() as con:
            with con.cursor() as cur:
                cur.execute(
                    "SELECT history_id, title, to_char(create_time, 'YYYY-MM-DD HH24:MI:SS') "
                    "FROM chat_history WHERE username=%s ORDER BY create_time DESC",
                    (username,)
                )
                return [{"historyId": r[0], "title": r[1], "time": r[2]} for r in cur.fetchall()]
    return {"code": 200, "data": await asyncio.to_thread(_q)}


# ---------- 选择某历史会话（返回消息 + session_id 恢复后端会话上下文）----------
@history_router.get("/selectHistory")
async def select_history(historyId: int, username: str):
    def _q():
        with pool.connection() as con:
            with con.cursor() as cur:
                cur.execute("SELECT session_id FROM chat_history WHERE history_id=%s", (historyId,))
                row = cur.fetchone()
                sid = row[0] if row else ""
                cur.execute(
                    "SELECT role, content FROM chat_message WHERE history_id=%s ORDER BY msg_id ASC",
                    (historyId,)
                )
                # 后端存 user/ai，前端期望 user/assistant
                msgs = [
                    {"role": ("assistant" if r[0] == "ai" else r[0]), "content": r[1]}
                    for r in cur.fetchall()
                ]
                return msgs, sid
    msgs, sid = await asyncio.to_thread(_q)
    return {"code": 200, "data": msgs, "session_id": sid}


# ---------- 模糊搜索 ----------
@history_router.get("/queryHistory")
async def query_history(username: str, keyword: str):
    def _q():
        with pool.connection() as con:
            with con.cursor() as cur:
                cur.execute(
                    "SELECT history_id, title, to_char(create_time, 'YYYY-MM-DD HH24:MI:SS') "
                    "FROM chat_history WHERE username=%s AND title LIKE %s ORDER BY create_time DESC",
                    (username, f"%{keyword}%")
                )
                return [{"historyId": r[0], "title": r[1], "time": r[2]} for r in cur.fetchall()]
    return {"code": 200, "data": await asyncio.to_thread(_q)}


# ---------- 删除 ----------
@history_router.get("/deleteHistory")
async def delete_history(historyId: int, username: str):
    def _q():
        with pool.connection() as con:
            with con.cursor() as cur:
                cur.execute("DELETE FROM chat_message WHERE history_id=%s", (historyId,))
                cur.execute("DELETE FROM chat_history WHERE history_id=%s", (historyId,))
                con.commit()
    await asyncio.to_thread(_q)
    return {"code": 200, "data": "删除成功"}
