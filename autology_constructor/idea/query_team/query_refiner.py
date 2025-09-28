"""
查询智能优化器 - QueryRefiner

重构为支持细粒度工具调用级别的决策和hints生成。
为每个工具-参数组合提供具体的行动指导和替代方案。
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import logging
from .ontology_tools import OntologyTools
from .schemas import ValidationReport, ValidationClassification, ToolCallClassification, RefinerDecision, ToolCallHint
# Moved to function-level imports to avoid circular dependency

logger = logging.getLogger(__name__)


class QueryRefiner:
    """查询智能优化器 - 细粒度版本
    
    职责：
    1. 分析每个工具调用的分类结果
    2. 为每个工具-参数组合生成具体的hints
    3. 使用get_class_richness_info评估替代类
    4. 提供整体的行动决策
    """
    
    def __init__(self, ontology_tools: OntologyTools):
        """初始化QueryRefiner
        
        Args:
            ontology_tools: 本体工具实例，用于评估类的丰富度
        """
        self.ontology_tools = ontology_tools
        
    def propose_next_action(self, state, validation_report: ValidationReport) -> RefinerDecision:
        """基于细粒度验证结果决定下一步行动
        
        Args:
            state: 当前查询状态
            validation_report: 包含每个工具调用分类的验证报告
            
        Returns:
            RefinerDecision: 包含整体行动和每个工具调用的具体hints
        """
        try:
            # NEW: 检查边界情况：遗漏概念社区
            if hasattr(validation_report, 'message') and "Missing conceptual communities detected" in validation_report.message:
                logger.info("[QueryRefiner] 检测到遗漏概念社区边界情况，生成实体扩展建议")
                return self._generate_missing_community_decision(state, validation_report)
            
            logger.info(f"[QueryRefiner] 开始分析 {len(validation_report.tool_classifications)} 个工具调用")
            
            retry_count = state.get("retry_count", 0)
            
            # 为每个工具调用生成hints
            tool_call_hints = []
            print(f"[DEBUG-REFINER] Starting hint generation for {len(validation_report.tool_classifications)} tool classifications")
            for i, tool_classification in enumerate(validation_report.tool_classifications):
                print(f"[DEBUG-REFINER] Processing tool classification {i}: {tool_classification}")
                hint = self._generate_tool_call_hint(state, tool_classification)
                print(f"[DEBUG-REFINER] Generated hint {i}: {hint}, type: {type(hint)}")
                if hint:
                    tool_call_hints.append(hint)
                    print(f"[DEBUG-REFINER] Added hint {i} to tool_call_hints")
                else:
                    print(f"[DEBUG-REFINER] Hint {i} is None, not adding to list")
            
            print(f"[DEBUG-REFINER] Final tool_call_hints: {tool_call_hints}")
            print(f"[DEBUG-REFINER] Final tool_call_hints count: {len(tool_call_hints)}")
            print(f"[DEBUG-REFINER] Final tool_call_hints types: {[type(h) for h in tool_call_hints]}")
            
            # 基于个别hints决定整体行动
            overall_action = self._determine_overall_action(validation_report, tool_call_hints, retry_count)
            
            # 生成决策推理
            reason = self._generate_decision_reason(validation_report, tool_call_hints, overall_action, retry_count)
            
            decision = RefinerDecision(
                overall_action=overall_action,
                reason=reason,
                tool_call_hints=tool_call_hints
            )
            
            logger.info(f"[QueryRefiner] 决策完成: {overall_action}, 生成了 {len(tool_call_hints)} 个工具hints")
            
            return decision
            
        except Exception as e:
            logger.error(f"[QueryRefiner] 决策过程出错: {e}")
            return RefinerDecision(
                overall_action="terminate",
                reason=f"Decision process failed: {e}",
                tool_call_hints=[]
            )
    
    def _generate_tool_call_hint(self, state, tool_classification: ToolCallClassification) -> Optional[ToolCallHint]:
        """为单个工具调用生成hint
        
        Args:
            state: 当前状态
            tool_classification: 工具调用分类结果
            
        Returns:
            ToolCallHint或None
        """
        try:
            classification = tool_classification.classification
            tool = tool_classification.tool
            class_name = tool_classification.class_name
            
            # 获取已尝试过的类列表
            tried_classes = self._get_tried_classes_for_tool(state, tool)
            tried_classes_str = ", ".join(tried_classes) if tried_classes else "none"
            
            # 基于分类决定行动
            if classification == ValidationClassification.SUFFICIENT:
                # 结果充分，无需额外行动
                return None
            
            elif classification == ValidationClassification.INSUFFICIENT_PROPERTIES:
                # 缺乏属性信息，建议使用更详细的工具
                return ToolCallHint(
                    tool=tool,
                    class_name=class_name,
                    action="replace_tool",
                    hint=f"Try more detailed tools like parse_class_definition or get_class_properties for class '{class_name}'",
                    alternative_tools=["parse_class_definition", "get_class_properties", "get_related_classes"]
                )
            
            elif classification == ValidationClassification.INSUFFICIENT_CONNECTIONS:
                # 缺失联系信息，建议使用获取属性和相关类工具
                return ToolCallHint(
                    tool=tool,
                    class_name=class_name,
                    action="replace_tool",
                    hint=f"Missing connection information for class '{class_name}'. Try tools that reveal relationships and properties.",
                    alternative_tools=["get_class_properties", "get_related_classes"]
                )
            
            elif classification == ValidationClassification.INSUFFICIENT:
                # 一般信息不足，策略取决于当前使用的工具
                if tool == "parse_class_definition":
                    # 已经用了最详细的工具，问题在于类本身，只替换类
                    return ToolCallHint(
                        tool=tool,
                        class_name=class_name,
                        action="replace_class",
                        hint=f"Used detailed tool '{tool}' but results still insufficient for '{class_name}'. Try different classes with potentially richer information. Previously tried classes: {tried_classes_str}.",
                        alternative_tools=[]
                    )
                else:
                    # 未用最详细工具，需要既换工具又考虑换类
                    return ToolCallHint(
                        tool=tool,
                        class_name=class_name,
                        action="replace_both",  # 新的action类型
                        hint=f"Results insufficient from '{tool}' on '{class_name}'. Try more detailed tools AND consider different classes. Previously tried classes for {tool}: {tried_classes_str}.",
                        alternative_tools=["parse_class_definition", "get_class_properties"]
                    )
            
            elif classification == ValidationClassification.NO_RESULTS:
                # 无结果，优先尝试替代类
                return ToolCallHint(
                    tool=tool,
                    class_name=class_name,
                    action="replace_class",
                    hint=f"No results found for '{class_name}'. Try different classes from available options. Previously tried: {tried_classes_str}. Look for related or alternative class names.",
                    alternative_tools=["parse_class_definition"] if not tried_classes else []
                )
            
            elif classification == ValidationClassification.ERROR:
                # 执行错误，跳过或尝试简单工具
                return ToolCallHint(
                    tool=tool,
                    class_name=class_name,
                    action="skip",
                    hint=f"Execution error occurred with {tool}({class_name}). Consider skipping or using simpler tools.",
                    alternative_tools=["get_class_info"]  # 最简单的工具
                )
            
            return None
            
        except Exception as e:
            logger.error(f"[QueryRefiner] 生成工具hint失败: {e}")
            return None
    
    def _get_tried_classes_for_tool(self, state, tool_name: str) -> List[str]:
        """获取特定工具已经尝试过的类列表
        
        Args:
            state: 当前状态
            tool_name: 工具名称
            
        Returns:
            已尝试过的类名列表
        """
        tried_calls = state.get("tried_tool_calls", {})
        tried_classes = []
        
        for call_info in tried_calls.values():
            if call_info.get("tool") == tool_name:
                params = call_info.get("params", {})
                class_names = params.get("class_names") or params.get("class_name")
                
                # 修复：正确处理列表和单个值
                if isinstance(class_names, list):
                    for class_name in class_names:
                        if class_name and class_name not in tried_classes:
                            tried_classes.append(class_name)
                elif class_names and class_names not in tried_classes:
                    tried_classes.append(class_names)
        
        return tried_classes
    
    def _get_alternative_classes(self, state, original_class: str, aggressive: bool = False) -> List[str]:
        """获取替代类，按丰富度排序
        
        Args:
            state: 当前状态
            original_class: 原始类名
            aggressive: 是否使用更激进的搜索策略
            
        Returns:
            按丰富度排序的替代类列表
        """
        try:
            # 从refined_classes或available_classes中获取候选
            refined_classes = state.get("refined_classes", [])
            available_classes = state.get("available_classes", [])
            
            if aggressive and len(refined_classes) < 20:
                # 激进模式：使用更大的候选集
                candidate_pool = available_classes[:100]  # 限制范围避免过慢
            else:
                candidate_pool = refined_classes
            
            # 移除原始类
            candidate_pool = [cls for cls in candidate_pool if cls != original_class]
            
            if not candidate_pool:
                return []
            
            # 使用丰富度评估前10个候选
            top_candidates = candidate_pool
            ranked_candidates, _ = self._rank_classes_by_richness_simple(state, top_candidates)
            
            # 返回前3-5个最佳选择
            return ranked_candidates[:5] if aggressive else ranked_candidates[:3]
            
        except Exception as e:
            logger.error(f"[QueryRefiner] 获取替代类失败: {e}")
            return []
    
    def _rank_classes_by_richness_simple(self, state, candidates: List[str]) -> Tuple[List[str], Dict]:
        """简化版的丰富度排序"""
        # Local import to avoid circular dependency
        from .workflow_utils import generate_tool_call_signature, has_tool_call_been_tried
        
        if not candidates:
            return [], {}
        
        try:
            scored_candidates = []
            
            for class_name in candidates:
                # 检查缓存
                tool_params = {"class_name": class_name}
                if has_tool_call_been_tried(state, "get_class_richness_info", tool_params):
                    signature = generate_tool_call_signature("get_class_richness_info", tool_params)
                    tried_calls = state.get("tried_tool_calls", {})
                    richness_info = tried_calls[signature]["result"]
                else:
                    # 使用QueryManager的共享锁保护
                    from .query_manager import QueryManager
                    lock = QueryManager.get_shared_lock()
                    if lock:
                        with lock:
                            richness_info = self.ontology_tools.get_class_richness_info(class_name)
                    else:
                        richness_info = self.ontology_tools.get_class_richness_info(class_name)
                
                score = richness_info.get("richness_score", 0.0)
                scored_candidates.append((class_name, score))
            
            # 按分数排序
            scored_candidates.sort(key=lambda x: x[1], reverse=True)
            ranked_classes = [item[0] for item in scored_candidates]
            
            stats = {
                "evaluated_count": len(candidates),
                "top_score": scored_candidates[0][1] if scored_candidates else 0.0
            }
            
            return ranked_classes, stats
            
        except Exception as e:
            logger.error(f"[QueryRefiner] 简化丰富度排序失败: {e}")
            return candidates, {"error": str(e)}
    
    def _determine_overall_action(self, validation_report: ValidationReport, 
                                tool_call_hints: List[ToolCallHint], retry_count: int) -> str:
        """基于所有工具调用的validation结果确定整体行动"""
        
        # 检查所有工具调用是否都充分
        all_sufficient = all(
            tc.classification == ValidationClassification.SUFFICIENT 
            for tc in validation_report.tool_classifications
        )
        
        # 如果所有工具调用都充分，继续到格式化
        if all_sufficient:
            return "continue"
        
        # 如果重试次数过多，终止
        if retry_count >= 4:  # MAX_RETRY_COUNT = 4
            return "terminate"
        
        # 否则就是重试（让decide_next_node基于具体的hints决定路由）
        return "retry"
    
    def _generate_decision_reason(self, validation_report: ValidationReport, 
                                tool_call_hints: List[ToolCallHint],
                                overall_action: str, retry_count: int) -> str:
        """生成决策推理说明"""
        
        total_tools = len(validation_report.tool_classifications)
        actionable_hints = len([h for h in tool_call_hints if h.action != "skip"])
        
        if overall_action == "continue":
            return f"All {total_tools} tool calls were sufficient, continuing workflow"
        
        elif overall_action == "retry":
            return f"Generated {actionable_hints} actionable hints for {total_tools} tool calls (retry #{retry_count + 1})"
        
        elif overall_action == "expand":
            return f"Insufficient hints generated, expanding search space (retry #{retry_count + 1})"
        
        elif overall_action == "terminate":
            if retry_count >= 4:  # MAX_RETRY_COUNT = 4
                return f"Maximum retry limit reached ({retry_count}), terminating"
            else:
                return f"No viable improvement options found, terminating"
        
    def _generate_missing_community_decision(self, state, validation_report: ValidationReport) -> RefinerDecision:
        """生成遗漏概念社区的处理决策（基于全局分析和相似类匹配）"""
        
        # 1. 从state中获取global_assessment
        global_assessment = state.get("global_assessment")
        if not global_assessment:
            logger.warning("[QueryRefiner] 未找到global_assessment，无法处理缺失社区")
            return self._fallback_decision()
        
        # 2. 获取已使用的类集合，确定topk
        used_classes = self._get_all_used_classes_from_tool_calls(state)
        topk = max(len(used_classes) + 3, 10)  # 至少比已用类多3个，最少10个
        
        # 3. 用全局分析文本在全量类集合中进行相似度匹配
        available_classes = state.get("available_classes", [])
        community_analysis_text = global_assessment.community_analysis
        
        candidate_classes = self._find_similar_classes_with_text(
            community_analysis_text, available_classes, topk
        )
        
        # 4. 排除已使用的类，得到缺失类集合
        missing_classes = [cls for cls in candidate_classes if cls not in used_classes]
        
        # 5. 生成一个hint，建议parse_class_definition
        if missing_classes:
            # 只生成一个hint，使用第一个缺失类
            hint = ToolCallHint(
                tool="parse_class_definition",
                class_name=missing_classes[0],
                action="replace_class",
                hint=f"Global analysis suggests missing conceptual communities. Try detailed analysis of '{missing_classes[0]}' which appears to be part of missing concept groups.",
                alternative_tools=["parse_class_definition", "get_class_properties"]
            )
            
            reason = f"Missing conceptual communities detected. Found {len(missing_classes)} candidate classes, focusing on: {missing_classes[0]}"
            
            return RefinerDecision(
                overall_action="retry",
                reason=reason,
                tool_call_hints=[hint]
            )
        else:
            return self._fallback_decision()
    
    def _find_similar_classes_with_text(self, text: str, available_classes: List[str], topk: int) -> List[str]:
        """用文本在类集合中进行相似度匹配"""
        from .entity_matcher import EntityMatcher
        
        if not text or not available_classes:
            return []
        
        entity_matcher = EntityMatcher(available_classes)
        
        # 使用EntityMatcher的search方法进行相似度匹配
        matches = entity_matcher.search(text, k=topk)
        
        # 返回匹配的类名列表
        return [match[0] for match in matches]  # match是(class_name, score)元组
    
    def _get_all_used_classes_from_tool_calls(self, state) -> List[str]:
        """获取已经在工具调用中使用的所有类"""
        used_classes = set()
        tried_tool_calls = state.get("tried_tool_calls", {})
        
        for call_info in tried_tool_calls.values():
            params = call_info.get("params", {})
            
            # 检查各种可能的参数名
            for param_name in ['class_name', 'class_names', 'classes']:
                if param_name in params:
                    value = params[param_name]
                    if isinstance(value, str):
                        used_classes.add(value)
                    elif isinstance(value, list):
                        used_classes.update(value)
        
        return list(used_classes)
    
    def _fallback_decision(self) -> RefinerDecision:
        """备用决策"""
        return RefinerDecision(
            overall_action="terminate",
            reason="Missing community processing failed, terminating",
            tool_call_hints=[]
        )
        
        return f"Action: {overall_action}, retry count: {retry_count}"