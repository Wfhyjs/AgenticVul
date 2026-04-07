import datetime
import email.utils
import json
import os
import smtplib
from collections import Counter
from datetime import datetime, timedelta
from email.header import Header
from email.mime.text import MIMEText
import jwt
import openai
from flask import Flask, request, jsonify, session, redirect, url_for, abort, send_from_directory
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from openai import OpenAI
from werkzeug.utils import secure_filename
import upgrade
import realtime_detection
from models import db, ProjectDetection, User
import start_check
import static_tools
import agents
import generate_report

app = Flask(__name__)
app.secret_key = 'c96d8f5314ea4e72811b8cbec965d0d1eebecf5d82e0e7eaecf6b8f27c39b528'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:wang060807@localhost/AgenticVul'  # 修改为你自己的数据库配置
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.update(
    SESSION_COOKIE_SAMESITE="None",  # 允许跨站点 cookies
    SESSION_COOKIE_SECURE=False,  # 开发环境下允许 HTTP，生产环境中设置为 True
    SESSION_COOKIE_HTTPONLY=True,  # 防止 JavaScript 访问 cookies
    SESSION_COOKIE_PATH="/",  # cookies 在整个应用中有效
)
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=10)
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # 设置为 None 以支持跨域
app.config['SESSION_COOKIE_SECURE'] = False  # 开发环境下关闭 HTTPS 限制
CORS(app, supports_credentials=True, origins="http://127.0.0.1:5173")

bcrypt = Bcrypt(app)
db.init_app(app)

# 创建数据库表
with app.app_context():
    db.create_all()
print("success")
# JWT 密钥
SECRET_KEY = "c96d8f5314ea4e72811b8cbec965d0d1eebecf5d82e0e7eaecf6b8f27c39b528"  # 需要使用一个密钥来签名和验证 JWT


