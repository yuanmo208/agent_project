import json

from fastapi.responses import StreamingResponse


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