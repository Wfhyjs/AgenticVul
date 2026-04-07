import os

from flask import jsonify
from openai import OpenAI
import ell
import json
import openai
client = openai.Client(
    api_key="sk-3QJqpcoBk8k6l3B3Pw1dNjiKzQ7H8rrwcY1fbFUsPTRh50Hb",
    base_url="https://xiaoai.plus/v1"
)

@ell.simple(model="gpt-3.5-turbo", client=client)
def report(function_data):
    # 创建报告的基本结构
    prompt = f"""
    <h2 style="text-align: center;">函数检测报告</h2>
    <h3>1. 函数基本信息</h3>
    <h6>函数名：{function_data['function_name']}</h6>
    <h6>所在文件：{function_data['file_path']}</h6>
    <h6>调用的函数：</h6>
    <ul>
    """

    # 处理调用函数信息
    if function_data['caller']:
        for caller in function_data['caller']:
            prompt += f"    <li>{caller}</li>\n"
    else:
        prompt += "    <li>无</li>\n"

    prompt += f"""
    </ul>
    <h6>被调用的函数：</h6>
    <ul>
    """

    # 处理被调用函数信息
    if function_data['callee']:
        for callee in function_data['callee']:
            prompt += f"    <li>{callee}</li>\n"
    else:
        prompt += "    <li>无</li>\n"

    prompt += f"""
    <h3>2. 检测到的漏洞</h3>
    <p>共检测到 {len(function_data['defects'])} 个可能的漏洞：</p>
    <ul>
    """

    # 遍历每个漏洞，并为每个漏洞加上序号
    for idx, defect in enumerate(function_data['defects'], start=1):
        prompt += f"""
        <b>漏洞 {idx}：</b><br>
        <ul>
            <li><b>漏洞类型：</b>{defect['CWE_id']}<br></li>
            <li><b>漏洞描述：</b>{defect['description']}<br></li>
            <li><b>漏洞影响指数：</b>{defect['defect_index']}<br></li>
            <li><b>修复率：</b>{defect['repair_rate']}<br></li>
            <li><b>影响程度：</b>{defect['impact_degree']}<br></li>
        </ul>
        """
    # 继续生成报告的其他部分
    prompt += f"""
    <h3>3.函数综合评估：</h3>
    <ul>
        <li><p>漏洞风险等级：{function_data['avg_defect_level']}</p></li>
        <li><p>平均影响指数：{function_data['avg_defect_index']}</p></li>
    </ul>
    <h3>4.修复建议：</h3>
    <p>{function_data['repairs']['repair_advice']}</p>
    <pre><code>{function_data['repairs']['repair_patch']}</code></pre>
    """

    return prompt

