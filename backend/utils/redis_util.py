import os
import redis
from dotenv import load_dotenv

load_dotenv()

# 全局连接池，应用启动时创建一次
_pool = redis.ConnectionPool(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    password=os.getenv("REDIS_PASSWORD"),
    db=int(os.getenv("REDIS_DB")),
    max_connections=20,
    decode_responses=True,       # 自动把 bytes 转成 str
    socket_timeout=5,
    socket_connect_timeout=5,
)


def get_redis_conn():
    return redis.Redis(connection_pool=_pool)
