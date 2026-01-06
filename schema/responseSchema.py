from pydantic import BaseModel,Field
from typing import Optional
class ResponseSchema(BaseModel):
    code: int = Field(description="响应编码,例如:200,404,500",default=200)
    msg: Optional[str] = Field(description="错误描述",default="")
    data: dict = Field(description="返回的数据",default={})
