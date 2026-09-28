import os

import redis
from dotenv import load_dotenv

load_dotenv()


def load_redis_conn():
    return redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT")),
        password=os.getenv("REDIS_PASSWORD"),
        db=int(os.getenv("REDIS_DB"))
    )


# 关闭连接
def close_redis_conn(conn):
    conn.close()

