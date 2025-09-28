from typing import List, Set, Dict, Tuple
import re
from collections import defaultdict
import numpy as np
from rank_bm25 import BM25Okapi

from config.settings import ENTITY_RETRIEVAL_CONFIG


class EntityMatcher:
    """实体名拆分和匹配工具
    
    提供程序化的实体验证和候选类生成功能，用于优化token使用。
    """
    
    def __init__(self, available_classes: List[str]):
        """初始化实体匹配器
        
        Args:
            available_classes: 可用的类名列表
        """
        self.available_classes = set(available_classes)
        self._build_word_to_classes_map()
    
    def _build_word_to_classes_map(self):
        """构建单词到类名的映射关系"""
        self.word_to_classes = defaultdict(set)
        
        for class_name in self.available_classes:
            words = self._split_class_name(class_name)
            for word in words:
                self.word_to_classes[word].add(class_name)
    
    def _split_class_name(self, class_name: str) -> List[str]:
        """将类名拆分为小写单词
        
        支持多种命名风格:
        - CamelCase: "ChemicalCompound" -> ["chemical", "compound"]
        - snake_case: "chemical_compound" -> ["chemical", "compound"] 
        - kebab-case: "chemical-compound" -> ["chemical", "compound"]
        
        Args:
            class_name: 类名
            
        Returns:
            拆分后的小写单词列表
        """
        if not class_name:
            return []
        
        # 处理CamelCase: 在大写字母前插入分隔符
        class_name = re.sub(r'([a-z])([A-Z])', r'\1_\2', class_name)
        
        # 用常见分隔符分割
        words = re.split(r'[_\-\s]+', class_name)
        
        # 转换为小写并过滤空字符串
        return [word.lower().strip() for word in words if word.strip()]
    
    def check_entities_in_classes(self, entities: List[str]) -> Dict[str, bool]:
        """检查实体是否直接存在于available_classes中
        
        Args:
            entities: 待检查的实体列表
            
        Returns:
            字典，键为实体名，值为是否存在的布尔值
        """
        result = {}
        for entity in entities:
            result[entity] = entity in self.available_classes
        return result
    
    def find_candidate_classes_for_entity(self, entity: str) -> Set[str]:
        """为单个实体找到候选类
        
        Args:
            entity: 实体名
            
        Returns:
            候选类名集合
        """
        # 如果实体直接存在，返回自身
        if entity in self.available_classes:
            return {entity}
        
        # 拆分实体名为单词
        entity_words = set(self._split_class_name(entity))
        
        # 找到包含至少一个单词的类
        candidate_classes = set()
        for word in entity_words:
            if word in self.word_to_classes:
                candidate_classes.update(self.word_to_classes[word])
        
        return candidate_classes
    
    def extract_candidate_classes(self, entities: List[str]) -> List[str]:
        """为实体列表提取候选类集合
        
        Args:
            entities: 实体列表
            
        Returns:
            候选类名列表（已去重并排序）
        """
        all_candidates = set()
        
        for entity in entities:
            candidates = self.find_candidate_classes_for_entity(entity)
            all_candidates.update(candidates)
        
        # 返回排序后的列表
        return sorted(list(all_candidates))
    
    def find_ranked_candidates_for_entity(self, entity: str, retriever_config: Dict = None, k: int = None, include_alternatives: bool = False) -> List[Tuple[str, float]]:
        """为单个实体使用排序检索找到候选类
        
        Args:
            entity: 实体名称
            retriever_config: 排序检索器配置，如果为None则使用settings.yaml中的配置
            k: 返回候选数量，如果为None则使用配置中的top_k
            include_alternatives: 是否在实体直接存在时也包含其他相似候选，默认False保持向后兼容
            
        Returns:
            (候选类名, 相关性分数)元组列表，按分数降序排列
        """
        # 使用settings配置作为默认值
        if retriever_config is None:
            retriever_config = ENTITY_RETRIEVAL_CONFIG
        
        if k is None:
            k = retriever_config.get('top_k', 15)
        
        # 如果实体直接存在且不需要替代候选，返回完美匹配（保持原有行为）
        if entity in self.available_classes and not include_alternatives:
            return [(entity, 1.0)]
        
        # 初始化排序检索器
        retriever = RankedRetriever(list(self.available_classes), retriever_config)
        
        # 执行排序检索获取所有候选
        candidates = retriever.search(entity, k)
        
        # 如果实体直接存在且需要替代候选，确保它以完美分数排在首位
        if entity in self.available_classes and include_alternatives:
            # 从候选中移除直接匹配（如果存在）
            candidates = [(name, score) for name, score in candidates if name != entity]
            # 将直接匹配添加到首位
            candidates.insert(0, (entity, 1.0))
            # 如果需要，截断到k个结果
            candidates = candidates[:k]
        
        return candidates
    
    def extract_ranked_candidate_classes(self, entities: List[str], retriever_config: Dict = None, k: int = None) -> Dict[str, List[Tuple[str, float]]]:
        """为实体列表使用排序检索提取候选类
        
        Args:
            entities: 实体列表
            retriever_config: 排序检索器配置，如果为None则使用settings.yaml中的配置
            k: 每个实体返回的候选数量，如果为None则使用配置中的top_k
            
        Returns:
            字典，键为实体名，值为(候选类名, 相关性分数)元组列表
        """
        # 使用settings配置作为默认值
        if retriever_config is None:
            retriever_config = ENTITY_RETRIEVAL_CONFIG
        
        if k is None:
            k = retriever_config.get('top_k', 15)
        
        result = {}
        
        # 只为不存在的实体创建一个检索器实例以提高效率
        missing_entities = [entity for entity in entities if entity not in self.available_classes]
        
        if missing_entities:
            retriever = RankedRetriever(list(self.available_classes), retriever_config)
        
        for entity in entities:
            if entity in self.available_classes:
                # 直接匹配
                result[entity] = [(entity, 1.0)]
            else:
                # 排序检索
                result[entity] = retriever.search(entity, k)
        
        return result
    
    def needs_refinement(self, entities: List[str]) -> bool:
        """判断是否需要进行候选集refinement
        
        如果所有实体都直接存在于available_classes中，则不需要refinement。
        
        Args:
            entities: 实体列表
            
        Returns:
            是否需要refinement的布尔值
        """
        if not entities:
            return False
        
        check_results = self.check_entities_in_classes(entities)
        return not all(check_results.values())
    
    def get_refinement_stats(self, entities: List[str]) -> Dict:
        """获取refinement统计信息
        
        Args:
            entities: 实体列表
            
        Returns:
            包含统计信息的字典
        """
        if not entities:
            return {
                "total_entities": 0,
                "direct_matches": 0,
                "missing_entities": 0,
                "candidate_classes_count": 0,
                "original_classes_count": len(self.available_classes),
                "reduction_ratio": 0.0
            }
        
        check_results = self.check_entities_in_classes(entities)
        direct_matches = sum(check_results.values())
        missing_entities = len(entities) - direct_matches
        
        candidate_classes = self.extract_candidate_classes(entities)
        candidate_count = len(candidate_classes)
        original_count = len(self.available_classes)
        reduction_ratio = 1.0 - (candidate_count / original_count) if original_count > 0 else 0.0
        
        return {
            "total_entities": len(entities),
            "direct_matches": direct_matches,
            "missing_entities": missing_entities,
            "missing_entity_names": [entity for entity, exists in check_results.items() if not exists],
            "candidate_classes_count": candidate_count,
            "original_classes_count": original_count,
            "reduction_ratio": reduction_ratio,
            "candidate_classes":candidate_classes
        }
    
    def get_ranked_refinement_stats(self, entities: List[str], retriever_config: Dict = None, k: int = None) -> Dict:
        """获取基于排序检索的refinement统计信息
        
        Args:
            entities: 实体列表
            retriever_config: 排序检索器配置，如果为None则使用settings.yaml中的配置
            k: 每个实体的候选数量，如果为None则使用配置中的top_k
            
        Returns:
            包含统计信息的字典
        """
        # 使用settings配置作为默认值
        if retriever_config is None:
            retriever_config = ENTITY_RETRIEVAL_CONFIG
        
        if k is None:
            k = retriever_config.get('top_k', 15)
        
        if not entities:
            return {
                "total_entities": 0,
                "direct_matches": 0,
                "missing_entities": 0,
                "total_ranked_candidates": 0,
                "avg_candidates_per_entity": 0.0,
                "original_classes_count": len(self.available_classes),
                "reduction_ratio": 0.0
            }
        
        check_results = self.check_entities_in_classes(entities)
        direct_matches = sum(check_results.values())
        missing_entities = len(entities) - direct_matches
        
        # 获取排序候选
        ranked_results = self.extract_ranked_candidate_classes(entities, retriever_config, k)
        
        # 统计所有候选
        all_candidates = set()
        total_candidates = 0
        for entity_candidates in ranked_results.values():
            entity_candidate_names = [candidate[0] for candidate in entity_candidates]
            all_candidates.update(entity_candidate_names)
            total_candidates += len(entity_candidate_names)
        
        unique_candidates_count = len(all_candidates)
        avg_candidates_per_entity = total_candidates / len(entities) if entities else 0.0
        original_count = len(self.available_classes)
        reduction_ratio = 1.0 - (unique_candidates_count / original_count) if original_count > 0 else 0.0
        
        return {
            "total_entities": len(entities),
            "direct_matches": direct_matches,
            "missing_entities": missing_entities,
            "missing_entity_names": [entity for entity, exists in check_results.items() if not exists],
            "total_ranked_candidates": total_candidates,
            "unique_candidates_count": unique_candidates_count,
            "avg_candidates_per_entity": avg_candidates_per_entity,
            "original_classes_count": original_count,
            "reduction_ratio": reduction_ratio,
            "ranked_results": ranked_results
        }


