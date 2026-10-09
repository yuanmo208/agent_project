from psycopg_pool import ConnectionPool
from dotenv import load_dotenv
import os
import asyncio
load_dotenv()


# 配置连接池
pool = ConnectionPool(
    conninfo=os.getenv("POSTGRESQL_URL"),
    max_size=20,  # 最大连接数，生成环境是20个
    min_size=10,  # 最小连接数，生成环境是10个
)


# 建表（首次启动自动创建，避免查询时报 UndefinedTable）
def _init_table():
    try:
        with pool.connection() as con:
            with con.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS conversation_summary (
                        session_id VARCHAR PRIMARY KEY,
                        summary TEXT,
                        update_time TIMESTAMP DEFAULT NOW()
                    )
                """)
                con.commit()
    except Exception as e:
        print(f"conversation_summary 建表失败:{e}")


_init_table()


class SummaryMemory:
    def __init__(self, session_id: str):
        self.session_id = session_id

    # 同步保存（放到线程中执行，避免阻塞事件循环）
    def _save_sync(self, summary: str):
        with pool.connection() as con:
            with con.cursor() as cur:
                sql = f"INSERT INTO conversation_summary(session_id, summary) VALUES('{self.session_id}','{summary}') ON CONFLICT(session_id) DO UPDATE SET summary=EXCLUDED.summary,update_time=NOW()"
                cur.execute(sql)
                # 提交事务
                con.commit()

    # 保存
    async def save(self, summary: str):
        await asyncio.to_thread(self._save_sync, summary)

    # 同步查询
    def _query_sync(self):
        with pool.connection() as con:
            with con.cursor() as cur:
                sql = f"select summary from conversation_summary where session_id ='{self.session_id}'"
                cur.execute(sql)
                # 查询单个值
                rs = cur.fetchone()

                if rs:
                    return rs[0]
                else:
                    return ""

    # 查询
    async def query(self):
        return await asyncio.to_thread(self._query_sync)


if __name__ == "__main__":
    async def _test():
        s = SummaryMemory("1")
        print(await s.query())

    asyncio.run(_test())
