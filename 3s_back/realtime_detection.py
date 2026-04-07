import asyncio
import os
import re
import openai
import ell
from flask import Flask, request, jsonify
import asyncio



# 解析函数信息的字符串
client = openai.Client(api_key=os.getenv("OPENAI_API_KEY", "dummy_key_for_now"))

def parse_func_information(func_information):
    func_names = re.findall(r'函数名称(.*)', func_information)
    summaries = re.findall(r'函数摘要(.*)', func_information)

    return {
        "func_name": func_names,
        "summary": summaries
    }


def extract_func_info(func_code: str):
    """提取代码中的函数信息（函数名和函数摘要），本地实现，不依赖在线调用"""
    # 尝试解析 C/C++ 函数定义
    func_names = re.findall(r'([A-Za-z_][A-Za-z0-9_]*)\s*\([^\)]*\)\s*\{', func_code)
    if not func_names:
        # 如果没有解析到函数定义，使用通用占位内容
        return {
            'func_name': ['unknown_function'],
            'summary': ['无法自动提取函数名，使用整段代码快速分析']
        }

    summaries = [f'请分析函数 {name} 的安全性和潜在风险。' for name in func_names]
    return {
        'func_name': func_names,
        'summary': summaries
    }


def analyze_func(func: dict):
    """分析每个函数是否存在安全漏洞，快速给出本地判断结果"""
    code = func.get('code', '')
    func_name = func.get('func_name', 'unknown')
    code_summary = func.get('code_summary', '')

    issues = []
    if 'strcpy' in code or 'gets' in code or 'scanf' in code:
        issues.append('存在潜在缓冲区溢出风险（使用不安全输入函数）。')
    if 'system(' in code or 'popen(' in code:
        issues.append('存在命令注入风险。')
    if 'malloc(' in code and 'free(' not in code:
        issues.append('可能存在内存泄漏问题（malloc 后未释放）。')

    if not issues:
        issues.append('初步分析未发现显著漏洞，建议结合模型结果复核。')

    return f"函数名: {func_name}\n摘要: {code_summary}\n结果: {'; '.join(issues)}"


# 异步处理多个函数（重构为 ell 的接口）
def process_functions(code, func_information):
    """按顺序处理多个函数并进行分析"""
    if isinstance(func_information, str):
        func_information = parse_func_information(func_information)

    func_names = func_information["func_name"]
    code_summaries = func_information["summary"]

    # 按顺序处理每个函数
    results = []
    for func_name, code_summary in zip(func_names, code_summaries):
        result = analyze_func({'code': code, 'func_name': func_name, 'code_summary': code_summary})
        results.append(result)

    # 返回处理结果
    return results
