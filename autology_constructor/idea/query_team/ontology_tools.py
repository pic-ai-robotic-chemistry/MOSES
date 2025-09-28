from typing import List, Tuple, Dict, Optional, Set, Any, Callable, Union
from owlready2 import *
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import re
from collections import deque
import traceback
import warnings
import threading

from autology_constructor.idea.query_team.utils import parse_json, format_sparql_results, extract_variables_from_sparql

from config.settings import ONTOLOGY_SETTINGS, OntologySettings

def thread_safe_method(func):
    """装饰器：为方法添加线程安全保护"""
    def wrapper(self, *args, **kwargs):
        # 优先使用共享锁，然后是实例锁
        lock_to_use = None
        
        # 1. 检查是否有QueryManager的共享锁
        try:
            from .query_manager import QueryManager
            shared_lock = QueryManager.get_shared_lock()
            if shared_lock:
                lock_to_use = shared_lock
        except (ImportError, AttributeError):
            pass
        
        # 2. 回退到实例锁
        if not lock_to_use and self._thread_safe and self._ontology_lock:
            lock_to_use = self._ontology_lock
        
        # 3. 使用锁保护或直接执行
        if lock_to_use:
            with lock_to_use:
                return func(self, *args, **kwargs)
        else:
            return func(self, *args, **kwargs)
    return wrapper

class SparqlExecutionError(Exception):
    """SPARQL查询执行错误"""
    pass


class SparqlOptimizer:
    """SPARQL查询优化器
    
    对SPARQL查询进行各种优化，提高查询效率和稳定性：
    1. 优化前缀声明
    2. 优化过滤条件
    3. 优化连接操作
    """
    
    def __init__(self):
        self.optimizations = [
            self._optimize_prefixes,
            self._optimize_filters,
            self._optimize_joins
        ]

    def optimize(self, query: str) -> str:
        """应用所有优化策略到查询
        
        Args:
            query: 原始SPARQL查询
            
        Returns:
            优化后的SPARQL查询
        """
        optimized = query
        for optimization in self.optimizations:
            optimized = optimization(optimized)
        return optimized
        
    def _optimize_prefixes(self, query: str) -> str:
        """优化前缀声明
        
        确保常用前缀存在，移除未使用前缀
        """
        # 检查常用前缀是否已声明
        common_prefixes = {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "owl": "http://www.w3.org/2002/07/owl#",
            "xsd": "http://www.w3.org/2001/XMLSchema#"
        }
        
        # 提取已声明的前缀
        prefix_pattern = r'PREFIX\s+(\w+):\s+<([^>]+)>'
        declared_prefixes = dict(re.findall(prefix_pattern, query, re.IGNORECASE))
        
        # 检查查询中使用的前缀
        used_prefixes = set(re.findall(r'(\w+):[^\s.]+', query))
        
        # 添加缺失但使用的常用前缀
        new_prefixes = ""
        for prefix, uri in common_prefixes.items():
            if prefix in used_prefixes and prefix not in declared_prefixes:
                new_prefixes += f"PREFIX {prefix}: <{uri}>\n"
        
        # 如果有新前缀，添加到查询开头
        if new_prefixes:
            # 检查查询是否已有PREFIX声明
            if re.search(prefix_pattern, query, re.IGNORECASE):
                # 在最后一个PREFIX后插入
                query = re.sub(
                    r'(PREFIX\s+\w+:\s+<[^>]+>)([^P]|$)',
                    r'\1\n' + new_prefixes + r'\2',
                    query,
                    count=1,
                    flags=re.IGNORECASE
                )
            else:
                # 在查询开头添加
                query = new_prefixes + query
        
        return query
        
    def _optimize_filters(self, query: str) -> str:
        """优化过滤条件
        
        将复杂过滤条件移到更早位置，优化执行计划
        """
        # 提取所有FILTER表达式
        filter_pattern = r'FILTER\s*\(([^)]+)\)'
        filters = re.findall(filter_pattern, query, re.IGNORECASE)
        
        # 如果没有过滤器，直接返回
        if not filters:
            return query
            
        # 优化过滤器位置（将过滤器尽可能移到WHERE子句前部）
        where_pattern = r'(WHERE\s*\{)(.*?)(\}) '
        
        def optimize_where(match):
            prefix = match.group(1)
            body = match.group(2)
            suffix = match.group(3)
            
            # 删除所有过滤器
            body_without_filters = re.sub(filter_pattern, '', body, flags=re.IGNORECASE)
            
            # 在三元组模式后添加所有过滤器
            optimized_body = body_without_filters
            for f in filters:
                optimized_body += f" FILTER({f})"
                
            return prefix + optimized_body + suffix
            
        # 仅优化没有OPTIONAL, UNION等复杂结构的简单查询
        if not re.search(r'OPTIONAL|UNION|MINUS', query, re.IGNORECASE):
            return re.sub(where_pattern, optimize_where, query, flags=re.IGNORECASE | re.DOTALL)
        
        return query
        
    def _optimize_joins(self, query: str) -> str:
        """优化连接操作
        
        重排三元组模式顺序，优化连接顺序
        """
        # 此优化需要更复杂分析，简化实现
        # 规则：将限制性更强的三元组模式（包含类型声明）移到前面
        
        # 查找WHERE子句
        where_match = re.search(r'WHERE\s*\{(.*?)\}', query, re.IGNORECASE | re.DOTALL)
        if not where_match:
            return query
            
        where_body = where_match.group(1)
        
        # 提取三元组模式
        patterns = [p.strip() for p in re.split(r'\.|\s*FILTER\s*\([^)]+\)', where_body) if p.strip()]
        
        # 优先级排序：类型声明 > 具体URI > 变量
        def pattern_priority(pattern):
            if 'rdf:type' in pattern or 'a ' in pattern:
                return 0  # 最高优先级
            elif re.search(r'<[^>]+>', pattern):
                return 1  # 次高优先级
            else:
                return 2  # 最低优先级
                
        # 尝试按优先级排序
        try:
            sorted_patterns = sorted(patterns, key=pattern_priority)
            
            # 如果排序结果与原始不同，替换WHERE子句
            if sorted_patterns != patterns:
                sorted_where = ' . '.join(sorted_patterns)
                if sorted_where:
                    sorted_where += ' .'
                new_query = query.replace(where_body, sorted_where)
                return new_query
        except:
            # 排序失败，返回原始查询
            pass
            
        return query


class SparqlExecutor:
    """SPARQL查询执行器
    
    负责执行SPARQL查询，包括：
    1. 查询优化
    2. 执行查询
    3. 异常处理和重试
    """
    
    def __init__(self):
        self.optimizer = SparqlOptimizer()
        self.max_retries = 2
        
    def execute(self, query: str, ontology: Any) -> Dict:
        """执行SPARQL查询
        
        Args:
            query: SPARQL查询字符串
            ontology: 查询的本体对象
            
        Returns:
            查询结果
            
        Raises:
            SparqlExecutionError: 查询执行失败
        """
        if not ontology:
            raise SparqlExecutionError("未设置本体")
            
        # 优化查询
        try:
            optimized_query = self.optimizer.optimize(query)
        except Exception as e:
            # 优化失败时使用原始查询
            optimized_query = query
            
        # 执行查询（带重试）
        retries = 0
        last_error = None
        
        while retries <= self.max_retries:
            try:
                return self._execute_query(optimized_query, ontology)
            except Exception as e:
                last_error = e
                retries += 1
                
                # 最后一次尝试使用原始查询
                if retries == self.max_retries:
                    try:
                        return self._execute_query(query, ontology)
                    except Exception as final_e:
                        last_error = final_e
                        break
        
        # 所有尝试都失败
        error_msg = str(last_error) if last_error else "未知错误"
        raise SparqlExecutionError(f"SPARQL执行失败: {error_msg}")
    
    def _execute_query(self, query: str, ontology: Any) -> Dict:
        """实际执行优化后的查询
        
        Args:
            query: 优化后的SPARQL查询
            ontology: 本体对象
            
        Returns:
            格式化的查询结果
        """
        # 使用传入的 ontology 对象的 world 来执行 SPARQL
        results = list(ontology.world.sparql(query))
        
        # 获取变量名
        variables = extract_variables_from_sparql(query)
        
        # 格式化结果
        formatted_results = format_sparql_results(results)
        
        # 添加变量映射和查询信息
        if variables:
            formatted_results["variables"] = variables
        
        formatted_results["query_info"] = {
            "original_query": query,
        }
        
        return formatted_results


