from typing import List, Dict, Any, Optional
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from autology_constructor.idea.query_team.utils import parse_json
from .base_finder import BaseFinder, FinderState


class MethodologyFinder(BaseFinder):
    """方法论迁移分析器
    
    该类用于分析一个本体中的方法论是否可以应用到其他本体中：
    1. 从源本体中识别方法论相关概念和属性
    2. 分析这些方法论是否可以迁移到目标本体
    3. 提出跨领域方法论迁移的研究创意
    """
    
    def _get_analysis_prompt(self) -> ChatPromptTemplate:
        """返回分析方法论迁移机会的提示模板"""
        return ChatPromptTemplate.from_template("""
        你是一位专注于跨领域方法论迁移的AI助手。请分析下面的跨领域分析结果，寻找方法论迁移的机会。
        
        ## 领域分析
        {domain_analysis}
        
        ## 任务
        1. 识别源本体中的方法论相关概念、属性和关系
        2. 分析这些方法论是否可以迁移到目标本体中
        3. 找出方法论迁移的机会和挑战
        4. 关注方法论适用性、迁移难度和潜在价值
        
        ## 输出格式
        请以JSON格式输出，包含以下字段：
        ```json
        [
          {{
            "id": "methodology_gap_1",
            "name": "方法论迁移机会名称",
            "description": "详细描述方法论迁移机会",
            "source_methodology": "源本体中的方法论名称",
            "target_domain": "目标领域名称",
            "adaptation_required": "高|中|低",
            "research_value": "高|中|低",
            "research_difficulty": "高|中|低"
          }}
        ]
        ```
        
        ## 注意
        - 重点关注有实际迁移价值的方法论
        - 考虑方法论迁移的科学合理性
        - 分析方法论迁移所需的适应和调整
        """)
    
    def _get_ideation_prompt(self) -> ChatPromptTemplate:
        """返回基于方法论迁移机会生成研究创意的提示模板"""
        return ChatPromptTemplate.from_template("""
        你是一位专注于跨领域方法论创新的研究专家。基于以下方法论迁移机会分析，提出有价值的研究创意。
        
        ## 方法论迁移机会
        {gaps}
        
        ## 任务
        为每个方法论迁移机会生成一个具体、可行的研究创意，研究创意应该：
        1. 明确说明如何将源领域方法论迁移到目标领域
        2. 提出必要的适应和修改步骤
        3. 阐述迁移后方法论的应用场景和价值
        
        ## 输出格式
        请以JSON格式输出，包含以下字段：
        ```json
        [
          {{
            "id": "idea_1",
            "gap_reference": "对应的方法论迁移机会ID",
            "title": "研究标题",
            "description": "详细研究描述",
            "methodology": "方法论迁移和适应方法",
            "expected_outcome": "预期研究成果",
            "significance": "研究意义",
            "novelty": "高|中|低",
            "feasibility": "高|中|低"
          }}
        ]
        ```
        
        ## 注意
        - 确保每个创意能够实际实现对应的方法论迁移
        - 研究方法应该详细说明迁移过程
        - 创意应该具有学术价值和原创性
        """)
    
    def analyze_gaps(self, domain_analysis: Dict) -> List[Dict]:
        """分析跨领域方法论迁移机会"""
        # 检查是否有跨领域分析结果
        cross_domain = domain_analysis.get("cross_domain", {})
        if not cross_domain:
            return []  # 没有跨领域分析，无法分析方法论迁移
        
        # 从跨领域分析中提取关键信息
        source_concepts = cross_domain.get("source_domain_concepts", [])
        target_concepts = cross_domain.get("target_domain_concepts", [])
        analogies = cross_domain.get("analogies", [])
        
        # 尝试识别方法论相关概念
        methodology_concepts = []
        
        # 根据关键词识别可能的方法论概念
        methodology_keywords = ["method", "技术", "方法", "procedure", "protocol", 
                               "approach", "technique", "methodology", "实验", 
                               "experiment", "分析", "analysis", "测试", "test"]
        
        for concept in source_concepts:
            concept_name = concept.get("name", "").lower()
            # 检查概念名称是否包含方法论相关关键词
            if any(keyword in concept_name for keyword in methodology_keywords):
                methodology_concepts.append(concept)
            # 或者检查概念描述是否与方法论相关
            elif concept.get("description") and any(keyword in concept.get("description", "").lower() for keyword in methodology_keywords):
                methodology_concepts.append(concept)
        
        # 找出方法论迁移机会
        migration_opportunities = []
        
        # 基于类比关系寻找迁移机会
        for i, method_concept in enumerate(methodology_concepts):
            method_name = method_concept.get("name", "")
            
            # 寻找目标领域中可能适用该方法论的概念
            for analogy in analogies:
                if analogy.get("source_concept") == method_name or method_name in analogy.get("source_related_concepts", []):
                    target_concept = analogy.get("target_concept")
                    
                    # 创建迁移机会
                    migration_opportunities.append({
                        "id": f"methodology_gap_{i+1}",
                        "name": f"将{method_name}应用到{target_concept}",
                        "description": f"基于{analogy.get('similarity_type', '概念')}相似性，探索将{method_name}方法论迁移到{target_concept}的可能性",
                        "source_methodology": method_name,
                        "target_domain": target_concept,
                        "similarity_basis": analogy.get('similarity_description', '概念相似'),
                        "adaptation_required": "中",
                        "research_value": "中",
                        "research_difficulty": "中"
                    })
        
        # 如果没有足够的基于类比的机会，尝试更广泛的搜索
        if len(migration_opportunities) < 3:
            # 遍历目标领域概念，寻找可能适用方法论的场景
            for i, method_concept in enumerate(methodology_concepts):
                method_name = method_concept.get("name", "")
                
                for target_concept in target_concepts:
                    target_name = target_concept.get("name", "")
                    
                    # 避免重复已有的机会
                    if not any(opp.get("target_domain") == target_name and opp.get("source_methodology") == method_name 
                             for opp in migration_opportunities):
                        
                        # 创建潜在的迁移机会
                        migration_opportunities.append({
                            "id": f"methodology_gap_{len(migration_opportunities)+1}",
                            "name": f"探索{method_name}在{target_name}中的应用",
                            "description": f"探索将源领域的{method_name}方法论迁移到目标领域的{target_name}概念的可能性",
                            "source_methodology": method_name,
                            "target_domain": target_name,
                            "similarity_basis": "潜在应用场景",
                            "adaptation_required": "高",
                            "research_value": "中",
                            "research_difficulty": "高"
                        })
                        
                        # 限制潜在机会数量
                        if len(migration_opportunities) >= 5:
                            break
                
                if len(migration_opportunities) >= 5:
                    break
        
        # 使用LLM增强机会描述
        if migration_opportunities:
            llm = ChatOpenAI()
            analysis_prompt = self._get_analysis_prompt().format(
                domain_analysis=str(domain_analysis)
            )
            
            try:
                llm_response = llm.invoke(analysis_prompt)
                enhanced_opportunities = parse_json(llm_response.content)
                if enhanced_opportunities and isinstance(enhanced_opportunities, list):
                    return enhanced_opportunities
            except Exception as e:
                print(f"LLM分析方法论迁移机会失败: {str(e)}")
        
        return migration_opportunities
    
    def _parse_gaps(self, content: str) -> List[Dict]:
        """解析LLM返回的方法论迁移机会"""
        try:
            gaps = parse_json(content)
            if not isinstance(gaps, list):
                return []
            
            # 确保每个gap有必要的字段
            validated_gaps = []
            for gap in gaps:
                if "id" in gap and "name" in gap and "description" in gap:
                    if "methodology_gap_" not in gap["id"]:
                        gap["id"] = f"methodology_gap_{gap.get('id', '')}"
                    validated_gaps.append(gap)
            
            return validated_gaps
        except Exception as e:
            print(f"解析方法论迁移机会失败: {str(e)}")
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