from typing import TypedDict,Literal
from pydantic import BaseModel

class TokenSchema(BaseModel):
    prompt_tokens: int = 0 #  提示词总的tokens
    complete_tokens: int = 0 #  大模型响应的tokens
    total_tokens: int = 0 #  总的token数，prompt_tokens + complete_tokens  
    prompt_cache_hit_tokens: int = 0 #  提示词缓存命中的tokens
    prompt_cache_miss_tokens: int = 0 #  提示词缓存未命中的tokens
    type: Literal["token"] = "token"
