"""查询工作流工具函数

此模块包含用于查询工作流状态管理的工具函数，包括：
- 工具调用签名生成和记录
- LLM停滞检测
- 状态管理相关的辅助函数
- 内部工具过滤和结果清理
"""

from typing import Dict, List, Literal, Optional, Any, Union, Set, Tuple
from datetime import datetime
import hashlib
import json
import logging
from .stategraph import QueryState

logger = logging.getLogger(__name__)

def generate_tool_call_signature(tool_name: str, params: Dict) -> str:
    """生成标准化的工具调用签名
    
    Args:
        tool_name: 工具函数名
        params: 参数字典
        
    Returns:
        唯一的调用签名字符串
    """
    # 标准化参数字典：排序并序列化
    normalized_params = json.dumps(params, sort_keys=True, ensure_ascii=False)
    
    # 创建签名字符串
    signature_content = f"{tool_name}:{normalized_params}"
    
    # 生成哈希以确保签名长度可控
    signature_hash = hashlib.md5(signature_content.encode('utf-8')).hexdigest()
    
    return f"{tool_name}_{signature_hash[:8]}"

def record_tool_call(state: QueryState, tool_name: str, params: Dict, result: Any) -> Dict:
    """记录工具调用到tried_tool_calls中
    
    Args:
        state: 当前QueryState
        tool_name: 工具名
        params: 参数
        result: 调用结果
        
    Returns:
        更新后的state片段
    """
    signature = generate_tool_call_signature(tool_name, params)
    
    # 初始化tried_tool_calls如果不存在
    tried_calls = state.get("tried_tool_calls", {})
    
    # 记录这次调用
    tried_calls[signature] = {
        "tool": tool_name,
        "params": params,
        "result": result,
        "timestamp": datetime.now().isoformat(),
        "retry_count": state.get("retry_count", 0)
    }
    
    return {"tried_tool_calls": tried_calls}

def has_tool_call_been_tried(state: QueryState, tool_name: str, params: Dict) -> bool:
    """检查特定工具调用是否已被尝试过
    
    Args:
        state: 当前QueryState
        tool_name: 工具名
        params: 参数
        
    Returns:
        是否已尝试过
    """
    signature = generate_tool_call_signature(tool_name, params)
    tried_calls = state.get("tried_tool_calls", {})
    return signature in tried_calls

def filter_internal_tools(tried_tool_calls: Dict) -> Dict:
    """过滤内部工具调用，排除用于系统决策而非用户查询的工具
    
    Args:
        tried_tool_calls: 原始工具调用记录
        
    Returns:
        过滤后的工具调用记录
    """
    # 定义内部工具列表 - 这些工具用于系统决策，不应包含在格式化结果中
    internal_tools = {
        'get_class_richness_info',  # 丰富度评估，用于内部决策
        'handle_stagnation',        # 停滞处理，系统内部工具
        'entity_matcher',           # 实体匹配，系统内部工具
    }
    
    filtered_calls = {}
    filtered_count = 0
    
    for signature, call_info in tried_tool_calls.items():
        tool_name = call_info.get("tool")
        if tool_name not in internal_tools:
            filtered_calls[signature] = call_info
        else:
            filtered_count += 1
    
    if filtered_count > 0:
        logger.info(f"过滤了 {filtered_count} 个内部工具调用")
    
    return filtered_calls

def clean_tool_results(tool_result: Dict) -> Dict:
    """清理工具结果，移除内部系统信息
    
    Args:
        tool_result: 单个工具调用结果
        
    Returns:
        清理后的工具结果
    """
    cleaned_result = tool_result.copy()
    
    # 如果result是字典，需要递归清理内部信息
    if isinstance(cleaned_result.get("result"), dict):
        result_data = cleaned_result["result"]
        
        # 遍历结果中的每个类，移除内部系统信息
        for class_name, class_data in result_data.items():
            if isinstance(class_data, dict):
                # 移除richness_score等内部评估信息
                internal_keys = {
                    'richness_score', 'property_count', 'sourced_info_count', 
                    'restriction_count', 'hierarchy_connections', 'details',
                    'richness_evaluations', 'class_candidates', 'tool_analysis'
                }
                
                for key in list(class_data.keys()):
                    if key in internal_keys:
                        del class_data[key]
    
    return cleaned_result

