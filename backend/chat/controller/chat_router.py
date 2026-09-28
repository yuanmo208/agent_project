import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

chat_router = APIRouter()


@chat_router.get("/chat")
async def chat(request: Request, question: str, user_id: str):
    print(f"用户问题:{question},用户ID:{user_id}")
    exam_agent = request.app.state.exam_agent
    # 定义一个异步迭代七
    async def generate(question, user_id, session_id):
        try:
            async for x in exam_agent.chat(question, user_id,"001"):
                # False 流式未结束
                data = {"data": x, "done": False}
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
            # 流式结束
            data = {"data": "", "done": True}
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        except Exception as e:
            # 流式结束
            data = {"data": f"流式异常{e}", "done": True}
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    return StreamingResponse(generate(question, user_id, "001"), media_type="text/event-stream")