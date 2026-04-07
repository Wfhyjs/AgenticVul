import os
import ell
import json
import openai
client = openai.Client(
    api_key="sk-3QJqpcoBk8k6l3B3Pw1dNjiKzQ7H8rrwcY1fbFUsPTRh50Hb",
    base_url="https://xiaoai.plus/v1"
)
from tqdm import tqdm
from static_tools import process_dataset as preprocess
from utils import *
from models import db, ProjectDetection, User


def complete_function_data(function_data, repo_name, LLM_analysis=True):
    """
    利用静态工具或LLM完善function_data的键
    :param function_data:
    :return:
    """
    for i in tqdm(function_data, desc="Each Function Detection"):
        # 添加函数名称与所在文件路径
        parts = i['function_id'].split('::')
        if len(parts) > 1:
            i['function_name'] = parts[-1]
            i['file_path'] = parts[0]

        # 添加编程语言
        _, extension = os.path.splitext(i['file_path'])
        i['language'] = extension.lstrip('.')

        # 添加该函数被多少个函数调用、该函数调用其他函数的个数
        i['caller_num'] = len(i['caller'])
        i['callee_num'] = len(i['callee'])

        if LLM_analysis:
            # 添加漏洞检测情况
            while True:
                try:
                    content_analysis_result = extract_from_backticks('json', function_analysis(i))  # 从反引号里提取json格式字符串
                    content_analysis_result_dict = json.loads(content_analysis_result)  # 转换为字典格式
                    break
                except Exception as e:
                    print('漏洞检测：LLM生成格式有误')
            i['defects'] = content_analysis_result_dict
            i['defect_num'] = len(i['defects'])
            i['avg_defect_index'] = sum(d.get('defect_index', 0) for d in i.get('defects', [])) / len(
                i['defects']) if i.get('defects') else 0
            i['avg_defect_level'] = get_defect_level(i['avg_defect_index'])
            i['main_defect'] = max(i['defects'], key=lambda x: x['defect_rate'])  # 主要的漏洞情况

            # 添加修复建议、修复补丁、修复后的代码
            while True:
                try:
                    repair_analysis_result = extract_from_backticks('json', repair_analysis(i))  # 从反引号里提取json格式字符串
                    repair_analysis_result_dict = json.loads(repair_analysis_result)  # 转换为字典格式
                    break
                except Exception as e:
                    print('漏洞修复：LLM生成格式有误')
            i['repairs'] = repair_analysis_result_dict

    return function_data


# 依赖分析agent
def dependence_analysis(function_data, k=5):
    """
    依赖分析
    :param function_data: 从项目中提取出的所有函数信息
    :param k: 项目中最频繁被调用的前k个函数
    :return: 该项目中包含的所有函数个数、最频繁被调用的前k个函数、调用其他函数最频繁的前k个函数
    """
    # 按 caller_num 排序并提取前 k 个元素
    top_k_caller = sorted(function_data, key=lambda x: x['caller_num'], reverse=True)[:k]

    # 按 callee_num 排序并提取前 k 个元素
    top_k_callee = sorted(function_data, key=lambda x: x['callee_num'], reverse=True)[:k]

    return top_k_caller, top_k_callee


def function_analysis_by_DL_models(func: str):
    """
    利用深度学习模型，初步判断函数func中的缺陷是何种类型
    --- 这一步不使用LLM判断的原因是：知识库过大，超出LLM的上下文窗口大小
    :param func: 需要检测的函数内容
    :return: CWE_id
    """
    pass


