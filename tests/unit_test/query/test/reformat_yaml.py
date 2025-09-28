import sys
from pathlib import Path
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString

def reformat_yaml_file(file_path_str: str):
    """
    Intelligently reformats 'response' fields in a YAML file to the literal block style ('|-').
    
    This script uses the `ruamel.yaml` library to:
    - Preserve existing formatting, comments, and structure.
    - Convert any 'response' field that is a plain string (single or multi-line with \n)
      into a literal block string.
    - Leave 'response' fields that are already in literal/folded block style untouched.
    - Correctly handle empty strings, formatting them as empty literal blocks.
    """
    file_path = Path(file_path_str)
    if not file_path.is_file():
        print(f"错误：找不到文件 {file_path}")
        return

    yaml = YAML()
    yaml.preserve_quotes = True
    # Set indentation to match the desired style (2-space mapping, 2-space sequence).
    yaml.indent(mapping=2, sequence=4, offset=2)
    
    try:
        data = yaml.load(file_path)
    except Exception as e:
        print(f"错误: 加载YAML文件失败 {file_path}。原因: {e}")
        return

    if not isinstance(data, list):
        print(f"错误: {file_path} 的顶层结构不是一个列表。")
        return

    for item in data:
        if isinstance(item, dict) and 'response' in item:
            response_value = item['response']
            
            # We only want to convert plain strings.
            # If it's already a LiteralScalarString or other special type, leave it alone.
            if isinstance(response_value, str):
                # Using LiteralScalarString ensures the output is in '|- ' format.
                # The library handles the content correctly.
                item['response'] = LiteralScalarString(response_value)

    try:
        yaml.dump(data, file_path)
        print(f"成功使用 `ruamel.yaml` 重新格式化并保存了 {file_path}")
    except Exception as e:
        print(f"错误：无法写入文件 {file_path}。原因: {e}")


if __name__ == '__main__':
    current_dir = Path(__file__).parent
    yaml_path = current_dir / "intern.yaml"
    reformat_yaml_file(str(yaml_path)) 