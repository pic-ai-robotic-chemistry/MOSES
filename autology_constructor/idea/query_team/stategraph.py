"""
查询团队状态图定义

此模块包含LangGraph QueryState的权威定义，用于查询工作流状态管理。
"""

from typing import Dict, List, Literal, Optional, Any
from typing_extensions import Annotated, TypedDict
from langgraph.graph.message import AnyMessage, add_messages
from .schemas import NormalizedQuery, ToolPlan, ValidationReport, ToolCallHint, GlobalCommunityAssessment
from config.settings import OntologySettings


class QueryState(TypedDict):
    """查询团队状态 - LangGraph StateGraph权威定义"""
    # Input
    query: str  # 自然语言查询
    source_ontology: OntologySettings  # 使用OntologySettings类型，而不是Any
    query_type: str  # 查询类型
    query_strategy: Optional[Literal["tool_sequence", "SPARQL"]]  # 查询策略
    originating_team: str  # 发起查询的团队
    originating_stage: str  # 发起查询的阶段
    available_classes: List[str]  # Add available classes from cache
    available_data_properties: List[str]  
    available_object_properties: List[str]
    refined_classes: Optional[List[str]]  # Refined candidate classes for optimization
    
    # Tools
    ontology_tools: Optional[Any]  # OntologyTools实例，存储在state中
    
    # Query Management
    query_results: Dict  # 查询结果
    normalized_query: Optional[NormalizedQuery]  # 标准化的查询结构
    execution_plan: Optional[ToolPlan]  # 执行计划
    validation_report: Optional[ValidationReport]  # Added field for report
    sparql_query: Optional[str]  # Generated SPARQL query
    status: str  # 状态
    stage: str  # 当前阶段
    previous_stage: Optional[str]  # 上一阶段
    error: Optional[str]  # Add error field for better tracking
    
    # Retry and Feedback
    retry_count: Optional[int]  # 重试计数
    force_strategy: Optional[str]  # 强制使用不同的策略
    refiner_hints: Optional[List[ToolCallHint]]  # NEW: QueryRefiner生成的hints，用于重试指导
    hypothetical_document: Optional[Dict]  # 假设性文档（由化学专家生成）
    validation_history: Optional[List]  # 验证报告历史
    global_assessment: Optional[GlobalCommunityAssessment]  # 全局社区评估
    formatted_results: Optional[Dict]  # 格式化后的结果
    iteration_history: Optional[List[Dict]] # ADD: To store history of each iteration
    
    # NEW: 迭代记忆系统
    tried_tool_calls: Optional[Dict[str, Dict]]  # 记录尝试过的工具调用 {signature: {tool, params, result, timestamp}}
    
    # System
    messages: Annotated[list[AnyMessage], add_messages]