def create_token(uname):
    """生成 JWT token"""
    payload = {
        'uname': uname,
        'exp': datetime.utcnow() + timedelta(days=10)  # 设置 token 的过期时间
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def decode_token(token):
    try:
        if token.startswith('Bearer '):
            token = token[7:]

        decoded = jwt.decode(token, SECRET_KEY, algorithms='HS256')
        return decoded.get('uname')  # 确保获取 'uname' 字段
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError as e:
        print(f"Token decode error: {str(e)}")
        return None


def allowed_file(filename):
    allowed_extensions = {'jpg', 'jpeg', 'png'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route('/')
def home():
    return "Flask 服务正在运行"


# 注册接口
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    uname = data.get('uname')
    uemail = data.get('uemail')
    upassword = data.get('pwd')

    if not uname or not uemail or not upassword:
        return jsonify({'msg': '所有字段均为必填'}), 400

    try:
        # 检查用户是否已存在
        existing_user = User.query.filter((User.Uname == uname) | (User.Uemail == uemail)).first()
        if existing_user:
            return jsonify({'msg': '用户名或邮箱已存在'}), 400

        # 创建新用户
        hashed_password = bcrypt.generate_password_hash(upassword).decode('utf-8')
        new_user = User(Uname=uname, Uemail=uemail, Upassword=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({'msg': '注册成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'数据库错误: {str(e)}'}), 500


# 登录接口
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    uname = data.get('uname')
    upassword = data.get('pwd')
    if not uname or not upassword:
        return jsonify({'msg': '用户名和密码均为必填'}), 400

    try:
        user = User.query.filter((User.Uname == uname) | (User.Uemail == uname)).first()
        if user is None:
            return jsonify({'msg': '用户不存在'}), 400

        # 验证密码
        if not bcrypt.check_password_hash(user.Upassword, upassword):
            return jsonify({'msg': '密码错误'}), 400

        # 生成 token
        token = create_token(user.Uname)
        # 返回用户信息
        user_info = {
            'uname': user.Uname,
            'Uemail': user.Uemail,
            'UFacePath': user.UFacePath,
            'Uorganization': user.Uorganization,
            'Uphone': user.Uphone,
            'Uposition': user.Uposition,
            'UFirstName': user.UFirstName,
            'ULastName': user.ULastName,
            'token': token  # 返回 token
        }
        return jsonify({'msg': '登录成功', 'user': user_info}), 200
    except Exception as e:
        return jsonify({'msg': f'数据库错误: {str(e)}'}), 500


# 忘记密码接口
@app.route('/forget', methods=['POST'])
def find():
    data = request.json
    uemail = data.get('uemail')

    if not uemail:
        return jsonify({'msg': '邮箱为必填项'}), 400

    try:
        user = User.query.filter_by(Uemail=uemail).first()

        if not user:
            return jsonify({'msg': '该邮箱未注册'}), 404

        uname = user.Uname
        reset_link = f"http://localhost:5000/reset_password?email={uemail}"

        # 构造邮件内容
        subject = "重置密码请求"
        body = f"您好 {uname}, 请点击以下链接重置密码：\n{reset_link}"
        message = MIMEText(body, 'plain', 'utf-8')

        # 设置邮件头
        message['From'] = email.utils.formataddr(('项目名称', '1635487611@qq.com'))
        message['To'] = email.utils.formataddr((uname, uemail))
        message['Subject'] = Header(subject, 'utf-8')

        with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
            server.login('1635487611@qq.com', 'ngxaovpzlgzhdacg')
            server.sendmail('1635487611@qq.com', [uemail], message.as_string())

        return jsonify({'msg': '重置密码邮件已发送'}), 200
    except Exception as e:
        return jsonify({'msg': f'错误: {str(e)}'}), 500


# 修改个人信息接口
@app.route('/profile/update', methods=['POST'])
def update_profile():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'msg': 'Token 为空'}), 401

    uname = decode_token(token)
    if not uname:
        return jsonify({'msg': '无效或过期的 Token'}), 401

    data = request.json

    try:
        user = User.query.filter_by(Uname=uname).first()
        if user:
            user.UFirstName = data.get('firstName')
            user.ULastName = data.get('lastName')
            user.Uemail = data.get('email')
            user.Uorganization = data.get('organization')
            user.Uphone = data.get('phone')
            user.Uposition = data.get('position')

            db.session.commit()
            return jsonify({'msg': '信息已更新'}), 200
        else:
            return jsonify({'msg': '用户未找到'}), 404
    except Exception as e:
        return jsonify({'msg': f'数据库错误: {str(e)}'}), 500


# 修改密码
@app.route('/profile/change_password', methods=['POST'])
def change_password():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'msg': 'Token 为空'}), 401

    uname = decode_token(token)
    if not uname:
        return jsonify({'msg': '用户未登录'}), 401

    data = request.json
    old_password = data.get('old_password')
    new_password = data.get('password')

    try:
        user = User.query.filter_by(Uname=uname).first()

        if not user or not bcrypt.check_password_hash(user.Upassword, old_password):
            return jsonify({'msg': '旧密码错误'}), 400

        user.Upassword = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()

        return jsonify({'msg': '密码已修改'}), 200
    except Exception as e:
        return jsonify({'msg': f'数据库错误: {str(e)}'}), 500


# 删除账户
@app.route('/profile/delete', methods=['POST'])
def delete_account():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'msg': 'Token 为空'}), 401

    uname = decode_token(token)
    if not uname:
        return jsonify({'msg': '用户未登录'}), 401

    try:
        user = User.query.filter_by(Uname=uname).first()

        if not user:
            return jsonify({'msg': '用户不存在'}), 404

        db.session.delete(user)
        db.session.commit()
        session.pop('uname', None)  # 清除会话

        return jsonify({'msg': '账户已删除'}), 200
    except Exception as e:
        return jsonify({'msg': f'数据库错误: {str(e)}'}), 500


