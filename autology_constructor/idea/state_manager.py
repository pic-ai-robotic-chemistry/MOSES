from typing import Dict, List, TypedDict, Annotated, Optional, Any, Generic, TypeVar
from langgraph.graph.message import AnyMessage, add_messages

# 导入LangGraph相关组件
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

# 通用状态处理框架
T = TypeVar('T')  # 状态类型
R = TypeVar('R')  # 结果类型

class StateHandler(Generic[T, R]):
    """状态处理器基类，泛型设计支持不同状态类型"""
    
    def handle(self, state: T, result: R) -> Dict:
        """处理结果，更新状态"""
        if self._validate_result(result):
            return self._handle_success(state, result)
        else:
            return self._handle_error(state, result)
    
    def _validate_result(self, result: R) -> bool:
        """验证结果是否有效，子类可覆盖"""
        return True
    
    def _handle_success(self, state: T, result: R) -> Dict:
        """处理成功结果，子类必须实现"""
        raise NotImplementedError
    
    def _handle_error(self, state: T, result: R) -> Dict:
        """处理错误结果，子类必须实现"""
        raise NotImplementedError

class WorkflowResultHandler(StateHandler):
    """工作流状态处理器基类"""
    
    def __init__(self, workflow_state: Dict):
        self.state = workflow_state
    
    def _is_success(self, result: Dict) -> bool:
        """检查结果是否成功"""
        return result.get("status") == "success"

class QueryResultHandler(WorkflowResultHandler):
    """查询结果处理器"""
    
    def handle(self, query_state: Dict) -> Dict:
        """处理查询结果，返回工作流状态更新"""
        if self._is_success(query_state):
            return self._handle_success(self.state, query_state)
        else:
            return self._handle_error(self.state, query_state)
    
    def _handle_success(self, state: Dict, query_state: Dict) -> Dict:
        """处理成功的查询结果"""
        updates = {
            "status": "success",
            "stage": state["previous_stage"],
            "previous_stage": state.get("stage"),
            "messages": []
        }
        
        # 更新本体分析结果
        results = query_state.get("query_results", {})
        if "ontology_analysis" in results:
            updates["shared_context"] = updates.get("shared_context", {})
            updates["shared_context"]["ontology_analysis"] = results["ontology_analysis"]
            updates["messages"].append("Successfully updated ontology analysis")
        
        # 更新查询结果
        updates["shared_context"] = updates.get("shared_context", {})
        updates["shared_context"]["query_results"] = results
        updates["messages"].append("Query completed successfully")
        
        # 更新验证信息
        if "validation" in query_state:
            updates["shared_context"]["validation"] = query_state["validation"]
        
        return updates
    
    def _handle_error(self, state: Dict, query_state: Dict) -> Dict:
        """处理失败的查询结果"""
        error_message = query_state.get("error", "Unknown error in query")
        validation = query_state.get("validation", {})
        
        # 提取验证详情中的错误信息
        if validation and "details" in validation:
            failed_rules = [r for r in validation["details"] if not r.get("valid", False)]
            if failed_rules:
                error_messages = [f"{r['dimension']}: {r['message']}" for r in failed_rules]
                error_message = ", ".join(error_messages)
        
        return {
            "status": "error",
            "stage": "error",
            "previous_stage": state.get("stage"),
            "error": error_message,
            "messages": [f"Query failed: {error_message}"]
        }

class DreamerResultHandler(WorkflowResultHandler):
    """Dreamer结果处理器"""
    
    def _handle_success(self, state: Dict, dream_state: Dict) -> Dict:
        """处理成功的梦想结果"""
        return {
            "stage": "critiquing",
            "previous_stage": state.get("stage"),
            "status": "success",
            "shared_context": {
                "research_ideas": dream_state.get("research_ideas", []),
                "gap_analysis": dream_state.get("gap_analysis", {})
            },
            "messages": dream_state.get("messages", ["Dream phase completed"]) 
        }
    
    def _handle_error(self, state: Dict, dream_state: Dict) -> Dict:
        """处理失败的梦想结果"""
        return {
            "status": "error",
            "stage": "error",
            "previous_stage": state.get("stage"),
            "error": dream_state.get("error", "Unknown error in dreamer"),
            "messages": [f"Dreamer failed: {dream_state.get('error')}"]
        }

class CriticResultHandler(WorkflowResultHandler):
    """Critic结果处理器"""
    
    def _handle_success(self, state: Dict, critic_state: Dict) -> Dict:
        """处理成功的批评结果"""
        return {
            "stage": "dreaming" if critic_state.get("needs_improvement") else "end",
            "previous_stage": state.get("stage"),
            "status": "success",
            "shared_context": {
                "evaluations": critic_state.get("evaluations", [])
            },
            "needs_improvement": critic_state.get("needs_improvement", False),
            "messages": critic_state.get("messages", [])
        }
    
    def _handle_error(self, state: Dict, critic_state: Dict) -> Dict:
        """处理失败的批评结果"""
        return {
            "status": "error",
            "stage": "error",
            "previous_stage": state.get("stage"),
            "error": critic_state.get("error", "Unknown error in critic"),
            "messages": [f"Critic failed: {critic_state.get('error')}"]
        }

class DreamerState(TypedDict):
    """Dreamer团队状态"""
    # 输入
    ontology: Any  # 主要本体
    additional_ontologies: Optional[List[Any]]  # 用于跨领域分析的其他本体
    
    # 分析
    analysis_type: str  # "single_domain" 或 "cross_domain"
    domain_analysis: Optional[Dict]  # 领域结构分析结果
    gap_analysis: Dict  # 研究空白分析
    research_ideas: List[Dict]  # 生成的研究创意
    
    # 评价与改进
    critic_feedback: Optional[Dict]  # 来自Critic Team的反馈
    idea_versions: Optional[List[Dict]]  # 记录创意的不同版本
    
    # 工作流状态管理
    stage: str  # 当前阶段
    previous_stage: Optional[str]  # 上一阶段
    status: str  # 状态：initialized, processing, waiting_for_critic, error, completed
    
    # 系统
    messages: Annotated[List[AnyMessage], add_messages]  # 系统消息


class StateManager:
    def __init__(self):
        """初始化Dreamer团队状态管理器"""
        self.state: DreamerState = {
            "ontology": None,
            "additional_ontologies": None,
            "analysis_type": "single_domain",
            "domain_analysis": None,
            "gap_analysis": {},
            "research_ideas": [],
            "critic_feedback": None,
            "idea_versions": [],
            "stage": "initialized",
            "previous_stage": None,
            "status": "initialized",
            "messages": []
        }
        
    def update_state(self, updates: Dict) -> None:
        """更新状态"""
        self.state.update(updates)
        
    def add_message(self, message: Dict) -> None:
        """添加消息"""
        self.state["messages"].append(message)

def create_state_manager() -> StateManager:
    """创建并返回一个StateManager实例"""
    return StateManager()

# 工厂函数，便于创建处理器
def create_result_handler(handler_type: str, workflow_state: Dict) -> WorkflowResultHandler:
    """创建结果处理器
    
    Args:
        handler_type: 处理器类型，可选值: "query", "dreamer", "critic"
        workflow_state: 工作流状态
        
    Returns:
        WorkflowResultHandler: 对应类型的结果处理器实例
    """
    handlers = {
        "query": QueryResultHandler,
        "dreamer": DreamerResultHandler,
        "critic": CriticResultHandler
    }
    
    handler_class = handlers.get(handler_type)
    if not handler_class:
        raise ValueError(f"Unknown handler type: {handler_type}")
    
    return handler_class(workflow_state)


