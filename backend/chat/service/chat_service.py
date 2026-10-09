import json

from fastapi.responses import StreamingResponse

from backend.chat.dao import chat_dao


async def chat_service(exam_agent, question: str, user_id: str, session_id: str):
    print(f"用户问题:{question},用户ID:{user_id}")

    # 定义一个异步迭代器
    async def generate(exam_agent, question, user_id, session_id):
        try:
            async for x in exam_agent.chat(question, user_id, session_id):
                # False 流式未结束
                data = {"data": x, "done": False}
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
            # 流式结束
            data = {"data": "", "done": True}
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        except Exception as e:
            import traceback
            print(f"generate错误:{e}")
            traceback.print_exc()
            # 流式结束
            data = {"data": "流式异常", "done": True}
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    return StreamingResponse(generate(exam_agent, question, user_id, session_id), media_type="text/event-stream")


async def create_session_service(exam_agent, user_id: str):
    """创建会话，返回 session_id"""
    session_id = await exam_agent.create_session(user_id)
    return {"session_id": session_id}


def save_conversation_service(username: str, session_id: str, question: str, answer: str, parent_id: int = 0):
    """
    保存一轮对话到 PostgreSQL 的核心逻辑
    """
    if parent_id == 0:
        # 截取前30个字符作为标题
        title = question[:30] + ("..." if len(question) > 30 else "")
        hid = chat_dao.insert_postgres_title(username, session_id, title)
    else:
        hid = parent_id
        # 若传了新 session_id 则同步更新
        if session_id:
            chat_dao.update_postgres_sid(session_id, hid)
    # 保存用户提问
    chat_dao.insert_postgres_message(hid, "user", question)
    # 保存ai回答
    chat_dao.insert_postgres_message(hid, "ai", answer)
    return hid
