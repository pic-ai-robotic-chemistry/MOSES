from typing import Optional, Tuple
import numpy as np
from openai import OpenAI
from rapidfuzz import fuzz
from autology_constructor.base_data_structures import Entity
import re

class EntityMatcher:
    def __init__(self):
        self.client = OpenAI()
        
    def get_embedding(self, text: str) -> np.ndarray:
        """获取文本的embedding向量"""
        response = self.client.embeddings.create(
            model="text-embedding-3-large",
            input=text
        )
        return np.array(response.data[0].embedding)
    
    def semantic_context_match(self, entity1: Entity, entity2: Entity, threshold: float = 0.8) -> bool:
        """基于语义和上下文的匹配方法"""
        # 1. 组合name和information
        text1 = entity1.name
        text2 = entity2.name
        
        if entity1.information:
            text1 = f"{entity1.name}. {entity1.information}"
        if entity2.information:
            text2 = f"{entity2.name}. {entity2.information}"
            
        # 2. 获取embedding并计算相似度
        embedding1 = self.get_embedding(text1)
        embedding2 = self.get_embedding(text2)
        
        similarity = np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )
        
        return float(similarity) >= threshold
    
    def smart_match(self, entity1: Entity, entity2: Entity) -> bool:
        """智能匹配策略：结合文本匹配和语义匹配"""
        # 1. 首先尝试缩写匹配
        # if self.abbreviation_match(entity1, entity2):
        #     return True
            
        # 2. 如果有information，使用语义上下文匹配
        if entity1.information or entity2.information:
            return self.semantic_context_match(entity1, entity2)
            
        # # 3. 如果没有information，使用模糊匹配
        # return self.fuzzy_match(entity1, entity2)
    
    def abbreviation_match(self, entity1: Entity, entity2: Entity) -> bool:
        """处理缩写的匹配方法"""
        def extract_abbr(text: str) -> tuple[str, str]:
            # 提取全称和缩写，如 "artificial_intelligence(AI)" -> ("artificial_intelligence", "AI")
            match = re.match(r'(.*?)\((.*?)\)', text)
            if match:
                return match.group(1).strip(), match.group(2).strip()
            return text.strip(), ""
        
        name1, abbr1 = extract_abbr(entity1.name)
        name2, abbr2 = extract_abbr(entity2.name)
        
        return (name1 == name2 or 
                (abbr1 and abbr1 == name2) or 
                (abbr2 and abbr2 == name1) or
                (abbr1 and abbr2 and abbr1 == abbr2))
    
    def fuzzy_match(self, entity1: Entity, entity2: Entity, threshold: float = 85) -> bool:
        """使用编辑距离的模糊匹配方法"""
        similarity = fuzz.ratio(entity1.name.lower(), entity2.name.lower())
        return similarity >= threshold

entity1 = Entity(name="hydrogen_atom", information="The hydrogen atom is the simplest atom with only one proton and one electron. Its electron configuration is 1s1, indicating a single electron occupying the 1s orbital.")
entity2 = Entity(name="hydrogen_atom", information="Hydrogen atom is highly reactive and can form covalent bonds with many elements. It readily participates in redox reactions and can act as both a reducing agent and an oxidizing agent.")

print(EntityMatcher().smart_match(entity1, entity2))
