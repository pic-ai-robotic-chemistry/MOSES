from autology_constructor.idea.state_manager import DreamerState

from typing import Dict, List, TypedDict, Literal, Annotated, Optional, Any
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import Graph, StateGraph, END, START
from langgraph.graph.message import AnyMessage, add_messages
from autology_constructor.idea.query_team.ontology_tools import OntologyAnalyzer
from .evidence_finder import EvidenceFinder
from .knowledge_finder import KnowledgeFinder
from .methodology_finder import MethodologyFinder
from .meta_science_finder import MetaScienceFinder
from autology_constructor.idea.query_team.utils import parse_json
from datetime import datetime
import uuid


def create_dreamer_graph() -> Graph:
    """创建Dreamer团队工作流图"""
    workflow = StateGraph(DreamerState)
    
    # 添加节点
    workflow.add_node("初始化", initialize_dreamer)
    workflow.add_node("领域分析", analyze_domain)
    workflow.add_node("信息充分性评估", assess_information_sufficiency)
    workflow.add_node("研究空白识别", identify_research_gaps)
    workflow.add_node("创意生成", generate_research_ideas)
    workflow.add_node("创意改进", refine_research_ideas)
    workflow.add_node("查询准备", prepare_query)
    
    # 定义工作流路径
    workflow.add_edge(START, "初始化")
    workflow.add_edge("初始化", "领域分析")
    
    # 从领域分析到信息充分性评估
    workflow.add_edge("领域分析", "信息充分性评估")
    
    # 从信息充分性评估条件跳转
    workflow.add_conditional_edges(
        "信息充分性评估",
        route_on_information_sufficiency,
        {
            "信息充分": "研究空白识别",
            "信息不足": "查询准备"
        }
    )
    
    # 查询准备后结束当前循环，等待Query Team返回
    workflow.add_edge("查询准备", END)
    
    # 研究空白识别后进行创意生成
    workflow.add_edge("研究空白识别", "创意生成")
    
    # 创意生成后结束，等待Critic Team评审
    workflow.add_edge("创意生成", END)
    
    # 当接收到Critic反馈后，进入创意改进环节
    workflow.add_edge("创意改进", "信息充分性评估")
    
    return workflow.compile()


def initialize_dreamer(state: DreamerState) -> Dict:
    """初始化Dreamer状态"""
    return {
        "stage": "initialized",
        "status": "processing",
        "messages": [{"role": "system", "content": "Dreamer团队已初始化，准备开始工作"}]
    }


def analyze_domain(state: DreamerState) -> Dict:
    """分析领域并生成科研想法"""
    try:
        analyzer = OntologyAnalyzer()
        # 使用主本体进行领域结构分析
        domain_analysis = analyzer.analyze_domain_structure(state["ontology"])
        domain_analysis["key_concepts"] = analyzer.find_key_concepts(state["ontology"])
        
        if state["analysis_type"] == "cross_domain" and state.get("additional_ontologies") and len(state["additional_ontologies"]) > 0:
            domain_analysis["cross_domain"] = analyzer.compare_domains(
                state["ontology"],
                state["additional_ontologies"][0]
            )
        
        return {
            "domain_analysis": domain_analysis,
            "stage": "domain_analyzed",
            "status": "processing",
            "messages": [{"role": "system", "content": "领域分析完成，已提取关键概念和结构信息"}]
        }
    except Exception as e:
        return {
            "stage": "domain_analysis",
            "status": "error",
            "messages": [{"role": "system", "content": f"领域分析出错: {str(e)}"}]
        }


def assess_information_sufficiency(state: DreamerState) -> Dict:
    """评估当前信息是否足够进行下一步分析"""
    # 检查必要信息是否完整
    info_needs = []
    
    # 检查领域结构信息
    if not state.get("domain_analysis") or not state["domain_analysis"].get("key_concepts"):
        info_needs.append({
            "type": "domain_structure",
            "query": "分析本体的基本领域结构和关键概念"
        })
    
    # 返回评估结果
    if info_needs:
        return {
            "information_needs": info_needs,
            "stage": "information_assessment",
            "status": "information_insufficient",
            "messages": [{"role": "system", "content": "信息不足，需要更多数据"}]
        }
    else:
        return {
            "stage": "information_assessment",
            "status": "information_sufficient",
            "messages": [{"role": "system", "content": "信息充足，可以继续进行"}]
        }


def route_on_information_sufficiency(state: DreamerState) -> str:
    """根据信息充分性决定下一步路径"""
    if state["status"] == "information_sufficient":
        return "信息充分"
    else:
        return "信息不足"


