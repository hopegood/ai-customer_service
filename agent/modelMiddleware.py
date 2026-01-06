from typing import Any
from langchain.agents import AgentState
from langchain.agents.middleware import AgentMiddleware
from langgraph.runtime import Runtime
from ai_customer_service.exception.stopAgentError import StopAgentError
from ai_customer_service.schema.customContext import CustomContext
from langchain.messages import AIMessage

_MAX_MODEL_CALL_COUNT =3
_MAX_MODEL_TOKEN_USAGE = 10000

class _ModelState(AgentState):
   model_call_count: int

class ModelMiddleware(AgentMiddleware):
    state_schema = _ModelState
    def before_model(self, state: _ModelState, runtime: Runtime[CustomContext]) -> dict[str, Any] | None:
        '''
        如果模型调用次数超过3次或者token已经超过1w,则需要提醒用户要关闭当前session，重新启动一个会话窗口
        '''
        context = runtime.context
        user_id = context["user_id"]
        store = runtime.store
        count = store.get(("usage_metdata",f"{user_id}"),"model_call_count")
        token_usage = store.get(("usage_metdata",f"{user_id}"),"model_token_usage")
        if  count is not None and count.value > _MAX_MODEL_CALL_COUNT:
           raise StopAgentError(f"模型调用次数超过指定次数,当前={count.value}")
        if token_usage is not None and token_usage.value > _MAX_MODEL_TOKEN_USAGE:
           raise StopAgentError(f"模型使用量超过指定的用量,当前={token_usage.value}")
    
    def after_model(self, state: _ModelState, runtime: Runtime[CustomContext]) -> dict[str, Any] | None:
        context = runtime.context
        user_id = context["user_id"]
        store = runtime.store
        count = store.get(("usage_metdata",f"{user_id}"),"model_call_count")
        token_usage = store.get(("usage_metdata",f"{user_id}"),"model_token_usage")
        last_ai_message = state["messages"][-1::][0]
        usage_metadata = last_ai_message.usage_metadata
        this_token_usage = usage_metadata["total_tokens"] - usage_metadata["input_token_details"]["cache_read"]
        store.put(("usage_metdata",f"{user_id}"),"model_call_count",1 if count is None else count.value + 1)
        store.put(("usage_metdata",f"{user_id}"),"model_token_usage",this_token_usage if token_usage is None else token_usage.value + this_token_usage)
        return None
      