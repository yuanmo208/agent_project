from app.ai.agent.multi_agent.schema.intent_schema import IntentSchema
from app.ai.agent.multi_agent.state.exam_state import ExamState
from app.ai.model.my_model import ModelManage
from app.ai.prompt.bulider_prompt import BuilderPromptYaml

from langchain.agents import create_agent
from langchain_core.messages import AIMessage

"""
意图识别节点
"""
# 读取外部配置文件
prompt = BuilderPromptYaml.get_prompt("intent_node.yaml")


async def intent_node(state: ExamState):
    # 获取用户输入问题
    user_input = state["messages"][0].content
    print("11")
    # # 获取本地模型
    # model = app.state.model.local_model
    print("12")
    model = ModelManage.get_local_model()
    # 创建智能体
    agent = create_agent(
        model=model,
        system_prompt=prompt,
        response_format=IntentSchema
    )
    print("13")
    # 提问
    user_msg = {"messages": {"role": "user", "content": user_input}}
    print("14")
    rs = await agent.ainvoke(user_msg)
    print("15")
    # 把输入结果转换成字典或者json
    data = rs["structured_response"].model_dump()
    print("16")
    # 自定义AI回复消息
    ai_msg = f"\n意图识别成功,课程名称:{data["course"]},课程数量:{data["num"]}\n"
    # 更新状态
    print("17")
    return {
         "messages": [AIMessage(content=ai_msg)],
         "course": data["course"],
         "total": data["num"],
         "exam_step": "intent"
    }
