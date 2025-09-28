from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from enum import Enum
import uuid
from datetime import datetime

# NEW: 验证结果分类枚举
class ValidationClassification(str, Enum):
    """验证结果分类标签"""
    SUFFICIENT = "sufficient"                    # 结果充分
    INSUFFICIENT_PROPERTIES = "insufficient_properties"  # 缺乏属性信息
    INSUFFICIENT_CONNECTIONS = "insufficient_connections"  # 缺失联系信息
    INSUFFICIENT = "insufficient"               # 全面信息不足  
    NO_RESULTS = "no_results"                   # 无结果
    ERROR = "error"                             # 执行错误

class NormalizedQuery(BaseModel):
    """Represents the structured understanding of a natural language query."""
    intent: str = Field(description="The main goal or action of the query, e.g., 'find information', 'compare entities', 'get property'.")
    relevant_entities: List[str] = Field(default_factory=list, description="The primary entities or concepts the query is about. The names in the list must be present in the available classes.")
    relevant_properties: List[str] = Field(default_factory=list, description="List of specific property names mentioned or relevant to the query.")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Filtering conditions to apply, where keys are property names and values are the filter criteria.")
    query_type_suggestion: Optional[str] = Field(default=None, description="A suggested type for the query based on the parsing, e.g., 'fact-finding', 'comparison', 'definition'.")

    @field_validator('relevant_properties', 'relevant_entities', mode='before')
    @classmethod
    def convert_none_to_empty_list(cls, value):
        if value is None:
            return []
        return value

class NormalizedQueryBody(BaseModel):
    """Represents the main body of a structured query, excluding properties."""
    intent: str = Field(description="The main goal or action of the query, e.g., 'find information', 'compare entities', 'get property'.")
    relevant_entities: List[str] = Field(default_factory=list, description="The primary entities or concepts the query is about. The names in the list must be present in the available classes.")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Filtering conditions to apply, where keys are property names and values are the filter criteria.")
    query_type_suggestion: Optional[str] = Field(default=None, description="A suggested type for the query based on the parsing, e.g., 'fact-finding', 'comparison', 'definition'.")

    @field_validator('relevant_entities', mode='before')
    @classmethod
    def convert_none_to_empty_list(cls, value):
        if value is None:
            return []
        return value

class ToolCallStep(BaseModel):
    """Represents a single step in a tool execution plan."""
    tool: str = Field(description="The name of the tool to be called. Must be one of the available OntologyTools methods.")
    params: Dict[str, Any] = Field(default_factory=dict, description="A dictionary of parameters required to call the specified tool.")

class ToolPlan(BaseModel):
    """Represents the planned sequence of tool calls."""
    steps: List[ToolCallStep] = Field(default_factory=list, description="The sequence of tool calls to execute.")
            


class DimensionReport(BaseModel):
    """Represents the validation result for a specific dimension."""
    dimension: str = Field(description="The dimension being evaluated, e.g., 'completeness', 'consistency', 'accuracy'.")
    # score: Optional[int] = Field(default=None, description="The score for this dimension (typically 1-5).")
    # valid: bool = Field(description="Whether the result passed validation for this dimension.")
    message: str = Field(description="Detailed assessment or reasoning for this dimension's validation outcome.")

# NEW: 简化的工具调用分类结构
class ToolCallClassification(BaseModel):
    """单个工具调用的分类结果 - 简化结构"""
    tool: str = Field(description="Tool function name")
    class_name: str = Field(description="Class name parameter passed to the tool") 
    classification: ValidationClassification = Field(description="Classification label for this tool call")
    reason: str = Field(description="Brief reason for the classification")

# NEW: Global conceptual community assessment report
class GlobalCommunityAssessment(BaseModel):
    """Global conceptual community assessment report"""
    community_analysis: str = Field(description="Conceptual community analysis report")
    requirements_fulfilled: bool = Field(description="Whether query requirements are satisfied")

class ValidationReport(BaseModel):
    """简化的验证报告结构"""
    tool_classifications: List[ToolCallClassification] = Field(default_factory=list, description="Classification for each tool call")
    message: str = Field(description="Brief summary message")

# NEW: 简化的Refiner决策结果 - 为每个工具-参数组合提供hints
class ToolCallHint(BaseModel):
    """针对单个工具调用的提示"""
    tool: str = Field(description="Original tool name")
    class_name: str = Field(description="Original class name")
    action: str = Field(description="Suggested action: retry, replace_class, replace_tool, skip")
    hint: str = Field(description="Detailed hint for LLM about what to try differently")
    alternative_tools: List[str] = Field(default_factory=list, description="Alternative tool functions")

class RefinerDecision(BaseModel):
    """QueryRefiner的决策结果 - 简化结构"""
    overall_action: str = Field(description="Overall action: continue, retry, expand, terminate")
    reason: str = Field(description="Reason for the decision")
    tool_call_hints: List[ToolCallHint] = Field(default_factory=list, description="Specific hints for each tool call")

class QueryStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Query(BaseModel):
    """查询请求"""
    query_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    natural_query: str

    # 元数据
    originating_team: str  # dreamer, critic等
    originating_agent: str  # 发起查询的agent
    priority: str = "normal"  # high, normal, low

    # 查询上下文
    query_context: Dict[str, Any] = Field(default_factory=dict)

    # 状态跟踪
    created_at: datetime = Field(default_factory=datetime.now)
    status: QueryStatus = QueryStatus.PENDING
    result: Optional[Dict] = None
    error: Optional[str] = None

class ExtractedProperties(BaseModel):
    """Represents a list of relevant properties extracted from a query."""
    relevant_properties: List[str] = Field(default_factory=list, description="List of specific property names identified from the query and available property lists.")

    @field_validator('relevant_properties', mode='before')
    @classmethod
    def convert_none_to_empty_list(cls, value):
        if value is None:
            return []
        return value 

class FormattedResult(BaseModel):
    """Schema for formatted query results with expert-level depth and breadth."""
    summary: str = Field(description="A direct, concise answer to the main query (1-2 sentences)")
    key_points: List[str] = Field(default_factory=list, description="Core information points that directly address the query")
    background_information: List[str] = Field(default_factory=list, description="Broader contextual information that provides expert-level depth, may have slightly lower direct relevance than key points but enriches understanding")
    relationships: List[str] = Field(default_factory=list, description="Significant relationships, patterns, or connections found in the data")
    
    @field_validator('key_points', 'background_information', 'relationships', mode='before')
    @classmethod
    def convert_none_to_empty_list(cls, value):
        if value is None:
            return []
        return value 