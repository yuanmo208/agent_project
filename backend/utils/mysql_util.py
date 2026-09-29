import pymysql
import os
from dotenv import load_dotenv
from dbutils.pooled_db import PooledDB

load_dotenv()


class MySQLManage:
    # 定义私有属性
    _pool = None

    # 定义静态函数

    @staticmethod
    def get_mysql_conn():
        # 判断_pool 是否为空
        if MySQLManage._pool is None:
            # 创建连接池
            MySQLManage._pool = PooledDB(
                creator=pymysql,
                maxconnections=10,       # 最大连接数
                mincached=2,             # 启动时预建 2 个空闲连接
                blocking=True,           # 池满时阻塞等待
                ping=1,                  # 取连接前检查是否可用
                host=os.getenv("DB_HOST"),
                port=int(os.getenv("DB_PORT")),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_DATABASE"),
                charset=os.getenv("DB_CHARSET"),
            )
        # 从连接池获取一个连接
        return MySQLManage._pool.connection()

    # 关闭连接（归还到连接池）
    @staticmethod
    def close_mysql_conn(cursor, conn):
        cursor.close()
        conn.close()
