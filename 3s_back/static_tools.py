import os
import json
from tree_sitter import Language, Parser

# 加载 C、C++、Python 和 Java 语言
# Windows平台下是 'my-languages.dll'；Linux平台下是 'my-languages.so'
# 确保 'my-languages.dll' 包含 'c', 'cpp', 'python' 和 'java'
current_dir = os.path.dirname(os.path.abspath(__file__))
LANGUAGE_LIBRARY = os.path.join(current_dir, 'my-languages.dll')
C_LANGUAGE = Language(LANGUAGE_LIBRARY, 'c')
CPP_LANGUAGE = Language(LANGUAGE_LIBRARY, 'cpp')
PYTHON_LANGUAGE = Language(LANGUAGE_LIBRARY, 'python')
JAVA_LANGUAGE = Language(LANGUAGE_LIBRARY, 'java')

# 创建四个独立的解析器
parser_c = Parser()
parser_c.set_language(C_LANGUAGE)

parser_cpp = Parser()
parser_cpp.set_language(CPP_LANGUAGE)

parser_python = Parser()
parser_python.set_language(PYTHON_LANGUAGE)

parser_java = Parser()
parser_java.set_language(JAVA_LANGUAGE)

# 全局结构体用于存储函数关系
global_function_map = {}  # 映射函数名到 function_id
global_call_map = {}  # 映射 function_id 到其调用者


def extract_dependencies(node, file_path, dependencies, file_content, language):
    """从解析的节点中提取函数依赖关系，并提取函数内容。"""
    if language in ['c', 'cpp']:
        if node.type == 'function_definition':
            # 提取函数名
            declarator_node = node.child_by_field_name('declarator')
            if not declarator_node:
                return

            # 对于 C++，函数名可能包含命名空间或类名
            function_name = get_function_name(declarator_node, language)

            if not function_name:
                return

            function_id = f"{file_path}::{function_name}"  # 使用双冒号分隔

            # 提取函数内容
            function_content = extract_function_content(node, file_content)

            dependencies[function_id] = {
                "caller": set(),
                "callee": set(),
                "function_content": function_content
            }

            # 存储在全局映射中，不包含参数详情以便更容易匹配
            base_function_name = function_name.split('(')[0].split('::')[-1]  # 仅使用函数名部分
            global_function_map[base_function_name] = function_id

            # 遍历子节点查找函数调用（标识符）
            stack = [node]
            while stack:
                current_node = stack.pop()
                if current_node.type == 'call_expression':
                    # 查找被调用的函数
                    callee_node = current_node.child_by_field_name('function')
                    if callee_node:
                        callee_name = get_callee_name(callee_node, language)
                        if not callee_name:
                            continue
                        base_callee_name = callee_name.split('(')[0].split('::')[-1]  # 无参数且仅函数名部分
                        if base_callee_name in global_function_map:
                            callee_id = global_function_map[base_callee_name]
                            dependencies[function_id]["callee"].add(callee_id)
                            global_call_map.setdefault(callee_id, set()).add(function_id)

                # 将子节点加入栈中以供进一步探索
                stack.extend(current_node.children)

    elif language == 'python':
        if node.type == 'function_definition':
            # 提取函数名
            name_node = node.child_by_field_name('name')
            if not name_node:
                return

            function_name = name_node.text.decode('utf-8')
            function_id = f"{file_path}::{function_name}"

            # 提取函数内容
            function_content = extract_function_content(node, file_content)

            dependencies[function_id] = {
                "caller": set(),
                "callee": set(),
                "function_content": function_content
            }

            # 存储在全局映射中
            global_function_map[function_name] = function_id

            # 遍历子节点查找函数调用（函数调用节点）
            stack = [node]
            while stack:
                current_node = stack.pop()
                if current_node.type == 'call':
                    # 查找被调用的函数
                    func_node = current_node.child_by_field_name('function')
                    if func_node:
                        callee_name = get_callee_name(func_node, language)
                        if not callee_name:
                            continue
                        if callee_name in global_function_map:
                            callee_id = global_function_map[callee_name]
                            dependencies[function_id]["callee"].add(callee_id)
                            global_call_map.setdefault(callee_id, set()).add(function_id)

                # 将子节点加入栈中以供进一步探索
                stack.extend(current_node.children)

    elif language == 'java':
        if node.type == 'method_declaration':
            # 提取方法名
            name_node = node.child_by_field_name('name')
            if not name_node:
                return

            function_name = name_node.text.decode('utf-8')
            # 获取类名作为前缀
            class_node = node.parent
            if class_node and class_node.type == 'class_declaration':
                class_name_node = class_node.child_by_field_name('name')
                if class_name_node:
                    class_name = class_name_node.text.decode('utf-8')
                    function_id = f"{file_path}::{class_name}.{function_name}"
                else:
                    function_id = f"{file_path}::{function_name}"
            else:
                function_id = f"{file_path}::{function_name}"

            # 提取函数内容
            function_content = extract_function_content(node, file_content)

            dependencies[function_id] = {
                "caller": set(),
                "callee": set(),
                "function_content": function_content
            }

            # 存储在全局映射中
            global_function_map[function_name] = function_id

            # 遍历子节点查找函数调用（方法调用节点）
            stack = [node]
            while stack:
                current_node = stack.pop()
                if current_node.type == 'method_invocation':
                    # 查找被调用的方法
                    method_node = current_node.child_by_field_name('name')
                    if method_node:
                        callee_name = method_node.text.decode('utf-8')
                        if callee_name in global_function_map:
                            callee_id = global_function_map[callee_name]
                            dependencies[function_id]["callee"].add(callee_id)
                            global_call_map.setdefault(callee_id, set()).add(function_id)

                # 将子节点加入栈中以供进一步探索
                stack.extend(current_node.children)

    # 递归处理子节点
    for child in node.children:
        extract_dependencies(child, file_path, dependencies, file_content, language)


