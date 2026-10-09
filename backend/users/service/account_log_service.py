from backend.users.service import email_log_service
from backend.users.dao import account_dao


def check_register(accountschema):
    # 取出邮箱号和验证码
    email = accountschema.email
    code = accountschema.code
    password = accountschema.password
    response = email_log_service.check_code(email, code)
    if response['code'] == 500:
        return {
            "code": 500,
            "msg": "验证码错误",
            "data": False,
        }
    elif response['code'] == 501:
        return {
            "code": 501,
            "msg": "验证码已过期",
            "data": False,
        }
    # 获取数据库中邮箱号所对应数据
    else:
        if account_dao.insert_mysql_email(email, password):
            return {
                "code": 200,
                "msg": "注册成功",
                "data": True,
            }
        else:
            return {
                "code": 500,
                "msg": "注册失败",
                "data": False,
            }


# 密码登录函数
def password_login(email, password):
    # 获取数据库信息
    result = account_dao.query_mysql_email(email)
    try:
        username = result[0][1]
        if result[0][4] == password:
            return {
                "code": 200,
                "msg": "登录成功",
                "data": username,
            }
        else:
            return {
                "code": 500,
                "msg": "密码错误",
                "data": False,
            }
    except Exception as e:
        return {
            "code": 500,
            "msg": "用户未注册",
            "data": False,
        }

