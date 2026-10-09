import json
import asyncio
from dotenv import load_dotenv
import os
from backend.utils import redis_util

load_dotenv()
"""
短期记忆-窗口记忆
"""


class WindowMemory:
    def __init__(self, session_id):
        self.redis = redis_util.get_redis_conn()
        # 限制窗口记忆次数，生成环境是40次
        self.window_size = int(os.getenv("WINDOW_MEMORY_ROUNDS"))
        self.session_id = session_id
        self.key = f"window_memory:{self.session_id}"
        # 过期时间
        self.window_limit_time = int(os.getenv("WINDOW_MEMORY_TIME"))

    # 同步执行保存逻辑（放到线程中执行，避免阻塞事件循环）
    def _save_sync(self, role: str, content: str):
        # 构建字典
        data = {"role": role, "content": content}
        # 添加到列表种
        self.redis.rpush(self.key, json.dumps(data, ensure_ascii=False))
        # 设置保留窗口记忆
        self.redis.ltrim(self.key, -self.window_size, -1)
        # 设置过期时间
        self.redis.expire(self.key, self.window_limit_time)

    # 保存记忆
    async def save(self, role: str, content: str):
        await asyncio.to_thread(self._save_sync, role, content)

    # 同步执行查询逻辑
    def _query_sync(self):
        # 判断key是否存在
        if self.redis.exists(self.key):
            data = self.redis.lrange(self.key, 0, -1)
            return [json.loads(i) for i in data]
        return []

    # 提取记忆
    async def query(self):
        return await asyncio.to_thread(self._query_sync)


if __name__ =="__main__":
    async def _test():
        w = WindowMemory("001")
        # 模拟人类消息添加
        await w.save("user", "你好")
        # 模拟AI回复消息
        await w.save("ai", "你好，我是AI助手")
        # 模拟人类消息添加
        await w.save("user", "你好1")
        # 模拟AI回复消息
        await w.save("ai", "你好1，我是AI助手1")
        # 模拟人类消息添加
        await w.save("user", "你好2")
        # 模拟AI回复消息
        await w.save("ai", "你好2，我是AI助手2")
        await w.save("user", "你好3")
        # 模拟AI回复消息
        await w.save("ai", "你好3，我是AI助手2")
        # 查询记忆
        rs = await w.query()
        print(rs)

    asyncio.run(_test())