def detect_stagnation(state: QueryState) -> bool:
    """检测LLM是否在实体选择上停滞
    
    Args:
        state: 当前QueryState
        
    Returns:
        bool: 是否检测到停滞
    """
    iteration_history = state.get("iteration_history", [])
    if len(iteration_history) < 2:
        return False
    
    # 获取最近两次的实体选择
    current_entities = set((state.get("refined_classes") or [])[:5])  # 比较前5个
    previous_entities = set()
    
    # 从历史中查找上一次的refined_classes
    for i in range(len(iteration_history) - 1, -1, -1):
        if "refined_classes" in iteration_history[i]:
            previous_entities = set((iteration_history[i]["refined_classes"] or [])[:5])
            break
    
    if not previous_entities:
        return False
    
    # 计算相似度
    intersection = len(current_entities.intersection(previous_entities))
    union = len(current_entities.union(previous_entities))
    
    if union == 0:
        return False
    
    similarity = intersection / union
    
    # 如果相似度 > 0.8，认为是停滞
    return similarity > 0.8

def handle_stagnation_with_entity_matcher(state: QueryState, entity_matcher, ontology_tools) -> Dict:
    """处理LLM停滞，使用EntityMatcher为每个refined实体找到信息最丰富的近义词
    
    Args:
        state: 当前QueryState
        entity_matcher: EntityMatcher实例
        ontology_tools: OntologyTools实例
        
    Returns:
        包含新候选类的状态更新
    """
    try:
        logger.info("[StagnationHandler] 检测到LLM停滞，使用refined实体扩展候选池")
        
        # 获取当前refined_classes作为扩展基础
        refined_classes = state.get("refined_classes", [])
        
        if not refined_classes:
            logger.warning("[StagnationHandler] 没有refined_classes，回退到原始查询")
            original_query = state.get("query", "")
            if not original_query:
                logger.warning("[StagnationHandler] 缺少原始查询和refined_classes")
                return {}
            refined_classes = [original_query]
        
        logger.info(f"[StagnationHandler] 基于 {len(refined_classes)} 个refined实体扩展候选")
        
        # 为每个refined实体找到3个信息最丰富的近义词
        min_similarity = 0.5  # 降低最小相似度阈值，获取更多有意义的候选
        max_synonyms_per_entity = 3  # 每个实体最多3个近义词
        
        new_candidates = set()
        expansion_details = {}
        
        for entity in refined_classes:
            # 使用EntityMatcher找到高相似度的候选，包括替代选项
            similar_candidates = entity_matcher.find_ranked_candidates_for_entity(
                entity, k=10, include_alternatives=True  # 启用多样化候选
            )
            
            # 过滤相似度并评估丰富度
            entity_synonyms = []
            for candidate, similarity in similar_candidates:
                if similarity >= min_similarity and candidate != entity:
                    # 评估候选的丰富度
                    # 使用对象级锁保护ontology_tools调用
                    lock = state.get("ontology_tools_lock")
                    if lock:
                        with lock:
                            richness_info = ontology_tools.get_class_richness_info(candidate)
                    else:
                        richness_info = ontology_tools.get_class_richness_info(candidate)
                    richness_score = richness_info.get("richness_score", 0.0)
                    entity_synonyms.append((candidate, similarity, richness_score))
            
            # 按丰富度降序排序，取前3个
            entity_synonyms.sort(key=lambda x: x[2], reverse=True)
            top_synonyms = entity_synonyms[:max_synonyms_per_entity]
            
            # 记录扩展详情
            if top_synonyms:
                expansion_details[entity] = [
                    {"synonym": syn[0], "similarity": syn[1], "richness": syn[2]} 
                    for syn in top_synonyms
                ]
                # 添加到候选集合
                for syn, _, _ in top_synonyms:
                    new_candidates.add(syn)
                
                logger.info(f"[StagnationHandler] 为'{entity}'找到{len(top_synonyms)}个高质量近义词")
            else:
                logger.info(f"[StagnationHandler] 为'{entity}'未找到符合要求的近义词")
        
        if not new_candidates:
            logger.warning("[StagnationHandler] 未找到任何高质量的近义词候选")
            return {}
        
        # 将所有新候选按丰富度重新排序
        final_candidates = []
        for candidate in new_candidates:
            # 使用对象级锁保护ontology_tools调用
            lock = state.get("ontology_tools_lock")
            if lock:
                with lock:
                    richness_info = ontology_tools.get_class_richness_info(candidate)
            else:
                richness_info = ontology_tools.get_class_richness_info(candidate)
            richness_score = richness_info.get("richness_score", 0.0)
            final_candidates.append((candidate, richness_score))
        
        # 按丰富度排序
        final_candidates.sort(key=lambda x: x[1], reverse=True)
        ranked_candidates = [item[0] for item in final_candidates]
        
        # 记录这次操作到tried_tool_calls
        stagnation_record = record_tool_call(
            state, 
            "handle_stagnation", 
            {"method": "refined_entity_synonyms", "min_similarity": min_similarity}, 
            {
                "source_entities": len(refined_classes),
                "new_candidates_count": len(ranked_candidates),
                "avg_richness_score": sum(item[1] for item in final_candidates) / len(final_candidates),
                "expansion_details": expansion_details,
                "top_candidates": ranked_candidates[:10]
            }
        )
        
        logger.info(f"[StagnationHandler] 成功扩展得到 {len(ranked_candidates)} 个按丰富度排序的新候选")
        
        # 返回状态更新，直接注入最佳候选
        return {
            "refined_classes": ranked_candidates,
            "stagnation_handled": True,
            "stagnation_method": "refined_entity_synonyms",
            **stagnation_record
        }
        
    except Exception as e:
        logger.error(f"[StagnationHandler] 处理停滞失败: {e}")
        return {"stagnation_error": str(e)}

