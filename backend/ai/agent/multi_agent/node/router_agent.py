from backend.ai.agent.multi_agent.schema.intent_schema import RouterSchema
from backend.ai.model.my_model import ModelManage
from backend.ai.prompt.bulider_prompt import BuilderPromptYaml
from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware
"""
路由分类节点
"""
#读取外部配置文件
prompt = BuilderPromptYaml.get_prompt("router_agent.yaml")
def router_agent(question):
    try:
        # 获取本地模型
        model = ModelManage.get_model()
        # 创建智能体
        agent = create_agent(
            model=model,
            system_prompt=prompt,
            response_format=RouterSchema,
            middleware=[
                ModelCallLimitMiddleware(
                    thread_limit=3,
                    exit_behavior="end"
                )

            ]
        )
        # 提问
        user_msg = {"messages": {"role": "user", "content": question}}
        rs = agent.invoke(user_msg)
        # 把输入结果转换成字典或者json
        data = rs["structured_response"].model_dump()
        return data.get("route", "chat")
    except Exception as e:
        print("==========大模型路由分类兜底=============")
        try:
            # 获取本地模型
            model = ModelManage.get_model()
            # 创建智能体
            agent = create_agent(
                model=model,
                system_prompt=prompt,
                response_format=RouterSchema,
                middleware=[
                    ModelCallLimitMiddleware(
                        thread_limit=3,
                        exit_behavior="end"
                    )

                ]
            )
            # 提问
            user_msg = {"messages": {"role": "user", "content": question}}
            rs = agent.invoke(user_msg)
            # 把输入结果转换成字典或者json
            data = rs["structured_response"].model_dump()
            return data.get("route", "chat")
        except Exception as e:
            print("==========返回自定义路由分类结果============")
            return "chat"