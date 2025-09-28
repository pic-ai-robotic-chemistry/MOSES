from typing import Dict, List, TypedDict, Literal, Annotated, Optional, Any
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import Graph, StateGraph, END
from langgraph.graph.message import AnyMessage, add_messages
from autology_constructor.idea.query_team.utils import parse_json

class FinderState(TypedDict):
    """Base state for gap finder agents"""
    # Input
    source_ontology: Any
    target_ontology: Optional[Any]
    domain_analysis: Dict
    
    # Analysis
    gaps: List[Dict]
    ideas: List[Dict]
    
    # State Management
    stage: str
    previous_stage: Optional[str]
    status: str
    needs_more_info: bool
    
    # System
    messages: Annotated[list[AnyMessage], add_messages]

class BaseFinder:
    """基础研究缝隙分析器 - 专注于研究机会识别"""
    
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.7)
    
    # 新增生成研究想法方法，供所有finder使用
    def generate_ideas(self, gaps: List[Dict]) -> List[Dict]:
        prompt = self._get_ideation_prompt()
        content = __import__("autonogy_constructor.idea.common.llm_helpers", fromlist=["invoke_llm"]).invoke_llm(prompt, gaps=gaps)
        return self._parse_ideas(content)
    
    def analyze_gaps(self, domain_analysis: Dict) -> List[Dict]:
        """基于本体分析结果识别研究缝隙"""
        prompt = self._get_analysis_prompt()
        content = __import__("autonogy_constructor.idea.common.llm_helpers", fromlist=["invoke_llm"]).invoke_llm(prompt, analysis=domain_analysis)
        return self._parse_gaps(content)
    
    def create_finder_graph(self) -> Graph:
        """Create base finder workflow"""
        workflow = StateGraph(FinderState)
        
        # 1. Gap Analysis Node
        def analyze_gaps(state: FinderState) -> Dict:
            """Analyze gaps based on current information"""
            response = self.llm.invoke(self._get_analysis_prompt().format_messages(
                info=state["collected_info"]
            ))
            gaps = self._parse_gaps(response.content)
            return {"gaps": gaps}
        
        # 2. Reflection Node
        def reflect(state: FinderState) -> Dict:
            """Reflect on analysis and decide if more info is needed"""
            prompt = ChatPromptTemplate.from_messages([
                ("system", "Analyze the completeness and quality of the current analysis."),
                ("user", """
                Current Information:
                {info}
                
                Gaps Found:
                {gaps}
                
                Evaluate:
                1. Evidence completeness
                2. Analysis depth
                3. Logical consistency
                4. Information needs
                
                Clearly indicate if additional information is needed.
                
                Return as JSON:
                {
                    "is_complete": bool,
                    "missing_aspects": list[str],
                    "reasoning": str,
                    "next_steps": list[str]
                }
                """)
            ])
            
            response = self.llm.invoke(prompt.format_messages(
                info=state["collected_info"],
                gaps=state["gaps"]
            ))
            
            reflection = response.content
            return {
                "reflection_notes": [reflection],
                "needs_more_info": "need more information" in reflection.lower(),
                "query_requests": [self._generate_query(reflection)] if "need more information" in reflection.lower() else []
            }
        
        # 3. Idea Generation Node
        def generate_ideas(state: FinderState) -> Dict:
            """Generate ideas based on gaps"""
            response = self.llm.invoke(self._get_ideation_prompt().format_messages(
                gaps=state["gaps"]
            ))
            ideas = self._parse_ideas(response.content)
            return {"ideas": ideas}
        
        # Build workflow
        workflow.add_node("analyze", analyze_gaps)
        workflow.add_node("reflect", reflect)
        workflow.add_node("generate", generate_ideas)
        
        # Add edges
        workflow.add_edge("analyze", "reflect")
        
        # Add conditional edges
        def needs_more_info(state: FinderState) -> Literal["needs_query", "no_query"]:
            """Check if more information is needed"""
            if state["needs_more_info"]:
                return "needs_query"
            return "no_query"
        
        workflow.add_conditional_edges(
            "reflect",
            needs_more_info,
            {
                "needs_query": END,  # 需要查询时结束当前图的执行
                "no_query": "generate"  # 不需要查询时生成想法
            }
        )
        
        workflow.add_edge("generate", END)
        
        # Set entry and exit
        workflow.set_entry_point("analyze")
        
        return workflow.compile()
    
    def _get_analysis_prompt(self) -> ChatPromptTemplate:
        """Get analysis prompt"""
        return ChatPromptTemplate.from_messages([
            ("system", "You are an expert in research gap analysis."),
            ("user", """
            Domain Analysis:
            {analysis}
            
            Identify research gaps in:
            1. Conceptual Understanding
            2. Methodological Approaches
            3. Validation Methods
            4. Application Areas
            
            Return as JSON:
            {
                "gaps": [
                    {
                        "type": str,
                        "description": str,
                        "evidence": list[str],
                        "impact": str,
                        "priority": int
                    }
                ]
            }
            """)
        ])
    
    def _get_ideation_prompt(self) -> ChatPromptTemplate:
        """Get ideation prompt"""
        return ChatPromptTemplate.from_messages([
            ("system", "You are an expert in research idea generation."),
            ("user", """
            Research Gaps:
            {gaps}
            
            Generate research ideas that:
            1. Address specific gaps
            2. Are scientifically rigorous
            3. Have clear objectives
            4. Show potential impact
            
            Return as JSON:
            {
                "ideas": [
                    {
                        "gap_addressed": str,
                        "title": str,
                        "description": str,
                        "methodology": str,
                        "expected_outcomes": list[str],
                        "potential_impact": str
                    }
                ]
            }
            """)
        ])
    
    def _generate_query(self, reflection: str) -> Dict:
        """根据反思生成查询请求"""
        return {
            "query": reflection,
            "requester": self.__class__.__name__,
            "priority": 1
        }
    
    def _parse_gaps(self, content: str) -> List[Dict]:
        """解析差距分析结果"""
        try:
            result = parse_json(content)
            return result.get("gaps", [])
        except Exception as e:
            print(f"Error parsing gaps: {e}")
            return []
    
    def _parse_ideas(self, content: str) -> List[Dict]:
        """解析研究想法"""
        try:
            result = parse_json(content)
            return result.get("ideas", [])
        except Exception as e:
            print(f"Error parsing ideas: {e}")
            return []