def get_tool_call_history(state: QueryState, tool_name: Optional[str] = None) -> List[Dict]:
    """获取工具调用历史
    
    Args:
        state: 当前QueryState
        tool_name: 可选的工具名过滤器
        
    Returns:
        工具调用历史列表
    """
    tried_calls = state.get("tried_tool_calls", {})
    
    if not tried_calls:
        return []
    
    history = []
    for signature, call_info in tried_calls.items():
        if tool_name is None or call_info.get("tool") == tool_name:
            history.append({
                "signature": signature,
                **call_info
            })
    
    # 按时间戳排序
    history.sort(key=lambda x: x.get("timestamp", ""))
    return history

def clear_tool_call_history(state: QueryState, tool_name: Optional[str] = None) -> Dict:
    """清除工具调用历史
    
    Args:
        state: 当前QueryState
        tool_name: 可选的工具名过滤器，如果为None则清除所有
        
    Returns:
        更新后的state片段
    """
    tried_calls = state.get("tried_tool_calls", {})
    
    if tool_name is None:
        # 清除所有
        return {"tried_tool_calls": {}}
    else:
        # 只清除特定工具的记录
        filtered_calls = {
            signature: call_info 
            for signature, call_info in tried_calls.items()
            if call_info.get("tool") != tool_name
        }
        return {"tried_tool_calls": filtered_calls}


# ====== 通用实体匹配工具函数 ======

from .entity_matcher import EntityMatcher


