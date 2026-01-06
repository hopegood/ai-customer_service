from dataclasses import dataclass
from typing import Literal, TypedDict
from typing_extensions import Doc

@dataclass
class InputSchema:
    """前端传递的输入模式
    Args:
        content: 表示用户提的问题
        user_id: 表示用户id，这个用户应该是已经登录系统
        type: 前端传递的数据是文本格式，默认是文本格式
    """
    content: str
    user_id: str
    type: Literal["text"] = "text"
  

