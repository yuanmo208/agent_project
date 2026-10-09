from backend.ai.agent.multi_agent.state.exam_state import ExamState
from backend.ai.tools.mysql_tool import mysql_tool
import ast
from langchain_core.messages import AIMessage
from langgraph.config import get_stream_writer
"""
出题节点，每次随机抽取一道未出过的题目：
"""

def question_node(state: ExamState):
    # 课程名称
    course = state["course"]
    # 题目数量
    num = state["total"]
    # 已出题目列表
    question_list = state.get("questions", [])
    # 当前题号（从1开始）
    current = state.get("current", 0) + 1

    # 查询未出过的题目
    if len(question_list) > 0:
        rs = ",".join([str(i["id"]) for i in question_list])
        sql = f"select * from question_bank where question_subject='{course}' and question_id not in ({rs})  ORDER BY RAND() desc LIMIT 1"
    else:
        sql = f"select * from question_bank where question_subject='{course}' ORDER BY RAND() desc LIMIT 1"

    # 调用mysql_tool
    data = mysql_tool.invoke({"sql": sql})
    print(f"mysql返回data={data}")

    # mysql_tool 返回类型注解为 -> str，LangChain 会将 tuple 转为字符串，需要解析
    if isinstance(data, str):
        try:
            data = ast.literal_eval(data)
        except Exception:
            raise RuntimeError(f"mysql 返回数据解析失败: {data}")

    if not isinstance(data, (list, tuple)) or len(data) == 0:
        raise RuntimeError(f"mysql 查询失败或无数据: {data}")

    # 取第一道题
    row = data[0]
    question_list.append({"id": row[0], "question": row[1], "answer": row[2]})

    ai_msg = f"\n第{current}题:{row[1]}\n"
    # 通过 custom 流输出题目内容（前端可见，exam 只订阅 custom 流不会重复）
    get_stream_writer()(ai_msg)

    return {
        "messages": [AIMessage(content=ai_msg)],  # 保留 AIMessage，让 manager 能判断"题目已出等待用户回答"
        "questions": question_list,  # 题目列表
        "total": num,  # 题目数量
        "current": current,  # 当前题号
        "question_id": row[0],  # 题目编号
        "exam_step": "question"
    }