def auto_fix_entity_mismatch(
    target_entities: List[str],
    primary_classes: List[str],
    fallback_classes: Optional[List[str]] = None,
    min_score_threshold: float = 0.3,
    top_k: int = 1
) -> tuple[List[str], bool, Dict[str, str]]:
    """
    通用实体不匹配自动修正工具函数
    
    同时适用于：
    1. 标准化环节：检测实体是否在refined_classes中，不在则在original_classes中找替代
    2. planner环节：检测toolcall参数是否在相关实体中，不在则找最相似替代
    
    Args:
        target_entities: 待检查的目标实体列表
        primary_classes: 主要类集合（refined_classes 或 available_entities）
        fallback_classes: 备选类集合（original_classes，可选）
        min_score_threshold: 最小匹配分数阈值
        top_k: 每个实体考虑的候选数量
    
    Returns:
        Tuple of (corrected_entities, has_corrections, correction_mapping)
        - corrected_entities: 修正后的实体列表
        - has_corrections: 是否进行了修正
        - correction_mapping: 原实体 -> 修正实体的映射字典
    """
    
    if not target_entities:
        return [], False, {}
    
    logger.debug(f"[auto_fix_entity_mismatch] Target entities: {target_entities}")
    logger.debug(f"[auto_fix_entity_mismatch] Primary classes: {len(primary_classes)}, "
                f"Fallback classes: {len(fallback_classes) if fallback_classes else 0}")
    
    corrected_entities = []
    correction_mapping = {}
    has_corrections = False
    
    # 创建主要EntityMatcher
    primary_matcher = EntityMatcher(primary_classes)
    
    # 如果有fallback，也创建fallback matcher
    fallback_matcher = None
    if fallback_classes and len(fallback_classes) > len(primary_classes):
        fallback_matcher = EntityMatcher(fallback_classes)
    
    for entity in target_entities:
        corrected_entity = entity
        
        # Step 1: 检查是否在primary_classes中直接存在
        if entity in primary_classes:
            # 直接匹配，无需修正
            corrected_entities.append(entity)
            continue
        
        # Step 2: 在primary_classes中寻找相似匹配
        primary_candidates = primary_matcher.find_ranked_candidates_for_entity(entity, k=top_k)
        
        if primary_candidates and primary_candidates[0][1] >= min_score_threshold:
            # 在primary中找到了好的匹配
            corrected_entity = primary_candidates[0][0]
            logger.debug(f"[auto_fix] Primary match: '{entity}' -> '{corrected_entity}' "
                        f"(score: {primary_candidates[0][1]:.3f})")
        
        elif fallback_matcher:
            # Step 3: 如果primary中没找到好的匹配，尝试fallback
            fallback_candidates = fallback_matcher.find_ranked_candidates_for_entity(entity, k=top_k)
            
            if fallback_candidates and fallback_candidates[0][1] >= min_score_threshold:
                corrected_entity = fallback_candidates[0][0]
                logger.debug(f"[auto_fix] Fallback match: '{entity}' -> '{corrected_entity}' "
                            f"(score: {fallback_candidates[0][1]:.3f})")
            else:
                logger.warning(f"[auto_fix] No suitable match found for '{entity}'")
                # 保留原实体，即使没找到匹配
                corrected_entity = entity
        
        else:
            logger.warning(f"[auto_fix] No match for '{entity}' and no fallback available")
            # 保留原实体
            corrected_entity = entity
        
        # 记录结果
        corrected_entities.append(corrected_entity)
        if corrected_entity != entity:
            correction_mapping[entity] = corrected_entity
            has_corrections = True
    
    if has_corrections:
        corrections_str = ", ".join([f"'{orig}' -> '{new}'" for orig, new in correction_mapping.items()])
        logger.info(f"[auto_fix_entity_mismatch] Applied corrections: {corrections_str}")
    
    return corrected_entities, has_corrections, correction_mapping