# 上传头像
@app.route('/profile/upload_photo', methods=['POST'])
def upload_photo():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'msg': 'Token 为空'}), 401

    uname = decode_token(token)
    if not uname:
        return jsonify({'msg': '无效或过期的 Token'}), 401

    if 'upload' not in request.files:
        return jsonify({'msg': '没有文件上传'}), 400

    file = request.files['upload']
    if file.filename == '':
        return jsonify({'msg': '没有选择文件'}), 400

    if file and allowed_file(file.filename):
        try:
            # 使用 secure_filename 确保文件名安全
            filename = secure_filename(file.filename)
            file_path = os.path.join('..', '3s_front', 'user', 'photo', filename)

            # 确保保存目录存在
            directory = os.path.dirname(file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            # 保存文件
            file.save(file_path)

            # 更新数据库中的文件路径
            user = User.query.filter_by(Uname=uname).first()
            if user:
                user.UFacePath = file_path
                db.session.commit()

            return jsonify({'msg': '头像已上传', 'url': file_path}), 200
        except Exception as e:
            return jsonify({'msg': f'文件上传失败: {str(e)}'}), 500
    else:
        return jsonify({'msg': '不允许的文件类型'}), 400


@app.route('/uploadProject', methods=['POST'])
def upload_project():
    # 获取前端传来的 token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'msg': 'Token 为空'}), 401

    # 解码 token 获取用户名
    uname = decode_token(token)
    print(uname)
    if not uname:
        return jsonify({'msg': '无效或过期的 Token'}), 401

    # 根据 uname 查询用户
    user = User.query.filter_by(Uname=uname).first()
    if not user:
        return jsonify({'msg': '未找到用户'}), 404  # 返回 404 表示用户未找到

    submit_button = request.form.get('submit_button')

    if submit_button == 'git':
        # 获取前端传来的 GitHub 项目信息
        Pname = request.form.get('Proname')
        input_path = request.form.get('Pfilepath', '')
        if input_path.startswith('https://github.com/'):
            GitHubPath = input_path
        else:
            GitHubPath = "https://github.com/" + input_path
        Pmodel = request.form.get('Pmodel')

        # 克隆 GitHub 仓库
        project_folder_name = upgrade.clone_project(GitHubPath)
        if project_folder_name:
            # 计算文件和函数数量
            project_path = f"user_sys\\toDetect\\{Pname}"
            file_count, func_count = upgrade.count_files_and_functions(f'user_sys/toDetect/{Pname}')

            # 创建项目记录并保存到数据库
            upgrade.create_new_project(user, Pname, Pmodel, project_path, file_count, func_count)

            return jsonify({
                'message': '上传成功！',
                'project_path': project_path,
                'model': Pmodel,
                'project_name': Pname,
                'file_count': file_count,
                'function_count': func_count
            }), 200
        else:
            return jsonify({'message': '仓库克隆失败，请重试！'}), 400

    elif submit_button == 'file':
        # 获取前端传来的文件和信息
        Pname = request.form.get('Proname')
        uploaded_file = request.files.get('uploaded_file')
        Pmodel = request.form.get('Pmodel')

        # 保存并解压上传的文件
        file_path = upgrade.handle_uploaded_file(uploaded_file, Pname)
        extracted_folder_path = upgrade.unzip_file(file_path,Pname)
        extracted_folder_path = extracted_folder_path.replace('user_sys/', '')  # 清理路径
        # 计算文件和函数数量
        file_count, func_count = upgrade.count_files_and_functions(f'user_sys/toDetect/{Pname}')
        # 创建项目记录并保存到数据库
        project_path = r"user_sys\\toDetect\\" + f"{Pname}"
        pid = upgrade.create_new_project(user, Pname, Pmodel, project_path, file_count, func_count)

        return jsonify({
            'message': '上传成功！',
            'project_path': project_path,
            'model': Pmodel,
            'project_name': Pname,
            'file_count': file_count,
            'function_count': func_count,
            'pid': pid
        }), 200

    return redirect(url_for('index'))


# 定义上传代码和检测的接口
@app.route('/upload_code', methods=['POST'])
def upload_code():
    data = request.get_json()  # 获取请求中的代码内容
    code = data.get('code')  # 提取代码内容
    print(code)

    if not code:
        return jsonify({'error': 'No code provided'}), 400  # 如果没有提供代码，则返回错误

    # 调用提取函数信息的函数
    func_information = realtime_detection.extract_func_info(code)
    print("first:", func_information)
    # 检查返回的格式并确保它是预期的
    if isinstance(func_information, str):
        func_information = realtime_detection.parse_func_information(func_information)
    print("second:", func_information)

    # 调用分析函数，得到安全性检测结果
    results = realtime_detection.process_functions(code, func_information)
    print("results:", results)

    # 返回包含函数名、摘要和结果的响应
    return results


@app.route('/startDetection', methods=['POST'])
def start_detection():
    try:
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'msg': 'Token 为空'}), 401

        uname = decode_token(token)
        user = User.query.filter_by(Uname=uname).first()
        if not user:
            return jsonify({"message": "User not found!"}), 404

        user_id = user.id  # 获取该用户的ID

        # 获取前端传递的参数
        data = request.get_json()
        project_path = data.get('project_path')
        print(project_path)
        Pmodel = data.get('Pmodel')
        print(Pmodel)
        repo_name = data.get('repo_name')
        print(repo_name)
        pname = data.get('pid')
        print(f"Received pid: {pname}, type: {type(pname)}")

        # 检查路径和模型是否有效
        if not project_path or not Pmodel:
            return jsonify({"error": "缺少项目路径或模型"}), 400

        if not os.path.exists(project_path) or not os.path.isdir(project_path):
            return jsonify({"error": "无效的项目路径"}), 400

        # 调用实际的检查和处理函数
        jsonl_file_path = start_check.startCheck(project_path, Pmodel, pname)
        dataset_path = project_path
        output_file = f'preprocessed_data/{repo_name}.json'
        static_tools.process_dataset(dataset_path, output_file)

        print("wanc1")

        # 定义文件路径
        jsonl_file_path = os.path.join(project_path, 'functions.jsonl')
        output_file = f'preprocessed_data/{repo_name}.json'

        # 检查 JSONL 文件是否存在
        if not os.path.exists(jsonl_file_path):
            return jsonify({"error": "functions.jsonl 文件不存在"}), 400

        if not os.path.exists(output_file):
            return jsonify({"error": f"{output_file} 文件不存在"}), 400

        # 读取 func.jsonl 文件
        with open(jsonl_file_path, 'r', encoding='utf-8') as func_file:
            func_data = [json.loads(line) for line in func_file]

        # 读取 test_tinycc.json 文件
        with open(output_file, 'r', encoding='utf-8') as test_file:
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
        merged_file_path = f'preprocessed_data/merged_{repo_name}.json'
        with open(merged_file_path, 'w', encoding='utf-8') as merged_file:
            json.dump(test_data, merged_file, ensure_ascii=False, indent=4)

        print("wanc2")
        result_path = r'merged_' + f'{repo_name}'
        overall_detection, each_function_detection = agents.main(repo_name, pname)
        
        # 计算统计数据
        total_functions = len(func_data)
        total_files = len(set(func.get('file_path', '') for func in func_data if func.get('file_path')))
        total_vul = sum(func.get('vul', 0) for func in test_data)
        total_fix = sum(func.get('fixed', 0) for func in test_data)
        if each_function_detection:
            avg_defect_index = sum(func.get('avg_defect_index', 0) for func in each_function_detection) / len(each_function_detection)
        else:
            avg_defect_index = 0
        
        # 更新数据库中的字段
        project_detection = ProjectDetection.query.filter_by(user_id=user_id, PID=int(pname)).first()
        if project_detection:
            project_detection.Pstatus = '已检测'
            project_detection.Pfunction = total_functions
            project_detection.Pfile = total_files
            project_detection.Pvul = total_vul
            project_detection.Pfix = total_fix
            project_detection.Pdanger = avg_defect_index
            db.session.commit()
        else:
            return jsonify({"error": "ProjectDetection record not found"}), 404
        return jsonify({"message": "检测完成并已更新状态"}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"发生错误: {str(e)}"}), 500


