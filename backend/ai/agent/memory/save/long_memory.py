import chromadb
import os
import asyncio
import uuid
from dotenv import load_dotenv
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
"""
长期记忆存储
"""


class LongMemory:
    def __init__(self):
        load_dotenv()
        path = os.getenv("CHROMA_PATH")
        # 链接数据库
        client = chromadb.PersistentClient(path)
        # 使用本地 MiniLM-L12-v2 向量化模型，避免 chroma 默认在线下载 onnx 模型
        embedding_function = SentenceTransformerEmbeddingFunction(
            model_name=r"E:\workspace\models\MiniLM-L12-v2"
        )
        # 创建集合（若之前用默认 embedding 建过同名集合会不匹配，删除重建）
        try:
            self.collection = client.get_or_create_collection(
                "long_memory",
                embedding_function=embedding_function
            )
        except Exception:
            try:
                client.delete_collection("long_memory")
            except Exception:
                pass
            self.collection = client.get_or_create_collection(
                "long_memory",
                embedding_function=embedding_function
            )

    # 添加
    async def save(self, user_id, query):
        id = f"memory_{user_id}+{uuid.uuid4()}"

        # 添加数据（chromadb 为同步阻塞接口，放到线程中执行）
        await asyncio.to_thread(
            self.collection.add,
            ids=[id],
            documents=[query],
            metadatas=[
                {"user_id": user_id}
            ]
        )

    # 查询数据
    async def query(self, user_id, question):
        # 查询数据库
        rs = await asyncio.to_thread(
            self.collection.query,
            query_texts=[question],
            n_results=3,
            where={"user_id": user_id}
        )
        return rs["documents"][0]


if __name__ == "__main__":
    async def _test():
        memory = LongMemory()
        rs = await memory.query(1, "我喜欢什么")
        print(rs)

    asyncio.run(_test())