def supplement_parse_definitions(state: QueryState) -> Dict:
    """全局评估通过后，自动为未使用parse_class_definition的类执行该工具
    
    Args:
        state: 当前QueryState
        
    Returns:
        更新后的状态字典
    """
    from langchain_core.messages import SystemMessage
    
    try:
        # 从 state 获取 ontology_tools
        ontology_tools = state.get("ontology_tools")
        if not ontology_tools:
            print("[supplement_parse_definitions] ontology_tools not found")
            return {
                "status": state.get("status", "supplement_skipped"),
                "stage": "supplement_skipped",
                "previous_stage": state.get("stage"),
                "messages": [SystemMessage(content="Supplement skipped: no ontology tools")]
            }
        
        # 获取当前的工具调用历史
        tried_tool_calls = state.get("tried_tool_calls", {})
        
        # 找出所有已经查询过的类名
        queried_classes = set()
        classes_with_parse_definition = set()
        
        for call_info in tried_tool_calls.values():
            tool_name = call_info.get("tool")
            params = call_info.get("params", {})
            class_name = params.get("class_name") or params.get("class_names")
            
            if class_name:
                if isinstance(class_name, list):
                    queried_classes.update(class_name)
                    if tool_name == "parse_class_definition":
                        classes_with_parse_definition.update(class_name)
                else:
                    queried_classes.add(class_name)
                    if tool_name == "parse_class_definition":
                        classes_with_parse_definition.add(class_name)
        
        # 找出需要补充 parse_class_definition 的类
        classes_need_supplement = queried_classes - classes_with_parse_definition
        
        if not classes_need_supplement:
            print("[supplement_parse_definitions] 所有类已经有parse_class_definition，无需补充")
            return {
                "status": state.get("status", "supplement_not_needed"),
                "stage": "supplement_not_needed",
                "previous_stage": state.get("stage"),
                "messages": [SystemMessage(content="Supplement not needed: all classes have parse_class_definition")]
            }
        
        print(f"[supplement_parse_definitions] 需要补充parse_class_definition的类: {classes_need_supplement}")
        
        # 执行补充的 parse_class_definition
        updated_tried_calls = tried_tool_calls.copy()
        for class_name in classes_need_supplement:
            try:
                print(f"[supplement_parse_definitions] 为类 {class_name} 执行parse_class_definition")
                # 使用对象级锁保护ontology_tools调用
                lock = state.get("ontology_tools_lock")
                if lock:
                    with lock:
                        definition_result = ontology_tools.parse_class_definition(class_name)
                else:
                    definition_result = ontology_tools.parse_class_definition(class_name)
                
                # 更新工具调用历史
                call_id = f"supplement_{class_name}_{len(updated_tried_calls)}"
                updated_tried_calls[call_id] = {
                    "tool": "parse_class_definition",
                    "params": {"class_name": class_name},
                    "result": definition_result
                }
                
            except Exception as e:
                print(f"[supplement_parse_definitions] 为类 {class_name} 执行parse_class_definition失败: {e}")
                # 继续处理其他类，不因单个失败而停止
        
        return {
            "status": state.get("status", "supplement_completed"),
            "stage": "supplement_completed",
            "previous_stage": state.get("stage"),
            "tried_tool_calls": updated_tried_calls,
            "messages": [SystemMessage(content=f"Supplemented parse_class_definition for {len(classes_need_supplement)} classes")]
        }
        
    except Exception as e:
        print(f"[supplement_parse_definitions] 执行过程中发生错误: {e}")
        return {
            "status": "error",
            "stage": "supplement_error",
            "previous_stage": state.get("stage"),
            "error": str(e),
            "messages": [SystemMessage(content=f"Supplement error: {str(e)}")]
        }


# ====== tried_tool_calls过滤和清理工具函数 ======

