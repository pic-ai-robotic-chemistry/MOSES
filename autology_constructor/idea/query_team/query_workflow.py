from typing import Dict, List, Literal, Optional, Any, Union
from datetime import datetime
import hashlib
import json
import logging
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langgraph.graph import Graph, StateGraph, END, START
from .ontology_tools import OntologyTools, SparqlExecutionError
from .query_agents import QueryParserAgent, StrategyPlannerAgent, ToolPlannerAgent, ToolExecutorAgent, SparqlExpertAgent, ValidationAgent, HypotheticalDocumentAgent, ResultFormatterAgent
from .query_refiner import QueryRefiner
from .query_manager import Query, QueryStatus
from .utils import format_sparql_error, format_sparql_results, extract_variables_from_sparql
from .workflow_utils import (
    generate_tool_call_signature, record_tool_call, has_tool_call_been_tried,
    detect_stagnation, handle_stagnation_with_entity_matcher,
    filter_internal_tools, clean_tool_results, supplement_parse_definitions
)
from .schemas import NormalizedQuery, ToolPlan, ValidationReport, ValidationClassification
from .entity_matcher import EntityMatcher

# 统一的重试次数配置 - 允许4轮重试 (retry_count: 0, 1, 2, 3, 4)
MAX_RETRY_COUNT = 4
from .stategraph import QueryState
from autology_constructor.idea.common.llm_provider import get_cached_default_llm

logger = logging.getLogger(__name__)