def identify_research_gaps(state: DreamerState) -> Dict:
    """识别研究空白"""
    try:
        # 根据本体情况选择性地调用不同的finder
        has_additional_ontologies = (
            state.get("additional_ontologies") is not None and 
            len(state.get("additional_ontologies", [])) > 0
        )
        
        # 选择适用的finder
        finders = {}
        
        # 单本体情况：启用证据gap和知识gap
        if not has_additional_ontologies:
            finders = {
                "evidence": EvidenceFinder(),
                "knowledge": KnowledgeFinder()
            }
        # 多本体情况：启用方法论gap和元科学gap
        else:
            finders = {
                "methodology": MethodologyFinder(),
                "meta_science": MetaScienceFinder()
            }
        
        # 调用选定的finder识别研究空白
        gaps = {}
        for name, finder in finders.items():
            # 调用find_gaps方法，为finder提供领域分析结果
            finder_state = {
                "source_ontology": state["ontology"],
                "target_ontology": state["additional_ontologies"][0] if has_additional_ontologies else None,
                "domain_analysis": state["domain_analysis"]
            }
            gaps[name] = finder.analyze_gaps(state["domain_analysis"])
        
        # 记录分析信息
        gap_info = {
            "analysis_context": {
                "analysis_type": "cross_domain" if has_additional_ontologies else "single_domain",
                "ontology_count": 1 + len(state.get("additional_ontologies", [])) if has_additional_ontologies else 1,
                "gap_types_analyzed": list(finders.keys())
            },
            "gap_summary": {
                gap_type: len(gaps_list) for gap_type, gaps_list in gaps.items()
            }
        }
        
        return {
            "gap_analysis": gaps,
            "gap_info": gap_info,
            "stage": "gaps_identified",
            "status": "processing",
            "messages": [{"role": "system", "content": f"已识别{sum(len(g) for g in gaps.values())}个研究空白，类型包括：{', '.join(finders.keys())}"}]
        }
    except Exception as e:
        return {
            "stage": "gap_identification",
            "status": "error",
            "messages": [{"role": "system", "content": f"识别研究空白出错: {str(e)}"}]
        }


def generate_research_ideas(state: DreamerState) -> Dict:
    """生成研究创意"""
    try:
        ideas = []
        # 基于领域分析和研究空白生成创意
        for gap_type, gaps in state["gap_analysis"].items():
            for gap in gaps:
                # 为每个识别到的空白生成一个创意
                idea = {
                    "title": f"研究{gap.get('name', '未命名空白')}",
                    "gap_type": gap_type,
                    "gap_reference": gap.get("id", str(uuid.uuid4())),
                    "description": f"基于{gap.get('description', '研究空白')}的研究想法",
                    "innovation_potential": "medium",  # 默认值
                    "feasibility": "medium",  # 默认值
                    "version": 1,
                    "created_at": datetime.now().isoformat()
                }
                ideas.append(idea)
        
        return {
            "research_ideas": ideas,
            "idea_versions": [{"version": 1, "ideas": ideas}],
            "stage": "ideas_generated",
            "status": "completed",
            "messages": [{"role": "system", "content": f"已生成{len(ideas)}个研究创意"}]
        }
    except Exception as e:
        return {
            "stage": "idea_generation",
            "status": "error",
            "messages": [{"role": "system", "content": f"生成研究创意出错: {str(e)}"}]
        }


def prepare_query(state: DreamerState) -> Dict:
    """准备查询请求供Query Team使用"""
    queries = []
    
    for need in state.get("information_needs", []):
        query = {
            "query_id": str(uuid.uuid4()),
            "query_text": need["query"],
            "query_type": need["type"],
            "originating_stage": state["stage"],
            "priority": "high"
        }
        queries.append(query)
    
    return {
        "pending_queries": queries,
        "stage": "query_prepared",
        "status": "waiting_for_query",
        "messages": [{"role": "system", "content": f"已准备{len(queries)}个查询请求"}]
    }


def refine_research_ideas(state: DreamerState) -> Dict:
    """根据Critic反馈改进研究创意"""
    if not state.get("critic_feedback"):
        return {
            "stage": "ideas_refinement",
            "status": "error",
            "messages": [{"role": "system", "content": "缺少Critic反馈，无法进行创意改进"}]
        }
    
    try:
        # 获取当前创意
        current_ideas = state["research_ideas"]
        feedback = state["critic_feedback"]
        
        # 根据反馈改进创意
        improved_ideas = []
        for idea in current_ideas:
            idea_feedback = feedback.get(idea["gap_reference"], {})
            
            improved_idea = idea.copy()
            improved_idea["version"] = idea.get("version", 1) + 1
            
            # 应用反馈进行改进
            if idea_feedback.get("title_feedback"):
                improved_idea["title"] = idea_feedback["title_feedback"]
            
            if idea_feedback.get("description_feedback"):
                improved_idea["description"] = idea_feedback["description_feedback"]
            
            # 更新评分
            if idea_feedback.get("innovation_rating"):
                improved_idea["innovation_potential"] = idea_feedback["innovation_rating"]
                
            if idea_feedback.get("feasibility_rating"):
                improved_idea["feasibility"] = idea_feedback["feasibility_rating"]
                
            improved_ideas.append(improved_idea)
        
        # 保存新版本
        versions = state.get("idea_versions", [])
        new_version = {
            "version": len(versions) + 1,
            "ideas": improved_ideas,
            "based_on_feedback": feedback
        }
        versions.append(new_version)
        
        return {
            "research_ideas": improved_ideas,
            "idea_versions": versions,
            "stage": "ideas_refined",
            "status": "processing",
            "messages": [{"role": "system", "content": f"已根据Critic反馈改进{len(improved_ideas)}个创意"}]
        }
    except Exception as e:
        return {
            "stage": "idea_refinement",
            "status": "error",
            "messages": [{"role": "system", "content": f"改进研究创意出错: {str(e)}"}]
        } 