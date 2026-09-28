from pydantic import BaseModel, Field


class MySQLSchema(BaseModel):
    sql: str = Field(description="sql语句")

