from app.ai.tools.mysql_tool import mysql_tool

import os
import random
import smtplib
from email.mime.text import MIMEText
from app.utils import redis_util
from dotenv import load_dotenv
load_dotenv()


# 发送验证码的函数
def send_email(email):
    try:
        # 查询数据库
        sql = f"SELECT * FROM users WHERE email = '{email}'"
        result = mysql_tool.invoke({"sql": sql})
        # 取出邮箱号对应用户名
        username = result[0][1]
        print(username)
    except Exception as e:
        return {
            "code": 500,
            "msg": e,
            "data": False,
        }

    # 生成验证码
    code = ""
    for i in range(4):
        code += str(random.randint(0, 9))
    # 配置发送信息
    sender = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_EMAIL_PASSWORD")
    # 邮件主题
    subject = "验证码"
    # 邮件内容
    content = f"尊敬的用户 {username}，您的验证码是 {code}，请在1分钟内使用。"
    # 创建邮箱对象
    message = MIMEText(content, 'plain', 'utf-8')
    # 配置发件人、收件人和主题
    message['From'] = sender
    message['To'] = email
    message['Subject'] = subject
    # 发送邮件
    try:
        # 构建发送邮件对象
        smtp = smtplib.SMTP(
            host=os.getenv("SMTP_HOST"),
            port=int(os.getenv("SMTP_PORT"))
        )
        # 开启邮件发送服务 TLS
        smtp.starttls()
        # 验证授权码是否正确
        smtp.login(sender, sender_password)
        # 发送邮件 -- sendmail 发送邮件的方法：发送方，接收方，邮件对象
        smtp.sendmail(sender, email, message.as_string())
        # 发送成功退出
        smtp.quit()
        # 加载redis对象
        r = redis_util.load_redis_conn()
        print(1)
        # 把验证码存入redis定时消除
        r.set(email, code, ex=60)
        # 关闭连接
        redis_util.close_redis_conn(r)
        print(2)
        return {
            "code": 200,
            "msg": "验证码已发送",
            "data": username,
        }
    except Exception as e:
        return {
            "code": 500,
            "msg": e,
            "data": False,
        }


# 验证验证码函数
def check_code(email, code):
    # 从redis中获取验证码
    r = redis_util.load_redis_conn()
    # 判断验证码是否存在
    if r.get(email) is None:
        return {
            "code": 501,
            "msg": "验证码已过期",
            "data": False,
        }
    else:
        redis_code = str(r.get(email), 'utf-8')
        print(redis_code)
        # 关闭连接
        redis_util.close_redis_conn(r)
        # 验证验证码
        if redis_code == code:
            return {
                "code": 200,
                "msg": "验证码正确",
                "data": True,
            }
        else:
            return {
                "code": 500,
                "msg": "验证码错误",
                "data": False,
            }
