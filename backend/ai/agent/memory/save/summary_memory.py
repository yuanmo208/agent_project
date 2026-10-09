from dotenv import load_dotenv
import asyncio

from backend.utils.postgres_util import PostgresManage
'''
摘要记忆
'''


class SummaryMemory:
    def __init__(self, session_id: str):
        self.session_id = session_id

    # 同步保存（放到线程中执行，避免阻塞事件循环）
    def _save_sync(self, summary: str):
        conn = PostgresManage.get_pg_conn()
        cursor = conn.cursor()
        try:
            sql = f"INSERT INTO conversation_summary(session_id, summary) VALUES('{self.session_id}','{summary}') ON CONFLICT(session_id) DO UPDATE SET summary=EXCLUDED.summary,update_time=NOW()"
            cursor.execute(sql)
            # 提交事务
            conn.commit()
        except Exception as e:
            conn.rollback()
            print("写入失败：", e)
        finally:
            PostgresManage.close_pg_conn(cursor, conn)

    # 保存
    async def save(self, summary: str):
        await asyncio.to_thread(self._save_sync, summary)

    # 同步查询
    def _query_sync(self):
        conn = PostgresManage.get_pg_conn()
        cursor = conn.cursor()
        try:
            sql = f"select summary from conversation_summary where session_id ='{self.session_id}'"
            cursor.execute(sql)
            # 查询单个值
            rs = cursor.fetchone()
            return rs[0]
        except Exception as e:
            print("查询失败：", e)
            return ""
        finally:
            PostgresManage.close_pg_conn(cursor, conn)

    # 查询
    async def query(self):
        return await asyncio.to_thread(self._query_sync)


if __name__ == "__main__":
    async def _test():
        s = SummaryMemory("1")
        print(await s.query())

    asyncio.run(_test())
