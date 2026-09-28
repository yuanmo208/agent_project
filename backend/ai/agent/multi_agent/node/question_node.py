from backend.ai.agent.multi_agent.state.exam_state import ExamState
from backend.ai.tools.mysql_tool import mysql_tool
import ast
from langchain_core.messages import AIMessage
"""
出题节点，随机抽取一道未出过的题目：
"""


def question_node(state: ExamState):
    print("1")
    # 课程名称
    course = state["course"]
    # 题目数量
    num = state["total"]
    # 查询题目列表
    question_list = state.get("questions", [])
    print("question_list", question_list)
    # 获取当前题目号
    current = state.get("current", 0)+1
    print("2")
    # 判断题目列表是否有数据
    if len(question_list) > 0:

        rs = ",".join([str(i["id"]) for i in question_list])

        sql = f"select * from question_bank where question_subject='{course}' and question_id not in ({rs})  ORDER BY RAND() desc LIMIT 1"

    else:

        sql = f"select * from question_bank where question_subject='{course}' ORDER BY RAND() desc LIMIT 1"
    print("3")
    # 调用mysql_tool
    data = mysql_tool.invoke({"sql": sql})
    # print("rs", rs)
    print("4")
    # 把rs字符粗转成元组
    # data = ast.literal_eval(rs)
    print("5")

    # 添加到题库列表
    question_list.append(
        {"id": data[0][0], "question": data[0][1], "answer": data[0][2]}
    )
    print("6")

    # ai回复消息
    ai_msg = f"\n第{current}题:{data[0][1]}\n"
    print("question")

    return {
        "messages": [AIMessage(content=ai_msg)],
        "questions": question_list,  # 题目列表
        "total": num,  # 题目数量
        "current": current,
        "question_id": data[0][0],  # 题目编号
        "exam_step": "question"
    }
