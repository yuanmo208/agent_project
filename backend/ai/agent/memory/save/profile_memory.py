import asyncio
from backend.utils import redis_util

"""
用户画像记忆存储
"""
class ProfileMemory:

    def __init__(self, user_id):
        # 复用全局连接池（带密码 + decode_responses=True，避免 Authentication required）
        self.redis = redis_util.get_redis_conn()
        self.key = f"profile:{user_id}"

    # 保存
    async def save(self, hashkey, value):
        await asyncio.to_thread(self.redis.hset, self.key, hashkey, str(value))

    # 同步执行查询逻辑（放到线程中执行，避免阻塞事件循环）
    def _query_sync(self):
        # 查询某个用户的用户画像（decode_responses=True 已自动转 str）
        rs = self.redis.hgetall(self.key)
        data = ""
        if rs:
            for hashkey, value in rs.items():
                data += f"{hashkey}:{value}\n"
        return data

    # 查询
    async def query(self):
        return await asyncio.to_thread(self._query_sync)

if __name__ =="__main__":
    async def _test():
        p = ProfileMemory(1)
        await p.save("name", "张三")
        await p.save("age", 23)
        # 查询
        print(await p.query())

    asyncio.run(_test())
