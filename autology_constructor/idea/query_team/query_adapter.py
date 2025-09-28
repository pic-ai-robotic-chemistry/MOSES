from typing import Dict, Optional, Any, List, Literal
from .schemas import Query, QueryStatus

class QueryToStateAdapter:
    """将Query转换为QueryState的转换器"""
    def transform(self, query: Query) -> Dict:
        """将Query对象转换为QueryState字典"""
        return {
            "query": query.natural_query,
            "source_ontology": query.query_context.get("ontology"),
            "query_type": query.query_context.get("query_type", "unknown"),
            "query_strategy": None,
            "originating_team": query.originating_team,
            "originating_stage": query.query_context.get("originating_stage", "unknown"),
            "query_results": {},
            "normalized_query": None,
            "execution_plan": None,
            "status": "initialized",
            "stage": "initialized",
            "previous_stage": None,
            "messages": []
        }

class StateToQueryAdapter:
    """将QueryState转换回Query的转换器"""
    def transform(self, state: Dict, query: Query) -> None:
        """将QueryState的状态更新到Query对象"""
        # 优先使用formatted_results，没有则使用过滤过的tried_tool_calls
        if state.get("formatted_results"):
            query.result = state["formatted_results"]
        else:
            # 没有formatted_results时，返回过滤过的tried_tool_calls
            from .workflow_utils import filter_validated_tool_calls
            tried_tool_calls = state.get("tried_tool_calls", {})
            filtered_calls = filter_validated_tool_calls(tried_tool_calls)
            query.result = {"filtered_tool_calls": filtered_calls}
            
        if state["status"] == "error":
            query.status = QueryStatus.FAILED
            query.error = state.get("error", "Unknown error")
        else:
            query.status = QueryStatus.COMPLETED 