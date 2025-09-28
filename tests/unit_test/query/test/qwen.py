import os
import yaml
import time
import concurrent.futures
from dashscope import Generation

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 定义YAML文件路径（使用绝对路径）
YAML_FILE = os.path.join(script_dir, 'qwen_vanilla.yaml')
# 设置并行工作线程数
MAX_WORKERS = 10

def process_query(item):
    """
    处理单个查询：调用API并返回结果。
    """
    query = item['query']
    messages = [{'role': 'user', 'content': query}]
    
    try:
        response = Generation.call(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            model="qwen3-14b",
            messages=messages,
            result_format="message",
            enable_thinking=False,
        )

        if response.status_code == 200:
            return response.output.choices[0].message.content
        else:
            return f"API Error: HTTP {response.status_code}, Code {response.code}, Message {response.message}"

    except Exception as e:
        return f"An exception occurred: {e}"

def main():
    """
    主函数：加载数据，并行处理，保存结果。
    """
    try:
        with open(YAML_FILE, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or []
    except FileNotFoundError:
        print(f"错误：找不到文件 {YAML_FILE}")
        return

    # 筛选出未回答的问题，并记录其索引
    tasks = []
    for i, item in enumerate(data):
        if not (item.get('response') and str(item.get('response')).strip()):
            tasks.append((i, item))

    if not tasks:
        print("所有问题都已回答。")
        return

    print(f"总共发现 {len(tasks)} 个问题需要处理。")

    completed_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 提交任务，并建立future到索引的映射
        future_to_index = {executor.submit(process_query, item): index for index, item in tasks}

        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                answer = future.result()
                data[index]['response'] = answer
                status = "Success"
            except Exception as exc:
                data[index]['response'] = f"生成答案时发生异常: {exc}"
                status = f"Failed ({exc})"
            
            completed_count += 1
            print(f"进度: {completed_count}/{len(tasks)} | 问题 #{index + 1}处理完毕 | 状态: {status}")

            # 每次有结果后就写回文件，以安全地保存进度
            with open(YAML_FILE, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False)

    print("\n所有查询已处理完毕。")

if __name__ == "__main__":
    main()