from typing import List, Dict, Any, Union, Protocol, Optional
from owlready2 import Thing, ThingClass
import json
import re
import html

def parse_json(content: str) -> Optional[Union[Dict, List]]:
    """
    Robustly parses a JSON string from LLM output.

    It attempts to handle common issues like:
    - Content being wrapped in markdown code fences (```json ... ```).
    - Extraneous text before or after the JSON object/array.
    - Standard JSON decoding errors.

    Args:
        content: The string content, potentially containing a JSON object or list.

    Returns:
        The parsed Python Dict or List if successful, otherwise None.
    
    Example:
        >>> content = 'Here is the plan: [{"operation": "get_class_info", "args": {"class_name": "calixarene"}}]'
        >>> result = parse_json(content)
        >>> isinstance(result, list)
        True
        >>> content = '{"key": "value"}'
        >>> parse_json(content)
        {'key': 'value'}
        >>> content = 'This is not json.'
        >>> parse_json(content) is None
        True
    """
    if not isinstance(content, str):
        return None

    # 1. Clean the string: strip whitespace and remove markdown fences
    processed_content = content.strip()
    if processed_content.startswith("```json"):
        processed_content = processed_content[7:]
    elif processed_content.startswith("```"):
        processed_content = processed_content[3:]
    
    if processed_content.endswith("```"):
        processed_content = processed_content[:-3]
    
    processed_content = processed_content.strip()

    # 2. First, try to parse the whole cleaned string
    try:
        return json.loads(processed_content)
    except json.JSONDecodeError:
        # If it fails, proceed to find the json structure within the string
        pass

    # 3. If direct parsing fails, find the first occurrence of a JSON-like structure
    # This helps if the LLM includes explanatory text before/after the JSON.
    match = re.search(r'\{.*\}|\[.*\]', processed_content, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            # This is the final attempt. If it fails, we log and return None.
            print(f"JSON解析错误: Failed to parse extracted string '{json_str[:100]}...': {e}")
            return None
    
    # 4. If no JSON-like structure is found at all
    print(f"JSON解析错误: No valid JSON structure found in the content.")
    return None

def format_owlready2_value(value: Any) -> Union[str, List[str], Dict]:
    """格式化owlready2返回的值
    
    Args:
        value: owlready2返回的值（可能是Thing, ThingClass或其他类型）
        
    Returns:
        格式化后的值
        
    Example:
        >>> class1 = ThingClass("Calixarene")
        >>> format_owlready2_value(class1)
        'Calixarene'
    """
    if isinstance(value, (Thing, ThingClass)):
        return value.name
    elif isinstance(value, (list, set)):
        return [format_owlready2_value(v) for v in value]
    elif isinstance(value, dict):
        return {k: format_owlready2_value(v) for k, v in value.items()}
    else:
        return str(value)

def format_sparql_results(results: List) -> Dict[str, Any]:
    """格式化SPARQL查询结果
    
    Args:
        results: SPARQL查询返回的结果列表
        
    Returns:
        格式化后的结果字典
        
    Example:
        >>> results = [(Thing("calixarene"), "binds", Thing("metal_ion"))]
        >>> format_sparql_results(results)
        {'results': [{'var0': 'calixarene', 'var1': 'binds', 'var2': 'metal_ion'}]}
    """
    formatted = []
    
    for result in results:
        if isinstance(result, tuple):
            item = {}
            for i, value in enumerate(result):
                item[f"var{i}"] = format_owlready2_value(value)
            formatted.append(item)
        else:
            formatted.append({"result": format_owlready2_value(result)})
            
    return {"results": formatted}

def extract_variables_from_sparql(query: str) -> List[str]:
    """从SPARQL查询中提取变量名
    
    Args:
        query: SPARQL查询字符串
        
    Returns:
        变量名列表
        
    Example:
        >>> query = "SELECT ?x ?y WHERE { ?x rdf:type ?y }"
        >>> extract_variables_from_sparql(query)
        ['x', 'y']
    """
    variables = re.findall(r'\?(\w+)', query)
    return list(dict.fromkeys(variables))  # 去重保持顺序

class FormatterBase(Protocol):
    """格式化器基础接口"""
    
    def format(self, results: Dict, options: Dict) -> str:
        """格式化查询结果
        
        Args:
            results: 查询结果字典
            options: 格式化选项
            
        Returns:
            格式化后的字符串
        """
        ...

class TextFormatter:
    """文本格式化器"""
    
    def format(self, results: Dict, options: Dict) -> str:
        """将结果格式化为文本
        
        Args:
            results: 查询结果字典
            options: 格式化选项，支持:
                - compact: 是否使用紧凑格式，默认False
                - delimiter: 结果项之间的分隔符，默认两个换行
                - item_template: 每个项的模板，默认"{key}: {value}"
                
        Returns:
            格式化后的文本
        """
        if not results or 'results' not in results:
            return "No results found"
        
        # 获取选项
        compact = options.get('compact', False)
        delimiter = options.get('delimiter', '\n\n')
        item_template = options.get('item_template', '{key}: {value}')
        
        # 获取变量名，如果有
        variables = results.get('variables', [])
        
        formatted = []
        for result in results['results']:
            if variables and len(variables) == len(result):
                # 使用变量名
                items = [
                    item_template.format(key=var, value=result.get(f"var{i}", "N/A"))
                    for i, var in enumerate(variables)
                ]
            else:
                # 使用默认键值
                items = [
                    item_template.format(key=k, value=v)
                    for k, v in result.items()
                ]
            
            # 紧凑模式使用单行
            if compact:
                formatted.append(", ".join(items))
            else:
                formatted.append("\n".join(items))
        
        return delimiter.join(formatted)

class JsonFormatter:
    """JSON格式化器"""
    
    def format(self, results: Dict, options: Dict) -> str:
        """将结果格式化为JSON
        
        Args:
            results: 查询结果字典
            options: 格式化选项，支持:
                - indent: JSON缩进，默认2
                - ensure_ascii: 是否转义非ASCII字符，默认False
                - rename_vars: 是否用变量名替换var0、var1等，默认True
                
        Returns:
            格式化后的JSON字符串
        """
        if not results or 'results' not in results:
            return json.dumps({"error": "No results found"})
        
        # 获取选项
        indent = options.get('indent', 2)
        ensure_ascii = options.get('ensure_ascii', False)
        rename_vars = options.get('rename_vars', True)
        
        # 获取变量名
        variables = results.get('variables', [])
        
        # 创建返回结果的副本
        formatted_results = {"results": []}
        
        # 处理查询信息
        if 'query_info' in results:
            formatted_results['query_info'] = results['query_info']
        
        # 如果有变量并且需要重命名
        if variables and rename_vars:
            for result in results['results']:
                renamed_result = {}
                for i, var in enumerate(variables):
                    if f"var{i}" in result:
                        renamed_result[var] = result[f"var{i}"]
                    else:
                        # 保留其他字段
                        for k, v in result.items():
                            if not k.startswith('var'):
                                renamed_result[k] = v
                
                formatted_results["results"].append(renamed_result)
        else:
            # 直接使用原始结果
            formatted_results["results"] = results['results']
            
        # 添加变量信息
        if variables:
            formatted_results["variables"] = variables
            
        # 转换为JSON
        return json.dumps(formatted_results, indent=indent, ensure_ascii=ensure_ascii)

class HtmlFormatter:
    """HTML格式化器"""
    
    def format(self, results: Dict, options: Dict) -> str:
        """将结果格式化为HTML
        
        Args:
            results: 查询结果字典
            options: 格式化选项，支持:
                - table_class: 表格CSS类，默认"query-results"
                - header: 是否显示表头，默认True
                - style: 内联CSS样式，默认提供基本样式
                
        Returns:
            格式化后的HTML字符串
        """
        if not results or 'results' not in results:
            return "<div class='no-results'>No results found</div>"
        
        # 获取选项
        table_class = options.get('table_class', 'query-results')
        show_header = options.get('header', True)
        style = options.get('style', """
            <style>
                .query-results {
                    border-collapse: collapse;
                    width: 100%;
                    margin: 10px 0;
                    font-family: Arial, sans-serif;
                }
                .query-results th, .query-results td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                .query-results tr:nth-child(even) {
                    background-color: #f2f2f2;
                }
                .query-results th {
                    padding-top: 12px;
                    padding-bottom: 12px;
                    background-color: #4CAF50;
                    color: white;
                }
                .no-results {
                    color: #666;
                    font-style: italic;
                    padding: 10px;
                }
            </style>
        """)
        
        # 获取变量名
        variables = results.get('variables', [])
        
        # 确定表头
        if variables:
            headers = variables
        elif results['results'] and len(results['results']) > 0:
            # 使用第一个结果的键作为表头
            headers = list(results['results'][0].keys())
        else:
            headers = []
        
        # 构建HTML
        html_parts = []
        
        # 添加样式
        if style:
            html_parts.append(style)
        
        # 开始表格
        html_parts.append(f"<table class='{table_class}'>")
        
        # 添加表头
        if show_header and headers:
            html_parts.append("<thead><tr>")
            for header in headers:
                html_parts.append(f"<th>{html.escape(header)}</th>")
            html_parts.append("</tr></thead>")
        
        # 添加表体
        html_parts.append("<tbody>")
        
        for result in results['results']:
            html_parts.append("<tr>")
            
            if variables:
                # 使用变量顺序显示
                for i, var in enumerate(variables):
                    value = result.get(f"var{i}", "")
                    html_parts.append(f"<td>{html.escape(str(value))}</td>")
            else:
                # 使用结果中的所有值
                for value in result.values():
                    html_parts.append(f"<td>{html.escape(str(value))}</td>")
                    
            html_parts.append("</tr>")
            
        html_parts.append("</tbody></table>")
        
        return "".join(html_parts)

class ResultFormatter:
    """查询结果格式化器
    
    支持多种输出格式的查询结果格式化器，基于策略模式实现。
    """
    
    def __init__(self, format_type: str = "text"):
        """初始化格式化器
        
        Args:
            format_type: 输出格式类型，支持 "text", "json", "html"
        """
        self.formatters = {
            "text": TextFormatter(),
            "json": JsonFormatter(),
            "html": HtmlFormatter()
        }
        
        if format_type not in self.formatters:
            raise ValueError(f"不支持的格式类型: {format_type}，可用类型: {', '.join(self.formatters.keys())}")
            
        self.formatter = self.formatters[format_type]
    
    def format(self, results: Dict, options: Optional[Dict] = None) -> str:
        """格式化查询结果
        
        Args:
            results: 查询结果字典
            options: 格式化选项，不同格式类型支持不同选项
            
        Returns:
            格式化后的字符串
        """
        return self.formatter.format(results, options or {})

def format_query_results(results: Dict, variables: List[str] = None, format_type: str = "text", options: Dict = None) -> str:
    """格式化查询结果为可读字符串
    
    Args:
        results: 查询结果字典
        variables: 可选的变量名列表
        format_type: 输出格式类型，支持 "text", "json", "html"
        options: 格式化选项
        
    Returns:
        格式化后的字符串
        
    Examples:
        >>> results = {"results": [{"var0": "CalixareneA", "var1": "binds"}]}
        >>> format_query_results(results, ["name", "action"])
        'name: CalixareneA\\naction: binds'
        
        >>> format_query_results(results, format_type="json")
        '{"results": [{"var0": "CalixareneA", "var1": "binds"}]}'
        
        >>> format_query_results(results, format_type="html")
        '<table class="query-results">...'
    """
    # 如果提供了变量，添加到结果中
    if variables:
        results = results.copy()
        results["variables"] = variables
    
    # 使用ResultFormatter
    formatter = ResultFormatter(format_type)
    return formatter.format(results, options or {})

def format_class_info(class_info: Dict) -> str:
    """Format class information as a readable string"""
    result = f"Information of '{class_info['name']}':\n"
    for item in class_info['information']:
        result += f"  - {item}\n"
    result += f"Source of '{class_info['name']}':\n"
    for item in class_info['source']:
        result += f"  - {item}\n"
    return result

def format_restrictions(restrictions: List[Dict], class_name: str, property_name: str) -> str:
    """Format property restrictions as a readable string"""
    result = f"{class_name} class restrictions on property {property_name}:\n"
    for r in restrictions:
        result += f"Type: {r['type']}\n"
        result += f"Value: {r['value']}\n"
        result += "---\n"
    return result

def format_hierarchy(parents: List[str], children: List[str], class_name: str) -> str:
    """Format class hierarchy information as a readable string"""
    result = f"Hierarchy for class '{class_name}':\n"
    if parents:
        result += "Parents:\n"
        for p in parents:
            result += f"  - {p}\n"
    if children:
        result += "Children:\n"
        for c in children:
            result += f"  - {c}\n"
    return result 

def format_sparql_error(error_dict: Dict) -> str:
    """格式化SPARQL查询错误信息为更友好的提示
    
    Args:
        error_dict: 包含错误信息的字典
        
    Returns:
        格式化后的错误信息字符串
        
    Example:
        >>> error = {"error": "Syntax error at line 2", "query": "SELECT ?x { ?x a ?y }"}
        >>> format_sparql_error(error)
        'SPARQL查询失败: Syntax error at line 2\n查询: SELECT ?x { ?x a ?y }'
    """
    if not error_dict or "error" not in error_dict:
        return "未知SPARQL查询错误"
    
    error_msg = error_dict["error"]
    query = error_dict.get("query", "")
    
    # 常见错误模式及友好提示
    error_patterns = {
        r"syntax\s+error": "语法错误",
        r"parse\s+error": "解析错误",
        r"undefined\s+prefix": "未定义前缀",
        r"type\s+error": "类型错误",
        r"variable\s+not\s+bound": "变量未绑定"
    }
    
    # 尝试匹配常见错误模式
    friendly_error = error_msg
    for pattern, message in error_patterns.items():
        if re.search(pattern, error_msg, re.IGNORECASE):
            # 提取错误位置或详情
            details = re.sub(pattern, "", error_msg, flags=re.IGNORECASE).strip()
            if details:
                friendly_error = f"{message}: {details}"
            else:
                friendly_error = message
            break
    
    # 格式化结果
    result = f"SPARQL查询失败: {friendly_error}"
    if query:
        # 如果查询太长，截断显示
        max_query_length = 150
        if len(query) > max_query_length:
            query = query[:max_query_length] + "..."
        result += f"\n查询: {query}"
    
    # 添加可能的修复建议
    if "syntax error" in error_msg.lower():
        result += "\n可能的修复: 检查查询语法，确保大括号配对并正确使用分隔符"
    elif "undefined prefix" in error_msg.lower():
        result += "\n可能的修复: 添加缺失的PREFIX声明"
    elif "variable not bound" in error_msg.lower():
        result += "\n可能的修复: 确保所有投影变量在查询模式中使用"
    
    return result 