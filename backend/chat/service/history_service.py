from backend.chat.dao.history_dao import select_list_menu_dao, select_history_dao, query_history_dao, delete_history_dao


# 获取历史记录菜单
def history_list_menu_service(username):
    result = select_list_menu_dao(username)
    return [{"historyId": r[0], "title": r[1], "time": r[2]} for r in result]


# 获取单次对话历史记录
def select_history_service(historyId):
    msgs, sid = select_history_dao(historyId)
    return msgs, sid


# 模糊查询历史记录菜单
def query_history_service(username, keyword):
    result = query_history_dao(username, keyword)
    return [{"historyId": r[0], "title": r[1], "time": r[2]} for r in result]


# 删除历史记录
def delete_history_service(historyId: int, username: str):
    return delete_history_dao(historyId, username)

