import re
import ast # 用于安全地解析类Python字面量的字符串

class OwlFormattor:
    def __init__(self, owl_content_string: str):
        self.content = owl_content_string
        self.skipped_bracket_expressions = [] # 存储因内容不一致而跳过的方括号表达式

    def _normalize_string(self, s: str) -> str:
        """
        将字符串转换为小写，并将一个或多个连续空格替换为单个下划线。
        """
        s = s.lower()
        s = re.sub(r'\s+', '_', s)
        return s

    def _process_square_brackets_match(self, match_obj) -> str:
        """
        处理正则表达式匹配到的方括号表达式。
        例如 "['example_text', 'Example Text']"
        """
        original_expression = match_obj.group(0) # 完整的匹配，如 "['text1', 'Text2']"

        try:
            # 尝试使用 ast.literal_eval 将其解析为 Python 列表
            # 这能安全地处理字符串内的引号和转义
            parsed_list = ast.literal_eval(original_expression)

            if not (isinstance(parsed_list, list) and len(parsed_list) == 2 and
                    isinstance(parsed_list[0], str) and isinstance(parsed_list[1], str)):
                # 如果解析结果不是预期的[str, str]列表，则不处理，保留原样
                self.skipped_bracket_expressions.append(original_expression + " (Reason: Not a list of two strings)")
                return original_expression

            str1 = parsed_list[0]
            str2 = parsed_list[1]

            norm_str1 = self._normalize_string(str1)
            norm_str2 = self._normalize_string(str2)

            if norm_str1 == norm_str2:
                return norm_str1 # 返回共同的规范化字符串
            else:
                self.skipped_bracket_expressions.append(original_expression + f" (Reason: Normalized forms differ: '{norm_str1}' vs '{norm_str2}')")
                return original_expression # 内容不一致，保留原样

        except (ValueError, SyntaxError) as e:
            # 如果 ast.literal_eval 解析失败，说明它不是一个标准的Python字面量列表
            self.skipped_bracket_expressions.append(original_expression + f" (Reason: ast.literal_eval failed: {e})")
            return original_expression


    def format_content(self) -> str:
        """
        执行所有格式化操作。
        """
        # 1. 处理花括号 (全局替换相对安全)
        self.content = self.content.replace('{', '(').replace('}', ')')

        # 2. 处理 IRI 中的尖括号 (针对 rdf:about 和 rdf:resource)
        def _process_iri_for_angle_brackets(match) -> str:
            attribute_prefix = match.group(1) # e.g., "rdf:about="
            quote_char = match.group(2)       # e.g., '"'
            iri_value = match.group(3)        # e.g., "http://example/path<foo>"
            
            modified_iri_value = iri_value.replace('<', '(').replace('>', ')')
            
            if modified_iri_value == iri_value: # 如果没有发生改变，返回原始匹配避免性能损耗
                return match.group(0) 
            
            return f"{attribute_prefix}{quote_char}{modified_iri_value}{quote_char}"

        # 正则表达式匹配 rdf:about="..." 和 rdf:resource="..."
        # group(1): rdf:about= 或 rdf:resource=
        # group(2): 开头引号 (" 或 ')
        # group(3): 引号内的 IRI 内容
        # \2: 匹配与 group(2) 相同的闭合引号
        iri_attribute_pattern = r'(rdf:(?:about|resource)=)(["\'])(.*?)\2'
        self.content = re.sub(iri_attribute_pattern, _process_iri_for_angle_brackets, self.content)

        # 3. 处理方括号
        # 正确的正则表达式，用于匹配如 ['string1', 'string2'] 的模式
        # 使用 r'''...''' 来避免内部双引号 " 的问题
        square_bracket_pattern = r'''\[\s*('([^']*)'|"([^"]*)")\s*,\s*('([^']*)'|"([^"]*)")\s*\]'''
        self.content = re.sub(square_bracket_pattern, self._process_square_brackets_match, self.content)
        
        return self.content

    def get_skipped_expressions(self) -> list[str]:
        return self.skipped_bracket_expressions

# 主处理逻辑
def process_owl_file(input_file_path: str, output_file_path: str):
    """
    读取OWL文件，进行格式化，然后写入新文件。
    """
    try:
        with open(input_file_path, 'r', encoding='utf-8') as f_in:
            owl_data = f_in.read()
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file_path}")
        return
    except Exception as e:
        print(f"Error reading input file {input_file_path}: {e}")
        return

    formatter = OwlFormattor(owl_data)
    formatted_content = formatter.format_content()
    skipped = formatter.get_skipped_expressions()

    try:
        with open(output_file_path, 'w', encoding='utf-8') as f_out:
            f_out.write(formatted_content)
        print(f"Successfully processed file. Output saved to: {output_file_path}")
        if skipped:
            print("\nThe following expressions with square brackets were skipped (not modified):")
            for item in skipped:
                print(f"- {item}")
        else:
            print("\nNo square bracket expressions were skipped.")

    except Exception as e:
        print(f"Error writing output file {output_file_path}: {e}")

if __name__ == '__main__':
    import argparse # 导入 argparse 用于处理命令行参数

    parser = argparse.ArgumentParser(description="Format OWL files by correcting special characters in IRIs.")
    parser.add_argument("input_file", help="Path to the input OWL file.")
    parser.add_argument("output_file", help="Path for the output formatted OWL file.")

    args = parser.parse_args()

    print(f"Starting OWL formatting process for {args.input_file}...")
    process_owl_file(args.input_file, args.output_file)
    print(f"Formatting process finished. Output at {args.output_file}")