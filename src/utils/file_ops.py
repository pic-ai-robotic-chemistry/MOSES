import yaml
from langchain_core.messages import AIMessage
from typing import Dict, List, Any

def save_qa_to_yaml(answers: Dict[int, Any], queries: List[str], output_path: str) -> None:
    """
    Processes a dictionary of answers and a list of queries, sorts them,
    and saves them to a YAML file with consistent multiline string formatting.

    Args:
        answers (Dict[int, Any]): A dictionary with integer keys and AIMessage objects as values.
        queries (List[str]): A list of query strings.
        output_path (str): The path to the output YAML file.
    """
    data_to_save = []
    
    # Sort keys to process the dictionary in order
    sorted_keys = sorted(answers.keys())
    
    for idx in sorted_keys:
        answer = answers.get(idx)
        if isinstance(answer, AIMessage):
            # The query index is assumed to be key - 1
            if idx > 0 and (idx - 1) < len(queries):
                query = queries[idx - 1]
                response = answer.content
                data_to_save.append({'query': query, 'response': response})
            else:
                print(f"Warning: No matching query found for answer key {idx} or key is out of bounds.")
        else:
            print(f"Warning: Item with key {idx} is not an AIMessage object.")

    # Define a custom Dumper to control string representation, avoiding global state changes.
    class MyDumper(yaml.SafeDumper):
        pass

    def str_presenter(dumper, data):
        """Custom string presenter to force literal block style for multiline strings."""
        if '\n' in data:
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)

    MyDumper.add_representer(str, str_presenter)

    # Write the data to the YAML file using the custom Dumper
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(data_to_save, f, Dumper=MyDumper, allow_unicode=True, default_flow_style=False, sort_keys=False, width=float('inf'))

    print(f"Successfully saved QA pairs to {output_path}") 