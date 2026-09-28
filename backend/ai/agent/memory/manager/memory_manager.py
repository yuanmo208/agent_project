from app.ai.agent.memory.retrieval.SummaryAgent import SummaryAgent
from app.ai.agent.memory.manager.session_mananger import SessionManager
from app.ai.agent.memory.retrieval.long_agent import LongAgent
from app.ai.agent.memory.retrieval.profile_agent import ProfileAgent

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

    def update(self, user_id, question):
        # 获取查询的窗口记忆
        query_window = self.window_memory.query()
        # 更新长期记忆
        self.long_agent.update(user_id, question)
        # 更新用户画像记忆
        self.profile_agent.update(question)

        if len(self.window_memory.query()) >= 2:
            self.summary_agent.update(query_window)
