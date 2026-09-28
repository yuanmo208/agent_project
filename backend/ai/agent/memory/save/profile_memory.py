import redis

"""
用户画像记忆存储
"""
class ProfileMemory:

    def __init__(self, user_id):
        self.redis = redis.StrictRedis(host="localhost", port=6379, db=0)
        self.key = f"profile:{user_id}"

    # 保存
    def save(self, hashkey, value):
        self.redis.hset(self.key, hashkey, value)

    # 查询
    def query(self):
        # 查询某个用户的用户画像
        rs = self.redis.hgetall(self.key)
        data = ""
        if rs:
            for hashkey,value in rs.items():
                data += f"{hashkey.decode()}:{self.redis.hget(self.key,hashkey).decode()}\n"
        return data
if __name__ =="__main__":
   p = ProfileMemory(1)
   p.save("name","张三")
   p.save("age",23)
   #查询
   p.query()





