from langchain_core.messages import HumanMessage, AIMessage
from backend.ai.model.my_model import ModelManage
from backend.ai.agent.multi_agent.state.exam_state import ExamState
from backend.ai.prompt.bulider_prompt import BuilderPromptYaml
from langchain.agents import create_agent
from langgraph.config import get_stream_writer
from langchain.agents.middleware import ModelCallLimitMiddleware,SummarizationMiddleware
"""
聊天+记忆的节点
"""
#读取外部配置文件
prompt = BuilderPromptYaml.get_prompt("chat_node.yaml")
# 定义摘要记忆配置
summary_memory = SummarizationMiddleware(
    model=ModelManage.get_model(),
    trigger=[
        ("tokens", 50),
        ("messages", 3)
    ],
    keep=("messages", 20),  # 保留最近20轮的对话，生成环境建议保留20以上
    trim_tokens_to_summarize=4000,  # 可选，摘要总结的摘要信息限制在4000token
)
# 正常处理
agent01 = create_agent(
    model=ModelManage.get_model(),
    system_prompt=prompt,
    debug=True,
    middleware=[
        ModelCallLimitMiddleware(
            thread_limit=3,
            exit_behavior="end",
        ),
       summary_memory
    ]
)
# 降级处理的智能体
agent02 = create_agent(
    model=ModelManage.get_model(),
    system_prompt=prompt,
    middleware=[
        ModelCallLimitMiddleware(
            thread_limit=3,
            exit_behavior="end"
        )

    ]
)
async def chat_node(state:ExamState):
    try:
        # 获取用户问题和记忆信息
        memory = state["messages"]
        print(f"获取用户问题和记忆信息:{memory}")
        # 提问
        user_msg = {"messages": memory}
        # 异步流式
        result = []
        # 获取流式写入对象
        write = get_stream_writer()
        async for c, m in agent01.astream(user_msg, stream_mode="messages"):
            if c.content:
                result.append(c.content)
                write(c.content)
        ai_msg = ""
        return {"messages": [AIMessage(content=ai_msg)], "exam_step": "done"}
    except Exception as e:
        print("=====大模型兜底=====")
        try:
            # 获取用户问题和记忆信息
            memory = state["messages"]

            # 提问
            user_msg = {"messages": memory}
            # 异步流式
            result = []
            # 获取流式写入对象
            write = get_stream_writer()
            async for c, m in agent02.astream(user_msg, stream_mode="messages"):
                if c.content:
                    result.append(c.content)
                    write(c.content)
            ai_msg = ""
            return {"messages": [AIMessage(content=ai_msg)], "exam_step": "done"}
        except Exception as e:
            print("=====超时=====")
            return {"messages": [AIMessage(content="\n请求超时，请重新再试\n")], "exam_step": "done"}