# 函数分析Agent：负责解析和分析每个函数的内容，识别潜在的漏洞点
@ell.simple(model="gpt-3.5-turbo", client=client)
def function_analysis(func: dict):
    """您是函数漏洞分析专家，您的任务是根据给出的函数信息进行分析，识别可能存在的漏洞点，并标注相关的CWE编号。"""
    positive_info = f"某个安全漏洞检测模型给出的该代码有漏洞的概率为：{func.get('positive', '无')}，请结合该信息分析漏洞。" if 'positive' in func else ""

    prompt = f"""以下是您需要分析的函数所在文件路径、函数名、调用该函数的函数情况、函数内容：

- 函数所在文件路径：{func['file_path']}
- 函数名：{func['function_name']}
- 调用该函数的函数一共有 {func['caller_num']} 个，分别是：{func['caller']}
- 函数内容：

```{func['language']}
{func['function_content']}
{positive_info}
```

---

请分析上述函数中可能包含多少缺陷（最少包含一个缺陷，最多包含五个缺陷），并返回一个JSON格式的列表，其中是您分析出的每个缺陷的相关信息。请严格按照以下JSON格式返回结果：

```json
[
    {{
        "defect_rate": 0.12,  # 该函数包含漏洞的概率，该值为 0 到 1 之间的两位小数，例如 0.12。
        "CWE_id": "CWE-119",  # 该函数可能包含的漏洞对应的 CWE 编号，例如"CWE-119"
        "description": "描述",  # 对该漏洞使用中文进行的简要描述
        "defect_index": 0.31,  # 该漏洞的风险指数，该值为 0 到 1 之间的两位小数，例如 0.12。
        "repair_rate": 0.90,  # 该漏洞能够被修复的概率，该值为 0 到 1 之间的两位小数，例如 0.12。
        "impact_degree": 0.23  # 该漏洞对整个项目的影响程度。调用该函数的次数越多，或者该函数本身的功能越关键，影响程度就越高。该值为 0 到 1 之间的两位小数，例如 0.12。
    }},
    {{
        "defect_rate": 0.48,
        "CWE_id": "CWE-121",
        "description": "描述",
        "defect_index": 0.98,
        "repair_rate": 0.40,
        "impact_degree": 0.76
    }},
]
```

请确保输出完全符合上述 JSON 格式，并注意大小写和标点符号。
"""
    return prompt


# 文件分析Agent：将一个文件中的所有函数名（不输入函数内容是防止超出上下文窗口）输入给LLM，让它分析该文件的作用
@ell.simple(model="gpt-3.5-turbo", client=client)
def file_analysis(repo_name: str, file_name: str, functions: list):
    """您是项目文件分析专家，您需要全面细致地分析一个开源项目中的某个文件的作用及目的。"""

    function_name_dependence = format_function_data(functions)

    # 随机的五个具体函数，如果不足五个，就取所有函数
    function_specification = format_random_functions(functions)

    prompt = f"""
## 项目名称：{repo_name}

## 该项目中的某个文件名称：{file_name}

### 在该文件中，各函数的名称及其调用关系为：

{function_name_dependence}

### 其中某些函数的具体实现为：

{function_specification}

---

请根据项目名称、该文件名称、该文件中的每个函数的名称及调用关系、某些函数的具体实现来对该文件展开分析，您需要遵循如下JSON格式，每一项内容均使用Markdown格式的中文描述：

```json
{{
  "functionality_and_purpose": "描述文件的主要功能和用途，以及其在项目中的角色和贡献，使用Markdown格式描述，不少于一百字",
  "function_dependency": "分析文件中各函数之间的依赖关系及其设计合理性，使用Markdown格式描述，不少于两百字",
  "modularity": "评估文件的模块化设计是否合理，使用Markdown格式描述，不少于一百字",
  "coding_standards": "评估文件是否遵循良好的编码规范，使用Markdown格式描述，不少于两百字",
  "readability_and_comments": "评估代码的可读性以及注释的完整性和清晰度，使用Markdown格式描述，不少于一百字",
  "code_duplication": "检查代码中是否存在重复逻辑或不必要的复杂性，使用Markdown格式描述，不少于一百字",
  "performance_bottlenecks": "识别代码中可能存在的性能瓶颈，并分析其对整体性能的影响，以及其是否可以优化，如何优化，使用Markdown格式描述，不少于两百字"
}}
```

注意，您不应当透露出您接收到了哪些信息。例如，您不应当在回答中提到“由于我并没有接收到文件中的所有内容，因此分析报告可能存在误差”。
"""
    return prompt


