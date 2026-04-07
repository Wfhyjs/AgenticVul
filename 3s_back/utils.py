import random
import tiktoken
from collections import defaultdict

def get_defect_level(defect_index: float):
    if defect_index > 0.5:
        return "高风险"
    elif defect_index < 0.2:
        return "安全"
    else:
        return "低风险"


def count_tokens(text, model="gpt-3.5-turbo"):
    # 根据模型名称加载对应的编码器
    encoding = tiktoken.encoding_for_model(model)

    # 将文本编码为 token 并计算 token 数
    token_count = len(encoding.encode(text))

    return token_count


def group_by_file_path(data):
    grouped_data = defaultdict(list)

    for item in data:
        file_path = item['file_path']
        grouped_data[file_path].append(item)

    result = [{"file_path": key, "items": value} for key, value in grouped_data.items()]
    return result


def extract_function_name(s):
    parts = s.split('::')
    if len(parts) > 1:
        return parts[-1]
    return None


def extract_from_backticks(language: str, text: str) -> str:
    import re
    # 构建正则表达式以匹配特定语言的代码块
    pattern = rf"```{language}\n(.*?)\n```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def format_function_data(data):
    result = []
    for index, item in enumerate(data, start=1):
        formatted_str = f"""{index}. function_id: {item['function_id']}
    - caller: {item['caller']}
    - callee: {item['callee']}"""
        result.append(formatted_str)
    return "\n".join(result)


def format_random_functions(data):
    # 随机选取最多三个字典
    selected_data = random.sample(data, min(5, len(data)))

    result = []
    for index, item in enumerate(selected_data, start=1):
        formatted_str = f"""{index}. function_name: {item['function_name']}

```
{item['function_content']}
```
"""
        result.append(formatted_str)
    return "\n".join(result)


def format_file_data(data, idx):
    return f"""## {idx}. `{data['file_path']}` 文件分析

### （1）总体分析

- 包含函数个数：{data['function_num']}
- 包含漏洞个数：{data['defect_num']}
- 风险评估等级：{data['avg_defect_level']}

### （2）功能分析

{data['text_analysis']['functionality_and_purpose']}

### （3）结构设计分析

#### 函数依赖分析

{data['text_analysis']['function_dependency']}

#### 模块化设计分析

{data['text_analysis']['modularity']}

#### 编码规范分析

{data['text_analysis']['coding_standards']}

### （4）代码质量分析

#### 可读性分析

{data['text_analysis']['readability_and_comments']}

#### 冗余性分析

{data['text_analysis']['code_duplication']}

### （5）性能分析

{data['text_analysis']['performance_bottlenecks']}

"""

def format_dependence_data(data, caller=True):
    if caller:
        who = 'caller'
        prefix = '调用其余函数的次数'
    else:
        who = 'callee'
        prefix = '被其余函数调用的次数'

    return f"""
#### `{data['function_id']}`    

```{data['language']}
{data['function_content']}
```

- {prefix}：{data[f'{who}_num']}
- 包含漏洞个数：{data['defect_num']}
- 风险等级评估：{data['avg_defect_level']}

"""