def filter_validated_tool_calls(tried_tool_calls: Dict) -> Dict:
    """基于新的过滤逻辑过滤工具调用
    
    新逻辑：只删除error、无结果和内部调用，其余结果按轮次倒序排列
    
    Args:
        tried_tool_calls: 原始工具调用记录
        
    Returns:
        过滤后的工具调用记录，按轮次倒序排列
    """
    
    # 首先过滤掉内部工具调用
    non_internal_calls = filter_internal_tools(tried_tool_calls)
    
    # 过滤掉error和无结果的调用（保留其他所有调用，不管是否有validator评价）
    filtered_calls = {}
    
    for call_id, call_info in non_internal_calls.items():
        # 检查结果是否为error
        result = call_info.get("result", {})
        
        # 跳过明显的错误结果
        if not result:  # 无结果
            continue
        if isinstance(result, dict) and "error" in result:  # 失败的调用
            continue
        
        # 检查是否是空内容的类信息（无结果）
        is_empty_result = False
        if isinstance(result, dict):
            for class_name, class_info in result.items():
                if isinstance(class_info, dict) and class_info.get("information") == []:
                    is_empty_result = True
                    break
        
        if is_empty_result:
            continue
            
        # 通过过滤的调用加入结果
        filtered_calls[call_id] = call_info
    
    # 按轮次（retry_count）倒序排列
    call_items = list(filtered_calls.items())
    call_items.sort(key=lambda x: x[1].get("retry_count", 0), reverse=True)
    
    # 重新构建有序字典
    ordered_filtered_calls = {}
    for call_id, call_info in call_items:
        ordered_filtered_calls[call_id] = call_info
    
    logger.info(f"[filter_validated_tool_calls] 原始调用: {len(tried_tool_calls)} 个")
    logger.info(f"[filter_validated_tool_calls] 过滤后调用: {len(ordered_filtered_calls)} 个")
    logger.info(f"[filter_validated_tool_calls] 按轮次倒序排列完成")
    
    return ordered_filtered_calls

def extract_class_name_from_params(params: Dict) -> str:
    """从参数中提取类名"""
    class_name = (params.get("class_name") or 
                 params.get("class_names") or 
                 params.get("classes") or "unknown")
    
    # 处理列表情况，取第一个
    if isinstance(class_name, list):
        return class_name[0] if class_name else "unknown"
    return str(class_name)

def select_best_call_for_class(class_calls: List[Tuple[str, Dict]]) -> Optional[str]:
    """为单个类选择最佳工具调用 - 旧逻辑，已被新的filter_validated_tool_calls替代
    
    策略：
    1. 过滤掉error和no_results
    2. 如果有sufficient的调用，按工具优先级选择最佳的一个
    3. 如果没有sufficient，保留第一个有效调用（按工具优先级排序）
    
    注意：此函数已不再被新的过滤逻辑使用，保留作为兼容性
    """
    
    # 工具优先级顺序
    TOOL_PRIORITY = {
        "parse_class_definition": 0,
        "get_class_properties": 1, 
        "get_related_classes": 2,
    }
    
    # 过滤掉失败和无结果的调用
    valid_calls = [
        (call_id, call_info) for call_id, call_info in class_calls
        if call_info.get("validation", {}).get("classification") not in ["error", "no_results"]
    ]
    
    if not valid_calls:
        logger.warning(f"[select_best_call_for_class] 没有有效的调用")
        return None
    
    # 检查是否有SUFFICIENT的调用
    sufficient_calls = [
        (call_id, call_info) for call_id, call_info in valid_calls
        if call_info.get("validation", {}).get("classification") == "sufficient"
    ]
    
    if sufficient_calls:
        # 有SUFFICIENT调用时，按工具优先级选择最佳的一个
        def priority_key(item):
            call_id, call_info = item
            tool_name = call_info.get("tool", "")
            return TOOL_PRIORITY.get(tool_name, 999)
        
        sufficient_calls.sort(key=priority_key)
        selected = sufficient_calls[0]
        logger.debug(f"[select_best_call_for_class] 选择sufficient调用: {selected[1].get('tool')}")
        return selected[0]
    else:
        # 没有SUFFICIENT时，选择工具优先级最高的有效调用
        def priority_key(item):
            call_id, call_info = item
            tool_name = call_info.get("tool", "")
            return TOOL_PRIORITY.get(tool_name, 999)
        
        valid_calls.sort(key=priority_key)
        selected = valid_calls[0]
        logger.debug(f"[select_best_call_for_class] 选择最佳有效调用: {selected[1].get('tool')}")
        return selected[0]