def get_knowledge(func: dict):
    if func['language'] == 'c':
        with open('knowledge_base/unique_knowledge_c.json', 'r', encoding='utf-8') as file:
            knowledge = json.load(file)
    elif func['language'] == 'cpp':
        with open('knowledge_base/unique_knowledge_cpp.json', 'r', encoding='utf-8') as file:
            knowledge = json.load(file)
    elif func['language'] == 'java':
        with open('knowledge_base/unique_knowledge_java.json', 'r', encoding='utf-8') as file:
            knowledge = json.load(file)
    else:
        with open('knowledge_base/unique_knowledge_python.json', 'r', encoding='utf-8') as file:
            knowledge = json.load(file)

    # 获取主要漏洞的CWE_id
    CWE_id = func['main_defect']['CWE_id']
    language = func['language']

    target_knowledge = None
    for i in knowledge:
        if CWE_id in i['cwe_id']:
            target_knowledge = i
            break

    if target_knowledge is None:
        return f"知识库中暂无 {CWE_id} 漏洞的内容"

    details = target_knowledge['details']

    # 使用 min 函数找到长度最小的那一项
    min_item = min(details, key=lambda i: len(i['code'] + i['code_before'] + i['patch']))

    code = min_item['code']
    code_before = min_item['code_before']
    patch = min_item['patch']

    s = f"""- 包含 {CWE_id} 漏洞的代码

```{language}
{code_before}
```

- 修复后的代码

```{language}
{code}
```

- 修复补丁情况

```{language}
{patch}
```"""
    if count_tokens(s) > 4096:
        return f"知识库中暂无 {CWE_id} 漏洞的内容"
    else:
        return s


# 根据深度学习模型或LLM分析得出可能的CWE_id后，再从知识库提取包含该CWE_id的对应编程语言的项目，构造prompt
# 修复agent
@ell.simple(model="gpt-3.5-turbo", client=client)
def repair_analysis(func: dict):
    """您是函数漏洞修复专家，您的任务是根据给出的函数及其存在的漏洞信息进行分析，识别可能存在的漏洞点，并标注相关的CWE编号。"""
    positive_info = f"某个安全漏洞检测模型给出的该代码有漏洞的概率为：{func.get('positive', '无')}，请结合该信息进行修复建议。" if 'positive' in func else ""
    prompt = f"""以下是您需要修复的函数内容及其存在的漏洞类型：

- 函数名：{func['function_name']}
- 漏洞类型：{func['main_defect']['CWE_id']}
- 漏洞描述：{func['main_defect']['description']}
- 函数内容：

```{func['language']}
{func['function_content']}
{positive_info}
```

以下是从知识库中提取到的与 {func['main_defect']['CWE_id']} 漏洞相关的先验知识：

{get_knowledge(func)}
---

请您根据上述内容，对包含漏洞的函数 {func['function_id']} 进行修复，按照如下JSON格式返回修复后的代码：

```json
{{
    "repair_advice": "在执行乘法运算之前，应该验证输入参数是否为数字类型，以避免不期望的异常或错误。", # 详细的修复建议
    "repair_patch": "- return a * b;\n+ if isinstance(a, (int, float)) and isinstance(b, (int, float)):\n+     return a * b\n+ else:\n+     raise ValueError(\"Both inputs must be numbers.\")", # 修复补丁情况
    "repair_code": "def multiply(a, b):\n    if isinstance(a, (int, float)) and isinstance(b, (int, float)):\n        return a * b\n    else:\n        raise ValueError(\"Both inputs must be numbers.\")" # 按照补丁修复后的代码
}}
```

注意，上述示例为 Python 代码，但 {func['function_name']} 函数为 {func['language']} 代码。请确保输出完全符合上述 JSON 格式，并注意大小写和标点符号。
"""
    return prompt


