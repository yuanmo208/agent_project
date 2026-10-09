from backend.utils.postgres_util import PostgresManage


# 保存对话标题
def insert_postgres_title(username, session_id, title):
    conn = PostgresManage.get_pg_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO chat_history(username, session_id, title) VALUES(%s,%s,%s) RETURNING history_id",
            (username, session_id, title)
        )
        hid = cursor.fetchone()[0]
        conn.commit()
        return hid
    except Exception as e:
        print("写入失败：", e)
        conn.rollback()
    finally:
        PostgresManage.close_pg_conn(cursor, conn)


# 更新session_id
def update_postgres_sid(session_id, hid):
    conn = PostgresManage.get_pg_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE chat_history SET session_id = %s WHERE history_id = %s",
            (session_id, hid)
        )
        conn.commit()
    except Exception as e:
        print("更新失败：", e)
        conn.rollback()
    finally:
        PostgresManage.close_pg_conn(cursor, conn)


# 保存对话信息
def insert_postgres_message(hid, role, question):
    conn = PostgresManage.get_pg_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO chat_message(history_id, role, content) VALUES(%s,%s,%s)",
            (hid, role, question)
        )
        conn.commit()
    except Exception as e:
        print("写入失败：", e)
        conn.rollback()
    finally:
        PostgresManage.close_pg_conn(cursor, conn)