class RankedRetriever:
    """基于BM25和Jaccard相似度的排序检索器
    
    使用混合评分模型结合BM25算法和Jaccard相似度，提供高质量的排序检索功能。
    BM25基于词级分词，Jaccard基于字符级trigrams。
    """
    
    def __init__(self, available_entities: List[str], config: Dict = None):
        """初始化排序检索器
        
        Args:
            available_entities: 可用实体列表
            config: 配置字典，包含超参数设置。如果为None，则使用settings.yaml中的配置
        """
        self.available_entities = available_entities
        
        # 使用settings配置作为默认值
        if config is None:
            config = ENTITY_RETRIEVAL_CONFIG
        
        # 合并默认配置和传入配置
        default_config = {
            'top_k': 15,
            'bm25_weight': 0.5,
            'jaccard_weight': 0.5,
            'trigram_size': 3,
            'min_score_threshold': 0.1
        }
        self.config = {**default_config, **config}
        
        # 构建索引
        self._build_bm25_index()
        self._build_trigram_index()
    
    def _tokenize_entity(self, entity: str) -> List[str]:
        """实体分词
        
        Args:
            entity: 实体名称
            
        Returns:
            分词后的单词列表
        """
        if not entity:
            return []
        
        # 处理CamelCase
        entity = re.sub(r'([a-z])([A-Z])', r'\1_\2', entity)
        
        # 用常见分隔符分割
        words = re.split(r'[_\-\s]+', entity)
        
        # 转换为小写并过滤空字符串
        return [word.lower().strip() for word in words if word.strip()]
    
    def _get_trigrams(self, text: str) -> Set[str]:
        """生成字符级trigrams
        
        Args:
            text: 输入文本
            
        Returns:
            trigrams集合
        """
        text = text.lower()
        trigram_size = self.config['trigram_size']
        
        if len(text) < trigram_size:
            return {text}
        
        trigrams = set()
        for i in range(len(text) - trigram_size + 1):
            trigrams.add(text[i:i + trigram_size])
        
        return trigrams
    
    def _build_bm25_index(self):
        """构建BM25索引"""
        # 对所有实体进行分词
        self.tokenized_entities = [self._tokenize_entity(entity) for entity in self.available_entities]
        
        # 创建BM25索引
        self.bm25 = BM25Okapi(self.tokenized_entities)
    
    def _build_trigram_index(self):
        """构建trigrams索引"""
        self.entity_trigrams = []
        for entity in self.available_entities:
            trigrams = self._get_trigrams(entity)
            self.entity_trigrams.append(trigrams)
    
    def _normalize_scores(self, scores: List[float]) -> List[float]:
        """使用min-max归一化将分数标准化到[0,1]区间
        
        Args:
            scores: 原始分数列表
            
        Returns:
            归一化后的分数列表
        """
        if not scores:
            return scores
        
        scores = np.array(scores)
        min_score = float(np.min(scores))
        max_score = float(np.max(scores))
        
        # 避免除零 - 使用Python原生比较
        if max_score == min_score:
            return [1.0] * len(scores)
        
        normalized = (scores - min_score) / (max_score - min_score)
        return normalized.tolist()
    
    def _calculate_jaccard_similarity(self, query_trigrams: Set[str], entity_trigrams: Set[str]) -> float:
        """计算Jaccard相似度
        
        Args:
            query_trigrams: 查询的trigrams集合
            entity_trigrams: 实体的trigrams集合
            
        Returns:
            Jaccard相似度分数 [0, 1]
        """
        if not query_trigrams or not entity_trigrams:
            return 0.0
        
        intersection = len(query_trigrams & entity_trigrams)
        union = len(query_trigrams | entity_trigrams)
        
        return intersection / union if union > 0 else 0.0
    
    def search(self, query: str, k: int = None) -> List[Tuple[str, float]]:
        """执行排序检索
        
        Args:
            query: 查询字符串
            k: 返回结果数量，默认使用配置中的top_k
            
        Returns:
            (实体名, 分数)元组列表，按分数降序排列
        """
        if k is None:
            k = self.config['top_k']
        
        # 预处理查询
        query_tokens = self._tokenize_entity(query)
        query_trigrams = self._get_trigrams(query)
        
        # 计算BM25分数
        bm25_scores = self.bm25.get_scores(query_tokens)
        
        # 计算Jaccard分数
        jaccard_scores = []
        for entity_trigrams in self.entity_trigrams:
            jaccard_score = self._calculate_jaccard_similarity(query_trigrams, entity_trigrams)
            jaccard_scores.append(jaccard_score)
        
        # 归一化分数
        normalized_bm25 = self._normalize_scores(bm25_scores.tolist() if hasattr(bm25_scores, 'tolist') else list(bm25_scores))
        normalized_jaccard = self._normalize_scores(jaccard_scores)
        
        # 计算混合分数
        bm25_weight = self.config['bm25_weight']
        jaccard_weight = self.config['jaccard_weight']
        
        final_scores = []
        for i in range(len(self.available_entities)):
            mixed_score = (bm25_weight * float(normalized_bm25[i]) + 
                          jaccard_weight * float(normalized_jaccard[i]))
            final_scores.append((self.available_entities[i], mixed_score))
        
        # 按分数降序排序
        final_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 应用最小分数阈值过滤
        min_threshold = self.config['min_score_threshold']
        filtered_scores = [(entity, score) for entity, score in final_scores 
                          if float(score) >= min_threshold]
        
        # 返回top-k结果
        return filtered_scores[:k]