# AgenticVul - 代码漏洞检测系统

一个基于 AI 的代码漏洞检测和修复系统，支持 C/C++、Python、Java 等多种编程语言。

## 项目总述

AgenticVul 是一个集代码上传、漏洞检测、结果分析于一体的综合平台，利用大语言模型和静态分析工具帮助开发者识别和修复代码中的安全漏洞。

**系统组成：**
- 后端服务：Flask + SQLAlchemy + MySQL
- 前端界面：Vue 3 + Vite
- 检测引擎：Tree-sitter + LLM (OpenAI Compatible API)
- 模型支持：CodeBERT、GraphCodeBERT、Devign 等

---

## 前置要求

### 系统环境
- Windows / macOS / Linux
- Python 3.8+
- Node.js 14+ 和 npm
- MySQL 5.7+

### 依赖工具
- Git
- 文本编辑器或 IDE（推荐 VS Code）

---

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/Wfhyjs/AgenticVul.git
cd AgenticVul
```

---

## 后端配置与启动

### 2. 配置后端环境

#### 2.1 创建虚拟环境（推荐）

**Windows:**
```bash
cd 3s_back
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
cd 3s_back
python -m venv venv
source venv/bin/activate
```

#### 2.2 安装 Python 依赖

```bash
# 确保在虚拟环境中
pip install -r requirements.txt
```

**主要依赖：**
- Flask 和 Flask-CORS
- SQLAlchemy 和 Flask-SQLAlchemy
- PyJWT
- PyBcrypt
- openai（LLM 调用）
- requests
- 其他依赖见 requirements.txt

### 2.3 配置数据库

#### 创建 MySQL 数据库

```sql
-- 使用 MySQL 客户端连接
mysql -u root -p

-- 创建数据库
CREATE DATABASE AgenticVul CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 修改数据库配置

编辑 `3s_back/app.py`，找到以下行并修改为你的数据库信息：

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:wang060807@localhost/AgenticVul'
```

修改为：
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://<用户名>:<密码>@<主机>:<端口>/AgenticVul'
```

例如：
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:yourpassword@localhost:3306/AgenticVul'
```

### 2.4 初始化数据库

数据库表会在 Flask 应用启动时自动创建（见 `app.py` 中的 `db.create_all()`）。

### 2.5 配置 LLM API（可选）

如果需要使用 LLM 功能，在 `3s_back/app.py` 中配置 OpenAI 兼容的 API：

```python
client = openai.Client(
    api_key="your_api_key_here",
    base_url="https://api.openai.com/v1"  # 或其他兼容 API 地址
)
```

### 2.6 启动后端服务

```bash
# 确保在 3s_back 目录中，且虚拟环境已激活
python app.py
```

**预期输出：**
```
success
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

后端服务运行于 `http://127.0.0.1:5000`

---

## 前端配置与启动

### 3. 配置前端环境

#### 3.1 安装 Node.js 依赖

```bash
cd ../3s_front
npm install
```

**耗时提示：** 首次安装可能需要 5-10 分钟，取决于网络速度。

#### 3.2 配置 API 地址（重要）

编辑 `3s_front/src/components/project/Project.vue` 等文件中的 API 地址，确保指向你的后端服务：

搜索并替换所有 `http://127.0.0.1:5000` 为你的后端 API 地址（如果不是本地开发）。

### 3.3 启动前端开发服务

```bash
npm run dev
```

**预期输出：**
```
VITE v4.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
```

前端服务运行于 `http://localhost:5173`

---

## 完整启动流程（推荐）

### 方式一：顺序启动（开发）

**终端 1 - 启动后端：**
```bash
cd AgenticVul/3s_back
python -m venv venv  # 首次需要创建虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

**终端 2 - 启动前端：**
```bash
cd AgenticVul/3s_front
npm install  # 首次需要安装依赖
npm run dev
```

**然后在浏览器中访问：** `http://localhost:5173`

### 方式二：使用 PowerShell 脚本（Windows）

```powershell
# 后端
cd .\3s_back
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

---

## 使用指南

### 1. 用户注册与登录

1. 打开前端界面 `http://localhost:5173`
2. 点击"注册"新建账户
3. 输入用户名、邮箱、密码后提交
4. 使用账户登录系统