@app.route('/getProjectData', methods=['GET'])
def get_project_data():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'msg': 'Token 为空'}), 401

    uname = decode_token(token)
    if not uname:
        return jsonify({'msg': '无效或过期的 Token'}), 401

    user = User.query.filter_by(Uname=uname).first()
    if not user:
        return jsonify({'msg': '未找到用户'}), 404  # 返回 404 表示用户未找到

    # 查询当前用户的所有项目
    projects = ProjectDetection.query.filter_by(user_id=user.id).all()
    project_data = []
    for project in projects:
        project_data.append({
            'id': project.PID,
            'name': project.Pname,
            'date': project.Ptime.strftime('%Y/%m/%d %H:%M'),
            'fileCount': project.Pfile,  # 存储文件数量
            'functionCount': project.Pfunction,  # 存储函数数量
            'Pfilepath': project.Pfilepath,
            'Pmodel': project.Pmodel,
            'Pvul': project.Pvul,
            'Pfix': project.Pfix,
            # 'progress': project.Pstatus == 'ACTIVE' and 50 or 100,  # 假设进度为50%或100%
            'status': project.Pstatus,
            'risk': get_risk_status(project.Pdanger),
        })

    return jsonify(project_data)


def calculate_progress(project):
    # 这里是一个简单的进度计算方法，您可以根据实际情况调整
    if project.Pfile == 0:
        return 0
    return (project.Pfix / project.Pfile) * 100


