from pydantic import BaseModel, Field


class ChatSchema(BaseModel):
    question: str = Field(..., description="用户问题")
    user_id: str = Field(..., description="用户ID")
    session_id: str = Field(..., description="会话ID")