### 2. 上传项目

1. 登录后进入"项目管理"页面
2. 点击"上传项目"按钮
3. 选择项目文件（支持 ZIP、TAR 等压缩格式）
4. 选择项目类型（C/C++、Python、Java）
5. 点击"上传"

### 3. 启动检测

1. 在项目列表中找到已上传的项目
2. 点击"开始检测"按钮
3. 等待检测完成（耗时取决于项目大小）
4. 检测完成后可查看详细报告

### 4. 查看检测报告

1. 点击项目名称进入项目详情页
2. 查看"可视化分析"部分的数据
3. 浏览"函数总览"中的各函数风险等级
4. 下载检测报告

---

## 常见问题

### Q1: 后端无法连接到数据库

**解决方案：**
```bash
# 确认 MySQL 服务已启动
mysql -u root -p  # 测试连接

# 修改 app.py 中的数据库配置
# 检查用户名、密码、主机、端口、数据库名是否正确
```

### Q2: 前端无法连接到后端 API

**解决方案：**
- 确认后端服务正在运行（`http://127.0.0.1:5000` 可访问）
- 检查前端 API 地址配置是否正确
- 检查浏览器控制台是否有 CORS 错误

### Q3: 检测结果为空或显示"未知"

**解决方案：**
- 确认项目上传成功（检查"文件数量"和"函数数量"）
- 确认项目类型选择正确
- 检查后端日志是否有错误信息
- 检查 `results/<项目名>/` 目录下是否存在检测结果文件

### Q4: LLM 调用失败

**解决方案：**
- 检查 API Key 是否正确
- 检查 API 地址是否可访问
- 查看后端日志获取详细错误信息
- 确保网络连接正常

---

## 项目结构

```
AgenticVul/
├── 3s_back/                    # 后端服务
│   ├── app.py                  # Flask 应用入口
│   ├── models.py               # 数据库模型
│   ├── agents.py               # 漏洞检测逻辑
│   ├── start_check.py          # 预处理模块
│   ├── realtime_detection.py   # 单文件检测
│   ├── static_tools.py         # 工具函数
│   ├── requirements.txt        # Python 依赖
│   ├── knowledge_base/         # 知识库数据
│   ├── results/                # 检测结果存储
│   └── preprocessed_data/      # 预处理数据
├── 3s_front/                   # 前端应用
│   ├── src/
│   │   ├── components/         # Vue 组件
│   │   ├── router/             # 路由配置
│   │   ├── App.vue             # 主应用
│   │   └── main.js             # 应用入口
│   ├── package.json            # Node 依赖
│   ├── vite.config.js          # Vite 配置
│   └── public/                 # 静态资源
└── README.md                   # 项目说明文档
```

---

## 开发指南

### 后端开发
- 代码规范：遵循 PEP 8
- 数据库操作：使用 SQLAlchemy ORM
- API 设计：RESTful 风格
- 错误处理：统一返回 JSON 格式

### 前端开发
- 框架：Vue 3 + Vite
- 组件库：使用本项目的自定义组件
- 状态管理：使用 ref 和 reactive（Vue 3 Composition API）
- HTTP 客户端：axios

---

## 部署指南

### 生产环境部署（后端）

```bash
# 使用 Gunicorn 部署
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 生产环境部署（前端）

```bash
# 构建生产版本
npm run build

# 生成的文件在 dist/ 目录中
# 使用 Nginx 或其他 Web 服务器提供服务
```

**Nginx 配置示例：**
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        root /path/to/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend_server:5000;
    }
}
```

---

## 许可证

MIT License

---

## 贡献

欢迎提交 Issue 和 Pull Request！

---

## 联系方式

- GitHub: https://github.com/Wfhyjs/AgenticVul
- 问题报告: 通过 GitHub Issues

---

## 更新日志

### v1.0.0 (2026-04-07)
- 初始版本发布
- 支持 C/C++、Python、Java 代码检测
- 实现基础的漏洞识别和修复建议功能
- 修复后端文件命名和数据统计逻辑

---

**最后更新：2026年4月7日**
