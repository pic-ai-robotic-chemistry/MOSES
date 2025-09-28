from typing import TypedDict, List, Dict, Literal, Annotated, Optional
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import Graph, StateGraph, END, START
from langgraph.graph.message import AnyMessage, add_messages
import json

from autology_constructor.idea.query_team.utils import parse_json

class CriticState(TypedDict):
    """Critic团队状态"""
    # Input
    research_ideas: List[Dict]
    gap_analysis: Dict
    
    # Evaluation
    evaluations: List[Dict]
    needs_improvement: bool
    
    # State Management
    stage: str
    previous_stage: Optional[str]
    status: str
    
    # System
    messages: Annotated[list[AnyMessage], add_messages]

def create_critic_graph() -> Graph:
    workflow = StateGraph(CriticState)
    
    def assess_information(state: CriticState) -> Dict:
        """评估是否有足够信息进行评估"""
        try:
            llm = ChatOpenAI(temperature=0)
            
            assessment_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert research evaluator. Assess if there is sufficient information for evaluation."),
                ("user", """
                Research Ideas:
                {ideas}
                
                Gap Analysis:
                {gap_analysis}
                
                Assess if we have enough information about:
                1. Research methodology details
                2. Expected outcomes
                3. Technical feasibility
                4. Resource requirements
                
                Return as JSON:
                {
                    "is_sufficient": bool,
                    "missing_information": list[str],
                    "required_queries": list[str],
                    "reasoning": str
                }
                """)
            ])
            
            response = llm.invoke(assessment_prompt.format_messages(
                ideas=state["research_ideas"],
                gap_analysis=state["gap_analysis"]
            ))
            
            result = parse_json(response.content)
            
            if not result["is_sufficient"]:
                return {
                    "stage": "querying",  # 需要更多信息，转到查询阶段
                    "previous_stage": state.get("stage"),
                    "query_requests": [{
                        "query": query,
                        "requester": "critic",
                        "priority": 1
                    } for query in result["required_queries"]],
                    "messages": [
                        f"Insufficient information: {result['reasoning']}",
                        f"Required information: {', '.join(result['missing_information'])}"
                    ]
                }
            
            return {
                "stage": "critiquing",  # 信息充足，继续评估
                "previous_stage": state.get("stage"),
                "can_proceed": True,
                "messages": ["Information assessment completed: sufficient information available"]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "stage": "error",
                "previous_stage": state.get("stage"),
                "error": str(e),
                "messages": [f"Information assessment failed: {str(e)}"]
            }
    
    def evaluate_ideas(state: CriticState) -> Dict:
        """评估研究想法"""
        try:
            llm = ChatOpenAI(temperature=0)
            
            evaluation_prompt = ChatPromptTemplate.from_messages([
                ("system", "你是一位专家研究评审，请对提出的科学问题进行综合评价。"),
                ("user", """
Research Ideas:
{ideas}

Gap Analysis:
{gap_analysis}

请针对以下方面对每个科学问题进行评价：
1. 创新性（0-10）：科学问题是否具有突破性的新观点？
2. 可行性（0-10）：提出的问题是否可以通过现有方法解决？
3. 科学性/知识针对性（0-10）：问题是否准确聚焦于科学知识而非仅仅是本体数据结构？
4. 本体知识衔接（0-10）：科学问题与本体提供的科学信息是否紧密衔接？

另外，如果对科学问题的正确性存在疑问，请在评价中予以说明，并建议补充查询以验证相关数据。

请将评价结果以JSON格式返回，格式如下：
{
    "evaluations": [
        {
            "idea_id": str,
            "scores": {
                "innovation": int,
                "feasibility": int,
                "scientific_accuracy": int,
                "knowledge_alignment": int
            },
            "comments": str,
            "suggestions": list[str]
        }
    ],
    "needs_improvement": bool,
    "improvement_areas": list[str]
}
""")
            ])
            
            response = llm.invoke(evaluation_prompt.format_messages(
                ideas=state["research_ideas"],
                gap_analysis=state["gap_analysis"]
            ))
            
            result = parse_json(response.content)
            
            return {
                "stage": "critiquing",
                "previous_stage": state.get("stage"),
                "status": "success",
                "evaluations": result["evaluations"],
                "needs_improvement": result["needs_improvement"],
                "messages": [
                    f"Evaluation completed with {len(result['evaluations'])} reviews",
                    f"Areas needing improvement: {', '.join(result['improvement_areas'])}" 
                    if result["needs_improvement"] else "No major improvements needed"
                ]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "stage": "error",
                "previous_stage": state.get("stage"),
                "error": str(e),
                "messages": [f"Evaluation failed: {str(e)}"]
            }
    
    # Add nodes
    workflow.add_node("assess", assess_information)
    workflow.add_node("evaluate", evaluate_ideas)
    
    # Add routing logic
    def route_after_assessment(state: CriticState) -> Literal["evaluate", "need_info"]:
        """Route based on information assessment"""
        return "evaluate" if state.get("can_proceed", False) else "need_info"
    
    # Add edges
    workflow.add_edge(START, "assess")
    
    workflow.add_conditional_edges(
        "assess",
        route_after_assessment,
        {
            "evaluate": "evaluate",
            "need_info": END  # 如果需要更多信息，结束当前图返回主工作流
        }
    )
    
    workflow.add_edge("evaluate", END)
    
    return workflow.compile()

def parse_evaluation(content: str) -> Dict:
    """Parse evaluation result"""
    try:
        return json.loads(content)
    except Exception as e:
        print(f"Error parsing evaluation: {e}")
        return {"score": 0, "analysis": "Error in evaluation"}

def parse_verification(content: str) -> Dict:
    """Parse verification needs"""
    try:
        return json.loads(content)
    except Exception as e:
        print(f"Error parsing verification: {e}")
        return {"missing_info": []}

def parse_synthesis(content: str) -> Dict:
    """Parse synthesis result"""
    try:
        return json.loads(content)
    except Exception as e:
        print(f"Error parsing synthesis: {e}")
        return {"suggestions": []} 