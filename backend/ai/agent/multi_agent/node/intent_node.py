import ast
from backend.ai.agent.multi_agent.state.exam_state import ExamState
from backend.ai.model.my_model import ModelManage
from backend.ai.prompt.bulider_prompt import BuilderPromptYaml

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.config import get_stream_writer

"""
意图识别节点
"""
# 读取外部配置文件
prompt = BuilderPromptYaml.get_prompt("intent_node.yaml")


async def intent_node(state: ExamState):
    # 获取用户输入问题（取最后一条 HumanMessage，避免取到记忆提示 SystemMessage）
    user_input = ""
    for msg in state["messages"]:
        if isinstance(msg, HumanMessage):
            user_input = msg.content
    print("11")
    # 获取本地模型
    model = ModelManage.get_local_model()
    print("12")
    # 补充输出格式要求，引导本地模型输出字典字符串
    sys_prompt = prompt + "\n六：输出格式必须严格为 {'course': '课程名', 'num': 数字} 的字典字符串，不要输出其他内容。若用户只是闲聊、自我介绍、不是要题目，则返回 {'course': '', 'num': 0}"
    # 创建智能体（不使用 response_format，避免本地模型返回纯文本时死循环）
    agent = create_agent(
        model=model,
        system_prompt=sys_prompt,
    )
    print("13")
    # 提问
    user_msg = {"messages": [{"role": "user", "content": user_input}]}
    print("14")
    rs = await agent.ainvoke(user_msg, config={"recursion_limit": 5})
    print("15")
    # 本地模型返回纯文本字典字符串，解析
    content = rs["messages"][-1].content
    try:
        data = ast.literal_eval(content)
    except Exception:
        # 解析失败视为闲聊
        data = {"course": "", "num": 0}
    course = data.get("course", "") or ""
    num = data.get("num", 0) or 0
    print("16")
    # 只有需要出题时才提示意图识别结果，闲聊不输出该信息
    if course and num > 0:
        ai_msg = f"\n意图识别成功,课程名称:{course},课程数量:{num}\n"
        # 通过 custom 流输出（避免 messages 流重复）
        get_stream_writer()(ai_msg)
    # 更新状态
    print("17")
    return {
         "course": course,
         "total": num,
         "exam_step": "intent"
    }
