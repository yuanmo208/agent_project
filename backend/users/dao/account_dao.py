from backend.utils.mysql_util import MySQLManage


# 定义查询数据库邮箱的函数
def query_mysql_email(email):
    # 加载数据库连接
    conn = MySQLManage.get_mysql_conn()
    # 获取游标对象
    cursor = conn.cursor()
    try:
        # 编写SQL查询语句
        sql = "SELECT * FROM users WHERE email = %s"
        # 执行SQL查询语句
        cursor.execute(sql, [email])
        # 获取查询结果
        result = cursor.fetchall()
        # 返回查询结果
        return result
    except Exception as e:
        print(f"查询邮箱失败:{e}")
    finally:
        # 关闭游标对象和返回数据库连接
        MySQLManage.close_mysql_conn(cursor, conn)


def insert_mysql_email(email, password):
    """

        查询操作不需要做事务管理
        增删改需要做事务管理
        操作成功---commit 提交事务；执行当前操作
        操作失败---rollback 回滚事务： 不执行当前操作

    """
    conn = MySQLManage.get_mysql_conn()
    cur = conn.cursor()
    try:
        sql = "UPDATE users SET password = %s WHERE email = %s;"
        cur.execute(sql, [password, email])
        conn.commit()
        print("修改密码成功")
        return True
    except Exception as e:
        print(f"修改密码失败:{e}")
        conn.rollback()
        return False
    finally:
        MySQLManage.close_mysql_conn(cur, conn)

if __name__ == '__main__':
    rs = query_mysql_email("1026473161@qq.com")
    print(rs)