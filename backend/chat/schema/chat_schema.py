from pydantic import BaseModel, Field


class ChatSchema(BaseModel):
    question: str = Field(..., description="用户问题")
    user_id: str = Field(..., description="用户ID")
    session_id: str = Field(..., description="会话ID")


class CreateSessionSchema(BaseModel):
    user_id: str = Field(..., description="用户ID")


class SaveConversationSchema(BaseModel):
    question: str = Field(..., description="用户问题")
    username: str = Field(..., description="用户名")
    parentId: int = Field(0, description="父对话ID，0表示新建对话")
    answer: str = Field(..., description="AI回答")
    sessionId: str = Field("", description="后端会话ID")
