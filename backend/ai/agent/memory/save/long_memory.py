import chromadb
import os
from dotenv import load_dotenv
import uuid
"""
长期记忆存储
"""


class LongMemory:
    def __init__(self):
        load_dotenv()
        path = os.getenv("CHROMA_PATH")
        # 链接数据库
        client = chromadb.PersistentClient(path)
        # 创建集合
        self.collection = client.get_or_create_collection("long_memory")

    # 添加
    def save(self, user_id, query):
        id = f"memory_{user_id}+{uuid.uuid4()}"

        # 添加数据
        self.collection.add(
            ids=[id],
            documents=[query],
            metadatas=[
                {"user_id": user_id}
            ]
        )

    # 查询数据
    def query(self, user_id, question):
        # 查询数据库
        rs = self.collection.query(
            query_texts=[question],
            n_results=3,
            where={"user_id": user_id}
        )
        return rs["documents"][0]


if __name__ == "__main__":
    memory = LongMemory()
    rs = memory.query(1, "我喜欢什么")
    print(rs)