class OntologyTools:
    """用于本体查询和解析的工具 (v3: 使用 OntologySettings)

    此类提供了用于处理 OWL 本体 的综合工具，需要一个配置好的 OntologySettings 实例。
    """

    # Class attribute for restriction type mapping
    RESTRICTION_TYPE_MAP = {
        24: "SOME", 
        25: "ONLY", 
        26: "EXACTLY",
        27: "MIN", 
        28: "MAX", 
        29: "VALUE",
    }

    def __init__(self, ontology_settings: OntologySettings, thread_safe: bool = False):
        """初始化 OntologyTools

        Args:
            ontology_settings (OntologySettings): 已配置和加载的本体设置对象。
            thread_safe (bool): 是否启用线程安全模式，默认True
        """
        if not isinstance(ontology_settings, OntologySettings):
            raise TypeError("ontology_settings 必须是 OntologySettings 的实例。")

        # 初始化线程锁（如果启用线程安全）
        self._thread_safe = thread_safe
        if thread_safe:
            self._ontology_lock = threading.RLock()  # 使用可重入锁
        else:
            self._ontology_lock = None

        self.onto_settings = ontology_settings
        self.onto = self.onto_settings.ontology # 可能为 None

        # 获取命名空间，需要处理 ontology 或 namespace 可能为 None 的情况
        self.meta_ns = self.onto_settings.meta
        self._classes_ns = self.onto_settings.classes
        self._obj_props_ns = self.onto_settings.object_properties
        self._data_props_ns = self.onto_settings.data_properties

        # 检查本体是否成功加载
        if self.onto is None:
            warnings.warn("OntologyTools 初始化时本体未加载。大多数功能将不可用。", RuntimeWarning)
            # 将关键组件设为 None 或默认值
            self.has_information_prop = None
            self.SourcedInformationClass = None
            return # 提前退出初始化或允许继续但功能受限

        # 获取关键的 Meta 属性和类
        if self.meta_ns:
            try:
                self.has_information_prop = self.meta_ns['has_information']
                # -- 修改检查方式 --
                # 移除之前的调试打印
                # 使用 is_a 属性进行检查，更符合 owlready2 的方式
                if owl.ObjectProperty not in getattr(self.has_information_prop, 'is_a', []):
                    warnings.warn(f"'{self.has_information_prop}' is not recognized as an owl:ObjectProperty based on its 'is_a' attribute.", ImportWarning)
                    self.has_information_prop = None
            except (KeyError, AttributeError):
                warnings.warn("'has_information' 未在 meta 命名空间中找到。", ImportWarning)
                self.has_information_prop = None
            # 移除之前的调试打印

            try:
                self.SourcedInformationClass = self.meta_ns['SourcedInformation']
                # 同样，对 SourcedInformationClass 的检查也应该基于 owlready2 的类型系统
                # issubclass(self.SourcedInformationClass, Thing) 看起来是正确的，暂时保留
                # 移除之前的调试打印
                if not issubclass(self.SourcedInformationClass, Thing): # issubclass is safer
                    warnings.warn("'meta.SourcedInformation' 不是有效的类 (ThingClass)。", ImportWarning)
                    self.SourcedInformationClass = None
            except (KeyError, AttributeError, TypeError): # TypeError for issubclass if not a class
                warnings.warn("'SourcedInformation' 未在 meta 命名空间中找到或不是有效类。", ImportWarning)
                self.SourcedInformationClass = None
            # 移除之前的调试打印
        else:
            warnings.warn("Meta 命名空间未加载。SourcedInformation 相关功能将不可用。", RuntimeWarning)
            self.has_information_prop = None
            self.SourcedInformationClass = None

        # 验证其他命名空间是否加载
        if not self._classes_ns: warnings.warn("Classes 命名空间未加载。", RuntimeWarning)
        if not self._obj_props_ns: warnings.warn("Object Properties 命名空间未加载。", RuntimeWarning)
        if not self._data_props_ns: warnings.warn("Data Properties 命名空间未加载。", RuntimeWarning)


    def _check_ontology_loaded(self) -> bool:
        """检查本体是否已加载"""
        if self.onto is None:
             warnings.warn("操作无法执行，因为本体未加载。", RuntimeWarning)
             return False
        return True

    @thread_safe_method
    def _get_class_by_name(self, class_name: str) -> Optional[ThingClass]:
        """辅助函数：通过名称安全地获取类对象 (首先尝试 classes 命名空间，然后后备搜索 IRI)"""
        if not self._check_ontology_loaded(): return None

        # 1. 尝试标准路径 (classes 命名空间)
        if self._classes_ns: # Check if classes_ns exists before trying
            try:
                cls = self._classes_ns[class_name]
                if isinstance(cls, ThingClass):
                    return cls
                else:
                     # Found something but not a ThingClass, might be an error in ontology or loading
                     warnings.warn(f"在 'classes' 命名空间中找到 '{class_name}' 但它不是 ThingClass。")
                     # Don't immediately return None, allow fallback search to potentially find the correct class
                     # return None
            except KeyError:
                 # Not found in classes_ns, proceed to fallback search
                 pass
            except Exception as e:
                 # Handle unexpected errors during primary lookup, but still allow fallback
                 warnings.warn(f"在 'classes' 命名空间中查找 '{class_name}' 时发生意外错误: {e}")
                 pass # Proceed to fallback

        # 2. 后备: 搜索 IRI 结尾匹配 class_name 的 owl:Class
        try:
            # 使用 owl_class 进行搜索，因为它在测试中有效
            search_results = self.onto.search(iri=f"*/{class_name}", type=owlready2.owl_class)

            if search_results:
                potential_cls = search_results[0]
                if len(search_results) > 1:
                    warnings.warn(f"通过后备 IRI 搜索找到多个类匹配 '{class_name}' ({len(search_results)} 个)，将返回第一个结果。")

                # 验证找到的对象是否确实是 ThingClass
                if isinstance(potential_cls, ThingClass):
                    warnings.warn(f"类 '{class_name}' 在预期的 'classes' 命名空间中未找到，但通过后备 IRI 搜索找到。")
                    return potential_cls
                else:
                    warnings.warn(f"后备 IRI 搜索找到的对象 '{potential_cls}' 不是有效的 ThingClass，无法返回。")
                    return None
            else:
                # 后备搜索也未找到
                return None # Class not found through either method

        except Exception as e:
            warnings.warn(f"后备 IRI 搜索类 '{class_name}' 时发生意外错误: {e}")
            return None

        # Fallback if _classes_ns didn't exist and search failed (should theoretically be covered above)
        # return None

    @thread_safe_method
    def _get_property_by_name(self, property_name: str) -> Optional[Union[ObjectProperty, DataProperty, ObjectPropertyClass, DataPropertyClass]]:
        """辅助函数：通过名称安全地获取属性对象 (尝试 meta, obj props, 然后 data props)
           MODIFIED: Now also checks the meta namespace and accepts metaclasses."""
        if not self._check_ontology_loaded(): return None
        prop = None

        # 1. 首先尝试 Meta 命名空间
        if self.meta_ns:
            try:
                prop_meta = self.meta_ns[property_name]
                if prop_meta is not None:
                    # 假设 meta 命名空间也可能包含实例或元类
                    if isinstance(prop_meta, (ObjectProperty, DataProperty, ObjectPropertyClass, DataPropertyClass)):
                        return prop_meta
                    else:
                        # Found something, but not the expected type
                        warnings.warn(f"在 meta 命名空间中找到 '{property_name}' 但其类型 '{type(prop_meta).__name__}' 不是预期的属性类型。")
                        # Do not return, continue searching other namespaces
                        # prop remains None
            except Exception as e:
                warnings.warn(f"在 meta 命名空间中查找 '{property_name}' 时出错: {e}")
                # prop remains None, continue searching

        # 2. 如果在 Meta 中未找到有效属性，尝试对象属性命名空间
        if prop is None and self._obj_props_ns:
            try:
                prop_obj = self._obj_props_ns[property_name]
                if prop_obj is not None:
                    if isinstance(prop_obj, (ObjectProperty, ObjectPropertyClass)):
                        return prop_obj
                    else:
                        warnings.warn(f"在 object_properties 命名空间中找到 '{property_name}' 但其类型 '{type(prop_obj).__name__}' 不是预期的 ObjectProperty 或 ObjectPropertyClass。")
                        # Do not return, continue searching
                        # prop remains None
            except Exception as e:
                 warnings.warn(f"在 object_properties 中查找 '{property_name}' 时出错: {e}")
                 # prop remains None, continue searching

        # 3. 如果仍未找到有效属性，尝试数据属性命名空间
        if prop is None and self._data_props_ns:
            try:
                prop_data = self._data_props_ns[property_name]
                if prop_data is not None:
                    if isinstance(prop_data, (DataProperty, DataPropertyClass)):
                        return prop_data
                    else:
                         warnings.warn(f"在 data_properties 命名空间中找到 '{property_name}' 但其类型 '{type(prop_data).__name__}' 不是预期的 DataProperty 或 DataPropertyClass。")
                         # Found in the last namespace but wrong type, return None as no valid prop found
                         return None
            except Exception as e:
                 warnings.warn(f"在 data_properties 中查找 '{property_name}' 时出错: {e}")
                 # Error in the last namespace search, return None
                 return None

        # 如果所有命名空间都找不到，或者找到但类型错误，返回 None (prop 初始为 None 且未被有效属性覆盖)
        return prop


    def _get_restriction_value_str(self, value: Any) -> str:
        """辅助函数：将限制值转换为字符串表示"""
        # ... (此函数不变)
        if isinstance(value, ThingClass) or isinstance(value, owlready2.PropertyClass): return getattr(value, 'name', str(value))
        elif isinstance(value, Or): return " OR ".join([self._get_restriction_value_str(c) for c in value.Classes])
        elif isinstance(value, And): return " AND ".join([self._get_restriction_value_str(c) for c in value.Classes])
        elif isinstance(value, Not): return f"NOT ({self._get_restriction_value_str(value.Class)})"
        elif isinstance(value, Thing): return getattr(value, 'name', str(value))
        else: return str(value)

    @thread_safe_method
    def _get_sourced_info(self, entity: Union[ThingClass, ObjectProperty, DataProperty], info_type: Optional[Union[str, List[str]]] = None) -> List[Thing]:
        """辅助函数：获取实体关联的 SourcedInformation 实例，可选地按类型过滤"""
        # ... (此函数不变)
        if not self._check_ontology_loaded() or not self.has_information_prop or not self.SourcedInformationClass: return []
        linked_info_instances = []
        try:
            raw_linked_items = getattr(entity, self.has_information_prop.name, [])
            if not isinstance(raw_linked_items, list): raw_linked_items = [raw_linked_items]
            for item in raw_linked_items:
                 if self.SourcedInformationClass in item.is_a:
                     if info_type:
                         item_types = getattr(item, 'type', []) or []; item_types = [item_types] if isinstance(item_types, str) else item_types
                         target_types = [info_type] if isinstance(info_type, str) else info_type
                         if any(t in item_types for t in target_types): linked_info_instances.append(item)
                     else: linked_info_instances.append(item)
        except AttributeError as e: warnings.warn(f"访问实体 '{getattr(entity, 'name', entity)}' 的 has_information 时出错: {e}")
        except Exception as e: warnings.warn(f"获取实体 '{getattr(entity, 'name', entity)}' 的 SI 时出错: {e}")
        return linked_info_instances


    # --- 内部单类处理函数 ---
    # 这些函数现在首先检查本体是否加载

    @thread_safe_method
    def _get_single_class_info(self, class_name: str) -> Dict:
        if not self._check_ontology_loaded(): return {"error": "本体未加载"}
        cls = self._get_class_by_name(class_name)
        if not cls: return {"error": f"类 '{class_name}' 未找到。"}
        entity_info_contents = []
        sourced_infos = self._get_sourced_info(cls, info_type="entity")
        for info_instance in sourced_infos:
            try:
                content = getattr(info_instance, 'content', None)
                if content is not None:
                    if isinstance(content, list): entity_info_contents.extend([str(c) for c in content])
                    else: entity_info_contents.append(str(content))
            except AttributeError: pass # warnings.warn(f"SI {getattr(info_instance, 'name', info_instance)} 缺少 'content' 属性。")
            except Exception as e: warnings.warn(f"处理 SI {getattr(info_instance, 'name', info_instance)} 时出错: {e}")
        return {"name": cls.name, "information": list(set(entity_info_contents))}

    @thread_safe_method
    def _get_single_information_sources(self, class_name: str) -> Union[List[str], Dict]:
         if not self._check_ontology_loaded(): return {"error": "本体未加载"}
         cls = self._get_class_by_name(class_name)
         if not cls: return {"error": f"类 '{class_name}' 未找到。"}
         sources = set()
         sourced_infos = self._get_sourced_info(cls)
         for info_instance in sourced_infos:
             try:
                 source_val = getattr(info_instance, 'source', None)
                 if source_val is not None:
                     if isinstance(source_val, list): sources.update([str(s) for s in source_val])
                     else: sources.add(str(source_val))
             except AttributeError: pass # warnings.warn(f"SI {getattr(info_instance, 'name', info_instance)} 缺少 'source' 属性。")
             except Exception as e: warnings.warn(f"处理 SI {getattr(info_instance, 'name', info_instance)} 的 source 时出错: {e}")
         return sorted(list(sources))

    # --- NEW: Refactored private methods for single class operations ---

    @thread_safe_method
    def _get_single_parents(self, class_name: str) -> Union[List[str], Dict]:
         """Internal: Get direct parents for a single class."""
         if not self._check_ontology_loaded(): return {"error": "本体未加载"}
         cls = self._get_class_by_name(class_name)
         if not cls: return {"error": f"类 '{class_name}' 未找到。"}
         parents = []
         try:
             # Iterate over is_a to find ThingClass parents (direct superclasses)
             for parent in cls.is_a:
                 # Ensure it's a class, not Thing itself, and has a name
                 if isinstance(parent, ThingClass) and parent != owlready2.Thing and hasattr(parent, 'name'):
                      parents.append(parent.name)
         except Exception as e: warnings.warn(f"获取类 '{class_name}' 的父类时出错: {e}")
         # Return unique sorted list
         return sorted(list(set(parents)))

    @thread_safe_method
    def _get_single_children(self, class_name: str) -> Union[List[str], Dict]:
         """Internal: Get direct children for a single class."""
         if not self._check_ontology_loaded(): return {"error": "本体未加载"}
         cls = self._get_class_by_name(class_name)
         if not cls: return {"error": f"类 '{class_name}' 未找到。"}
         children = []
         try:
             # Use the subclasses() generator provided by owlready2
             for child in cls.subclasses():
                 if isinstance(child, ThingClass) and hasattr(child, 'name'): children.append(child.name)
         except Exception as e: warnings.warn(f"获取类 '{class_name}' 的子类时出错: {e}")
         return sorted(list(set(children)))

    @thread_safe_method
    def _get_single_ancestors(self, class_name: str) -> Union[List[str], Dict]:
         """Internal: Get all ancestors for a single class."""
         if not self._check_ontology_loaded(): return {"error": "本体未加载"}
         cls = self._get_class_by_name(class_name)
         if not cls: return {"error": f"类 '{class_name}' 未找到。"}
         ancestors = []
         try:
             # Use the ancestors() method
             all_ancestors = cls.ancestors()
             for ancestor in all_ancestors:
                 # Exclude self and Thing
                 if isinstance(ancestor, ThingClass) and ancestor != cls and ancestor != owlready2.Thing and hasattr(ancestor, 'name'): ancestors.append(ancestor.name)
         except Exception as e: warnings.warn(f"获取类 '{class_name}' 的祖先时出错: {e}")
         return sorted(list(set(ancestors)))

    @thread_safe_method
    def _get_single_descendants(self, class_name: str) -> Union[List[str], Dict]:
          """Internal: Get all descendants for a single class."""
          if not self._check_ontology_loaded(): return {"error": "本体未加载"}
          cls = self._get_class_by_name(class_name)
          if not cls: return {"error": f"类 '{class_name}' 未找到。"}
          descendants = []
          try:
              # Use the descendants() method
              all_descendants = cls.descendants()
              for descendant in all_descendants:
                   # Exclude self
                   if isinstance(descendant, ThingClass) and descendant != cls and hasattr(descendant, 'name'): descendants.append(descendant.name)
          except Exception as e: warnings.warn(f"获取类 '{class_name}' 的后代时出错: {e}")
          return sorted(list(set(descendants)))

    @thread_safe_method
    def _get_single_related_classes(self, class_name: str) -> Union[Dict[str, List[str]], Dict]:
         """Internal: Get related classes via object properties for a single class."""
         if not self._check_ontology_loaded(): return {"error": "本体未加载"}
         cls = self._get_class_by_name(class_name)
         if not cls: return {"error": f"类 '{class_name}' 未找到。"}
         related_map = {}
         try:
             # Use the NEW _get_single_class_properties method
             properties_details_res = self._get_single_class_properties(class_name) # Call the new detailed method
             if isinstance(properties_details_res, dict) and "error" in properties_details_res:
                 warnings.warn(f"无法获取 '{class_name}' 的属性以查找相关类: {properties_details_res.get('error', '未知错误')}")
                 return {"error": f"获取属性失败: {properties_details_res.get('error', '未知错误')}"}

             # Iterate through the detailed properties
             for prop_name, details in properties_details_res.items():
                 prop = self._get_property_by_name(prop_name)
                 # Only consider object properties for related classes
                 if not prop or not isinstance(prop, (ObjectProperty, ObjectPropertyClass)): continue

                 related_class_names_for_prop = set()
                 # Analyze restrictions from the details obtained
                 relevant_restriction_types = {"SOME", "ONLY", "VALUE"} # Include VALUE for specific individuals/classes
                 for restriction in details.get("restrictions", []): # Iterate through restrictions list
                     if restriction.get("type") in relevant_restriction_types:
                         raw_value = restriction.get("raw_value")
                         classes_to_process = []
                         # Handle different types of restriction values
                         if isinstance(raw_value, ThingClass):
                             classes_to_process.append(raw_value)
                         elif isinstance(raw_value, Or) or isinstance(raw_value, And):
                             classes_to_process.extend(getattr(raw_value, 'Classes', []))
                         # Could add handling for Individuals if needed:
                         # elif isinstance(raw_value, Thing):
                         #     related_class_names_for_prop.add(f"Individual:{raw_value.name}") # Or its class

                         for related_cls in classes_to_process:
                              if isinstance(related_cls, ThingClass) and hasattr(related_cls, 'name'):
                                  related_class_names_for_prop.add(related_cls.name)

                 if related_class_names_for_prop:
                      related_map[prop_name] = sorted(list(related_class_names_for_prop))

         except Exception as e:
             warnings.warn(f"获取类 '{class_name}' 的相关类时出错: {e}")
             # Return partial results if possible, or an error
             return {"error": f"获取相关类时发生意外错误: {e}"} # Or return related_map if partially successful

         return related_map

    @thread_safe_method
    def _get_single_disjoint_classes(self, class_name: str) -> Union[List[str], Dict]:
          """Internal: Get disjoint classes for a single class."""
          if not self._check_ontology_loaded(): return {"error": "本体未加载"}
          cls = self._get_class_by_name(class_name)
          if not cls: return {"error": f"类 '{class_name}' 未找到。"}
          disjoint_classes = set()
          try:
              # Use the disjoints() method which returns AllDisjoint objects
              for disjoint_set in cls.disjoints():
                   # disjoint_set.entities contains the classes in the disjoint axiom
                   if cls in disjoint_set.entities:
                      for entity in disjoint_set.entities:
                          # Add other classes from the set, excluding self
                          if isinstance(entity, ThingClass) and entity != cls and hasattr(entity, 'name'): disjoint_classes.add(entity.name)
          except Exception as e: warnings.warn(f"获取类 '{class_name}' 的不相交类时出错: {e}")
          return sorted(list(disjoint_classes))

    # --- MODIFIED: _get_single_class_properties based on Restrictions ---
    # Returns detailed property info including restrictions and descriptions
    @thread_safe_method
    def _get_single_class_properties(self, class_name: str) -> Union[Dict[str, Dict[str, Any]], Dict]:
         """Internal: Get detailed properties used in restrictions for a single class, including descriptions."""
         if not self._check_ontology_loaded(): return {"error": "本体未加载"}
         cls = self._get_class_by_name(class_name)
         if not cls: return {"error": f"类 '{class_name}' 未找到。"}

         temp_restrictions: Dict[str, List[Dict]] = {}
         properties_found_via_restrictions = set() # Keep track of properties seen in restrictions

         try:
             # 1. Collect Restrictions by iterating through is_a
             for item in cls.is_a:
                 if isinstance(item, owlready2.Restriction):
                     prop = getattr(item, 'property', None)
                     if prop and isinstance(prop, (ObjectProperty, DataProperty, ObjectPropertyClass, DataPropertyClass)) and hasattr(prop, 'name') and prop.name != "has_information":
                         prop_name = prop.name
                         properties_found_via_restrictions.add(prop_name)
                         try:
                             restriction_type_code = getattr(item, 'type', -1)
                             restriction_type = self.RESTRICTION_TYPE_MAP.get(restriction_type_code, item.__class__.__name__.upper())
                             restriction_value_raw = getattr(item, 'value', None)
                             if restriction_value_raw is None and restriction_type_code in [27, 28, 29]: # MIN, MAX, EXACTLY
                                 restriction_value_raw = getattr(item, 'cardinality', None)
                             restriction_value_str = self._get_restriction_value_str(restriction_value_raw)

                             restriction_info = {
                                 "type": restriction_type,
                                 "value": restriction_value_str,
                                 "raw_value": restriction_value_raw
                             }
                             temp_restrictions.setdefault(prop_name, []).append(restriction_info)
                         except Exception as parse_err:
                             warnings.warn(f"解析类 '{class_name}' 上属性 '{prop_name}' 的限制 '{item}' 时出错: {parse_err}")

             # 2. Collect Descriptions from SourcedInformation
             temp_descriptions: Dict[str, List[Dict]] = {}
             sourced_infos = self._get_sourced_info(cls, info_type=["data_property", "object_property"])
             for info in sourced_infos:
                 try:
                     # Assume 'property' attribute on SI holds the name of the described property
                     prop_name_list = getattr(info, 'property', [])
                     prop_name_from_info = prop_name_list[0] if prop_name_list else None

                     if prop_name_from_info:
                         content_list = getattr(info, 'content', [])
                         content = content_list[0] if content_list else None
                         source_list = getattr(info, 'source', [])
                         source = source_list[0] if source_list else None
                         file_path_list = getattr(info, 'file_path', [])
                         file_path = file_path_list[0] if file_path_list else None

                         if content: # Only add if there's actual content
                             description_info = {
                                 "content": str(content),
                                 "source": str(source) if source else None,
                                 "file_path": str(file_path) if file_path else None
                             }
                             temp_descriptions.setdefault(prop_name_from_info, []).append(description_info)
                 except Exception as e:
                     warnings.warn(f"处理类 '{class_name}' 的属性 SI {getattr(info, 'name', info)} 时出错: {e}")

             # 3. Merge Results
             final_result: Dict[str, Dict[str, Any]] = {}
             all_prop_names = properties_found_via_restrictions | set(temp_descriptions.keys()) # Combine properties from restrictions and descriptions

             for prop_name in all_prop_names:
                 restrictions = temp_restrictions.get(prop_name, [])
                 descriptions = temp_descriptions.get(prop_name, [])
                 final_result[prop_name] = {"restrictions": restrictions, "descriptions": descriptions}

             return final_result

         except Exception as e:
             warnings.warn(f"从类 '{class_name}' 提取属性细节时出错: {e}")
             return {"error": f"提取属性细节时出错: {e}"}


    # --- MODIFIED: _parse_single_class_definition using new private methods ---
    @thread_safe_method
    def _parse_single_class_definition(self, class_name: str) -> Dict:
         if not self._check_ontology_loaded(): return {"error": "本体未加载"}
         cls = self._get_class_by_name(class_name)
         if not cls: return {"error": f"类 '{class_name}' 未找到。"}

         definition = {}
         errors = {}

         # Basic Info
         basic_info = self._get_single_class_info(class_name)
         if "error" in basic_info: errors["basic_info"] = basic_info["error"]
         definition["basic_info"] = basic_info

         # Properties (using the NEW detailed property method)
         properties_details_res = self._get_single_class_properties(class_name) # Call the new detailed method
         properties_summary = {"data": [], "object": []} # Store as lists of dicts

         if isinstance(properties_details_res, dict) and "error" in properties_details_res:
              errors["properties"] = properties_details_res["error"]
         elif isinstance(properties_details_res, dict):
             # Process properties found
             for prop_name, details in properties_details_res.items():
                 prop = self._get_property_by_name(prop_name)
                 if not prop:
                     # Property might be mentioned in description but not found via restriction or vice-versa
                     # Or it might genuinely not exist if IRI is wrong in SI
                     warnings.warn(f"在 _parse_single_class_definition 中无法通过名称 '{prop_name}' 找到属性对象。它可能只存在于限制或描述中。")
                     # Decide how to handle - skip, or add with limited info? Let's add with available info.
                     # We need to guess the type or leave it ambiguous if prop object not found.
                     # For simplicity, let's try adding it with a note, assuming it's data property if unknown.
                     # A better approach might involve looking at the restriction types if available.
                     guessed_type_key = "data" # Default guess
                     # Attempt to guess based on restriction value types if prop not found? Too complex for now.

                     prop_entry = {
                         "name": prop_name,
                         "restrictions": details["restrictions"],
                         "sourced_information": details["descriptions"],
                         "warning": "Property object not found by name, type unknown/guessed."
                     }
                     # Attempt to add to a type list - let's default to data or create an 'unknown' category
                     # For now, adding to 'data' as a fallback representation
                     properties_summary["data"].append(prop_entry) # Or properties_summary.setdefault("unknown", []).append(prop_entry)
                     continue # Skip further processing for this prop_name

                 # Determine property type (handle metaclass case)
                 prop_type_key = "object" if isinstance(prop, (ObjectProperty, ObjectPropertyClass)) else "data"

                 # Create the entry using details from the new function
                 prop_entry = {
                     "name": prop_name,
                     "restrictions": details["restrictions"], # Already a list of dicts
                     "sourced_information": details["descriptions"] # Already a list of dicts
                 }
                 properties_summary[prop_type_key].append(prop_entry)

         # Assign the lists directly
         definition["properties"] = properties_summary


         # Hierarchy (using new private methods)
         parents = self._get_single_parents(class_name); # Call self!
         children = self._get_single_children(class_name) # Call self!
         if isinstance(parents, dict): errors["parents"] = parents["error"]
         if isinstance(children, dict): errors["children"] = children["error"]
         definition["hierarchy"] = {
             "parents": parents if isinstance(parents, list) else [],
             "children": children if isinstance(children, list) else [],
             "sourced_hierarchy_info": [{"content": str((getattr(i, 'content', ['']) or [''])[0]), "source": str((getattr(i, 'source', ['']) or [''])[0])} for i in self._get_sourced_info(cls, info_type="hierarchy")]
         }

         # Relations (using new private method)
         relations = self._get_single_related_classes(class_name) # Call self!
         if isinstance(relations, dict) and "error" in relations: errors["relations"] = relations["error"]
         definition["relations"] = relations if not ("error" in relations) else {}

         # Disjointness (using new private method)
         disjoint_with = self._get_single_disjoint_classes(class_name) # Call self!
         if isinstance(disjoint_with, dict): errors["disjoint_with"] = disjoint_with["error"]
         definition["disjoint_with"] = disjoint_with if isinstance(disjoint_with, list) else []

         if errors: definition["parsing_errors"] = errors
         return definition


    ####################################
    # Public API - Supports List Input
    ####################################

    # --- MODIFIED: Public API methods now call corresponding _get_single_... ---

    @thread_safe_method
    def get_class_info(self, class_names: Union[str, List[str]]) -> Dict[str, Dict]:
        """Get source information for one or more ontology classes.

        This function extracts basic descriptive content for the specified class(es)
        from their original information source. It is primarily used to provide
        background context from when the entity was recorded, such as its original,
        unstructured descriptive text.

        Usage Guidelines for get_class_info:
        - Use this function when: You want to understand the origin of a class or view
        its initial, raw descriptions. This function will return less information because the raw descriptions are short sentences or phrases.
        - Do not use this function when: You need structured knowledge, relationships,
        or a complete definition of the class.

        Alternative tools to get_class_info:
        - For comprehensive knowledge (properties, behavior, applications, etc.),
        use `get_class_properties`.
        - For other classes related to the specified class(es),
        use `get_related_classes`.
        - For the most detailed information available (including its raw ontology definition),
        use `parse_class_definition`.

        Args:
            class_names (Union[str, List[str]]): A single class name or a list of class names to query.

        Returns:
            Dict[str, Dict]: A dictionary where keys are the input class names.
                             Each value is a dictionary containing:
                             - 'name': The class name.
                             - 'information': A list of unique descriptive strings found.
                             If a class is not found or the ontology is not loaded, the value
                             will be a dictionary like {'error': '...'}.
        """
        if not self._check_ontology_loaded(): return {name: {"error": "本体未加载"} for name in ([class_names] if isinstance(class_names, str) else class_names)}
        if isinstance(class_names, str): class_names = [class_names]
        return {name: self._get_single_class_info(name) for name in class_names}

    @thread_safe_method
    def get_information_sources(self, class_names: Union[str, List[str]]) -> Dict[str, Union[List[str], Dict]]:
        """Get the sources of information associated with one or more ontology classes.

        Retrieves a list of unique source identifiers (e.g., document names, URLs)
        linked to the specified class(es) via 'SourcedInformation' instances.

        Args:
            class_names (Union[str, List[str]]): A single class name or a list of class names.

        Returns:
            Dict[str, Union[List[str], Dict]]: A dictionary where keys are input class names.
                                             Each value is either:
                                             - A sorted list of unique source identifier strings.
                                             - A dictionary like {'error': '...'} if the class
                                               is not found or the ontology is not loaded.
        """
        if not self._check_ontology_loaded(): return {name: {"error": "本体未加载"} for name in ([class_names] if isinstance(class_names, str) else class_names)}
        if isinstance(class_names, str): class_names = [class_names]
        return {name: self._get_single_information_sources(name) for name in class_names}

    # def get_information_by_source(self, class_names: Union[str, List[str]], source: str) -> Dict[str, Union[List[str], Dict]]:
    #     """Get information content associated with specific classes and a specific source.

    #     Retrieves the 'content' from 'SourcedInformation' instances that are linked
    #     to the specified class(es) AND have the specified 'source' identifier.

    #     Args:
    #         class_names (Union[str, List[str]]): A single class name or a list of class names.
    #         source (str): The specific source identifier to filter by.

    #     Returns:
    #         Dict[str, Union[List[str], Dict]]: A dictionary where keys are input class names.
    #                                          Each value is either:
    #                                          - A list of unique content strings matching the source.
    #                                          - A dictionary like {'error': '...'} if the class
    #                                            is not found or the ontology is not loaded.
    #     """
    #     if not self._check_ontology_loaded(): return {name: {"error": "本体未加载"} for name in ([class_names] if isinstance(class_names, str) else class_names)}
    #     if isinstance(class_names, str): class_names = [class_names]
    #      # Keep the internal function here as it's specific to this method's logic
    #     def _get_single_information_by_source(class_name: str, src: str) -> Union[List[str], Dict]:
    #         cls = self._get_class_by_name(class_name)
    #         if not cls: return {"error": f"类 '{class_name}' 未找到。"}
    #         matching_content = []
    #         sourced_infos = self._get_sourced_info(cls) # Use the class-level helper
    #         for info_instance in sourced_infos:
    #             try:
    #                 instance_sources = getattr(info_instance, 'source', [])
    #                 if isinstance(instance_sources, str): instance_sources = [instance_sources]
    #                 if src in instance_sources:
    #                     content = getattr(info_instance, 'content', None)
    #                     if content is not None:
    #                         if isinstance(content, list): matching_content.extend([str(c) for c in content])
    #                         else: matching_content.append(str(content))
    #             except AttributeError: pass
    #             except Exception as e: warnings.warn(f"为 '{class_name}' 和源 '{src}' 查找信息时出错: {e}")
    #         return list(set(matching_content))
    #     return {name: _get_single_information_by_source(name, source) for name in class_names}

    @thread_safe_method
    def get_class_properties(self, class_names: Union[str, List[str]]) -> Dict[str, Union[Dict[str, Dict[str, Any]], Dict]]:
        """Get detailed properties for one or more classes, including restrictions and descriptions.

        Retrieves detailed information about all the properties associated with the specified class(es),
        focusing on properties defined through restrictions (e.g., some, only, min, max)
        and descriptions derived from linked 'SourcedInformation'.

        Args:
            class_names (Union[str, List[str]]): A single class name or a list of class names. Never fill this with property names.

        Returns:
            Dict[str, Union[Dict[str, Dict[str, Any]], Dict]]:
                A dictionary where keys are the input class names. Each value is either:
                - A dictionary where keys are property names. Each property name maps to a
                  dictionary with keys 'restrictions' and 'descriptions'.
                    - 'restrictions': A list of dictionaries, each describing a restriction
                      (e.g., {'type': 'SOME', 'value': 'RelatedClass', 'raw_value': <RelatedClass>}).
                    - 'descriptions': A list of dictionaries from SourcedInformation, each with
                      'content', 'source', 'file_path'.
                - A dictionary like {'error': '...'} if the class is not found or the ontology is not loaded.
                Note: The top-level property dictionary includes properties found via restrictions OR descriptions.
                      If a property object isn't directly found but mentioned, a warning might be included.
        """
        if not self._check_ontology_loaded(): return {name: {"error": "本体未加载"} for name in ([class_names] if isinstance(class_names, str) else class_names)}
        if isinstance(class_names, str): class_names = [class_names]
        return {name: self._get_single_class_properties(name) for name in class_names} # Call self!

    def get_parents(self, class_names: Union[str, List[str]]) -> Dict[str, Union[List[str], Dict]]:
        """Get the direct parent classes (superclasses) for one or more classes.

        Retrieves the immediate parent classes in the hierarchy for the specified class(es).
        Excludes owl:Thing.

        Args:
            class_names (Union[str, List[str]]): A single class name or a list of class names.

        Returns:
            Dict[str, Union[List[str], Dict]]: A dictionary where keys are input class names.
                                             Each value is either:
                                             - A sorted list of direct parent class names.
                                             - An empty list if the class has no parents (or is top-level).
                                             - A dictionary like {'error': '...'} if the class
                                               is not found or the ontology is not loaded.
        """
        if not self._check_ontology_loaded(): return {name: {"error": "本体未加载"} for name in ([class_names] if isinstance(class_names, str) else class_names)}
        if isinstance(class_names, str): class_names = [class_names]
        return {name: self._get_single_parents(name) for name in class_names} # Call self!

    def get_children(self, class_names: Union[str, List[str]]) -> Dict[str, Union[List[str], Dict]]:
        """Get the direct child classes (subclasses) for one or more classes.

        Retrieves the immediate child classes in the hierarchy for the specified class(es).

        Args:
            class_names (Union[str, List[str]]): A single class name or a list of class names.

        Returns:
            Dict[str, Union[List[str], Dict]]: A dictionary where keys are input class names.
                                             Each value is either:
                                             - A sorted list of direct child class names.
                                             - An empty list if the class has no children (is a leaf).
                                             - A dictionary like {'error': '...'} if the class
                                               is not found or the ontology is not loaded.
        """
        if not self._check_ontology_loaded(): return {name: {"error": "本体未加载"} for name in ([class_names] if isinstance(class_names, str) else class_names)}
        if isinstance(class_names, str): class_names = [class_names]
        # Remove the internal definition, call the class-level private method
        return {name: self._get_single_children(name) for name in class_names} # Call self!

    def get_ancestors(self, class_names: Union[str, List[str]]) -> Dict[str, Union[List[str], Dict]]:
        """Get all ancestor classes (superclasses) for one or more classes.

        Retrieves all ancestor classes in the hierarchy for the specified class(es),
        going up to the top level. Excludes the class itself and owl:Thing.

        Args:
            class_names (Union[str, List[str]]): A single class name or a list of class names.

        Returns:
            Dict[str, Union[List[str], Dict]]: A dictionary where keys are input class names.
                                             Each value is either:
                                             - A sorted list of all unique ancestor class names.
                                             - An empty list if the class has no ancestors other than Thing.
                                             - A dictionary like {'error': '...'} if the class
                                               is not found or the ontology is not loaded.
        """
        if not self._check_ontology_loaded(): return {name: {"error": "本体未加载"} for name in ([class_names] if isinstance(class_names, str) else class_names)}
        if isinstance(class_names, str): class_names = [class_names]
         # Remove the internal definition, call the class-level private method
        return {name: self._get_single_ancestors(name) for name in class_names} # Call self!

    def get_descendants(self, class_names: Union[str, List[str]]) -> Dict[str, Union[List[str], Dict]]:
        """Get all descendant classes (subclasses) for one or more classes.

        Retrieves all descendant classes in the hierarchy for the specified class(es),
        going down to the leaf level. Excludes the class itself.

        Args:
            class_names (Union[str, List[str]]): A single class name or a list of class names.

        Returns:
            Dict[str, Union[List[str], Dict]]: A dictionary where keys are input class names.
                                             Each value is either:
                                             - A sorted list of all unique descendant class names.
                                             - An empty list if the class has no descendants.
                                             - A dictionary like {'error': '...'} if the class
                                               is not found or the ontology is not loaded.
        """
        if not self._check_ontology_loaded(): return {name: {"error": "本体未加载"} for name in ([class_names] if isinstance(class_names, str) else class_names)}
        if isinstance(class_names, str): class_names = [class_names]
         # Remove the internal definition, call the class-level private method
        return {name: self._get_single_descendants(name) for name in class_names} # Call self!

    def get_related_classes(self, class_names: Union[str, List[str]]) -> Dict[str, Union[Dict[str, List[str]], Dict]]:
        """Get classes related through object properties for one or more classes.

        Identifies classes that are related to the specified class(es) via existential (SOME),
        universal (ONLY), or value (VALUE) restrictions on object properties defined on the class
        or its ancestors.

        Args:
            class_names (Union[str, List[str]]): A single class name or a list of class names.

        Returns:
            Dict[str, Union[Dict[str, List[str]], Dict]]:
                A dictionary where keys are the input class names. Each value is either:
                - A dictionary where keys are object property names and values are sorted lists
                  of related class names found through restrictions on that property.
                - An empty dictionary if no such relationships are found.
                - A dictionary like {'error': '...'} if the class is not found, ontology is not loaded,
                  or an error occurs during property fetching.
        """
        if not self._check_ontology_loaded(): return {name: {"error": "本体未加载"} for name in ([class_names] if isinstance(class_names, str) else class_names)}
        if isinstance(class_names, str): class_names = [class_names]
        # Remove the internal definition, call the class-level private method
        return {name: self._get_single_related_classes(name) for name in class_names} # Call self!

    def get_disjoint_classes(self, class_names: Union[str, List[str]]) -> Dict[str, Union[List[str], Dict]]:
        """Get classes declared as disjoint with one or more classes.

        Retrieves classes that are explicitly declared as being disjoint with the
        specified class(es) using owl:disjointWith axioms.

        Args:
            class_names (Union[str, List[str]]): A single class name or a list of class names.

        Returns:
            Dict[str, Union[List[str], Dict]]: A dictionary where keys are input class names.
                                             Each value is either:
                                             - A sorted list of disjoint class names.
                                             - An empty list if no disjoint classes are declared.
                                             - A dictionary like {'error': '...'} if the class
                                               is not found or the ontology is not loaded.
        """
        if not self._check_ontology_loaded(): return {name: {"error": "本体未加载"} for name in ([class_names] if isinstance(class_names, str) else class_names)}
        if isinstance(class_names, str): class_names = [class_names]
         # Remove the internal definition, call the class-level private method
        return {name: self._get_single_disjoint_classes(name) for name in class_names} # Call self!

    @thread_safe_method
    def parse_class_definition(self, class_names: Union[str, List[str]]) -> Dict[str, Dict]:
        """Parse and retrieve a comprehensive definition for one or more classes.

        Aggregates various details about the specified class(es) into a structured format,
        including basic info, properties (data/object with restrictions/descriptions),
        hierarchy (parents/children), related classes, and disjoint classes.

        Args:
            class_names (Union[str, List[str]]): A single class name or a list of class names.

        Returns:
            Dict[str, Dict]: A dictionary where keys are input class names. Each value is either:
                             - A dictionary containing the comprehensive class definition with keys like
                               'basic_info', 'properties', 'hierarchy', 'relations', 'disjoint_with'.
                               See individual getter methods (e.g., get_class_properties, get_parents)
                               for the structure within these keys.
                             - A dictionary like {'error': '...'} if the class is not found or
                               the ontology is not loaded. May also contain a 'parsing_errors' key
                               if specific parts of the definition could not be retrieved.
        """
        if not self._check_ontology_loaded(): return {name: {"error": "本体未加载"} for name in ([class_names] if isinstance(class_names, str) else class_names)}
        if isinstance(class_names, str): class_names = [class_names]
        return {name: self._parse_single_class_definition(name) for name in class_names} # Call self!

    # --- MODIFIED: get_semantic_similarity using new private methods ---
    # def get_semantic_similarity(self, class1_name: str, class2_name: str) -> Union[float, Dict]:
    #     if not self._check_ontology_loaded(): return {"error": "本体未加载"}
    #     if class1_name == class2_name: return 1.0
    #     cls1 = self._get_class_by_name(class1_name); cls2 = self._get_class_by_name(class2_name)
    #     if not cls1: return {"error": f"类 '{class1_name}' 未找到。"}
    #     if not cls2: return {"error": f"类 '{class2_name}' 未找到。"}
    #     def jaccard_similarity(set1: Set, set2: Set) -> float: intersection = len(set1.intersection(set2)); union = len(set1.union(set2)); return intersection / union if union > 0 else 0.0
    #     try:
    #         # Use the NEW restriction-based property method via self
    #         props1_res = self._get_single_class_properties(class1_name)
    #         props2_res = self._get_single_class_properties(class2_name)
    #         prop_sim = 0.0
    #         # MODIFIED: Handle new return structure and exclude 'has_information'
    #         props1_names = set()
    #         props2_names = set()
    #         if isinstance(props1_res, dict) and "error" not in props1_res:
    #             props1_names = set(props1_res.keys())
    #         if isinstance(props2_res, dict) and "error" not in props2_res:
    #             props2_names = set(props2_res.keys())

    #         # Exclude 'has_information' if present
    #         props1_filtered = props1_names - {'has_information'}
    #         props2_filtered = props2_names - {'has_information'}

    #         # Calculate similarity only if both sets could be determined
    #         if props1_filtered is not None and props2_filtered is not None:
    #              prop_sim = jaccard_similarity(props1_filtered, props2_filtered)


    #         # Use the NEW ancestor method via self
    #         anc1_res = self._get_single_ancestors(class1_name); anc2_res = self._get_single_ancestors(class2_name); ancestor_sim = 0.0
    #         if not isinstance(anc1_res, dict) and not isinstance(anc2_res, dict): ancestor_sim = jaccard_similarity(set(anc1_res), set(anc2_res))

    #         # Info calculation remains the same
    #         info1_res = self._get_single_class_info(class1_name); info2_res = self._get_single_class_info(class2_name); info_sim = 0.0
    #         # Ensure we handle potential errors from _get_single_class_info
    #         info1_data = info1_res.get("information", []) if isinstance(info1_res, dict) else []
    #         info2_data = info2_res.get("information", []) if isinstance(info2_res, dict) else []
    #         info_sim = jaccard_similarity(set(info1_data), set(info2_data))

    #         # Weights can remain the same, or adjust if needed
    #         total_similarity = (0.4 * prop_sim) + (0.4 * ancestor_sim) + (0.2 * info_sim)
    #     except Exception as e: warnings.warn(f"计算 '{class1_name}' 和 '{class2_name}' 相似度时出错: {e}"); return {"error": f"计算相似度时出错: {e}"}
    #     return round(total_similarity, 4)


    # --- MODIFIED: parse_hierarchy_structure using new private methods ---
    def parse_hierarchy_structure(self, root_class_name: Optional[str] = None) -> Union[Dict, List[Dict]]:
        """Parse the class hierarchy structure of the ontology.

        Builds a tree or forest representation of the class hierarchy. If a root class
        is specified, it builds the subtree starting from that class. Otherwise, it builds
        a forest representing all top-level classes and their descendants. Detects cycles.

        Args:
            root_class_name (Optional[str], optional): The name of the class to use as the root
                                                      of the hierarchy tree. Defaults to None,
                                                      which parses the entire ontology hierarchy.

        Returns:
            Union[Dict, List[Dict]]:
                - If root_class_name is provided: A nested dictionary representing the subtree.
                  Each node has 'name' (str) and 'children' (List[Dict]). May include
                  'cyclic_dependency_detected': True or 'error_fetching_children': str.
                - If root_class_name is None: A list of such nested dictionaries, representing
                  the forest of top-level classes.
                - A dictionary like {'error': '...'} if the root class is not found, the ontology
                  is not loaded, or a critical error occurs during parsing.
        """
        if not self._check_ontology_loaded(): return {"error": "本体未加载"}
        memo = {}
        # build_subtree now needs access to self to call _get_single_children
        def build_subtree(self_obj: 'OntologyTools', class_name: str, visited_path: Set[str]) -> Dict: # Pass self_obj
            if class_name in memo: return memo[class_name]
            node = {"name": class_name, "children": []}
            if class_name in visited_path: node["cyclic_dependency_detected"] = True; memo[class_name] = node; return node
            visited_path.add(class_name)
            # Use the class-level private method via self_obj
            children_result = self_obj._get_single_children(class_name) # Call self_obj!
            if isinstance(children_result, dict) and "error" in children_result: node["error_fetching_children"] = children_result["error"]
            else:
                for child_name in children_result: node["children"].append(build_subtree(self_obj, child_name, visited_path.copy())) # Pass self_obj
            visited_path.remove(class_name); memo[class_name] = node; return node
        try:
            if root_class_name:
                root_cls = self._get_class_by_name(root_class_name)
                if not root_cls: return {"error": f"根类 '{root_class_name}' 未找到。"}
                memo.clear(); return build_subtree(self, root_class_name, set()) # Pass self
            else:
                top_level_classes = []
                all_classes = list(self.onto.classes()) # Assumes onto is loaded
                for cls in all_classes:
                     if not isinstance(cls, ThingClass) or cls == owlready2.Thing or not hasattr(cls, 'name'): continue
                     # Use the class-level private method via self
                     parents_res = self._get_single_parents(cls.name) # Call self!
                     if isinstance(parents_res, dict): warnings.warn(f"无法获取 '{cls.name}' 父类: {parents_res['error']}"); continue
                     if not parents_res: top_level_classes.append(cls.name)
                forest = []
                for top_class_name in sorted(top_level_classes): memo.clear(); forest.append(build_subtree(self, top_class_name, set())) # Pass self
                return forest
        except Exception as e: error_msg = f"解析层级结构时出错: {e}\n{traceback.format_exc()}"; warnings.warn(error_msg); return {"error": error_msg}

    def get_class_richness_info(self, class_name: str) -> Dict[str, Any]:
        """快速评估类的信息丰富度
        
        用于在查询处理中快速评估候选类的潜在价值，基于：
        1. 关联的属性数量（restrictions）
        2. SourcedInformation实例数量
        3. 层次关系丰富度
        
        Args:
            class_name: 类名
            
        Returns:
            包含丰富度指标的字典：
            - property_count: 关联的属性数量
            - sourced_info_count: SourcedInformation实例数量  
            - restriction_count: 限制条件数量
            - hierarchy_connections: 层次连接数（父类+子类）
            - richness_score: 综合丰富度分数 (0-1)
            - details: 详细信息用于调试
        """
        if not self._check_ontology_loaded():
            return {"error": "本体未加载", "richness_score": 0.0}
        
        cls = self._get_class_by_name(class_name)
        if not cls:
            return {"error": f"类 '{class_name}' 未找到", "richness_score": 0.0}
        
        try:
            # 1. 获取属性相关信息
            properties_result = self._get_single_class_properties(class_name)
            property_count = 0
            restriction_count = 0
            
            if isinstance(properties_result, dict) and "error" not in properties_result:
                property_count = len(properties_result)
                # 统计限制条件总数
                for prop_details in properties_result.values():
                    if isinstance(prop_details, dict) and "restrictions" in prop_details:
                        restriction_count += len(prop_details.get("restrictions", []))
            
            # 2. 获取SourcedInformation数量
            sourced_info_count = 0
            if self.has_information_prop and self.SourcedInformationClass:
                try:
                    sourced_infos = self._get_sourced_info(cls)
                    sourced_info_count = len(sourced_infos)
                except Exception as e:
                    warnings.warn(f"获取 '{class_name}' 的SourcedInformation时出错: {e}")
            
            # 3. 获取层次关系信息
            parents_result = self._get_single_parents(class_name)
            children_result = self._get_single_children(class_name)
            
            parent_count = len(parents_result) if isinstance(parents_result, list) else 0
            children_count = len(children_result) if isinstance(children_result, list) else 0
            hierarchy_connections = parent_count + children_count
            
            # 4. 计算综合丰富度分数
            # 使用加权评分系统，各指标权重可调整
            weights = {
                "properties": 0.3,      # 属性数量权重
                "sourced_info": 0.3,    # 源信息权重 
                "restrictions": 0.3,    # 限制条件权重
                "hierarchy": 0.1        # 层次关系权重最低
            }
            
            # 归一化各指标到0-1范围（使用经验性的最大值）
            normalized_scores = {
                "properties": min(property_count / 10.0, 1.0),  # 假设10个属性为满分
                "sourced_info": min(sourced_info_count / 10.0, 1.0),  # 假设5个SI为满分
                "restrictions": min(restriction_count / 10.0, 1.0),  # 假设15个限制为满分
                "hierarchy": min(hierarchy_connections / 8.0, 1.0)   # 假设8个连接为满分
            }
            
            # 计算加权平均分
            richness_score = sum(
                weights[key] * normalized_scores[key] 
                for key in weights.keys()
            )
            
            return {
                "property_count": property_count,
                "sourced_info_count": sourced_info_count,
                "restriction_count": restriction_count,
                "hierarchy_connections": hierarchy_connections,
                "richness_score": round(richness_score, 4),
                "details": {
                    "normalized_scores": normalized_scores,
                    "weights": weights,
                    "parent_count": parent_count,
                    "children_count": children_count
                }
            }
            
        except Exception as e:
            error_msg = f"评估类 '{class_name}' 丰富度时出错: {e}"
            warnings.warn(error_msg)
            return {
                "error": error_msg,
                "richness_score": 0.0,
                "property_count": 0,
                "sourced_info_count": 0,
                "restriction_count": 0,
                "hierarchy_connections": 0
            }