def get_risk_status(pdanger):
    # 根据风险评分返回风险状态
    if pdanger == -1:
        return "未检测"
    elif pdanger < 0.5:
        return "安全"
    else:
        return "危险"


@app.route('/deleteProject/<int:id>', methods=['DELETE'])
def delete_project(id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'msg': 'Token 为空'}), 401

    uname = decode_token(token)
    if not uname:
        return jsonify({'msg': '无效或过期的 Token'}), 401

    user = User.query.filter_by(Uname=uname).first()
    if not user:
        return jsonify({'msg': '未找到用户'}), 404

    project = ProjectDetection.query.filter_by(PID=id, user_id=user.id).first()
    if not project:
        return jsonify({'msg': '未找到该项目'}), 404

    db.session.delete(project)
    db.session.commit()

    return jsonify({'msg': '项目已删除'}), 200


@app.route('/get-json', methods=['GET'])
def get_json_data():
    pname = request.args.get('pname')  # 从请求中获取 pname 参数
    if not pname:
        return jsonify({'error': 'Missing pname parameter'}), 400  # 如果没有 pname 参数，则返回 400 错误

    try:
        # 构建 JSON 文件路径
        json_file_path = os.path.join('results', pname, 'each_function_detection.json')

        # 检查文件是否存在
        if not os.path.exists(json_file_path):
            return jsonify({'error': 'File not found'}), 404

        # 打开并读取 JSON 文件
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 返回 JSON 数据
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API端点：获取用户的所有项目数据
@app.route('/projects', methods=['GET'])
def get_projects():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'msg': 'Token 为空'}), 401

    uname = decode_token(token)
    user = User.query.filter_by(Uname=uname).first()
    if not user:
        return jsonify({"message": "User not found!"}), 404

    user_id = user.id  # 获取该用户的ID

    # 获取筛选参数
    pname_filter = request.args.get('pname', default="", type=str)

    # 查询该用户的所有项目，且pname进行模糊查询
    projects = ProjectDetection.query.filter(ProjectDetection.user_id == user_id, ProjectDetection.Pstatus == '已检测',
                                             ProjectDetection.Pname.like(f"%{pname_filter}%")).all()

    # 计算检测项目数量、已识别漏洞数量、已修复漏洞数量
    project_count = len(projects)
    total_vulns = sum([project.Pvul for project in projects])
    total_fixed = sum([project.Pfix for project in projects])

    # 统计 Pdanger 不同区间的项目数量
    danger_high = sum(1 for project in projects if project.Pdanger > 0.5)
    danger_medium = sum(1 for project in projects if 0.2 < project.Pdanger <= 0.5)
    danger_low = sum(1 for project in projects if project.Pdanger <= 0.2)
    print(danger_low)

    # 返回项目数据
    projects_data = [{
        'name': project.Pname,
        'date': project.Ptime.strftime("%Y-%m-%d"),
        'vul': project.Pvul,
        'fixed_count': project.Pfix,
        'danger': project.Pdanger
    } for project in projects]

    return jsonify({
        'project_count': project_count,
        'total_vulns': total_vulns,
        'total_fixed': total_fixed,
        'danger_high': danger_high,
        'danger_medium': danger_medium,
        'danger_low': danger_low,
        'projects': projects_data
    })




