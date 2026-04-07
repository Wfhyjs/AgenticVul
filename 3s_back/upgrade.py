import ast
import re

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from tree_sitter import Language, Parser
import os
import subprocess
import datetime
import zipfile
from models import db, ProjectDetection, User

# 初始化 Flask 应用


current_dir = os.path.dirname(os.path.abspath(__file__))
LANGUAGE_LIBRARY = os.path.join(current_dir, 'my-languages.dll')
C_LANGUAGE = Language(LANGUAGE_LIBRARY, 'c')


def extract_func(file_path):
    """ 根据文件类型提取函数定义 """
    functions = []
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == '.py':
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                tree = ast.parse(f.read(), filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
        except Exception:
            pass
        return functions

    if ext in {'.c', '.h', '.cpp', '.cc', '.cxx'}:
        parser = Parser()
        parser.set_language(C_LANGUAGE)

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()

        tree = parser.parse(code.encode('utf-8'))
        root_node = tree.root_node

        def get_function_name(node):
            """ 获取函数名 """
            for child in node.children:
                if 'identifier' in child.type:
                    return child.text.decode('utf-8')
                else:
                    name = get_function_name(child)
                    if name:
                        return name

        def collect_functions(node):
            """ 收集函数定义 """
            if node.type == 'function_definition':
                function_name = get_function_name(node)
                if function_name:
                    functions.append(function_name)
            for child in node.children:
                collect_functions(child)

        collect_functions(root_node)
        return functions

    if ext == '.java':
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            functions = re.findall(r'\b(?:public|private|protected)?\s+[\w<>,\[\]]+\s+([A-Za-z_][A-Za-z0-9_]*)\s*\([^\)]*\)\s*\{', code)
        except Exception:
            pass
        return functions

    return functions


def clone_project(github_path, local_path='./user_sys/toDetect/'):
    try:
        # 确保本地路径存在
        if not os.path.exists(local_path):
            os.makedirs(local_path)

        # 构建项目名
        project_name = github_path.split('/')[-1]
        if project_name.endswith('.git'):
            project_name = project_name[:-4]

        # 构建完整的本地项目路径
        full_local_path = os.path.join(local_path, project_name)

        # 检查仓库是否已经被克隆
        if os.path.exists(full_local_path):
            print(f"Repository already cloned at {full_local_path}.")
            return project_name

        # 执行 Git 克隆
        subprocess.check_call(['git', 'clone', github_path, full_local_path])

        return project_name
    except subprocess.CalledProcessError as e:
        print("An error occurred while cloning the repository.")
        return None


def count_files_and_functions(folder_path):
    """ 遍历文件夹，统计文件和函数数量 """
    file_count = 0
    function_count = 0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('.c', '.h', '.cpp', '.cc', '.cxx', '.py', '.java')):
                file_count += 1
                file_path = os.path.join(root, file)
                functions = extract_func(file_path)
                function_count += len(functions)
    return file_count, function_count


def handle_uploaded_file(uploaded_file, project_name):
    """ 保存上传的文件并返回文件路径 """
    to_detect_dir = 'user_sys/toDetect/'
    if not os.path.exists(to_detect_dir):
        os.makedirs(to_detect_dir)

    # 获取文件扩展名
    file_extension = os.path.splitext(uploaded_file.filename)[1]

    # 使用项目名称作为新文件名
    new_filename = f"{project_name}{file_extension}"

    # 拼接新文件路径
    filepath = os.path.join(to_detect_dir, new_filename)
    print("Uploading file: ", filepath)

    # 保存文件
    uploaded_file.save(filepath)

    return filepath

def unzip_file(zip_path, project_name):
    """ 解压文件并返回解压后的路径 """
    # base_path, _ = os.path.splitext(zip_path)
    # extract_path = base_path  # 设定目标解压目录为 zip 文件名（不包括扩展名）
    # print(extract_path)
    extract_path = os.path.join('user_sys','toDetect', project_name)  # 解压目录为 pname 目录
    print(f"解压路径: {extract_path}")
    # 确保目标路径存在
    if not os.path.exists(extract_path):
        os.makedirs(extract_path)

    # 解压文件，提取文件内容到指定路径
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    os.remove(zip_path)  # 删除原始的 zip 文件
    return extract_path


def create_new_project(user, Pname, Pmodel, Pfilepath, Pfile, Pfunction):
    """ 创建新项目并保存到数据库 """
    if not user:
        raise ValueError("User not found!")

    new_project = ProjectDetection(
        user_id=user.id,  # 使用解码后的用户信息
        Pname=Pname,
        Ptime=datetime.datetime.now(),  # 当前时间
        Pvul=-1,  # 漏洞数量
        Pstatus='ACTIVE',  # 状态
        Pfilepath=Pfilepath,
        Pmodel=Pmodel,
        Pfile=Pfile,  # 文件数量
        Pfunction=Pfunction  # 函数数量
    )
    db.session.add(new_project)
    db.session.commit()
    return new_project.PID


