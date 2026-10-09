from backend.ai.agent.memory.retrieval.SummaryAgent import SummaryAgent
from backend.ai.agent.memory.manager.session_mananger import SessionManager
from backend.ai.agent.memory.retrieval.long_agent import LongAgent
from backend.ai.agent.memory.retrieval.profile_agent import ProfileAgent

"""
记忆管理器，管理记忆的更新
"""
class MemoryManager:
    def __init__(self, sessionManger:SessionManager):
        # 摘要智能体
        self.summary_agent = SummaryAgent(sessionManger.summary_memory)
        # 获取窗口记忆对象
        self.window_memory = sessionManger.window_memory
        # 创建长期记忆智能体
        self.long_agent = LongAgent(sessionManger.long_memory)
        # 创建用户画像智能体
        self.profile_agent = ProfileAgent(sessionManger.profile_memory)

    async def update(self, user_id, question):
        # 获取查询的窗口记忆
        query_window = await self.window_memory.query()
        # 更新长期记忆
        try:
            await self.long_agent.update(user_id, question)
        except Exception as e:
            print(f"长期记忆更新失败: {e}")
        # 更新用户画像记忆
        try:
            await self.profile_agent.update(question)
        except Exception as e:
            print(f"画像记忆更新失败: {e}")

        if len(query_window) >= 2:
            try:
                await self.summary_agent.update(query_window)
            except Exception as e:
                print(f"摘要记忆更新失败: {e}")
