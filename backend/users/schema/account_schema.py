from pydantic import BaseModel, Field


class AccountSchema(BaseModel):
    email: str = Field(..., description="邮箱")
    code: str = Field(..., description="验证码")
    password: str = Field(..., description="密码")
