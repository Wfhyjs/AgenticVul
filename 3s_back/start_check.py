import importlib.util

from tree_sitter import Language, Parser
import os
import json
import datetime
from user_sys.DetectionModels import run
from models import db, ProjectDetection, User

# 配置 Tree-Sitter 的语言库
current_dir = os.path.dirname(os.path.abspath(__file__))
LANGUAGE_LIBRARY = os.path.join(current_dir, 'my-languages.dll')
C_LANGUAGE = Language(LANGUAGE_LIBRARY, 'c')

# 格式化代码
def get_str_code(code):
    code_list = list(code)
    for i in range(0, len(code_list) - 1):
        if code_list[i] == ";" and code_list[i + 1] != "\n":
            code_list[i] = ";" + "\n"
        if code_list[i] == "{" and code_list[i + 1] != "\n":
            code_list[i] = "{" + "\n"
        if code_list[i + 1] == "}" and code_list[i] != "\n":
            code_list[i] += "\n"
        if code_list[i] == ' ' and code_list[i + 1] == ";":
            code_list[i] = ''
    return ''.join(code_list)

# 函数抽取
# 函数抽取
def extractFunc(file_path):
    parser = Parser()
    parser.set_language(C_LANGUAGE)

    # 获取文件名（不包含路径）
    file_name = os.path.basename(file_path)

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    with open(file_path, 'rb') as f:
        code = f.read()

    tree = parser.parse(code)
    root_node = tree.root_node
    functions = []
    names = []

    def format_function_code(function_code):
        return function_code.replace('\n', ' ').replace('\t', ' ')

    def get_function_name(node):
        for child in node.children:
            if 'identifier' in child.type:
                return child.text.decode('utf-8')
            else:
                name = get_function_name(child)
                if name:
                    return name

    def collect_functions(node):
        if node.type == 'function_definition':
            start_line, start_col = node.start_point
            end_line, end_col = node.end_point

            function_code = '\n'.join(lines[start_line:end_line + 1])
            function_code = function_code[:function_code.rfind('\n') + end_col + 1]
            formatted_function_code = get_str_code(format_function_code(function_code))

            function_name = get_function_name(node)

            # 拼接文件名和函数名，生成“文件名::函数名”格式
            full_func_name = f"{file_name}::{function_name}"

            functions.append(formatted_function_code)
            names.append(full_func_name)
        elif node.type == 'translation_unit':
            for child in node.children:
                collect_functions(child)

    collect_functions(root_node)
    return functions, names


# 检测函数
def startCheck(project_path, Pmodel,pid):
    cpp_files = ['.h', '.c', '.cpp']
    all_functions = []
    all_names = []
    print("111")
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if any(file.endswith(ext) for ext in cpp_files):
                file_path = os.path.join(root, file)
                functions, names = extractFunc(file_path)
                all_functions.extend(functions)
                all_names.extend(names)

    jsonl_file_path = os.path.join(project_path, 'functions.jsonl')
    print("222")
    with open(jsonl_file_path, 'w') as outfile:
        idx = 0
        for function, name in zip(all_functions, all_names):
            json_record = json.dumps({"idx": idx, "func": function, "func_name": name})
            outfile.write(json_record + '\n')
            idx += 1

    # 模型参数
    # 构造 tokenizer_name 和 output_dir
    tokenizer_name = (
        os.path.join('user_sys', 'DetectionModels', 'BaseModel', 'GraphCodeBERT-base')
        if Pmodel in ['ReGVD', 'Devign', 'DFEVD']
        else os.path.join('user_sys', 'DetectionModels', 'BaseModel', f"{Pmodel}-base")
    )
    output_dir = os.path.join('user_sys', 'DetectionModels', Pmodel)

    # # 标准化路径，强制使用正斜杠（可选）
    # tokenizer_name = os.path.normpath(tokenizer_name).replace(os.path.sep, '/')
    # output_dir = os.path.normpath(output_dir).replace(os.path.sep, '/')

    # 构造 args
    args = {
        "output_dir": output_dir,
        "test_data_file": jsonl_file_path,
        "model_type": "roberta" if Pmodel != 'CodeT5' else 'codet5',
        "model_name_or_path": tokenizer_name,
        "tokenizer_name": tokenizer_name,
        "block_size": 400,
        "do_test": False,
        "model": Pmodel,
    }
    print("444")
    # 调用模型
    test_results, possibilities = run.runModel(args)
    print("555")
    # 更新 JSONL 文件并统计结果
    vul_count = 0
    total_count = 0
    fix_count = 0
    updated_lines = []
    with open(jsonl_file_path, 'r', encoding='utf-8') as file:
        for line, result, possibility in zip(file, test_results, possibilities):
            data = json.loads(line.strip())
            data['vul'] = bool(result)
            data['positive'] = float(possibility)
            data['fixed'] = not result
            data['fixed_time'] = datetime.datetime.now().strftime('%Y-%m-%d') if not result else None
            updated_lines.append(json.dumps(data))
            vul_count += result
            total_count += 1
            if not result:
                fix_count += 1

    with open(jsonl_file_path, 'w', encoding='utf-8') as file:
        for line in updated_lines:
            file.write(line + '\n')

    # 输出结果
    danger_score = (vul_count / total_count) * 100 if total_count > 0 else 0

    project = ProjectDetection.query.get(pid)
    if project:
        project.Pvul = vul_count
        project.Pfix = fix_count
        project.Pdanger = danger_score
        db.session.commit()

    print(f"Summary:\n - Vul Count: {vul_count}\n - Total Count: {total_count}\n - Fixed Count: {fix_count}\n - Danger Score: {danger_score:.2f}%")
    print(f"JSONL file updated: {jsonl_file_path}")
    return jsonl_file_path

