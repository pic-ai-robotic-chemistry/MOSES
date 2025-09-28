from typing import List, Dict, Any, Optional
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from autology_constructor.idea.query_team.utils import parse_json
from .base_finder import BaseFinder, FinderState


class MetaScienceFinder(BaseFinder):
    """元科学分析器
    
    该类用于深层次分析本体结构与知识，并进行跨本体比较以寻找潜在的偏差和偏见：
    1. 分析本体结构、关系及其表示知识的方式
    2. 跨本体比较知识结构和表示偏好
    3. 识别概念化、分类体系和价值导向的差异
    4. 发现潜在的认知偏见、理论局限和盲点
    """
    
    def _get_analysis_prompt(self) -> ChatPromptTemplate:
        """返回分析元科学问题的提示模板"""
        return ChatPromptTemplate.from_template("""
        你是一位专注于元科学分析的AI助手。请对下面的本体进行深层次分析，识别潜在的知识论偏差、偏见和盲点。
        
        ## 领域分析
        {domain_analysis}
        
        ## 任务
        1. 分析本体结构及其反映的思维模式和分类体系
        2. 比较不同本体间的概念化差异和理论前提
        3. 识别本体中的价值导向、默认假设和潜在偏见
        4. 发现知识表示中的盲点和未被充分考虑的视角
        5. 评估不同本体之间知识整合的可能性和挑战
        
        ## 输出格式
        请以JSON格式输出，包含以下字段：
        ```json
        [
          {{
            "id": "meta_science_gap_1",
            "name": "元科学问题名称",
            "description": "详细描述元科学问题",
            "gap_type": "认知偏见|结构局限|盲点|价值偏向|理论冲突|整合挑战",
            "domains_involved": ["相关领域1", "相关领域2"],
            "implications": "问题的科学影响和意义",
            "research_value": "高|中|低",
            "research_difficulty": "高|中|低"
          }}
        ]
        ```
        
        ## 注意
        - 深入分析本体背后的哲学和方法论前提
        - 识别可能被学科惯性或传统掩盖的问题
        - 寻找跨领域整合可能揭示的新视角
        """)
    
    def _get_ideation_prompt(self) -> ChatPromptTemplate:
        """返回基于元科学问题生成研究创意的提示模板"""
        return ChatPromptTemplate.from_template("""
        你是一位专注于元科学和科学哲学的研究专家。基于以下元科学问题分析，提出前沿的研究创意。
        
        ## 元科学问题
        {gaps}
        
        ## 任务
        为每个元科学问题生成一个具有突破性的研究创意，研究创意应该：
        1. 挑战现有的知识表示范式或理论前提
        2. 提出新的概念框架或跨学科整合方法
        3. 解决本体中的认知偏见或理论盲点
        
        ## 输出格式
        请以JSON格式输出，包含以下字段：
        ```json
        [
          {{
            "id": "idea_1",
            "gap_reference": "对应的元科学问题ID",
            "title": "研究标题",
            "description": "详细研究描述",
            "methodology": "拟使用的研究方法",
            "expected_outcome": "预期研究成果",
            "significance": "研究意义",
            "novelty": "高|中|低",
            "feasibility": "高|中|低"
          }}
        ]
        ```
        
        ## 注意
        - 创意应该具有哲学深度和方法论创新性
        - 考虑跨学科视角和方法的融合
        - 关注研究如何改变科学知识的生产和组织方式
        """)
    
    def analyze_gaps(self, domain_analysis: Dict) -> List[Dict]:
        """分析领域中的元科学问题"""
        # 检查是否有跨领域分析结果
        cross_domain = domain_analysis.get("cross_domain", {})
        if not cross_domain:
            return []  # 没有跨领域分析，无法进行元科学分析
        
        # 从跨领域分析中提取关键信息
        source_domain = cross_domain.get("source_domain_info", {})
        target_domain = cross_domain.get("target_domain_info", {})
        
        # 分析本体结构
        source_structure = self._analyze_ontology_structure(domain_analysis.get("key_concepts", []))
        target_structure = self._analyze_ontology_structure(cross_domain.get("target_domain_concepts", []))
        
        # 识别潜在的元科学问题
        meta_science_gaps = []
        
        # 1. 分析分类体系差异
        if source_structure["hierarchy_depth"] != target_structure["hierarchy_depth"]:
            meta_science_gaps.append({
                "id": "meta_science_gap_1",
                "name": "分类体系复杂性差异",
                "description": f"源本体与目标本体的层次结构复杂性存在差异（深度：{source_structure['hierarchy_depth']} vs {target_structure['hierarchy_depth']}），这可能反映了不同的知识组织范式",
                "gap_type": "结构局限",
                "domains_involved": [source_domain.get("name", "源领域"), target_domain.get("name", "目标领域")],
                "implications": "不同的分类复杂性可能导致知识表示的不完整或过度简化",
                "research_value": "中",
                "research_difficulty": "中"
            })
        
        # 2. 分析属性表示偏好
        if source_structure["avg_properties_per_concept"] > target_structure["avg_properties_per_concept"] * 1.5:
            meta_science_gaps.append({
                "id": "meta_science_gap_2",
                "name": "属性详细度偏见",
                "description": f"源本体比目标本体使用更详细的属性描述（平均每概念属性数：{source_structure['avg_properties_per_concept']} vs {target_structure['avg_properties_per_concept']}），可能反映研究关注点偏好",
                "gap_type": "认知偏见",
                "domains_involved": [source_domain.get("name", "源领域"), target_domain.get("name", "目标领域")],
                "implications": "属性描述详细度的差异可能导致某些领域知识被过分强调或忽略",
                "research_value": "高",
                "research_difficulty": "中"
            })
        
        # 3. 分析关系类型差异
        if source_structure["relation_types"] != target_structure["relation_types"]:
            missing_relations = set(source_structure["relation_types"]) - set(target_structure["relation_types"])
            additional_relations = set(target_structure["relation_types"]) - set(source_structure["relation_types"])
            
            description = "本体间使用了不同类型的关系来表示知识："
            if missing_relations:
                description += f" 源本体独有的关系类型：{', '.join(missing_relations)};"
            if additional_relations:
                description += f" 目标本体独有的关系类型：{', '.join(additional_relations)};"
            
            meta_science_gaps.append({
                "id": "meta_science_gap_3",
                "name": "关系表示类型差异",
                "description": description,
                "gap_type": "理论冲突",
                "domains_involved": [source_domain.get("name", "源领域"), target_domain.get("name", "目标领域")],
                "implications": "不同的关系类型可能反映理论框架和因果解释模型的差异",
                "research_value": "高",
                "research_difficulty": "高"
            })
        
        # 4. 分析概念表示偏好
        core_source_concepts = source_structure.get("core_concepts", [])
        core_target_concepts = target_structure.get("core_concepts", [])
        
        if core_source_concepts and core_target_concepts:
            # 比较核心概念类型
            source_concept_types = [c.split("_")[0] if "_" in c else c for c in core_source_concepts]
            target_concept_types = [c.split("_")[0] if "_" in c else c for c in core_target_concepts]
            
            # 检查概念类型分布
            source_type_counts = {}
            for t in source_concept_types:
                source_type_counts[t] = source_type_counts.get(t, 0) + 1
                
            target_type_counts = {}
            for t in target_concept_types:
                target_type_counts[t] = target_type_counts.get(t, 0) + 1
            
            # 找出差异最大的概念类型
            all_types = set(source_type_counts.keys()) | set(target_type_counts.keys())
            type_diffs = {}
            for t in all_types:
                src_count = source_type_counts.get(t, 0)
                tgt_count = target_type_counts.get(t, 0)
                if src_count > 0 and tgt_count > 0:
                    ratio = max(src_count, tgt_count) / min(src_count, tgt_count)
                    if ratio > 2:  # 比例差异超过2倍
                        type_diffs[t] = (src_count, tgt_count, ratio)
            
            # 从差异中生成元科学问题
            if type_diffs:
                for i, (concept_type, (src_count, tgt_count, ratio)) in enumerate(type_diffs.items()):
                    emphasis = "源本体" if src_count > tgt_count else "目标本体"
                    meta_science_gaps.append({
                        "id": f"meta_science_gap_{len(meta_science_gaps)+1}",
                        "name": f"{concept_type}概念强调偏向",
                        "description": f"{emphasis}中{concept_type}类型的概念比例明显较高（{max(src_count, tgt_count)}:{min(src_count, tgt_count)}），反映了不同领域的概念强调偏好",
                        "gap_type": "价值偏向",
                        "domains_involved": [source_domain.get("name", "源领域"), target_domain.get("name", "目标领域")],
                        "implications": f"对{concept_type}概念的不同强调可能导致研究方向和问题框定的系统性差异",
                        "research_value": "中",
                        "research_difficulty": "中"
                    })
        
        # 5. 寻找潜在的整合挑战
        integrable_concepts = cross_domain.get("integrable_concepts", [])
        if len(integrable_concepts) < 5:  # 可整合概念较少
            meta_science_gaps.append({
                "id": f"meta_science_gap_{len(meta_science_gaps)+1}",
                "name": "本体整合挑战",
                "description": "两个领域本体间可整合概念较少，表明存在本质性的理论或方法论差异",
                "gap_type": "整合挑战",
                "domains_involved": [source_domain.get("name", "源领域"), target_domain.get("name", "目标领域")],
                "implications": "本体整合困难可能反映根本性的认识论差异或范式差异",
                "research_value": "高",
                "research_difficulty": "高"
            })
        
        # 使用LLM增强元科学问题描述
        if meta_science_gaps:
            llm = ChatOpenAI()
            analysis_prompt = self._get_analysis_prompt().format(
                domain_analysis=str(domain_analysis)
            )
            
            try:
                llm_response = llm.invoke(analysis_prompt)
                enhanced_gaps = parse_json(llm_response.content)
                if enhanced_gaps and isinstance(enhanced_gaps, list):
                    return enhanced_gaps
            except Exception as e:
                print(f"LLM分析元科学问题失败: {str(e)}")
        
        return meta_science_gaps
    
    def _analyze_ontology_structure(self, concepts: List[Dict]) -> Dict:
        """分析本体结构特征"""
        if not concepts:
            return {
                "hierarchy_depth": 0,
                "avg_properties_per_concept": 0,
                "relation_types": [],
                "core_concepts": []
            }
        
        # 计算层次结构深度
        max_depth = 0
        for concept in concepts:
            depth = concept.get("depth", 0)
            if depth > max_depth:
                max_depth = depth
        
        # 计算平均每个概念的属性数
        total_properties = 0
        relation_types = set()
        
        for concept in concepts:
            properties = concept.get("properties", [])
            total_properties += len(properties)
            
            # 收集关系类型
            for prop in properties:
                prop_type = prop.get("type", "")
                if prop_type:
                    relation_types.add(prop_type)
        
        avg_properties = total_properties / len(concepts) if concepts else 0
        
        # 识别核心概念（基于连接度或其他重要性指标）
        # 简单实现：选择属性数最多的前30%概念
        concepts_by_property_count = sorted(concepts, key=lambda c: len(c.get("properties", [])), reverse=True)
        core_count = max(1, int(len(concepts) * 0.3))
        core_concepts = [c.get("name", "") for c in concepts_by_property_count[:core_count]]
        
        return {
            "hierarchy_depth": max_depth,
            "avg_properties_per_concept": avg_properties,
            "relation_types": list(relation_types),
            "core_concepts": core_concepts
        }
    
    def _parse_gaps(self, content: str) -> List[Dict]:
        """解析LLM返回的元科学问题"""
        try:
            gaps = parse_json(content)
            if not isinstance(gaps, list):
                return []
            
            # 确保每个gap有必要的字段
            validated_gaps = []
            for gap in gaps:
                if "id" in gap and "name" in gap and "description" in gap:
                    if "meta_science_gap_" not in gap["id"]:
                        gap["id"] = f"meta_science_gap_{gap.get('id', '')}"
                    validated_gaps.append(gap)
            
            return validated_gaps
        except Exception as e:
            print(f"解析元科学问题失败: {str(e)}")
            return []
    
    def _parse_ideas(self, content: str) -> List[Dict]:
        """解析LLM返回的研究创意"""
        try:
            ideas = parse_json(content)
            if not isinstance(ideas, list):
                return []
            
            # 确保每个idea有必要的字段
            validated_ideas = []
            for idea in ideas:
                if "id" in idea and "title" in idea and "description" in idea:
                    if "idea_" not in idea["id"]:
                        idea["id"] = f"idea_{idea.get('id', '')}"
                    validated_ideas.append(idea)
            
            return validated_ideas
        except Exception as e:
            print(f"解析研究创意失败: {str(e)}")
            return []
    
    def find_gaps(self, domain_analysis: Dict) -> List[Dict]:
        """兼容性方法，调用analyze_gaps"""
        return self.analyze_gaps(domain_analysis) 