class OntologyAnalyzer:
    """本体分析工具 - 专注于本体结构分析"""
    
    def __init__(self, ontology_settings: Optional[OntologySettings] = None):
        # Store settings or use global default
        if ontology_settings is None:
            from config.settings import ONTOLOGY_SETTINGS as global_settings
            self.settings = global_settings
        else:
            self.settings = ontology_settings
            
        # Initialize LLM
        # Ensure OPENAI_API_KEY is loaded if ChatOpenAI relies on it implicitly
        # from config.settings import OPENAI_API_KEY 
        self.llm = ChatOpenAI(temperature=0) 
        
        # Initialize tools with the determined settings
        self.tools = OntologyTools(self.settings)
        
    def analyze_domain_structure(self) -> Dict:
        """分析领域的基本结构 (using self.settings and self.tools)"""
        
        # Use self.tools for parsing
        hierarchy = self.tools.parse_hierarchy_structure()
        properties_info = [self.tools.parse_property_definition(p.name) 
                         for p in self.settings.ontology.properties() 
                         if "error" not in self.tools.parse_property_definition(p.name)] # Filter errors
        class_names = [c.name for c in self.settings.ontology.classes()]

        structure_info = {
            "hierarchy": hierarchy, 
            "properties": properties_info,
            "classes": class_names
        }
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert in ontology analysis.
            Analyze the given ontology structure and identify key patterns and characteristics."""),
            ("user", """Analyze the following ontology structure:
            
            Classes: {classes}
            Properties: {properties}
            Hierarchy: {hierarchy}
            
            Provide a comprehensive analysis including:
            1. Core concepts and their relationships
            2. Key structural patterns
            3. Important property distributions
            4. Potential research areas
            
            Format as JSON with:
            - core_concepts: list[str]
            - key_patterns: list[dict]
            - property_analysis: dict
            - research_opportunities: list[dict]
            """)
        ])
        
        try:
            response = self.llm.invoke(prompt.format_messages(**structure_info))
            return parse_json(response.content)
        except Exception as e:
             print(f"Error during LLM invocation or JSON parsing in analyze_domain_structure: {e}")
             return {"error": f"Analysis failed: {e}"}
    
    def find_key_concepts(self) -> List[Dict]:
        """识别关键概念 (using self.settings and self.tools)"""
        
        classes_info = []
        for cls in self.settings.ontology.classes():
            cls_name = cls.name
            try: # Add error handling for tool calls
                 properties = self.tools.get_class_properties(cls_name)
                 parents = self.tools.get_parents(cls_name)
                 children = self.tools.get_children(cls_name)
                 related = self.tools.get_related_classes(cls_name)
                 class_info = {
                     "name": cls_name,
                     "properties": properties, 
                     "parents": parents, 
                     "children": children,
                     "related": related
                 }
                 classes_info.append(class_info)
            except Exception as e:
                 print(f"Error processing class {cls_name} in find_key_concepts: {e}")
                 # Optionally append an error entry or skip
                 classes_info.append({"name": cls_name, "error": str(e)})
            
        relationships = []
        for prop in self.settings.ontology.properties(): 
             try: # Add error handling
                  prop_def = self.tools.parse_property_definition(prop.name)
                  if "error" not in prop_def:
                       relationships.append(prop_def)
             except Exception as e:
                  print(f"Error processing property {prop.name} in find_key_concepts: {e}")
                  relationships.append({"name": prop.name, "error": str(e)})
            
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert in identifying key concepts in scientific domains."""),
            ("user", """Analyze these ontology concepts:
            
            Classes: {classes}
            Relationships: {relationships}
            
            Identify key concepts based on:
            1. Centrality in the network
            2. Property richness
            3. Connection patterns
            4. Research potential
            
            Format as JSON with:
            - key_concepts: list[dict]  # Each with name, importance_score, reasoning
            - research_value: dict  # Research potential for each concept
            """)
        ])
        
        try:
            response = self.llm.invoke(prompt.format_messages(
                classes=classes_info,
                relationships=relationships
            ))
            return parse_json(response.content)
        except Exception as e:
             print(f"Error parsing LLM response for key concepts: {e}")
             return {"error": "Failed to parse LLM response", "raw_content": response.content}
        
    def compare_domains(self, other_settings: OntologySettings) -> Dict:
        """比较 self.settings 和 other_settings 代表的领域"""
        
        # Analyze source domain (self)
        try:
            source_structure = self.analyze_domain_structure()
            source_key_concepts = self.find_key_concepts()
            source_analysis = {
                "structure": source_structure,
                "key_concepts": source_key_concepts
            }
        except Exception as e:
             print(f"Error analyzing source domain ({self.settings.ontology_iri}): {e}")
             return {"error": f"Failed to analyze source domain: {e}"}
        
        # Analyze target domain (other)
        try:
            # Create a temporary analyzer for the other settings
            target_analyzer = OntologyAnalyzer(other_settings)
            target_structure = target_analyzer.analyze_domain_structure()
            target_key_concepts = target_analyzer.find_key_concepts()
            target_analysis = {
                "structure": target_structure,
                "key_concepts": target_key_concepts
            }
        except Exception as e:
             print(f"Error analyzing target domain ({other_settings.ontology_iri}): {e}")
             return {"error": f"Failed to analyze target domain: {e}"}
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert in cross-domain knowledge transfer."""),
            ("user", """Compare these two domains:
            
            Source Domain Analysis ({self.settings.ontology_iri}):
            {source_analysis}
            
            Target Domain Analysis ({other_settings.ontology_iri}):
            {target_analysis}
            
            Analyze:
            1. Conceptual analogies
            2. Methodological differences
            3. Transfer opportunities
            4. Potential innovations
            
            Format as JSON with:
            - analogies: list[dict]  # 概念对应关系
            - method_differences: list[dict]  # 方法论差异
            - transfer_opportunities: list[dict]  # 知识迁移机会
            - innovation_points: list[dict]  # 创新点
            """)
        ])
        
        try:
            # Include IRIs in the formatted prompt for context
            response = self.llm.invoke(prompt.format_messages(
                source_analysis=source_analysis,
                target_analysis=target_analysis,
                # Pass IRIs separately if needed in the prompt template
                source_iri = self.settings.ontology_iri, 
                target_iri = other_settings.ontology_iri
            ))
            return parse_json(response.content)
        except Exception as e:
            print(f"Error parsing LLM response for domain comparison: {e}")
            return {"error": "Failed to parse LLM response", "raw_content": response.content}
    
    def get_research_opportunities(self, analysis_result: Dict) -> List[Dict]:
        """从分析结果中提取研究机会"""
        opportunities = []
        
        # 从领域结构分析中提取
        if isinstance(analysis_result, dict) and "research_opportunities" in analysis_result and isinstance(analysis_result["research_opportunities"], list):
            opportunities.extend(analysis_result["research_opportunities"]) 
            
        # 从关键概念分析中提取
        if isinstance(analysis_result, dict) and "key_concepts" in analysis_result and isinstance(analysis_result["key_concepts"], list):
             for concept in analysis_result["key_concepts"]:
                 # Add more robust checking for nested dictionaries/keys
                 if isinstance(concept, dict) and "research_value" in concept and isinstance(concept["research_value"], dict) and concept["research_value"].get("potential", 0) > 0.7:
                     opportunities.append({
                         "type": "concept_based",
                         "concept": concept.get("name", "Unknown"),
                         "opportunity": concept["research_value"].get("description", "N/A")
                     }) 
                    
        # 从跨领域分析中提取 (If analysis_result is from compare_domains)
        if isinstance(analysis_result, dict):
             transfer_opps = analysis_result.get("transfer_opportunities")
             innovation_pts = analysis_result.get("innovation_points")

             if isinstance(transfer_opps, list):
                 opportunities.extend([{"type": "transfer", **opp} for opp in transfer_opps if isinstance(opp, dict)])
             if isinstance(innovation_pts, list):
                 opportunities.extend([{"type": "innovation", **point} for point in innovation_pts if isinstance(point, dict)])
                
        return opportunities

    