def get_overall_detect_report(function_data: list, repo_name: str):
    """
    获取总体的检测报告，包含：依赖分析（dependence_analysis）+针对各文件的分析（file_analysis）
    :param repo_path:
    :return:
    """

    # 1. 项目总体分析部分
    defect_sum, defect_index_sum = 0, 0
    for i in function_data:
        defect_sum += i['defect_num']
        defect_index_sum += i['avg_defect_index']
    
    if len(function_data) > 0:
        avg_defect_num = defect_sum / len(function_data)
        avg_defect_index = defect_index_sum / len(function_data)
    else:
        avg_defect_num = 0
        avg_defect_index = 0

    top_k_caller, top_k_callee = dependence_analysis(function_data, 5)
    caller_str, callee_str = "", ""

    for i, j in zip(top_k_caller, top_k_callee):
        caller_str += format_dependence_data(i, True)
        callee_str += format_dependence_data(j, False)

    # 2. 文件分析部分
    grouped_data = group_by_file_path(function_data)
    file_data = []

    for i in tqdm(grouped_data, desc="Overall Detection"):
        avg_defect_index = 0
        defect_sum = 0
        for j in i['items']:
            avg_defect_index += j['avg_defect_index']
            defect_sum += j['defect_num']
        avg_defect_index /= len(i['items'])

        # 按文件分类
        file_data.append({
            'file_path': i['file_path'],
            'function_num': len(i['items']),
            'defect_num': defect_sum,
            'avg_defect_index': avg_defect_index,
            'avg_defect_level': get_defect_level(avg_defect_index),
            'text_analysis': json.loads(
                extract_from_backticks('json', file_analysis(repo_name, i['file_path'], i['items']))),
        })

    formated_file_data = ""
    for idx, i in enumerate(file_data):
        formated_file_data += format_file_data(i, idx + 1)

    overall_detect_report = f"""
# 一、项目总体漏洞分析

## 1. 漏洞总体情况分析

- {repo_name} 项目中共包含 {len(grouped_data)} 个代码文件、 {len(function_data)} 个函数、 {defect_sum} 个漏洞。
- 平均每个函数包含 {avg_defect_num} 个漏洞，整个项目的漏洞等级评估为 “{get_defect_level(avg_defect_index)}”。

## 2. 依赖分析

### （1）调用其他函数最频繁的前五个函数

{caller_str}

### （2）被其他函数调用最频繁的前五个函数

{callee_str}

# 二、各文件内容分析

{formated_file_data}
"""
    return overall_detect_report


def main(repo_name: str, pid):
    """
    根据静态工具分析出的json文件（保存在preprocessed_data中），对其进行进一步的漏洞检测与修复
    :param pid:
    :param repo_name:
    :return: 总体检测报告（txt格式，为markdown语法书写的文本）、各函数分析报告（json格式，为字典列表）
    """
    with open(f'preprocessed_data/{repo_name}.json', 'r', encoding='utf-8') as file:
        # function_data = json.load(file)
        function_data = json.load(file)[:25]  # 测试时，为了节省token，只用前25个函数，即五个文件

    each_function_detection = complete_function_data(function_data, repo_name)
    overall_detection = get_overall_detect_report(function_data, repo_name)

    output_dir = f"results/{repo_name}"
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/each_function_detection.json", "w", encoding="utf-8") as json_file:
        json.dump(each_function_detection, json_file, ensure_ascii=False, indent=4)
    with open(f"{output_dir}/overall_detection.txt", "w", encoding="utf-8") as txt_file:
        txt_file.write(overall_detection)

    # project = ProjectDetection.query.get(pid)
    # if project:
    #     project.Pfuncpath: repo_name
    #     db.session.commit()

    return overall_detection, each_function_detection

#
# if __name__ == '__main__':
#     repo_name = "../merge/test"  # 测试用，每个文件只有五个函数
#     main(repo_name)
