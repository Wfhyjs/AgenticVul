import json

# 读取 func.jsonl 文件
with open('user_sys/toDetect/tinycc_c/functions.jsonl', 'r', encoding='utf-8') as func_file:
    func_data = [json.loads(line) for line in func_file]

# 读取 test_tinycc.json 文件
with open('preprocessed_data/test_tinycc.json', 'r', encoding='utf-8') as test_file:
    test_data = json.load(test_file)

# 将 func.jsonl 中的函数信息合并到 test_tinycc.json 中
for func in func_data:
    func_name = func['func_name']
    # 在 test_tinycc.json 中查找相同的函数名
    for test_func in test_data:
        if test_func['function_id'].endswith(func_name):
            # 合并字段
            test_func['vul'] = func['vul']
            test_func['positive'] = func['positive']
            test_func['fixed'] = func['fixed']
            test_func['fixed_time'] = func['fixed_time']

# 保存合并后的数据
with open('merged_test_tinycc.json', 'w') as merged_file:
    json.dump(test_data, merged_file, indent=4)

print("合并完成！")
