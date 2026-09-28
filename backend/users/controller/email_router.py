from fastapi import APIRouter
from app.users.service import email_log_service

# 创建子路由对象
email_router = APIRouter()


# 发送验证码
@email_router.get(
    # 请求路径
    path="/sendEmail",
    # 接口简短摘要
    summary="发送邮件"
)
def send_email(email: str):
    return email_log_service.send_email(email)


# 验证验证码
@email_router.get(
    # 请求路径
    path="/checkCode",
    # 接口简短摘要
    summary="验证邮件"
)
def check_code(email: str, code: str):
    return email_log_service.check_code(email, code)