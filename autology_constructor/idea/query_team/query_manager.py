from enum import Enum
from typing import Dict, List, Optional, Callable, Any
from pydantic import BaseModel, Field
import uuid
from datetime import datetime, timedelta
from queue import PriorityQueue
import threading
import time
import hashlib
# Assuming owlready2 is available in the environment
# from owlready2 import World, ThingClass # For type hinting if needed
from .schemas import Query, QueryStatus # Import Query and QueryStatus from schemas
from .query_adapter import QueryToStateAdapter, StateToQueryAdapter
from concurrent.futures import Future, ThreadPoolExecutor
import queue


class QueryCache:
    def __init__(self, ttl: int = 3600):  # 默认缓存1小时
        self.cache = {}  # 查询哈希到结果的映射
        self.timestamps = {}  # 查询哈希到时间戳的映射
        self.ttl = ttl  # 缓存生存时间(秒)
    
    def _generate_key(self, query: Query) -> str:
        """生成更稳定的缓存键"""
        # 使用内容哈希而非对象ID
        natural_query_hash = hashlib.md5(query.natural_query.encode()).hexdigest()
            
        # 使用查询类型、内容和本体哈希构建缓存键
        return f"{query.natural_query}:{natural_query_hash}"
    
    def get(self, query: Query) -> Optional[Dict]:
        """获取缓存的查询结果"""
        key = self._generate_key(query)
        if key in self.cache:
            # 检查是否过期
            timestamp = self.timestamps[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return self.cache[key]
            else:
                # 过期删除
                del self.cache[key]
                del self.timestamps[key]
        return None
    
    def set(self, query: Query, result: Dict) -> None:
        """缓存查询结果"""
        key = self._generate_key(query)
        self.cache[key] = result
        self.timestamps[key] = datetime.now()
    
    def clear(self) -> None:
        """清空缓存"""
        self.cache.clear()
        self.timestamps.clear()
    
    def cleanup(self) -> int:
        """清理过期缓存，返回清理的数量"""
        expired_keys = []
        now = datetime.now()
        
        for key, timestamp in self.timestamps.items():
            if now - timestamp > timedelta(seconds=self.ttl):
                expired_keys.append(key)
                
        for key in expired_keys:
            del self.cache[key]
            del self.timestamps[key]
            
        return len(expired_keys)


class QueryQueueManager:
    def __init__(self):
        self.pending_queries = PriorityQueue()  # 优先级队列
        self.active_queries = {}  # 正在处理的查询
        self.completed_queries = {}  # 已完成的查询
        self.retries = {}  # 查询ID到重试次数的映射
        self.max_retries = 3  # 最大重试次数
        self.failed_queries = {}  # 失败的查询
        self.cache = QueryCache()
        self._counter = 0  # 添加计数器，用于优先级队列中的稳定排序
        
    def enqueue(self, query: Query) -> str:
        """添加查询到队列，先检查缓存"""
        # 检查缓存
        cached_result = self.cache.get(query)
        if cached_result:
            # 直接存储为完成结果
            query.status = QueryStatus.COMPLETED
            self.completed_queries[query.query_id] = (query, cached_result)
            return query.query_id
            
        # 无缓存时正常入队
        priority = {"high": 1, "normal": 2, "low": 3}.get(query.priority, 2)
        # 递增计数器并使用它作为第二排序依据
        self._counter += 1
        self.pending_queries.put((priority, self._counter, query))
        return query.query_id
        
    def get_next_query(self) -> Optional[Query]:
        """获取下一个要处理的查询"""
        if self.pending_queries.empty():
            return None
        # 解包三元素元组
        _, _, query = self.pending_queries.get()
        self.active_queries[query.query_id] = query
        query.status = QueryStatus.PROCESSING
        return query
        
    def store_result(self, query_id: str, result: Dict) -> None:
        """存储查询结果并缓存"""
        if query_id in self.active_queries:
            query = self.active_queries.pop(query_id)
            query.status = QueryStatus.COMPLETED
            self.completed_queries[query_id] = (query, result)
            
            # 缓存结果(非错误结果才缓存)
            if not result.get("error"):
                self.cache.set(query, result)
            
    def get_result(self, query_id: str) -> Optional[Dict]:
        """获取查询结果，如果存在"""
        if query_id in self.completed_queries:
            return self.completed_queries[query_id][1]
        return None
    
    def mark_failed(self, query_id: str, error_message: str) -> None:
        """标记查询失败"""
        if query_id in self.active_queries:
            query = self.active_queries.pop(query_id)
            query.status = QueryStatus.FAILED
            self.failed_queries[query_id] = query  # 添加到失败查询字典
            self.completed_queries[query_id] = (query, {"error": error_message})

    def retry_query(self, query_id: str) -> bool:
        """尝试重新排队一个失败的查询。

        如果查询存在于失败列表且未达到最大重试次数，
        则更新重试次数，重置状态为 PENDING，将其重新放入队列，
        并从失败列表中移除，然后返回 True。否则返回 False。
        """
        if query_id in self.failed_queries:
            query = self.failed_queries[query_id]
            current_retries = self.retries.get(query_id, 0)

            if current_retries < self.max_retries:
                # 更新重试计数
                self.retries[query_id] = current_retries + 1

                # 重置状态并重新入队
                query.status = QueryStatus.PENDING
                priority = {"high": 1, "normal": 2, "low": 3}.get(query.priority, 2)
                # 递增计数器并使用三元素元组
                self._counter += 1
                self.pending_queries.put((priority, self._counter, query))

                # 从失败列表中移除
                del self.failed_queries[query_id]
                print(f"Query {query_id} successfully re-queued for retry ({self.retries[query_id]}/{self.max_retries}).")
                return True # Indicate success
            else:
                print(f"Query {query_id} reached max retries ({self.max_retries}). Cannot retry.")
        else:
            print(f"Query {query_id} not found in failed list. Cannot retry.")
        return False # Indicate failure to retry

class QueryManager:
    """独立的查询管理器，负责处理和管理所有查询请求"""
    
    # 类级别的共享锁，供所有实例和静态方法使用
    _shared_ontology_lock = None
    
    @classmethod
    def get_shared_lock(cls):
        """获取共享的本体工具锁"""
        return cls._shared_ontology_lock
    
    def __init__(self, max_workers: int = 4, ontology_settings=None, staggered_start: bool = False, start_interval: int = 5):
        """初始化查询管理器
        
        Args:
            max_workers: 最大工作线程数
            ontology_settings: OntologySettings实例，用于创建共享ontology_tools
            staggered_start: 是否使用错开启动（第一批查询错开提交）
            start_interval: 查询提交间隔（秒）
        """
        self.query_queue_manager = QueryQueueManager()
        self._query_to_state = QueryToStateAdapter()
        self._state_to_query = StateToQueryAdapter()
        self.class_name_cache: List[str] = []
        self.data_property_cache: List[str] = []  # 新增: 数据属性缓存
        self.object_property_cache: List[str] = []  # 新增: 对象属性缓存
        
        # ADDED Executor and Dispatcher related attributes
        self.executor = ThreadPoolExecutor(max_workers=max_workers) # Executor for query tasks
        self.task_futures: Dict[str, Future] = {} # Tracks Futures returned to callers
        self._task_futures_lock = threading.Lock() # Lock for task_futures dict
        self._dispatcher_thread: Optional[threading.Thread] = None # Dispatcher thread object
        self._stop_dispatcher_event = threading.Event() # Event to signal dispatcher stop

        # 错开启动配置
        self.staggered_start = staggered_start
        self.start_interval = start_interval
        self._first_batch_count = 0  # 第一批查询计数
        self._first_batch_lock = threading.Lock()  # 保护第一批计数
        
        # 新增：共享本体工具支持（并发优化）
        self.shared_ontology_tools = None
        self.shared_ontology_settings = None
        if ontology_settings:
            self._init_shared_ontology_tools(ontology_settings)

        # 推迟 LangGraph 初始化，避免循环导入
        self.query_graph = None
    
    def _initialize_graph(self):
        """Initializes the LangGraph query graph if not already done."""
        if self.query_graph is None:
            from .query_workflow import create_query_graph # Local import
            self.query_graph = create_query_graph()

    def _init_shared_ontology_tools(self, ontology_settings):
        """初始化共享OntologyTools + 对象级锁
        
        Args:
            ontology_settings: OntologySettings实例
        """
        try:
            print("正在初始化共享本体工具（对象级锁保护）...")
            
            # 创建临时SQLite文件支持缓存
            import tempfile
            import os
            from owlready2 import World
            
            sqlite_file = os.path.join(tempfile.gettempdir(), f"shared_ontology_object_lock_{os.getpid()}.sqlite3")
            
            # 创建共享World
            shared_world = World()
            
            # 检查是否已有缓存
            if os.path.exists(sqlite_file):
                print("  使用现有SQLite缓存...")
                shared_world.set_backend(filename=sqlite_file, exclusive=False)
                ontology = shared_world.get_ontology(ontology_settings.ontology_iri).load()
            else:
                print("  首次加载，创建SQLite缓存...")
                shared_world.set_backend(filename=sqlite_file, exclusive=False)
                ontology = shared_world.get_ontology(ontology_settings.ontology_iri).load(only_local=True)
                shared_world.save()  # 保存到SQLite文件
            
            # 创建OntologySettings副本
            from config.settings import OntologySettings
            shared_settings = OntologySettings(
                base_iri=ontology_settings.base_iri,
                ontology_file_name=ontology_settings.ontology_file_name,
                directory_path=ontology_settings.directory_path,
                # closed_ontology_file_name=ontology_settings.closed_ontology_file_name
            )
            
            # 替换其内部World为共享的World
            shared_settings._world = shared_world
            shared_settings._ontology = ontology
            
            # 创建共享的OntologyTools（不启用内部锁）
            from .ontology_tools import OntologyTools
            self.shared_ontology_tools = OntologyTools(shared_settings, thread_safe=False)
            self.shared_ontology_settings = shared_settings
            
            # 创建对象级锁保护整个OntologyTools
            import threading
            self.ontology_tools_lock = threading.RLock()
            
            # 设置类级别的共享锁，供其他模块使用
            QueryManager._shared_ontology_lock = self.ontology_tools_lock
            
            # 同时更新所有缓存
            self.update_all_caches(ontology)
            
            print(f"共享本体工具初始化完成，SQLite文件：{sqlite_file}")
            print(f"对象级RLock保护已启用，支持最大{self.executor._max_workers}个并发线程")
            
        except Exception as e:
            print(f"共享本体工具初始化失败：{e}")
            print("将回退到独立实例模式")
            import traceback
            traceback.print_exc()
            self.shared_ontology_tools = None
            self.shared_ontology_settings = None
            self.ontology_tools_lock = None

    def _validate_query_ontology(self, query_ontology_settings):
        """验证查询使用的本体是否与共享本体匹配
        
        Args:
            query_ontology_settings: 查询指定的本体设置
            
        Returns:
            bool: True表示匹配或可以使用共享本体，False表示不匹配
        """
        if not query_ontology_settings:
            # 空值默认使用共享本体
            return True
        
        if not self.shared_ontology_settings:
            # 共享本体未初始化
            return False
        
        # 检查关键标识符是否匹配
        return (query_ontology_settings.base_iri == self.shared_ontology_settings.base_iri and 
                query_ontology_settings.ontology_file_name == self.shared_ontology_settings.ontology_file_name)

    def update_class_name_cache(self, ontology: Any):
        """Manually update the class name cache from the ontology."""
        if ontology and hasattr(ontology, 'classes'):
            try:
                self.class_name_cache = sorted([cls.name for cls in ontology.classes()])
                print(f"Class name cache updated with {len(self.class_name_cache)} classes.")
            except Exception as e:
                print(f"Error updating class name cache: {e}")
        else:
            print("Warning: Ontology object invalid or missing 'classes' attribute during cache update.")
            self.class_name_cache = []
            
    def update_data_property_cache(self, ontology: Any):
        """更新数据属性缓存。

        从本体中提取所有数据属性的名称并排序存储。
        
        Args:
            ontology: 包含data_properties方法的本体对象
        """
        self.data_property_cache = []
        if ontology and hasattr(ontology, 'data_properties'):
            try:
                self.data_property_cache = sorted([prop.name for prop in ontology.data_properties()])
                print(f"数据属性缓存更新完成，共 {len(self.data_property_cache)} 个属性")
            except Exception as e:
                print(f"更新数据属性缓存时出错: {e}")
        else:
            print("警告: 本体对象无效或缺少'data_properties'属性，数据属性缓存已清空")
            
    def update_object_property_cache(self, ontology: Any):
        """更新对象属性缓存。

        从本体中提取所有对象属性的名称并排序存储。
        
        Args:
            ontology: 包含object_properties方法的本体对象
        """
        self.object_property_cache = []
        if ontology and hasattr(ontology, 'object_properties'):
            try:
                self.object_property_cache = sorted([prop.name for prop in ontology.object_properties()])
                print(f"对象属性缓存更新完成，共 {len(self.object_property_cache)} 个属性")
            except Exception as e:
                print(f"更新对象属性缓存时出错: {e}")
        else:
            print("警告: 本体对象无效或缺少'object_properties'属性，对象属性缓存已清空")
            
    def update_all_caches(self, ontology: Any):
        """更新所有本体相关缓存（类名、数据属性、对象属性）。
        
        提供一个统一的入口点，确保所有缓存同时更新，保持数据一致性。
        
        Args:
            ontology: 本体对象，应具有classes、data_properties和object_properties方法
        """
        self.update_class_name_cache(ontology)
        self.update_data_property_cache(ontology)
        self.update_object_property_cache(ontology)
        print("所有本体缓存更新完成")

    def start(self):
        """Initializes the graph and starts the dispatcher thread."""
        self._initialize_graph()
        if self._dispatcher_thread is None or not self._dispatcher_thread.is_alive():
            self._stop_dispatcher_event.clear()
            self._dispatcher_thread = threading.Thread(target=self._dispatch_loop, daemon=True, name="QueryDispatcherThread")
            self._dispatcher_thread.start()
            print("Query Manager dispatcher started.")

    def stop(self):
        """Stops the dispatcher thread and shuts down the executor."""
        print("Stopping Query Manager...")
        self._stop_dispatcher_event.set()
        if self._dispatcher_thread and self._dispatcher_thread.is_alive():
            # Give the dispatcher a chance to exit cleanly after seeing the event
            self._dispatcher_thread.join(timeout=2.0) 
        print("Shutting down query executor...")
        # Shutdown executor, wait=True ensures tasks finish (adjust as needed)
        self.executor.shutdown(wait=True) 
        print("Query Manager stopped.")

    def _dispatch_loop(self):
        """Continuously fetches queries from the queue and submits them to the executor."""
        print(f"Dispatcher loop started on thread {threading.current_thread().name}")
        while not self._stop_dispatcher_event.is_set():
            try:
                # Use timeout in get() to allow checking the stop event periodically
                priority, _, query = self.query_queue_manager.pending_queries.get(block=True, timeout=0.5)
                # print(f"Dispatching query: {query.query_id}") # Optional: for debugging
                # Submit the task execution to the thread pool
                # We don't need the future returned by submit here, as we already created one in submit_query
                self.executor.submit(self._execute_query_task, query)
            except queue.Empty:
                # Queue is empty, loop continues to check stop event
                continue
            except Exception as e:
                # Log unexpected errors in the dispatcher loop itself
                print(f"Error in dispatcher loop: {e}")
                # Avoid tight loop on persistent errors
                time.sleep(0.5) 
        print("Dispatcher loop exiting.")

    def _execute_query_task(self, query: Query):
        """Executes a single query task in an executor thread and completes its Future."""
        # print(f"Executing query {query.query_id} on thread {threading.current_thread().name}") # Optional: debugging
        result: Optional[Dict] = None
        exception: Optional[Exception] = None
        result_future: Optional[Future] = None # To store the future associated with this query

        try:
            # Retrieve the future BEFORE execution
            with self._task_futures_lock:
                # Don't pop yet, just retrieve.
                result_future = self.task_futures.get(query.query_id)

            if not result_future:
                 print(f"Warning: Future not found for query {query.query_id} at start of execution.")
                 self.query_queue_manager.mark_failed(query.query_id, "Internal error: Future not found")
                 return 

            # Ensure graph is ready 
            if self.query_graph is None:
                 raise RuntimeError("Query graph not initialized before executing task.")

            # Execute the core logic
            result = self._execute_query_with_langgraph(query)
            self.query_queue_manager.store_result(query.query_id, result)

        except Exception as e:
            exception = e
            self.handle_error(e) # Log or handle the error
            self.query_queue_manager.mark_failed(query.query_id, str(e)) # Mark in QQM state

        finally:
            # Complete the Future and remove it from tracking
            final_future_to_complete: Optional[Future] = None
            with self._task_futures_lock:
                # Use pop to get and remove atomically
                final_future_to_complete = self.task_futures.pop(query.query_id, None)

            if final_future_to_complete:
                # Check if the future is already done (e.g., cancelled), though cancellation isn't implemented here
                if not final_future_to_complete.done(): 
                    if exception:
                        final_future_to_complete.set_exception(exception)
                    else:
                        # Ensure result is a dict even if None was somehow returned
                        final_result = result if result is not None else {}
                        final_future_to_complete.set_result(final_result)
                    # print(f"Completed future for query {query.query_id}") # Optional: debugging
            # else: (Optional log) Future was already removed or never found.

    def handle_error(self, error: Exception):
        """处理错误"""
        # Consider adding more sophisticated logging here
        print(f"Query processing error: {str(error)}")
        
    def _execute_query_with_langgraph(self, query: Query) -> Dict:
        """使用共享OntologyTools执行查询（对象级锁保护）"""
        # 将Query转换为QueryState
        query_state = self._query_to_state.transform(query)
        
        # 将所有缓存添加到初始状态
        query_state["available_classes"] = self.class_name_cache
        query_state["available_data_properties"] = self.data_property_cache
        query_state["available_object_properties"] = self.object_property_cache

        # 获取查询指定的本体设置
        original_settings = query_state["source_ontology"]
        
        # 优先使用共享OntologyTools（对象级锁保护）
        if self.shared_ontology_tools and self.ontology_tools_lock and self._validate_query_ontology(original_settings):
            print(f"使用共享本体工具（对象级锁保护），线程：{threading.current_thread().name}")
            query_state["ontology_tools"] = self.shared_ontology_tools
            query_state["source_ontology"] = self.shared_ontology_settings
            query_state["ontology_tools_lock"] = self.ontology_tools_lock  # 传递锁给工作流
        else:
            # 回退到独立实例
            if not original_settings:
                if self.shared_ontology_tools:
                    print("使用共享本体工具作为回退选项")
                    query_state["ontology_tools"] = self.shared_ontology_tools
                    query_state["source_ontology"] = self.shared_ontology_settings
                    query_state["ontology_tools_lock"] = self.ontology_tools_lock
                else:
                    raise ValueError("source_ontology is required when shared tools unavailable")
            else:
                print(f"回退到独立本体工具实例，线程：{threading.current_thread().name}")
                from .ontology_tools import OntologyTools
                from config.settings import OntologySettings
                
                independent_settings = OntologySettings(
                    base_iri=original_settings.base_iri,
                    ontology_file_name=original_settings.ontology_file_name,
                    directory_path=original_settings.directory_path,
                    # closed_ontology_file_name=original_settings.closed_ontology_file_name
                )
                # 创建独立实例（不需要锁）
                ontology_tools = OntologyTools(independent_settings, thread_safe=False)
                query_state["ontology_tools"] = ontology_tools
                query_state["source_ontology"] = independent_settings
                query_state["ontology_tools_lock"] = None  # 独立实例不需要锁
        
        # 创建query graph
        from .query_workflow import create_query_graph
        query_graph = create_query_graph()
             
        # 配置递归限制
        config = {"recursion_limit": 50}
        final_state = query_graph.invoke(query_state, config=config)

        # 将最终的QueryState转换回Query对象
        self._state_to_query.transform(final_state, query)

        return final_state
    
    def submit_query(self, query_text: str, 
                    query_context: Dict = None,
                    priority: str = "normal") -> Future: # Changed return type
        """提交查询并返回一个 concurrent.futures.Future 对象来获取结果。

        可以通过 Future 对象的 result(), exception(), done() 等方法交互。
        使用 add_done_callback(fn) 注册的回调函数 fn 将接收 Future 对象本身作为其唯一参数 (fn(future))。
        在回调内部，使用 future.result() (可能引发异常) 或 future.exception() 获取结果。
        """        
        # 创建查询实例
        query = Query(
            natural_query=query_text,
            originating_team=query_context.get("originating_team", "unknown"),
            originating_agent=query_context.get("originating_agent", "unknown"),
            priority=priority,
            query_context=query_context or {}
        )
        
        # 错开启动逻辑：第一批查询错开提交
        if self.staggered_start:
            with self._first_batch_lock:
                current_batch_index = self._first_batch_count
                if self._first_batch_count < self.executor._max_workers:
                    self._first_batch_count += 1
                    stagger_delay = current_batch_index * self.start_interval
                    if stagger_delay > 0:
                        print(f"[StaggeredStart] 查询 {query.query_id} 将延迟 {stagger_delay} 秒提交")
                        time.sleep(stagger_delay)
        
        # Create and store the Future before enqueuing
        future = Future()
        with self._task_futures_lock:
            self.task_futures[query.query_id] = future
        
        # Enqueue the query; the dispatcher will pick it up
        self.query_queue_manager.enqueue(query)
        
        return future
    
    def retry_failed_queries(self) -> Dict[str, Future]: # Changed return type
        """尝试重试所有当前失败的查询。

        对于每个成功重新排队的查询，会创建一个新的 Future 对象来追踪这次重试。
        返回一个字典，其中键是成功发起重试的查询 ID，值是对应的新的 Future 对象。
        调用者负责处理这些返回的 Future。原始失败的 Future 状态不变。
        """
        retried_futures: Dict[str, Future] = {} # Initialize dict for returning new futures
        # Grab IDs first to avoid modification issues during iteration
        failed_ids = list(self.query_queue_manager.failed_queries.keys())

        print(f"Attempting to retry {len(failed_ids)} failed queries...")
        for query_id in failed_ids:
            # Call the modified QQM method
            was_requeued = self.query_queue_manager.retry_query(query_id)
            if was_requeued:
                # Create and register a NEW future for this retry attempt
                new_future = Future()
                with self._task_futures_lock:
                    # Overwrite any existing future for this query_id in the manager's tracking
                    # This ensures the task executor finds and completes this new future
                    self.task_futures[query_id] = new_future
                # Store the new future in the dictionary to be returned
                retried_futures[query_id] = new_future

        print(f"Successfully initiated retry for {len(retried_futures)} queries.")
        return retried_futures