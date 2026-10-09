import psycopg2
import os
from dotenv import load_dotenv
from dbutils.pooled_db import PooledDB

load_dotenv()


class PostgresManage:
    # 定义私有属性
    _pool = None

    @staticmethod
    def get_pg_conn():
        # 判断_pool 是否为空
        if PostgresManage._pool is None:
            # 获取连接字符串
            dsn = os.getenv("POSTGRESQL_URL")
            if not dsn:
                raise ValueError("未找到 POSTGRESQL_URL 环境变量")

            # 创建连接池
            PostgresManage._pool = PooledDB(
                creator=psycopg2,
                maxconnections=10,  # 最大连接数
                mincached=2,  # 启动时预建 2 个空闲连接
                blocking=True,  # 池满时阻塞等待
                ping=1,  # 取连接前检查是否可用
                dsn=dsn,  # 直接使用完整的连接字符串
            )
        # 从连接池获取一个连接
        return PostgresManage._pool.connection()

    # 关闭连接（归还到连接池）
    @staticmethod
    def close_pg_conn(cursor, conn):
        if cursor:
            cursor.close()
        if conn:
            conn.close()