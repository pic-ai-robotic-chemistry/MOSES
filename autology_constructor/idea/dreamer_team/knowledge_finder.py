from typing import List, Dict, Any, Optional
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from owlready2 import *
from autology_constructor.idea.query_team.utils import parse_json
from .base_finder import BaseFinder, FinderState


class KnowledgeFinder(BaseFinder):
    """知识空白分析器
    
    该类使用封闭世界假设和Owlready2推理引擎查找本体中的不一致类：
    1. 将本体转换为封闭世界假设模式
    2. 使用推理引擎识别逻辑不一致
    3. 分析不一致原因并提出研究创意
    """
    
    def _get_analysis_prompt(self) -> ChatPromptTemplate:
        """返回分析知识空白的提示模板"""
        return ChatPromptTemplate.from_template("""
        你是一位专注于分析本体知识一致性的AI助手。请分析下面领域本体中存在的知识不一致性和潜在知识空白。
        
        ## 领域分析
        {domain_analysis}
        
        ## 不一致类分析
        {inconsistent_classes}
        
        ## 任务
        1. 分析每个不一致类的问题原因
        2. 确定知识表示中的逻辑矛盾
        3. 识别概念定义不完整或不准确的地方
        4. 发现知识空白和需要澄清的领域
        
        ## 输出格式
        请以JSON格式输出，包含以下字段：
        ```json
        [
          {{
            "id": "knowledge_gap_1",
            "name": "知识空白名称",
            "description": "知识空白的详细描述",
            "related_classes": ["相关类1", "相关类2"],
            "inconsistency_type": "类型矛盾|属性矛盾|关系矛盾|定义不完整",
            "research_value": "高|中|低",
            "research_difficulty": "高|中|低"
          }}
        ]
        ```
        
        ## 注意
        - 重点关注有明确研究价值的知识空白
        - 提供足够详细的描述以支持后续研究
        - 考虑知识表示和推理的角度
        """)
    
    def _get_ideation_prompt(self) -> ChatPromptTemplate:
        """返回基于知识空白生成研究创意的提示模板"""
        return ChatPromptTemplate.from_template("""
        你是一位专注于解决知识表示和推理问题的研究专家。基于以下知识空白分析，提出有价值的研究创意。
        
        ## 知识空白
        {gaps}
        
        ## 任务
        为每个知识空白生成一个具体、可行的研究创意，研究创意应该：
        1. 直接解决所识别的知识不一致或空白
        2. 提出明确的研究方法来完善或修正知识
        3. 考虑知识表示、推理或本体工程的改进
        
        ## 输出格式
        请以JSON格式输出，包含以下字段：
        ```json
        [
          {{
            "id": "idea_1",
            "gap_reference": "对应的知识空白ID",
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
        - 确保每个创意能够实际解决对应的知识空白
        - 研究方法应该合理且与问题匹配
        - 创意应该具有学术价值和原创性
        """)
    
    def analyze_gaps(self, domain_analysis: Dict) -> List[Dict]:
        """分析领域中的知识空白"""
        # 尝试获取本体
        source_ontology = domain_analysis.get("source_ontology")
        if not source_ontology:
            # 没有本体，使用领域分析结果模拟
            return self._analyze_from_domain_analysis(domain_analysis)
        
        # 有本体，使用Owlready2进行推理
        try:
            # 尝试将本体转换为封闭世界假设模式
            inconsistent_classes = self._find_inconsistent_classes(source_ontology)
            
            # 使用LLM分析不一致类
            llm = ChatOpenAI()
            analysis_prompt = self._get_analysis_prompt().format(
                domain_analysis=str(domain_analysis),
                inconsistent_classes=str(inconsistent_classes)
            )
            
            llm_response = llm.invoke(analysis_prompt)
            knowledge_gaps = parse_json(llm_response.content)
            
            if knowledge_gaps and isinstance(knowledge_gaps, list):
                return knowledge_gaps
        except Exception as e:
            print(f"使用推理引擎分析知识空白失败: {str(e)}")
        
        # 如果推理失败，回退到使用领域分析
        return self._analyze_from_domain_analysis(domain_analysis)
    
    def _find_inconsistent_classes(self, ontology) -> List[Dict]:
        """使用Owlready2推理引擎查找不一致的类"""
        try:
            # 为安全起见，使用本体的副本
            onto_copy = ontology
            
            # 开启推理引擎
            with onto_copy:
                # 将本体设置为封闭世界假设模式
                # 注意：实际使用时需要确认Owlready2的具体API
                sync_reasoner_pellet(onto_copy, infer_property_values=True, 
                                   infer_data_property_values=True)
            
            # 查找不一致的类
            inconsistent_classes = []
            
            # 检查本体一致性
            # 注意：Owlready2的API可能与此不同，需根据实际情况调整
            for cls in onto_copy.classes():
                # 检查是否被分类为Nothing类的子类，这通常表示矛盾
                if cls.is_a and Thing in cls.is_a and Nothing in cls.is_a:
                    inconsistent_classes.append({
                        "class_name": cls.name,
                        "properties": [p.name for p in cls.get_properties()],
                        "parents": [c.name for c in cls.is_a if c != Thing and c != Nothing],
                        "restrictions": [str(r) for r in cls.is_a if not isinstance(r, ThingClass)]
                    })
            
            return inconsistent_classes
        except Exception as e:
            print(f"查找不一致类失败: {str(e)}")
            return []
    
    def _analyze_from_domain_analysis(self, domain_analysis: Dict) -> List[Dict]:
        """从领域分析结果中推断可能的知识空白"""
        # 从领域分析中提取关键信息
        key_concepts = domain_analysis.get("key_concepts", [])
        
        # 检查定义不完整的概念
        incomplete_concepts = []
        for concept in key_concepts:
            concept_name = concept.get("name", "")
            properties = concept.get("properties", [])
            
            # 检查属性是否完整
            if len(properties) < 2:  # 简单启发式：属性太少可能表示定义不完整
                incomplete_concepts.append({
                    "concept": concept_name,
                    "properties_count": len(properties),
                    "reason": "属性数量不足"
                })
            
            # 检查关系是否存在潜在冲突
            property_domains = {}
            for prop in properties:
                prop_name = prop.get("name", "")
                prop_range = prop.get("range", "")
                
                if prop_range in property_domains:
                    # 同一个值域有多个属性，可能存在冗余或冲突
                    property_domains[prop_range].append(prop_name)
                else:
                    property_domains[prop_range] = [prop_name]
        
        # 找出可能存在逻辑矛盾的概念
        potential_contradictions = []
        for concept in key_concepts:
            concept_name = concept.get("name", "")
            properties = concept.get("properties", [])
            
            # 检查是否有互斥的属性值
            property_values = {}
            for prop in properties:
                prop_name = prop.get("name", "")
                prop_value = prop.get("value")
                
                if prop_name in property_values and prop_value != property_values[prop_name]:
                    # 同一属性有不同的值，可能存在矛盾
                    potential_contradictions.append({
                        "concept": concept_name,
                        "property": prop_name,
                        "values": [property_values[prop_name], prop_value],
                        "reason": "属性值冲突"
                    })
                else:
                    property_values[prop_name] = prop_value
        
        # 生成知识空白
        knowledge_gaps = []
        
        # 从不完整概念生成空白
        for i, incomplete in enumerate(incomplete_concepts):
            knowledge_gaps.append({
                "id": f"knowledge_gap_{i+1}",
                "name": f"{incomplete['concept']}的知识不完整",
                "description": f"概念{incomplete['concept']}的定义不完整，只有{incomplete['properties_count']}个属性",
                "related_classes": [incomplete['concept']],
                "inconsistency_type": "定义不完整",
                "research_value": "中",
                "research_difficulty": "中"
            })
        
        # 从潜在矛盾生成空白
        for i, contradiction in enumerate(potential_contradictions):
            knowledge_gaps.append({
                "id": f"knowledge_gap_{len(incomplete_concepts)+i+1}",
                "name": f"{contradiction['concept']}的{contradiction['property']}属性冲突",
                "description": f"概念{contradiction['concept']}的{contradiction['property']}属性有多个不同的值: {contradiction['values']}",
                "related_classes": [contradiction['concept']],
                "inconsistency_type": "属性矛盾",
                "research_value": "高",
                "research_difficulty": "中"
            })
        
        # 使用LLM增强知识空白描述
        if knowledge_gaps:
            llm = ChatOpenAI()
            analysis_prompt = self._get_analysis_prompt().format(
                domain_analysis=str(domain_analysis),
                inconsistent_classes=str(knowledge_gaps)
            )
            
            try:
                llm_response = llm.invoke(analysis_prompt)
                enhanced_gaps = parse_json(llm_response.content)
                if enhanced_gaps and isinstance(enhanced_gaps, list):
                    return enhanced_gaps
            except Exception as e:
                print(f"LLM分析知识空白失败: {str(e)}")
        
        return knowledge_gaps
    
    def _parse_gaps(self, content: str) -> List[Dict]:
        """解析LLM返回的知识空白分析结果"""
        try:
            gaps = parse_json(content)
            if not isinstance(gaps, list):
                return []
            
            # 确保每个gap有必要的字段
            validated_gaps = []
            for gap in gaps:
                if "id" in gap and "name" in gap and "description" in gap:
                    if "knowledge_gap_" not in gap["id"]:
                        gap["id"] = f"knowledge_gap_{gap.get('id', '')}"
                    validated_gaps.append(gap)
            
            return validated_gaps
        except Exception as e:
            print(f"解析知识空白失败: {str(e)}")
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