from fastapi import APIRouter

from backend.users.service import email_log_service, account_log_service
from backend.users.schema.account_schema import AccountSchema
# 创建子路由对象
account_router = APIRouter()


@account_router.get(
    path="/register",
    summary="发送验证码"
)
def send_code(email: str):
    return email_log_service.send_email(email)


@account_router.post(
    path="/checkRegister",
    summary="注册用户"
)
def check_register(accountschema: AccountSchema):
    return account_log_service.check_register(accountschema)


@account_router.get(
    path="/login",
    summary="用户登录"
)
def account_login(email: str, password: str):
    return account_log_service.password_login(email, password)


