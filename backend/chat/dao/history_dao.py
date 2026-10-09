from backend.utils.postgres_util import PostgresManage


def select_list_menu_dao(username):
    conn = PostgresManage.get_pg_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT history_id, title, to_char(create_time, 'YYYY-MM-DD HH24:MI:SS') "
            "FROM chat_history WHERE username=%s ORDER BY create_time DESC",
            (username,)
        )
        result = cursor.fetchall()
        return result
    except Exception as e:
        print("查询失败：", e)
    finally:
        PostgresManage.close_pg_conn(cursor, conn)


def select_history_dao(historyId):
    conn = PostgresManage.get_pg_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT session_id FROM chat_history WHERE history_id=%s",
            (historyId,)
        )
        row = cursor.fetchone()
        sid = row[0] if row else ""
        cursor.execute(
            "SELECT role, content FROM chat_message WHERE history_id=%s ORDER BY msg_id ASC",
            (historyId,)
        )
        # 后端存 user/ai，前端期望 user/assistant
        msgs = [
            {"role": ("assistant" if r[0] == "ai" else r[0]), "content": r[1]}
            for r in cursor.fetchall()
        ]
        return msgs, sid
    except Exception as e:
        print("查询失败：", e)
    finally:
        PostgresManage.close_pg_conn(cursor, conn)


def query_history_dao(username, keyword):
    conn = PostgresManage.get_pg_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT history_id, title, to_char(create_time, 'YYYY-MM-DD HH24:MI:SS') "
            "FROM chat_history WHERE username=%s AND title LIKE %s ORDER BY create_time DESC",
            (username, f"%{keyword}%")
        )
        result = cursor.fetchall()
        return result
    except Exception as e:
        print("查询失败：", e)
    finally:
        PostgresManage.close_pg_conn(cursor, conn)


def delete_history_dao(historyId: int, username: str):
    conn = PostgresManage.get_pg_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM chat_message WHERE history_id=%s", (historyId,))
        cursor.execute("DELETE FROM chat_history WHERE history_id=%s", (historyId,))
        conn.commit()
        return {
            "code": 200,
            "message": "删除成功"
        }
    except Exception as e:
        print("删除失败：", e)
        conn.rollback()
        return {
            "code": 500,
            "message": "删除失败"
        }
    finally:
        PostgresManage.close_pg_conn(cursor, conn)