# 代理人 (Agent) 配置，每个代理有不同的 Prompt
AGENT_PROMPTS = {
    1: "I am the agent responsible for generating repair patches for code. You can ask me about fixing bugs and generating patches.",
    2: "I am the agent responsible for code vulnerability analysis. You can ask me about finding vulnerabilities and improving security in the code.",
    3: "I am the agent responsible for code functionality analysis. You can ask me about explaining code purposes, features, and usage.",
    4: "I am the agent responsible for explaining technical terms in software engineering. You can ask me about terminology in this field."
}


@app.route("/get_response", methods=["POST"])
def get_response():
    print("yes")
    data = request.json
    agent_id = data.get("agent_id")
    user_message = data.get("message")
    print(agent_id)
    print(user_message)
    if agent_id not in AGENT_PROMPTS:
        return jsonify({"error": "Invalid agent ID"}), 400

    prompt = AGENT_PROMPTS[agent_id]
    print(prompt)
    try:
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message}
        ]
        client = openai.Client(
            api_key="sk-3QJqpcoBk8k6l3B3Pw1dNjiKzQ7H8rrwcY1fbFUsPTRh50Hb",
            base_url="https://xiaoai.plus/v1"
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150
        )

        # prompt = f"{prompt}\nUser: {user_message}\nAgent:",
        # # 调用 LLM 进行文本重写
        # response = client.chat.completions.create(
        #     model="gpt-3.5-turbo",  # 根据需要选择模型
        #     messages=[{"role": "user", "content": prompt}],
        #     max_tokens=150
        # )

        agent_reply = response.choices[0].message.content
        return jsonify({"response": agent_reply})
    except Exception as e:
        # 捕获所有其他异常
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route('/get-number', methods=['GET'])
def get_json_number():
    # 获取pname参数（字符串）
    pname_str = request.args.get('pname')  # 获取传递的字符串

    # 将逗号分隔的字符串转换为列表
    if pname_str:
        project_names = pname_str.split(',')
    else:
        project_names = []

    print(project_names)

    if not project_names:
        return jsonify({'error': 'Missing pname parameter'}), 400  # 如果没有项目名称参数，则返回 400 错误

    project_stats = {}

    for pname in project_names:
        print(pname)
        try:
            print("1111")
            # 构建 JSON 文件路径
            json_file_path = os.path.join('results', pname, 'each_function_detection.json')
            print(pname)
            # 检查文件是否存在
            if not os.path.exists(json_file_path):
                project_stats[pname] = {'error': 'File not found'}
                continue

            # 打开并读取 JSON 文件
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # 统计CWE_id的分布
            cwe_counter = Counter()
            defect_level_counter = {"高风险": 0, '中风险': 0, '低风险': 0}

            for function in data:
                # 统计CWE_id
                if 'defects' in function:
                    for defect in function['defects']:
                        if 'CWE_id' in defect:
                            cwe_counter[defect['CWE_id']] += 1

                # 统计avg_defect_level
                if 'avg_defect_level' in function:
                    level = function['avg_defect_level']
                    if level in defect_level_counter:
                        defect_level_counter[level] += 1

            # 获取最多的5个CWE_id
            top_5_cwe_ids = cwe_counter.most_common(5)
            print(top_5_cwe_ids)
            print(defect_level_counter)

            # 保存项目统计结果
            project_stats[pname] = {
                'top_5_cwe_ids': top_5_cwe_ids,
                'defect_level_counts': defect_level_counter
            }

        except Exception as e:
            project_stats[pname] = {'error': str(e)}

    return jsonify(project_stats)


