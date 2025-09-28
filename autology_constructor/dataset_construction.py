import json
import os
import random
import dspy 
import math


from config.settings import DATASET_CONSTRUCTION_CONFIG

def load_dspy_examples(filepath):
    """从JSON文件加载DSPy示例列表
    
    Args:
        filepath: JSON文件路径
        
    Returns:
        list: DSPy Example对象列表
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [dspy.Example(context=item["context"]).with_inputs("context") 
            for item in data]

class DatasetConstructor:
    def __init__(self, folder_path=DATASET_CONSTRUCTION_CONFIG["raw_data_folder_path"], template_str='content_list', dev_size=20, train_size=100, min_chunk_size=0, max_chunk_size=math.inf, max_attempts=5000):
        self.folder_path = folder_path
        self.template_str = template_str
        self.dev_size = dev_size
        self.train_size = train_size 
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.max_attempts = max_attempts
        
        self.raw_data = []
        self.dev_data = []
        self.train_data = []
        self.used_texts = set()
        
        self.devset = []
        self.trainset = []
        
    def load_json_files(self):
        """从文件夹加载所有符合条件的JSON文件数据"""
        for filename in os.listdir(self.folder_path):
            if filename.endswith('.json') and self.template_str in filename:
                file_path = os.path.join(self.folder_path, filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.raw_data.extend(data)
        print(f"加载了{len(self.raw_data)}条原始数据")
        
    def sample_dataset(self, target_data, target_size):
        """采样数据集"""
        attempts = 0
        while len(target_data) < target_size and attempts < self.max_attempts:
            item = random.choice(self.raw_data)
            if item.get('type') == 'text':
                text = item['text']
                text_len = len(text)
                if text_len > self.min_chunk_size and text_len < self.max_chunk_size and text not in self.used_texts:
                    target_data.append(item)
                    self.used_texts.add(text)
            attempts += 1
            
    def create_samples(self):
        """创建开发集和训练集样本"""
        # 采样开发集
        self.sample_dataset(self.dev_data, self.dev_size)
        # 采样训练集
        self.sample_dataset(self.train_data, self.train_size)
        
        # 打印采样结果
        print(f"\n随机抽取到{len(self.dev_data)}个开发集文本:")
        for i, item in enumerate(self.dev_data, 1):
            print(f"\n{i}. 文本长度: {len(item['text'])}")
            print(f"文本内容: {item['text'][:100]}...")
            
        print(f"\n随机抽取到{len(self.train_data)}个训练集文本:")
        for i, item in enumerate(self.train_data, 1):
            print(f"\n{i}. 文本长度: {len(item['text'])}")
            print(f"文本内容: {item['text'][:100]}...")
            
    def build_examples(self):
        """构建DSPy示例"""
        # 构建开发集
        for sample in self.dev_data:
            self.devset.append(dspy.Example(
                context=sample['text']
            ).with_inputs("context"))
        print(f"生成了{len(self.devset)}个开发集样本")
        
        # 构建训练集
        for sample in self.train_data:
            self.trainset.append(dspy.Example(
                context=sample['text']
            ).with_inputs("context"))
        print(f"生成了{len(self.trainset)}个训练集样本")
        
    def save_datasets(self):
        """保存数据集到JSON文件"""
        # 转换训练集格式
        train_json = [{"context": example.context} for example in self.trainset]
        # 转换开发集格式
        dev_json = [{"context": example.context} for example in self.devset]
        
        # 保存训练集
        with open(DATASET_CONSTRUCTION_CONFIG["trainset_file_path"], "w", encoding="utf-8") as f:
            json.dump(train_json, f, ensure_ascii=False, indent=2)
            
        # 保存开发集
        with open(DATASET_CONSTRUCTION_CONFIG["devset_file_path"], "w", encoding="utf-8") as f:
            json.dump(dev_json, f, ensure_ascii=False, indent=2)
            
        print("数据集已保存到data目录下")
        
    def load_saved_datasets(self):
        """加载保存的数据集"""
        self.trainset = load_dspy_examples(DATASET_CONSTRUCTION_CONFIG["trainset_file_path"])
        self.devset = load_dspy_examples(DATASET_CONSTRUCTION_CONFIG["devset_file_path"])
        print(f"已读取并恢复训练集({len(self.trainset)}个样本)和开发集({len(self.devset)}个样本)")
        
    def construct(self):
        """执行完整的数据集构建流程"""
        self.load_json_files()
        self.create_samples()
        self.build_examples()
        self.save_datasets()
        
# 使用示例
if __name__ == "__main__":
    constructor = DatasetConstructor()
    constructor.construct()
    constructor.load_saved_datasets()

