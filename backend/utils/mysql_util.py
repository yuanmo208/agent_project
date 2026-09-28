import pymysql
import os
from dotenv import load_dotenv
load_dotenv()


# 创建mysql连接
def load_mysql_conn():
    return pymysql.connect(
        # ip地址
        host=os.getenv("DB_HOST"),
        # 端口号
        port=int(os.getenv("DB_PORT")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_DATABASE"),
        charset=os.getenv("DB_CHARSET"),
        # 以字典的方式返回结果
        cursorclass=pymysql.cursors.DictCursor
    )


# 关闭连接
def close_mysql_conn(cursor, conn):
    cursor.close()
    conn.close()