@app.route('/get-vulnerability-stats', methods=['GET'])
def get_vulnerability_stats():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'msg': 'Token 为空'}), 401

    uname = decode_token(token)
    user = User.query.filter_by(Uname=uname).first()
    if not user:
        return jsonify({"message": "User not found!"}), 404

    user_id = user.id  # 获取该用户的ID

    # 查询该用户的所有项目，且pname进行模糊查询
    project_names = ProjectDetection.query.filter(ProjectDetection.user_id == user_id,
                                                  ProjectDetection.Pstatus == '已检测').all()
    if not project_names:
        return jsonify({'error': 'No projects found for the user'}), 400

    cwe_counter = Counter()

    for pname in project_names:
        try:
            # Construct JSON file path
            json_file_path = os.path.join('results', pname.Pname, 'each_function_detection.json')

            # Check if the file exists
            if not os.path.exists(json_file_path):
                continue

            # Read JSON file
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # Count CWE_id occurrences in defects
            for function in data:  # 直接遍历data中的每个项目
                if 'defects' in function:
                    for defect in function['defects']:  # 遍历 defects 列表
                        if 'CWE_id' in defect:  # 检查是否有 CWE_id 字段
                            cwe_counter[defect['CWE_id']] += 1  # 统计出现次数

        except Exception as e:
            print(f"Error processing project {pname.Pname}: {e}")
            continue  # Skip this project if an error occurs

    # Get top 8 most common CWE_ids
    top_cwe_ids = cwe_counter.most_common(8)

    # Return data to frontend
    return jsonify({'cwe_stats': top_cwe_ids})


@app.route('/get-report', methods=['GET'])
def get_report():
    pname = request.args.get('pname')
    function_id = request.args.get('function_id')

    # 如果 pname 或 function_id 缺失，返回 400 错误
    if not pname:
        return jsonify({'error': 'Missing pname parameter'}), 400
    if not function_id:
        return jsonify({'error': 'Missing function_id parameter'}), 400

    try:
        # 构建 JSON 文件路径
        json_file_path = os.path.join('results', pname, 'each_function_detection.json')

        # 检查文件是否存在
        if not os.path.exists(json_file_path):
            return jsonify({'error': 'File not found'}), 404

        # 打开并读取 JSON 文件
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 查找匹配的 function_id
        function_data = None
        for function in data:
            if function['function_id'] == function_id:
                function_data = function
                break

        # 如果没有找到匹配的 function_id
        if not function_data:
            return jsonify({'error': 'Function ID not found'}), 404
        # 生成报告
        report = generate_report.report(function_data)

        # 返回生成的报告
        return jsonify({'report': report})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    # 假设文件存储在服务器的 `results` 目录下
    directory = os.path.join(os.getcwd(), '3s_back/results/project 3')  # 文件夹路径
    file_path = os.path.join(directory, filename)
    # file_path = os.path.join('results', filename, 'project 8(修复后).zip')

    # 检查文件是否存在
    if not os.path.exists(file_path):
        abort(404)  # 如果文件不存在，返回 404 错误

    # 使用 send_from_directory 发送文件
    return send_from_directory(directory, filename, as_attachment=True)