def extract_function_content(node, file_content):
    """提取函数的源代码内容。"""
    start_byte = node.start_byte
    end_byte = node.end_byte
    function_code = file_content[start_byte:end_byte].decode('utf-8', errors='ignore')
    return function_code


def get_function_name(declarator_node, language):
    """提取函数名，处理 C、C++ 和 Java 的不同情况。"""
    if language == 'c':
        # 对于 C，函数名通常是简单的标识符
        identifier = declarator_node.child_by_field_name('declarator')
        if identifier and identifier.type == 'identifier':
            return identifier.text.decode('utf-8')
    elif language == 'cpp':
        # 对于 C++，函数名可能是限定标识符
        return extract_cpp_function_name(declarator_node)
    # Java 的函数名处理在 extract_dependencies 中
    return None


def extract_cpp_function_name(declarator_node):
    """提取 C++ 中的函数名，包括命名空间和类名。"""
    # 遍历限定标识符链，拼接完整的函数名
    name_parts = []
    current_node = declarator_node.child_by_field_name('declarator')
    while current_node:
        if current_node.type == 'identifier':
            name_parts.insert(0, current_node.text.decode('utf-8'))
            break
        elif current_node.type == 'qualified_identifier':
            left = current_node.child_by_field_name('left')
            right = current_node.child_by_field_name('right')
            if left:
                if left.type == 'qualified_identifier':
                    # 递归处理
                    left_name = extract_cpp_function_name(left)
                    if left_name:
                        name_parts.insert(0, left_name)
            if right and right.type == 'identifier':
                name_parts.append(right.text.decode('utf-8'))
            break
        else:
            break
    return '::'.join(name_parts) if name_parts else None


def get_callee_name(callee_node, language):
    """提取被调用函数的名称，处理 C、C++、Python 和 Java 的不同情况。"""
    if language in ['c', 'cpp']:
        if callee_node.type == 'identifier':
            return callee_node.text.decode('utf-8')
        elif language == 'cpp' and callee_node.type == 'qualified_identifier':
            return extract_cpp_function_name(callee_node)
    elif language == 'python':
        if callee_node.type == 'identifier':
            return callee_node.text.decode('utf-8')
        elif callee_node.type == 'attribute':
            # 处理类似 obj.method() 的调用
            attr_node = callee_node.child_by_field_name('attribute')
            if attr_node and attr_node.type == 'identifier':
                return attr_node.text.decode('utf-8')
    elif language == 'java':
        if callee_node.type == 'identifier':
            return callee_node.text.decode('utf-8')
        elif callee_node.type == 'field_access':
            # 处理类似 obj.method() 的调用
            method_node = callee_node.child_by_field_name('field')
            if method_node and method_node.type == 'identifier':
                return method_node.text.decode('utf-8')
    return None


def process_file(file_path, dataset_path):
    """处理单个文件以提取依赖关系。"""
    absolute_file_path = os.path.join(dataset_path, file_path)
    with open(absolute_file_path, 'rb') as file:
        code = file.read()

    # 根据文件扩展名选择解析器
    _, ext = os.path.splitext(file_path)
    if ext == '.c':
        parser = parser_c
        language = 'c'
    elif ext == '.cpp':
        parser = parser_cpp
        language = 'cpp'
    elif ext == '.py':
        parser = parser_python
        language = 'python'
    elif ext == '.java':
        parser = parser_java
        language = 'java'
    else:
        # 不支持的文件类型
        return {}

    tree = parser.parse(code)
    dependencies = {}
    extract_dependencies(tree.root_node, file_path, dependencies, code, language)
    return dependencies


def process_dataset(dataset_path, output_file):
    """处理整个数据集并将结果保存到文件中。"""
    dependencies = {}

    # 第一遍：收集所有函数定义
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            if file.endswith(('.c', '.cpp', '.py', '.java')):
                file_path = os.path.relpath(os.path.join(root, file), dataset_path)
                process_file(file_path, dataset_path)  # 仅用于填充 global_function_map

    # 第二遍：处理依赖关系
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            if file.endswith(('.c', '.cpp', '.py', '.java')):
                file_path = os.path.relpath(os.path.join(root, file), dataset_path)
                file_dependencies = process_file(file_path, dataset_path)
                dependencies.update(file_dependencies)

    # 将依赖关系与 global_call_map 结合
    results = []
    for function_id, dep in dependencies.items():
        caller_ids = global_call_map.get(function_id, set())
        result = {
            "function_id": function_id.replace("\\", "/"),
            "caller": list(caller_ids),  # 将 set 转换为 list
            "callee": list(dep["callee"]),  # 将 set 转换为 list
            "function_content": dep["function_content"]  # 添加函数内容
        }
        results.append(result)

    # 将结果保存为 JSON 文件
    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(results, outfile, indent=4, ensure_ascii=False)  # 将整个列表作为 JSON 写入


if __name__ == "__main__":
    repo_name = 'spring-framework_java'
    dataset_path = f'repos/{repo_name}'
    output_file = f'preprocessed_data/{repo_name}.json'
    process_dataset(dataset_path, output_file)
    print(f"Dependencies extracted and saved to {output_file}")
