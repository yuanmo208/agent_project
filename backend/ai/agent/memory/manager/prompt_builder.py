from backend.ai.agent.memory.save.window_memory import WindowMemory
from backend.ai.agent.memory.save.summary_memory import SummaryMemory
from backend.ai.agent.memory.save.long_memory import LongMemory
from backend.ai.agent.memory.save.profile_memory import ProfileMemory


class PromptBuilder:
    def __init__(self, session_id, user_id):
        self.window_memory = WindowMemory(session_id)
        self.summary_memory = SummaryMemory(session_id)
        self.long_memory = LongMemory()
        self.profile_memory = ProfileMemory(user_id)

    # 构建提示词
    async def builder_prompt(self, user_id, question):
        prompt = """
        一: 角色：你是一个记忆提取助手
        二: 任务：
              - 理解用户需求
              - 根据用户问题，提取相关记忆
        """
        # 查询窗口记忆（容错：失败时不阻塞对话）
        try:
            window_memory = await self.window_memory.query()
        except Exception:
            window_memory = []
        prompt += "短期记忆-窗口记忆"
        for i in window_memory:
            if i["role"] == "user":
                prompt += f"用户提问：{i['content']}"
            else:
                prompt += f"AI回复：{i['content']}"
        # 查询摘要记忆（容错）
        try:
            summary_memory = await self.summary_memory.query()
        except Exception:
            summary_memory = ""
        prompt += "短期记忆-摘要记忆:"
        prompt += summary_memory
        # 查询长期记忆（容错）
        try:
            long_memory = await self.long_memory.query(user_id, question)
        except Exception:
            long_memory = []
        prompt += "长期记忆:"
        for x in long_memory:
            prompt += x+"\n"
        # 查询用户画像（容错）
        try:
            profile_memory = await self.profile_memory.query()
        except Exception:
            profile_memory = ""
        prompt += f"用户画像:{profile_memory}"
        return prompt
