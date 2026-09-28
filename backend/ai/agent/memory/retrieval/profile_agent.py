from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

from backend.ai.model.my_model import ModelManage
from backend.ai.agent.memory.save.profile_memory import ProfileMemory
from pydantic import BaseModel,Field

class ProfileParams(BaseModel):
    name:str = Field( description="姓名")
    age: int = Field(description="年龄")
    job: str = Field( description="职业")
    address: str = Field( description="地址")
    xueli: str = Field( description="学历")

"""
用户画像智能体
"""
class ProfileAgent:

    def __init__(self, profile_memory: ProfileMemory):
        self.model = ModelManage.get_model()
        self.prompt = self.get_prompt()
        self.agent = self.get_agent()
        # 获取用户画像记忆的保存对象
        self.profile_memory = profile_memory

    def get_prompt(self):
        self.prompt = """
           一: 角色：你是一个用户画像提取助手
           二：任务：
                  - 根据用户问题提取相关用户画像信息
           三：规则：
                  1、用户画像信息包含以下信息：姓名，年龄，职业，地址，学历
                  2、去掉闲聊内容
                  3、避免重复
                  4、使用第三人称描述
                  5、不要做总结，只记录重要信息即可
                  6、如果没有用户画像信息，就返回空
                
           四:输出
                - 输出的用户画像信息
           五:示例：
                 用户输入：我喜欢打游戏
                 输出:{'name': '', 'age': 0, 'job': '', 'address': '', 'xueli': ''}
                 
                 用户输入：我是张三
                 输出:{'name': '张三', 'age': 0, 'job': '', 'address': '', 'xueli': ''}
        """
        return self.prompt

    def get_agent(self):
        self.agent = create_agent(
            model=self.model,
            system_prompt=self.prompt,
            tools=[],
            debug=True,
            response_format=ProfileParams
        )
        return self.agent

    # 记忆更新
    def update(self, question):
        # 提问
        rs = self.agent.invoke({"messages": [HumanMessage(content=question)]})
        data = rs["structured_response"].model_dump()
        #print(data)
        #查询出是否有新的画像信息
        for key,value in data.items():
            if value:
                self.profile_memory.save(key,value)

if __name__ == "__main__":
    Long_memory =  ProfileMemory(1)
    agent = ProfileAgent(Long_memory)
    q1 = "我喜欢打游戏"
    q2 = "我擅长编程"
    q3="我是李四"
    q4="我今年24岁"
    agent.update( q2)








