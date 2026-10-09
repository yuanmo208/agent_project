import contextlib
import json

from backend.ai.agent.multi_agent.state.exam_state import ExamState
from backend.ai.agent.multi_agent.node.intent_node import intent_node
from backend.ai.agent.multi_agent.node.question_node import question_node
from backend.ai.agent.multi_agent.node.manager_node import manager_node
from backend.ai.agent.multi_agent.node.answer_node import answer_node
from backend.ai.agent.multi_agent.node.evaluate_node import evaluate_node
from backend.ai.agent.multi_agent.node.chat_node import chat_node
from langgraph.graph import StateGraph, START
from langchain_core.messages import HumanMessage
import asyncio
import uuid
import time
from backend.ai.agent.memory.manager.session_mananger import SessionManager
from backend.ai.agent.memory.manager.memory_manager import MemoryManager
from backend.utils import redis_util


"""
模拟面试智能体，有并发场景
"""


class ExamGraphAgent:

    def __init__(self, checkpoint):
        self.memory = checkpoint
        # 获取redis实例
        self.redis = redis_util.get_redis_conn()
        self.agent = self.get_agent()

    # 构建图
    def get_agent(self):
        graph = StateGraph(ExamState)
        # 添加节点
        graph.add_node("intent", intent_node)
        graph.add_node("question", question_node)
        graph.add_node("manager", manager_node)
        graph.add_node("answer", answer_node)
        graph.add_node("evaluate", evaluate_node)
        graph.add_node("chat", chat_node)

        # 画边
        graph.add_edge(START, "manager")
        graph.add_edge("intent", "manager")
        graph.add_edge("question", "manager")
        graph.add_edge("answer", "manager")
        graph.add_edge("evaluate", "manager")
        graph.add_edge("chat", "manager")

        # 编译
        self.agent = graph.compile(checkpointer=self.memory)
        return self.agent

    # 会话创建
    async def create_session(self, user_id) -> str:
        print("创建会话")
        # 生成一个键名，采用uuid，保持唯一性
        key = f"session:"+uuid.uuid4().hex
        # 兜底，判断redis是否可用
        if self.redis:
            # 定义要存的数据，存入user_id 和 创建时间
            data = {"user_id": user_id, "create_time": time.time()}
            # 存入,过期时间是1天（同步 redis，放到线程中执行，避免阻塞事件循环）
            await asyncio.to_thread(self.redis.set, key, json.dumps(data), ex=60 * 60 * 24)
        return key
    """
    检查会话： 会话id 是否创建 和 会话是否归属该用户
    """
    async def check_session(self, user_id, session_id):
        print(f"检查会话,会id:{session_id}")
        if session_id:
            # 获取会话数据（同步 redis，放到线程中执行）
            data = await asyncio.to_thread(self.redis.get, session_id)
            print(f"是否有会话:{data}")
            # 检查会话是否是该用户创建的或者是伪造的
            if not data:
                print("会话不存在")
                return False, "会话不存在"
            # 检查会话归属
            rs = json.loads(data)
            if rs["user_id"] != user_id:
                print("会话不属于该用户")
                return False, "会话不属于该用户"
            print("会话存在且归属该用户")
            return True, "会话存在且归属该用户"
        return False, "会话id为空"

    # 对话
    async def chat(self, question, user_id, session_id):
        print(f"进入聊天:用户问题：{question},用户ID:{user_id},会话ID:{session_id}")

        # 1. 校验会话存在 + 归属匹配
        ok, reason = await self.check_session(user_id, session_id)
        print(f"会话检查结果:{ok},{reason}")
        # 如果会话不存在或不属于该用户，直接返回原因
        if not ok:
            yield reason
            return
        # 记录AI答案
        ai_answer = ""
        session_manager = None
        # -----------------------添加记忆 + 流式对话-------------------------
        try:
            # 创建会话管理器
            session_manager = SessionManager(session_id, user_id)
            # 添加窗口记忆
            await session_manager.save("user", question)
            # 构建记忆的提示词
            memory_prompt = await session_manager.build_prompt(user_id, question)

            # 构建用户问题
            user_msg = {"messages": [memory_prompt, HumanMessage(content=question)]}
            # 配置检测点
            config = {"configurable": {"thread_id": session_id}}

            async with self._session_lock(session_id):
                print(f"开始处理会话:{session_id}")
                # 采用异步流式（只订阅 custom 流，避免 messages 流透传内层 agent 的 LLM chunk 导致重复输出）
                async for c, m in self.agent.astream(user_msg, config, stream_mode=["custom"]):
                    # 累加
                    ai_answer += m
                    yield m
            print(f"AI回复:{ai_answer}")
        except Exception as e:
            import traceback
            print(f"错误:{e}")
            traceback.print_exc()
            yield str(e)
        # ---------------------更新记忆---------------------------
        # 添加AI回复的记忆 + 更新记忆（失败不影响已流式输出的回复）
        if session_manager is not None:
            try:
                await session_manager.save("ai", ai_answer)
                memory_manger = MemoryManager(session_manager)
                await memory_manger.update(user_id, question)
            except Exception as e:
                import traceback
                print(f"更新记忆错误:{e}")
                traceback.print_exc()
        # ------------------------------------------------

    """
     会话锁：同一 session 同一时刻只允许一个请求进入。
    """
    @contextlib.asynccontextmanager
    async def _session_lock(self, session_id: str):

        key = f"lock:session:{session_id}"
        # 生成随机 token
        token = uuid.uuid4().hex
        # 尝试获取锁， px=60 * 1000 表示锁的过期时间，单位毫秒
        # nx=True 是 Redis SET 命令的一个选项，意思是：只有当这个 key 不存在时，才设置成功
        # 同步 redis，放到线程中执行，避免阻塞事件循环
        ok = await asyncio.to_thread(self.redis.set, key, token, nx=True, px=5*60 * 1000)
        # 获取锁成功，执行 yield 语句块中的代码
        if not ok:
            raise RuntimeError("会话忙，请稍后再试")

        try:
            # yield 的位置，就是"锁内要执行的所有代码"插入的地方。
            yield
        finally:
            # 兜底处理，确保锁一定能释放
            # 释放锁，使用 Lua 脚本确保原子性，防止误删，误释放
            lua = """
            if redis.call('get', KEYS[1]) == ARGV[1] then
                return redis.call('del', KEYS[1])
            else
                return 0
            end
            """
            try:
                # 执行 Lua 脚本，释放锁（同步 redis，放到线程中执行）
                await asyncio.to_thread(self.redis.eval, lua, 1, key, token)
            except Exception:
                pass

    # 画图
    def draw(self):
        data = self.agent.get_graph().draw_mermaid_png()
        with open("考试图.png", "wb") as f:
            f.write(data)


if __name__ == "__main__":
    # exam_graph = ExamGraph()
    # exam_graph.draw()
    q1 = "给我3道java题目"
    q2 = "给我几道面试题"

    async def test():
        agent = ExamGraphAgent()
        async for c in agent.chat(q1, "1", "001"):
            print(c, end="")
    asyncio.run(test())