def create_query_graph() -> Graph:
    """创建查询工作流 - ontology_tools现在从QueryState中获取"""

    workflow = StateGraph(QueryState)

    # Get the default LLM instance
    try:
        default_model = get_cached_default_llm()
    except Exception as e:
        print(f"Critical Error: Failed to initialize default LLM: {e}")
        # Decide how to handle this - maybe raise the error or use a fallback
        raise RuntimeError("LLM initialization failed, cannot create query graph.") from e

    # Instantiate agents with the default model
    parser_agent = QueryParserAgent(model=default_model)
    strategy_agent = StrategyPlannerAgent(model=default_model)
    tool_planner_agent = ToolPlannerAgent(model=default_model)
    tool_agent = ToolExecutorAgent(model=default_model)
    sparql_agent = SparqlExpertAgent(model=default_model)
    validator_agent = ValidationAgent(model=default_model)
    hypothetical_document_agent = HypotheticalDocumentAgent(model=default_model)
    result_formatter_agent = ResultFormatterAgent(model=default_model)
    
    # 注意：ontology_tools现在从state中获取，不再在这里初始化
    # QueryRefiner和EntityMatcher将在节点函数中按需创建
    
    # 节点实现
    def normalize_query(state: QueryState) -> Dict:
        """解析并标准化查询，优先使用refined_classes，包含LLM停滞检测"""
        retry_count = state.get("retry_count",0)
        print(f"[DEBUG-NORMALIZE] Starting normalize_query, retry_count: {retry_count}")
        print(f"[DEBUG-NORMALIZE] State type: {type(state)}")
        print(f"[DEBUG-NORMALIZE] State keys: {list(state.keys()) if isinstance(state, dict) else 'Not a dict'}")
        
        # 特别检查refiner_hints
        refiner_hints_in_state = state.get("refiner_hints", "NOT_FOUND")
        print(f"[DEBUG-NORMALIZE] refiner_hints in state: {refiner_hints_in_state}")
        print(f"[DEBUG-NORMALIZE] refiner_hints type: {type(refiner_hints_in_state)}")
        if isinstance(refiner_hints_in_state, list):
            print(f"[DEBUG-NORMALIZE] refiner_hints length: {len(refiner_hints_in_state)}")
            for i, hint in enumerate(refiner_hints_in_state):
                print(f"[DEBUG-NORMALIZE] refiner_hints[{i}]: {hint}")
        
        # 检查其他重要字段
        print(f"[DEBUG-NORMALIZE] refiner_decision in state: {type(state.get('refiner_decision', 'NOT_FOUND'))}")
        print(f"[DEBUG-NORMALIZE] stage: {state.get('stage', 'NOT_FOUND')}")
        print(f"[DEBUG-NORMALIZE] status: {state.get('status', 'NOT_FOUND')}")
        
        try:
            # 从state获取ontology_tools
            ontology_tools = state.get("ontology_tools")
            print(f"[DEBUG-NORMALIZE] ontology_tools: {type(ontology_tools)}")
            if not ontology_tools:
                raise ValueError("ontology_tools not found in state")
            
            # 安全地获取state中的必需字段
            print(f"[DEBUG-NORMALIZE] Accessing required state fields...")
            try:
                query = state["query"]
                print(f"[DEBUG-NORMALIZE] query: {query}")
            except KeyError as e:
                print(f"[DEBUG-NORMALIZE] ERROR: Missing query in state: {e}")
                raise
            except Exception as e:
                print(f"[DEBUG-NORMALIZE] ERROR: Unexpected error accessing query: {e}")
                raise
                
            try:
                available_classes = state["available_classes"]
                print(f"[DEBUG-NORMALIZE] available_classes count: {len(available_classes) if available_classes else 'None'}")
            except KeyError as e:
                print(f"[DEBUG-NORMALIZE] ERROR: Missing available_classes in state: {e}")
                raise
            except Exception as e:
                print(f"[DEBUG-NORMALIZE] ERROR: Unexpected error accessing available_classes: {e}")
                raise
                
            try:
                available_data_properties = state["available_data_properties"]
                available_object_properties = state["available_object_properties"]
                print(f"[DEBUG-NORMALIZE] properties loaded successfully")
            except KeyError as e:
                print(f"[DEBUG-NORMALIZE] ERROR: Missing properties in state: {e}")
                raise
            except Exception as e:
                print(f"[DEBUG-NORMALIZE] ERROR: Unexpected error accessing properties: {e}")
                raise
            
            # 创建EntityMatcher
            entity_matcher = EntityMatcher(available_classes)
            
            # NEW: 检测LLM停滞
            if detect_stagnation(state):
                logger.info("[normalize_query] 检测到LLM停滞，启动EntityMatcher干预")
                stagnation_result = handle_stagnation_with_entity_matcher(
                    state, entity_matcher, ontology_tools
                )
                if stagnation_result.get("refined_classes"):
                    logger.info(f"[normalize_query] 停滞处理成功，强制使用新候选: {len(stagnation_result['refined_classes'])} 个类")
                    # 更新状态，强制使用新的候选类
                    state = {**state, **stagnation_result}
            
            # 优先使用refined_classes，如果存在的话
            refined_classes = state.get("refined_classes")
            if refined_classes:
                effective_classes = refined_classes
                print(f"[TOKEN OPTIMIZATION] Using refined classes: {len(effective_classes)} classes (~{len(effective_classes) * 2} tokens)")
            else:
                effective_classes = available_classes
                original_classes_count = len(available_classes)
                estimated_tokens = original_classes_count * 2  # 估算每个类名平均2个token
                print(f"[TOKEN OPTIMIZATION] Using original classes: {original_classes_count} classes (~{estimated_tokens} tokens)")
            
            # NEW: 处理来自refiner的hints - 只处理class相关的hints
            refiner_hints = state.get("refiner_hints", [])
            print(f"[DEBUG-HINTS] Raw refiner_hints: {refiner_hints}")
            print(f"[DEBUG-HINTS] Type of refiner_hints: {type(refiner_hints)}")
            print(f"[DEBUG-HINTS] Length of refiner_hints: {len(refiner_hints) if isinstance(refiner_hints, list) else 'Not a list'}")
            
            # 安全检查每个hint对象
            class_related_hints = []
            if isinstance(refiner_hints, list):
                for i, h in enumerate(refiner_hints):
                    print(f"[DEBUG-HINTS] Processing hint {i}: {h}, type: {type(h)}")
                    if h is None:
                        print(f"[DEBUG-HINTS] Hint {i} is None, skipping")
                        continue
                    try:
                        if hasattr(h, 'action') and h.action in ["replace_class", "replace_both"]:
                            class_related_hints.append(h)
                            print(f"[DEBUG-HINTS] Added class-related hint {i}: action={h.action}")
                        else:
                            print(f"[DEBUG-HINTS] Hint {i} not class-related: action={getattr(h, 'action', 'NO_ACTION_ATTR')}")
                    except Exception as e:
                        print(f"[DEBUG-HINTS] Error processing hint {i}: {e}")
                        continue
            else:
                print(f"[DEBUG-HINTS] refiner_hints is not a list: {type(refiner_hints)}")
            
            print(f"[DEBUG-HINTS] Final class_related_hints count: {len(class_related_hints)}")
            
            # Prepare state for parser agent, including available classes
            if state.get("validation_report"):
                enhanced_feedback = getattr(state.get("validation_report"), "message", None)
            else:
                enhanced_feedback = None
                
            parser_state = {
                "natural_query": query,
                "available_classes": effective_classes,  # 使用优化后的类集合
                "original_available_classes": available_classes,  # 传递原始类集合给内部重试使用
                "available_data_properties": available_data_properties,
                "available_object_properties": available_object_properties,
                "enhanced_feedback": enhanced_feedback,
                "hypothetical_document": state.get("hypothetical_document"),
                "class_hints": class_related_hints  # NEW: 传递类相关的hints给parser agent
            }
            # Use parser agent
            normalized_result = parser_agent(parser_state)
            # Check if parsing resulted in an error reported by the agent
            if isinstance(normalized_result, dict) and normalized_result.get("error"):
                    raise ValueError(f"Query parsing failed: {normalized_result.get('error')}")
            elif not isinstance(normalized_result, NormalizedQuery):
                    # Should not happen if agent works correctly, but good to check
                    raise TypeError(f"Query parser returned unexpected type: {type(normalized_result)}")
            
            result = {
                "normalized_query": normalized_result,
                "status": "parsing_complete",
                "stage": "normalized",
                "previous_stage": state.get("stage"),
                "messages": [SystemMessage(content=f"Query normalized: {query}")]
            }
            
            # 如果处理了停滞，保留相关信息
            if state.get("stagnation_handled"):
                result["stagnation_handled"] = True
                result["stagnation_method"] = state.get("stagnation_method")
                if state.get("tried_tool_calls"):
                    result["tried_tool_calls"] = state["tried_tool_calls"]
            
            return result
        except Exception as e:
            error_message = f"Query normalization failed: {str(e)}"
            print(error_message)
            return {
                "status": "error",
                "stage": "error",
                "previous_stage": state.get("stage"),
                "error": error_message,
                "messages": [SystemMessage(content=error_message)]
            }
    
    def determine_strategy(state: QueryState) -> Dict:
        """确定查询执行策略"""
        try:
            # If strategy is already provided (e.g., via context), use it.
            # Otherwise, use the strategy agent.
            strategy = state.get("query_strategy")
            if not strategy:
                normalized_query_obj = state.get("normalized_query")
                if not normalized_query_obj or not isinstance(normalized_query_obj, NormalizedQuery):
                    raise ValueError("NormalizedQuery object is missing or invalid, cannot determine strategy.")
                
                # Use strategy planner agent
                strategy = strategy_agent.decide_strategy(normalized_query_obj.model_dump())
                # Basic validation of strategy output
                if strategy not in ["tool_sequence", "SPARQL"]:
                     print(f"Warning: Strategy agent returned unsupported strategy '{strategy}'. Defaulting to tool_sequence.")
                     strategy = "tool_sequence"

            return {
                "query_strategy": strategy,
                "status": "strategy_determined",
                "stage": "strategy",
                "previous_stage": state.get("stage"),
                "messages": [SystemMessage(content=f"Query strategy determined: {strategy}")]
            }
        except Exception as e:
            error_message = f"Strategy determination failed: {str(e)}"
            print(error_message)
            return {
                "status": "error",
                "stage": "error",
                "previous_stage": state.get("stage"),
                "error": error_message,
                "messages": [SystemMessage(content=error_message)]
            }
    
    def execute_query(state: QueryState) -> Dict:
        """执行查询 (工具序列或SPARQL) - 从state获取ontology_tools实例"""
        try:
            # 从state获取ontology_tools
            ontology_tools = state.get("ontology_tools")
            if not ontology_tools:
                raise ValueError("ontology_tools not found in state")
            
            strategy = state.get("query_strategy")
            normalized_query_obj = state["normalized_query"]
            ontology_settings = state["source_ontology"]

            if not strategy or not ontology_settings or not isinstance(normalized_query_obj, NormalizedQuery):
                 raise ValueError("Missing strategy, ontology settings, or invalid NormalizedQuery object.")
            
            # 设置工具代理的OntologyTools实例
            tool_agent.set_ontology_tools(ontology_tools)
            
            if strategy == "tool_sequence":
                # NEW: 处理来自refiner的tool相关hints
                refiner_hints = state.get("refiner_hints", [])
                tool_related_hints = [h for h in refiner_hints if h.action in ["replace_tool", "replace_both"]]
                
                # 生成执行计划，传递tool hints
                if tool_related_hints:
                    print(f"[execute_query] 传递 {len(tool_related_hints)} 个tool hints给planner")
                    plan_result = tool_planner_agent.generate_plan(
                        normalized_query_obj, 
                        ontology_tools, 
                        tool_hints=tool_related_hints
                    )
                else:
                    plan_result = tool_planner_agent.generate_plan(normalized_query_obj, ontology_tools)
                
                # 检查计划生成是否出错
                if isinstance(plan_result, dict) and plan_result.get("error"):
                    raise ValueError(f"Failed to generate tool plan: {plan_result.get('error')}")
                elif not isinstance(plan_result, Union[ToolPlan, Dict]):
                     raise TypeError(f"Tool planner returned unexpected type: {type(plan_result)}")
                
                # 执行计划 - 已经在上面设置了OntologyTools
                execution_results = tool_agent.execute_plan(plan_result)
                
                # NEW: 记录所有工具调用到tried_tool_calls（使用现有去重机制）
                current_state_for_recording = {"tried_tool_calls": state.get("tried_tool_calls", {}), "retry_count": state.get("retry_count", 0)}
                for result_item in execution_results:
                    if isinstance(result_item, dict) and "tool" in result_item:
                        tool_name = result_item["tool"]
                        params = result_item.get("params", {})
                        result = result_item.get("result")
                        
                        # 记录这次工具调用（自动处理去重）
                        update_record = record_tool_call(
                            current_state_for_recording, 
                            tool_name, 
                            params, 
                            result
                        )
                        current_state_for_recording.update(update_record)
                
                print(f"[execute_query] 记录了 {len(execution_results)} 个工具调用到tried_tool_calls")

                # 处理结果
                return {
                    "execution_plan": plan_result,
                    "query_results": {"results": execution_results}, # Wrap tool results for consistency
                    "tried_tool_calls": current_state_for_recording["tried_tool_calls"],  # NEW: 传递更新后的tried_tool_calls
                    "status": "executed",
                    "stage": "executed",
                    "previous_stage": state.get("stage"),
                    "messages": [SystemMessage(content="Tool-based query executed.")]
                }
                
            elif strategy == "SPARQL":
                # 生成SPARQL查询
                sparql_query_str = sparql_agent.generate_sparql(normalized_query_obj.model_dump())

                # 使用创建的OntologyTools实例执行SPARQL（对象级锁保护）
                lock = state.get("ontology_tools_lock")
                if lock:
                    with lock:
                        results = ontology_tools.execute_sparql(sparql_query_str)
                else:
                    results = ontology_tools.execute_sparql(sparql_query_str)
                
                # 错误检查
                if isinstance(results, dict) and results.get("error"):
                    raise SparqlExecutionError(f"SPARQL execution failed: {results.get('error')}. Query: {results.get('query')}")

                return {
                    "query_results": results, # Already formatted by execute_sparql
                    "sparql_query": sparql_query_str,
                    "execution_plan": None, # Explicitly set plan to None for SPARQL path
                    "status": "executed",
                    "stage": "executed",
                    "previous_stage": state.get("stage"),
                    "messages": [SystemMessage(content="SPARQL query executed successfully.")]
                }
            else:
                raise ValueError(f"Unsupported query strategy: {strategy}")

        except Exception as e:
            error_message = f"Query execution failed: {str(e)}"
            print(error_message)
            return {
                "status": "error",
                "stage": "error",
                "previous_stage": state.get("stage"),
                "error": error_message,
                "messages": [SystemMessage(content=error_message)]
            }
    
    def validate_results(state: QueryState) -> Dict:
        """验证查询结果并记录迭代历史"""
        try:
            results_to_validate = state.get("query_results")
            normalized_query_obj = state.get("normalized_query")

            # Initialize or retrieve history
            iteration_history = state.get("iteration_history", [])

            if not results_to_validate or not isinstance(results_to_validate, dict):
                print("Warning: Skipping validation due to missing or malformed results.")
                return {"status": state.get("status", "executed"), "stage": "validated", "validation_report": None, "iteration_history": iteration_history}

            if results_to_validate.get("error"):
                print(f"Skipping validation because previous step failed: {results_to_validate.get('error')}")
                return {
                    "status": "error",
                    "stage": "validation_skipped_due_to_error",
                    "error": results_to_validate.get("error"),
                    "validation_report": None,
                    "previous_stage": state.get("stage"),
                    "messages": [SystemMessage(content="Validation skipped due to prior error.")],
                    "iteration_history": iteration_history
                }

            # Prepare query context for validation agent
            query_context = {}
            if isinstance(normalized_query_obj, NormalizedQuery):
                query_context = {
                    "intent": normalized_query_obj.intent,
                    "relevant_entities": ", ".join(normalized_query_obj.relevant_entities),
                    "relevant_properties": ", ".join(normalized_query_obj.relevant_properties),
                }
            query_context["query"] = state.get("query")
            query_context["type"] = state.get("query_type", "unknown")
            query_context["strategy"] = state.get("query_strategy")
            # 添加tried_tool_calls到context中 - 修复关键问题！
            query_context["tried_tool_calls"] = state.get("tried_tool_calls", {})
            query_context["retry_count"] = state.get("retry_count", 0)
            
            print(f"[DEBUG-QUERY-CONTEXT] tried_tool_calls在validation context中包含 {len(query_context.get('tried_tool_calls', {}))} 个调用")

            # Use validation agent
            validation_result = validator_agent.validate(results_to_validate, query_context)

            # Handle the new return format with global_assessment
            if isinstance(validation_result, dict):
                if validation_result.get("error"):
                    print(f"Validation Report: {validation_result.get('validation_report')}")
                    raise ValueError(f"Validation agent failed: {validation_result.get('error')}")
                
                # Extract ValidationReport and global_assessment
                validation_report = validation_result.get("validation_report")
                global_assessment = validation_result.get("global_assessment")
                
                if not isinstance(validation_report, ValidationReport):
                    raise TypeError(f"Validation report has unexpected type: {type(validation_report)}")
            else:
                # Backward compatibility: direct ValidationReport return
                validation_report = validation_result
                global_assessment = None
                if not isinstance(validation_report, ValidationReport):
                    raise TypeError(f"Validation agent returned unexpected type: {type(validation_result)}")

            # Create a snapshot of the current iteration
            current_iteration_snapshot = {
                "retry_count": state.get("retry_count", 0),
                "hypothetical_document": state.get("hypothetical_document"),
                "refined_classes": state.get("refined_classes"),
                "normalized_query": state.get("normalized_query"),
                "query_strategy": state.get("query_strategy"),
                "execution_plan": state.get("execution_plan"),
                "sparql_query": state.get("sparql_query"),
                "query_results": state.get("query_results"),
                "validation_report": validation_report,
                "tried_tool_calls": state.get("tried_tool_calls"),
                "refiner_hints": state.get("refiner_hints"),
                "global_assessment": state.get("global_assessment"),
                "timestamp": datetime.now().isoformat(),
                "messages": state.get("messages")
            }
            iteration_history.append(current_iteration_snapshot)

            # Determine final status based on validation - check if all tool classifications are sufficient
            all_sufficient = all(
                tc.classification == ValidationClassification.SUFFICIENT 
                for tc in validation_report.tool_classifications
            )
            final_status = "success" if all_sufficient else "warning"
            validation_message = validation_report.message

            result = {
                "validation_report": validation_report,
                "status": final_status,
                "stage": "validated",
                "previous_stage": state.get("stage"),
                "messages": [SystemMessage(content=f"Results validation {final_status}: {validation_message}")],
                "iteration_history": iteration_history  # Pass the updated history
            }
            
            # Save global_assessment to state if available
            if global_assessment:
                result["global_assessment"] = global_assessment
                
            return result
        except Exception as e:
            error_message = f"Results validation failed: {str(e)}"
            print(error_message)
            # Also update history on error if possible
            iteration_history = state.get("iteration_history", [])
            iteration_history.append({
                "error": error_message,
                "stage": "validate_results",
                "timestamp": datetime.now().isoformat()
            })
            return {
                "status": "error",
                "stage": "error",
                "previous_stage": state.get("stage"),
                "error": error_message,
                "validation_report": None,
                "messages": [SystemMessage(content=error_message)],
                "iteration_history": iteration_history
            }
    
    def generate_hypothetical_document(state: QueryState) -> Dict:
        """从专业化学家角度生成假设性答案，帮助查询标准化"""
        try:
            # 从state获取ontology_tools并设置给agent
            ontology_tools = state.get("ontology_tools")
            if ontology_tools:
                hypothetical_document_agent.set_ontology_tools(ontology_tools)
            
            query = state.get("query")
            validation_history = state.get("validation_history", [])
            
            if not query:
                raise ValueError("Cannot generate hypothetical document: query is missing")
            
            # 使用HypotheticalDocumentAgent生成假设性文档
            hypothetical_doc = hypothetical_document_agent.generate_hypothetical_document(
                query=query, 
                validation_history=validation_history
            )
            
            # 更新状态
            return {
                "hypothetical_document": hypothetical_doc,
                "status": "hypothetical_generated",
                "stage": "hypothetical_generated",
                "previous_stage": state.get("stage"),
                "messages": [SystemMessage(content=f"Generated hypothetical document to aid in query understanding: {hypothetical_doc.get('interpretation', '')[:100]}...")]
            }
        except Exception as e:
            error_message = f"Hypothetical document generation failed: {str(e)}"
            print(error_message)
            return {
                "status": "error",
                "stage": "error",
                "previous_stage": state.get("stage"),
                "error": error_message,
                "messages": [SystemMessage(content=error_message)]
            }
    
    def format_results(state: QueryState) -> Dict:
        """格式化查询结果为用户友好的形式 - 使用过滤后的tried_tool_calls"""
        try:
            from .workflow_utils import filter_validated_tool_calls
            
            query = state.get("query")
            current_results = state.get("query_results")
            normalized_query_obj = state.get("normalized_query")
            tried_tool_calls = state.get("tried_tool_calls", {})
            
            if not query:
                raise ValueError("Cannot format results: query is missing")
            
            # 基于验证结果过滤工具调用 - 替代原有的filter_internal_tools
            filtered_tool_calls = filter_validated_tool_calls(tried_tool_calls)
            
            print(f"[format_results] 原始调用: {len(tried_tool_calls)} 个")
            print(f"[format_results] 过滤后调用: {len(filtered_tool_calls)} 个")
            
            # 从过滤后的tried_tool_calls汇总所有用户相关的工具调用结果
            all_results = {"results": []}
            
            if filtered_tool_calls:
                for call_id, call_info in filtered_tool_calls.items():
                    tool_result = {
                        "tool": call_info.get("tool"),
                        "params": call_info.get("params"),
                        "result": call_info.get("result")
                    }
                    # 清理工具结果中的内部系统信息
                    cleaned_tool_result = clean_tool_results(tool_result)
                    all_results["results"].append(cleaned_tool_result)
                
                print(f"[format_results] 向formatter发送 {len(all_results['results'])} 个高质量工具调用结果")
            
            # 如果过滤后的调用为空，使用tried_tool_calls作为fallback（过滤掉失败和无结果的调用）
            if not all_results["results"] and tried_tool_calls:
                print(f"[format_results] 过滤机制失效，使用tried_tool_calls作为fallback")
                
                # 过滤掉失败和无结果的工具调用
                for call_id, call_info in tried_tool_calls.items():
                    result = call_info.get("result", {})
                    
                    # 过滤条件：跳过失败和无结果的调用
                    if not result:  # 无结果
                        continue
                    if isinstance(result, dict) and "error" in result:  # 失败的调用
                        continue
                    # 检查是否空内容的类信息
                    if isinstance(result, dict):
                        for class_name, class_info in result.items():
                            if isinstance(class_info, dict) and class_info.get("information") == []:
                                continue
                    
                    # 通过过滤的调用加入结果
                    tool_result = {
                        "tool": call_info.get("tool"),
                        "params": call_info.get("params"),
                        "result": result
                    }
                    cleaned_tool_result = clean_tool_results(tool_result)
                    all_results["results"].append(cleaned_tool_result)
                
                print(f"[format_results] Fallback获得 {len(all_results['results'])} 个有效工具调用结果")
            
            # 准备query_context
            query_context = {}
            if isinstance(normalized_query_obj, NormalizedQuery):
                query_context = {
                    "intent": normalized_query_obj.intent,
                    "relevant_entities": ", ".join(normalized_query_obj.relevant_entities),
                    "relevant_properties": ", ".join(normalized_query_obj.relevant_properties),
                }
            
            # 使用ResultFormatterAgent格式化结果
            formatted_results = result_formatter_agent.format_results(
                query=query,
                results=all_results,
                query_context=query_context
            )
            
            # 更新状态
            return {
                "formatted_results": formatted_results,
                "status": "completed",
                "stage": "completed",
                "previous_stage": state.get("stage"),
                "messages": [SystemMessage(content=f"Results formatted: {formatted_results.get('summary', '')}")]
            }
        except Exception as e:
            error_message = f"Results formatting failed: {str(e)}"
            print(error_message)
            return {
                "status": "error",
                "stage": "error",
                "previous_stage": state.get("stage"),
                "error": error_message,
                "messages": [SystemMessage(content=error_message)]
            }
    
    def refine_entities(state: QueryState) -> Dict:
        """根据初步标准化结果refinement候选类集合"""
        try:
            # 检查是否已有normalized_query结果
            normalized_query_obj = state.get("normalized_query")
            if not normalized_query_obj or not isinstance(normalized_query_obj, NormalizedQuery):
                return {
                    "status": "error",
                    "stage": "error", 
                    "error": "Cannot refine entities: normalized_query missing or invalid",
                    "messages": [SystemMessage(content="Cannot refine entities: normalized_query missing or invalid")]
                }
            
            available_classes = state.get("available_classes", [])
            if not available_classes:
                print("Warning: No available_classes found, skipping refinement")
                return {
                    "status": state.get("status", "refinement_skipped"),
                    "stage": "refinement_skipped",
                    "previous_stage": state.get("stage"),
                    "messages": [SystemMessage(content="Refinement skipped: no available classes")]
                }
            
            # 创建EntityMatcher并检查是否需要refinement
            entity_matcher = EntityMatcher(available_classes)
            entities = normalized_query_obj.relevant_entities

            print(f"首次查询实体: {entities}")
            
            if not entity_matcher.needs_refinement(entities):
                print("Entities refinement not needed - all entities found in available classes")
                return {
                    "status": state.get("status", "refinement_not_needed"),
                    "stage": "refinement_not_needed", 
                    "previous_stage": state.get("stage"),
                    "messages": [SystemMessage(content="Entity refinement not needed")]
                }
            
            # 生成候选类集合 - 使用新的排序检索
            ranked_results = entity_matcher.extract_ranked_candidate_classes(entities)
            stats = entity_matcher.get_ranked_refinement_stats(entities)
            
            # 从排序结果中提取候选类名（用于向后兼容）
            candidate_classes = set()
            for entity_candidates in ranked_results.values():
                for candidate, score in entity_candidates:
                    candidate_classes.add(candidate)
            candidate_classes = sorted(list(candidate_classes))
            
            print(f"[ENTITY REFINEMENT] {stats}")
            
            # 安全检查：如果候选集太小，不使用refinement
            if len(candidate_classes) < 3:
                print(f"Warning: Candidate set too small ({len(candidate_classes)}), skipping refinement")
                return {
                    "status": state.get("status", "refinement_skipped"),
                    "stage": "refinement_skipped",
                    "previous_stage": state.get("stage"),
                    "messages": [SystemMessage(content=f"Refinement skipped: candidate set too small ({len(candidate_classes)})")]
                }
            
            return {
                "refined_classes": candidate_classes,
                "status": "entities_refined",
                "stage": "entities_refined",
                "previous_stage": state.get("stage"),
                "messages": [SystemMessage(content=f"Entities refined: {len(candidate_classes)} candidate classes generated (reduction: {stats['reduction_ratio']:.2%})")]
            }
            
        except Exception as e:
            error_message = f"Entity refinement failed: {str(e)}"
            print(error_message)
            return {
                "status": "error",
                "stage": "error",
                "previous_stage": state.get("stage"),
                "error": error_message,
                "messages": [SystemMessage(content=error_message)]
            }
    
    def refine_query_decision(state: QueryState) -> Dict:
        """增强QueryRefiner决策节点 - 完善状态传递和记忆利用"""
        try:
            # 从state获取ontology_tools
            ontology_tools = state.get("ontology_tools")
            if not ontology_tools:
                raise ValueError("ontology_tools not found in state")
            
            validation_report = state.get("validation_report")
            if not validation_report:
                # 没有验证报告，跳过refiner
                return {
                    "status": state.get("status", "refiner_skipped"),
                    "stage": "refiner_skipped",
                    "previous_stage": state.get("stage"),
                    "messages": [SystemMessage(content="Refiner skipped: no validation report")]
                }
            
            # 创建QueryRefiner实例
            query_refiner = QueryRefiner(ontology_tools)
            
            # 传递完整的状态信息给QueryRefiner，包括记忆和历史
            enhanced_state = {
                **state,
                "query_results": state.get("query_results"),  # 用于获取工具调用信息
                "tried_tool_calls": state.get("tried_tool_calls", {}),  # 记忆系统
                "iteration_history": state.get("iteration_history", []),  # 历史信息
                "refined_classes": state.get("refined_classes", []),  # 当前候选类
                "available_classes": state.get("available_classes", [])  # 全部可用类
            }
            
            # 使用QueryRefiner分析并决策
            refiner_decision = query_refiner.propose_next_action(enhanced_state, validation_report)
            
            logger.info(f"[refine_query_decision] Refiner决策: {refiner_decision.overall_action}")
            
            # 获取当前retry_count
            current_retry_count = state.get("retry_count", 0)
            
            # 基于决策更新状态
            result = {
                "refiner_decision": refiner_decision,
                "status": f"refiner_{refiner_decision.overall_action}",
                "stage": "refiner_decision",
                "previous_stage": state.get("stage"),
                "messages": [SystemMessage(content=f"Refiner decision: {refiner_decision.overall_action} - {refiner_decision.reason}")]
            }
            
            # 保持关键状态信息
            if state.get("tried_tool_calls"):
                result["tried_tool_calls"] = state["tried_tool_calls"]
            if state.get("iteration_history"):
                result["iteration_history"] = state["iteration_history"]
            
            # 基于决策类型进行不同处理 - 简化版本
            if refiner_decision.overall_action == "continue":
                # 继续：保持当前结果和retry_count
                result["validation_success"] = True
                result["retry_count"] = current_retry_count
            elif refiner_decision.overall_action == "terminate":
                # 终止：设置终止标志，保持当前retry_count
                result["should_terminate"] = True
                result["retry_count"] = current_retry_count
                result["termination_reason"] = refiner_decision.reason
            else:
                # 所有其他情况（主要是retry）：递增retry_count并传递hints给下一轮执行
                new_retry_count = current_retry_count + 1
                result["retry_count"] = new_retry_count
                result["refiner_hints"] = refiner_decision.tool_call_hints
                print(f"[refiner_decision] 递增retry_count: {current_retry_count} -> {new_retry_count}")
                print(f"[refiner_decision] 传递 {len(refiner_decision.tool_call_hints)} 个hints进行重试")
                print(f"[refiner_decision] 设置的hints: {refiner_decision.tool_call_hints}")
                print(f"[refiner_decision] result keys: {result.keys()}")
                print(f"[refiner_decision] result['refiner_hints']: {result['refiner_hints']}")
            
            return result
            
        except Exception as e:
            error_message = f"Query refiner decision failed: {str(e)}"
            logger.error(error_message)
            return {
                "status": "error",
                "stage": "error",
                "previous_stage": state.get("stage"),
                "error": error_message,
                "messages": [SystemMessage(content=error_message)]
            }
    
    # Add nodes
    workflow.add_node("normalize", normalize_query)
    workflow.add_node("refine_entities", refine_entities)  # 新增refinement节点
    workflow.add_node("strategy", determine_strategy)
    workflow.add_node("execute", execute_query)
    workflow.add_node("validate", validate_results)
    workflow.add_node("refine_decision", refine_query_decision)  # NEW: QueryRefiner决策节点
    workflow.add_node("generate_hypothetical_document", generate_hypothetical_document)  # 新增节点
    workflow.add_node("supplement_parse_definitions", supplement_parse_definitions)  # NEW: 补充节点
    workflow.add_node("format_results", format_results)  # 新增节点
    
    # Define conditional edges for enhanced error handling and intelligent routing
    def decide_next_node(state: QueryState):
        # 检查是否存在错误状态
        if state.get("status") == "error":
            print(f"Workflow ending due to error at stage: {state.get('stage')}, Error: {state.get('error')}")
            return END

        # 获取当前阶段和重试计数
        current_stage = state.get("stage")
        current_state = state.get("status")
        retry_count = state.get("retry_count", 0)
        print(f"Current stage: {current_stage}, Status: {current_state}, Retry count: {retry_count}")
        
        # 智能终止条件检查
        if state.get("should_terminate") or retry_count >= MAX_RETRY_COUNT:
            if retry_count >= MAX_RETRY_COUNT:
                termination_reason = f"已超出最大重试次数限制 ({MAX_RETRY_COUNT} 轮)，终止查询处理"
                print(f"[decide_next_node] {termination_reason}")
            else:
                termination_reason = state.get("termination_reason", f"Maximum retry limit reached ({retry_count})")
                print(f"[decide_next_node] 终止工作流: {termination_reason}")
            return "format_results"
        
        # NEW: 增强的Refiner决策路由
        if current_stage == "refiner_decision":
            refiner_decision = state.get("refiner_decision")
            validation_report = state.get("validation_report")
            
            print(f"[decide_next_node] State中的refiner_hints: {state.get('refiner_hints', 'NOT_FOUND')}")
            print(f"[decide_next_node] State keys: {list(state.keys())}")
            
            if refiner_decision:
                action = refiner_decision.overall_action
                print(f"[decide_next_node] Refiner决策: {action}")
                
                if action == "continue":
                    # 验证成功，先补充parse_class_definition再格式化结果
                    return "supplement_parse_definitions"
                elif action == "terminate":
                    # 明确终止
                    print("[decide_next_node] Refiner决策终止")
                    return "format_results"
                else:
                    # 所有其他情况（主要是retry）：基于hints类型决定路由
                    hints = refiner_decision.tool_call_hints
                    if not hints:
                        print("[decide_next_node] 无可用hints，默认路由到normalize")
                        return "normalize"
                    
                    # 统计各种action类型
                    replace_tool_hints = [h for h in hints if h.action == "replace_tool"]
                    replace_class_hints = [h for h in hints if h.action == "replace_class"]
                    replace_both_hints = [h for h in hints if h.action == "replace_both"]  # 新增
                    skip_hints = [h for h in hints if h.action == "skip"]
                    
                    print(f"[decide_next_node] Hints分析: replace_tool={len(replace_tool_hints)}, replace_class={len(replace_class_hints)}, replace_both={len(replace_both_hints)}, skip={len(skip_hints)}")
                    
                    # 如果全部都是skip，终止重试
                    if len(skip_hints) == len(hints):
                        print("[decide_next_node] 所有hints都是skip，终止重试")
                        return "format_results"
                    
                    
                    # 根据hint类型决定路由
                    if replace_both_hints or (replace_class_hints and replace_tool_hints):
                        # replace_both 或 混合情况：需要改类也需要改工具 → 路由到normalize
                        print("[decide_next_node] 需要同时更换类和工具 → normalize")
                        return "normalize"
                    elif replace_class_hints and not replace_tool_hints:
                        # 只需要更换类 → 路由到normalize (标准化agent)
                        print("[decide_next_node] 仅需更换类 → normalize")  
                        return "normalize"
                    elif replace_tool_hints and not replace_class_hints:
                        # 只需要更换工具 → 路由到strategy (planner agent)
                        print("[decide_next_node] 仅需更换工具 → strategy")
                        return "strategy"
                    else:
                        # 其他情况，默认重试normalize
                        print("[decide_next_node] 其他hint情况，默认重试 → normalize")
                        return "normalize"
            else:
                print("[decide_next_node] 缺少refiner_decision，继续到format_results")
                return "format_results"
        
        # 验证后统一进入refiner决策节点，但先检查边界情况
        if current_stage == "validated":
            # 检查是否存在遗漏概念社区的边界情况
            validation_report = state.get("validation_report")
            if validation_report and hasattr(validation_report, 'message') and "BOUNDARY_CASE: MISSING_COMMUNITY" in validation_report.message:
                print("[decide_next_node] 检测到遗漏概念社区边界情况，直接路由到refiner进行实体扩展")
                # 设置特殊标记，让refiner知道这是实体扩展任务
                return "refine_decision"
            else:
                return "refine_decision"
        
        # 传统重试逻辑（保留作为后备，但优先级降低）
        if current_stage == "validated" and current_state == "warning" and not state.get("refiner_decision"):
            print(f"[decide_next_node] 进入传统重试逻辑, Retry count: {retry_count}")
            if retry_count <= MAX_RETRY_COUNT - 2:  # 允许到retry_count=2
                return "normalize"
            elif retry_count == MAX_RETRY_COUNT - 1:  # retry_count=3时
                return "generate_hypothetical_document"
            else:
                print(f"[decide_next_node] 超出重试次数 ({retry_count})")
                return "format_results"

        # 标准流程节点决策
        if current_stage == "normalized":
            return "refine_entities"  # 标准化后进行entity refinement
        elif current_stage == "entities_refined" or current_stage == "refinement_not_needed" or current_stage == "refinement_skipped":
            return "strategy"  # refinement完成后进入策略阶段
        elif current_stage == "strategy":
            return "execute"
        elif current_stage == "executed":
            return "validate"
        elif current_stage == "hypothetical_generated":
            return "normalize"  # 生成假设性文档后返回到标准化阶段
        elif current_stage == "supplement_completed" or current_stage == "supplement_not_needed" or current_stage == "supplement_skipped":
            return "format_results"  # 补充完成后进入结果格式化
        elif current_stage == "completed":
            return END

        # 默认情况（包括其他未明确处理的状态）
        print(f"Warning: Unexpected state '{current_stage}' reached. Ending workflow.")
        return END
    
    # Add edges using the conditional logic
    workflow.add_edge(START, "generate_hypothetical_document")
    workflow.add_conditional_edges("normalize", decide_next_node)
    workflow.add_conditional_edges("refine_entities", decide_next_node)  # 新增refinement节点的边
    workflow.add_conditional_edges("strategy", decide_next_node)
    workflow.add_conditional_edges("execute", decide_next_node)
    workflow.add_conditional_edges("validate", decide_next_node)
    workflow.add_conditional_edges("refine_decision", decide_next_node)  # 修复：添加缺失的refine_decision路由
    workflow.add_conditional_edges("generate_hypothetical_document", decide_next_node)  # 新增边
    workflow.add_conditional_edges("supplement_parse_definitions", decide_next_node)  # NEW: 补充节点路由
    workflow.add_edge("format_results", END)  # 修复：format_results直接连接到END，避免循环
    
    # 编译工作流
    compiled_graph = workflow.compile()
    return compiled_graph 