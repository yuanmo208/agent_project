import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from langgraph.checkpoint.memory import InMemorySaver

from app.ai.agent.multi_agent.graph.exam_graph import ExamGraph
from app.chat.controller.chat_router import chat_router
from app.users.controller.account_router import account_router
from app.users.controller.email_router import email_router



# 生命周期加载模型
@asynccontextmanager
async def get_model(app: FastAPI):
    memory = InMemorySaver()
    app.state.exam_agent = ExamGraph(memory)
    print("智能体初始化成功")
    yield
    app.state.exam_agent = None
    print("智能体释放完成")
app = FastAPI(lifespan=get_model)

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册子路由
app.include_router(chat_router, prefix="/chat")

app.include_router(email_router, prefix="/email")

app.include_router(account_router, prefix="/account")

# 服务器启动配置
uvicorn.run(
    app=app,
    host="localhost",
    port=8000,
    reload=False,
)

