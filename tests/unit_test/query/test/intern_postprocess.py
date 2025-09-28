import yaml
import os

def read_yaml(file_path):
    """
    读取并解析一个YAML文件。
    
    Args:
        file_path (str): 要读取的YAML文件的路径。

    Returns:
        list or dict: 解析后的YAML数据。如果文件不存在或格式无效，则返回空列表。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        return data
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")
        return []
    except yaml.YAMLError as e:
        print(f"错误：文件 {file_path} 不是有效的YAML格式。原因: {e}")
        return []

def save_yaml(file_path, data):
    """
    将数据以YAML格式保存到文件中。

    Args:
        file_path (str): 要保存到的文件的路径。
        data (list or dict): 要保存的数据。
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            yaml.dump(data, file, allow_unicode=True, indent=4)
        print(f"成功将数据保存到 {file_path}")
    except IOError as e:
        print(f"错误：无法写入文件 {file_path}。原因: {e}")

def clear_and_save_responses(file_path, indices_to_clear=None):
    """
    读取YAML文件，清除一个或所有response字段，然后覆写保存。

    Args:
        file_path (str): 目标YAML文件的路径。
        indices_to_clear (list, optional): 一个包含要清除的response的索引列表。
                                           如果为None，则清除所有response。默认为None。
    """
    data = read_yaml(file_path)
    if not data:
        return

    if indices_to_clear is None:
        # 清除所有response
        for item in data:
            if 'response' in item:
                item['response'] = "\n"
    else:
        # 只清除指定索引的response
        for index in indices_to_clear:
            if 0 <= index < len(data):
                if 'response' in data[index]:
                    data[index]['response'] = "\n"
            else:
                print(f"警告：索引 {index} 超出范围，将被忽略。")
    
    # 调用保存函数
    save_yaml(file_path, data)

if __name__ == '__main__':
    # 获取当前文件的目录路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建intern.yaml的完整路径
    yaml_path = os.path.join(current_dir, "intern.yaml")

    # 示例用法1：清除所有response
    clear_and_save_responses(yaml_path)

    # 示例用法2：清除索引为0和2的response
    # clear_and_save_responses(yaml_path, indices_to_clear=[0, 2])

    # 示例用法3：只读取和打印数据
    # content = read_yaml(yaml_path)
    # if content:
    #     print(yaml.dump(content, allow_unicode=True, indent=4))
    pass