# @app.route('/get-overall-report', methods=['GET'])
# def get_overall_report():
#     pname = request.args.get('pname')
#     if not pname:
#         return jsonify({"error": "pname parameter is missing"}), 400
#
#     json_file_path = os.path.join('results', pname, 'overall_detection.txt')
#     if not os.path.exists(json_file_path):
#         return jsonify({"error": "Report not found"}), 404
#
#     try:
#         with open(json_file_path, 'r', encoding='utf-8') as file:  # 指定编码为 'utf-8'
#             report_content = file.read()
#             report_content=report_content.replace(r'#', '')
#             report_content = report_content.replace(r'-', '')
#             report_content = report_content.replace(r'\n', '<br>')
#             report_content = report_content.replace(r'\r', '<br>')
#         return jsonify({"report": report_content})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@app.route('/get-overall-report', methods=['GET'])
def get_overall_report():
    pname = request.args.get('pname')
    if not pname:
        return jsonify({"error": "pname parameter is missing"}), 400

    json_file_path = os.path.join('results', pname, 'overall_detection.txt')
    if not os.path.exists(json_file_path):
        return jsonify({"error": "Report not found"}), 404

    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:  # 指定编码为 'utf-8'
            report_content = file.read()

            # # 按照 \n 分割文本
            # report_list = report_content.split(r'\n')
            # print(report_list)
            #
            # # 返回包含文本分段的 JSON 数据
            return jsonify({"report": report_content})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/get-overall-data', methods=['GET'])
def get_overall_data():
    pname = request.args.get('pname')
    if not pname:
        return jsonify({"error": "pname parameter is missing"}), 400
    # 查询该用户的所有项目，且pname进行模糊查询
    project = ProjectDetection.query.filter(ProjectDetection.Pname == pname).first()
    if not project:
        return jsonify({"error": "Project not found"}), 404

    project_danger = project.Pdanger

    # 构建 JSON 文件路径
    json_file_path = os.path.join('results', pname, 'each_function_detection.json')
    if not os.path.exists(json_file_path):
        return jsonify({'error': 'Detection results not found'}), 404

    # 打开并读取 JSON 文件
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 统计CWE_id的分布
    cwe_counter = Counter()
    function_number = 0
    total_impact_degree = 0.0
    total_repair_rate = 0.0
    total_avg_defect_index = 0.0
    total_defect_items = 0

    for function in data:
        function_number += 1

        # 统计CWE_id
        if 'defects' in function:
            for defect in function['defects']:
                if 'CWE_id' in defect:
                    cwe_counter[defect['CWE_id']] += 1
                if 'impact_degree' in defect:
                    total_impact_degree += defect['impact_degree']
                if 'repair_rate' in defect:
                    total_repair_rate += defect['repair_rate']
            total_defect_items += len(function['defects'])

        if 'avg_defect_index' in function:
            total_avg_defect_index += function['avg_defect_index']

    # 计算均值
    average_impact_degree = total_impact_degree / total_defect_items if total_defect_items > 0 else 0
    average_repair_rate = total_repair_rate / total_defect_items if total_defect_items > 0 else 0
    average_avg_defect_index = total_avg_defect_index / function_number if function_number > 0 else 0

    # 获取出现次数最多的CWE_id
    top_cwe_ids = cwe_counter.most_common(1)[0][0] if cwe_counter else None

    # 保存项目统计结果
    project_stats = {
        'top_cwe_ids': top_cwe_ids,
        'impact_degree': format(average_impact_degree * 100, '.2f'),
        'repair_rate': format(average_repair_rate * 100, '.2f'),
        'avg_defect_index': format(average_avg_defect_index, '.3f'),
        'project_danger': format(project_danger, '.2f'),
    }
    return jsonify(project_stats)


if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)
