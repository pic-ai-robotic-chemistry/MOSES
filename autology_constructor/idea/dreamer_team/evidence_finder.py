from typing import List, Dict, Any, TypedDict, Annotated, Optional, Literal
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from autology_constructor.idea.query_team.utils import parse_json
from .base_finder import BaseFinder, FinderState


class EvidenceFinder(BaseFinder):
    """证据冲突分析器
    
    该类用于分析本体中基于sourcedInformation的证据冲突，主要功能：
    1. 检查同一关系使用了不同证据源
    2. 分析不同证据源之间的潜在冲突
    3. 根据冲突提出研究创意
    """
    
    def _get_analysis_prompt(self) -> ChatPromptTemplate:
        """返回分析证据冲突的提示模板"""
        return ChatPromptTemplate.from_template("""
        你是一位专注于分析科学证据冲突的AI助手。请分析下面的领域本体中存在的证据冲突，特别关注sourcedInformation属性。
        
        ## 领域分析
        {domain_analysis}
        
        ## 任务
        1. 识别具有多个不同证据来源的同一关系或属性
        2. 分析这些证据之间是否存在潜在冲突、矛盾或不一致
        3. 寻找证据缺乏、证据质量问题或证据争议的领域
        
        ## 输出格式
        请以JSON格式输出，包含以下字段：
        ```json
        [
          {{
            "id": "evidence_gap_1",
            "name": "冲突名称",
            "description": "冲突详细描述",
            "relation": "存在冲突的关系",
            "evidence_sources": ["证据来源1", "证据来源2"],
            "conflict_type": "直接矛盾|方法学差异|结论差异|强度差异",
            "research_value": "高|中|低",
            "research_difficulty": "高|中|低"
          }}
        ]
        ```
        
        ## 注意
        - 只关注有明确证据来源不同的关系
        - 证据冲突应该有明确的科学研究价值
        - 每个冲突应包含足够细节以支持后续研究
        """)
    
    def _get_ideation_prompt(self) -> ChatPromptTemplate:
        """返回基于证据冲突生成研究创意的提示模板"""
        return ChatPromptTemplate.from_template("""
        你是一位专注于解决科学证据冲突的研究专家。基于以下证据冲突分析，提出有针对性的研究创意。
        
        ## 证据冲突
        {gaps}
        
        ## 任务
        为每个证据冲突生成一个具体、可行的研究创意，研究创意应该：
        1. 直接解决所识别的证据冲突
        2. 提出明确的研究方法学来调和或解释冲突
        3. 具有科学意义和实际应用价值
        
        ## 输出格式
        请以JSON格式输出，包含以下字段：
        ```json
        [
          {{
            "id": "idea_1",
            "gap_reference": "对应的冲突ID",
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
        - 确保每个创意能够实际解决对应的证据冲突
        - 研究方法应该合理且与问题匹配
        - 创意应该具有学术价值和原创性
        """)
    
    def analyze_gaps(self, domain_analysis: Dict) -> List[Dict]:
        """分析领域中的证据冲突"""
        # 从领域分析中提取关键信息
        key_concepts = domain_analysis.get("key_concepts", [])
        
        # 使用本体工具查找有sourcedInformation属性的关系
        sourced_relations = []
        relations_by_source = {}
        
        # 模拟从本体中提取的证据来源信息
        # 实际实现中，应该使用OntologyTools从本体中获取这些信息
        for concept in key_concepts:
            concept_name = concept.get("name", "")
            properties = concept.get("properties", [])
            
            for prop in properties:
                if "evidence_source" in prop or "sourcedInformation" in prop:
                    relation_key = f"{concept_name}.{prop.get('name')}"
                    source = prop.get("evidence_source", prop.get("sourcedInformation", "unknown"))
                    
                    sourced_relations.append({
                        "concept": concept_name,
                        "relation": prop.get("name"),
                        "value": prop.get("value"),
                        "source": source
                    })
                    
                    # 按证据来源分组
                    if relation_key not in relations_by_source:
                        relations_by_source[relation_key] = {}
                    
                    if source not in relations_by_source[relation_key]:
                        relations_by_source[relation_key][source] = []
                    
                    relations_by_source[relation_key][source].append(prop.get("value"))
        
        # 找出有多个不同证据来源的关系
        conflicts = []
        for relation_key, sources in relations_by_source.items():
            if len(sources) > 1:  # 有多个不同的证据来源
                concept, relation = relation_key.split(".")
                
                # 检查值是否存在冲突
                values_by_source = {src: vals for src, vals in sources.items()}
                
                # 添加到冲突列表
                conflicts.append({
                    "id": f"evidence_gap_{len(conflicts)+1}",
                    "name": f"{relation}关系的证据冲突",
                    "description": f"概念{concept}的{relation}关系有多个不同的证据来源，可能存在冲突",
                    "relation": relation,
                    "concept": concept,
                    "evidence_sources": list(sources.keys()),
                    "values_by_source": values_by_source,
                    "conflict_type": "结论差异",  # 默认值，实际应该分析冲突类型
                    "research_value": "中",
                    "research_difficulty": "中"
                })
        
        # 使用LLM进一步分析和增强冲突描述
        if conflicts:
            llm = ChatOpenAI()
            analysis_prompt = self._get_analysis_prompt().format(
                domain_analysis=str(domain_analysis),
                conflicts=str(conflicts)
            )
            
            try:
                llm_response = llm.invoke(analysis_prompt)
                enhanced_conflicts = parse_json(llm_response.content)
                if enhanced_conflicts and isinstance(enhanced_conflicts, list):
                    return enhanced_conflicts
            except Exception as e:
                print(f"LLM分析证据冲突失败: {str(e)}")
        
        return conflicts
    
    def _parse_gaps(self, content: str) -> List[Dict]:
        """解析LLM返回的证据冲突分析结果"""
        try:
            gaps = parse_json(content)
            if not isinstance(gaps, list):
                return []
            
            # 确保每个gap有必要的字段
            validated_gaps = []
            for gap in gaps:
                if "id" in gap and "name" in gap and "description" in gap:
                    if "gap_" not in gap["id"]:
                        gap["id"] = f"evidence_gap_{gap.get('id', '')}"
                    validated_gaps.append(gap)
            
            return validated_gaps
        except Exception as e:
            print(f"解析证据冲突失败: {str(e)}")
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