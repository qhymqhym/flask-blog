基于 Flask 框架开发的轻量级个人博客系统（毕业设计）（勿抄袭）

✨ 项目介绍

本项目是基于 Python Flask 框架开发的轻量级个人博客系统，采用前后端不分离架构，实现了博客展示、后台管理、Markdown 渲染、用户权限验证等功能。界面简洁、结构清晰、易于部署，适合作为毕业设计、课程设计或二次开发使用。

🧩 功能特性

 用户登录 / 权限管理（管理员角色）
 
 博客发布、编辑、删除
 
 Markdown 文章编辑 + 代码高亮
 
 前台博客展示页面
 
 后台管理面板
 
 响应式页面布局
 
 XSS 防护、密码加密、CSRF 验证
 
 404 / 500 错误页面处理
 
🛠 技术栈

后端：Python 3.9 + Flask 2.x

数据库：SQLite（开发）/ MySQL（生产）

ORM：Flask-SQLAlchemy

表单验证：Flask-WTF

用户登录：Flask-Login

密码加密：Flask-Bcrypt

数据库迁移：Flask-Migrate

前端：HTML5 + CSS3 + Jinja2 模板

Markdown 渲染：markdown + bleach

📂 项目结构

plaintext

flask-blog/

├── app.py              # 项目入口

├── config.py           # 配置文件

├── extensions.py       # 扩展初始化

├── models.py           # 数据模型

├── forms.py            # 表单验证

├── routes/             # 路由模块

├── templates/          # 前端模板

├── static/             # 静态资源

├── utils/              # 工具函数

└── requirements.txt    # 依赖包

🚀 快速启动

1. 克隆项目
   
bash
运行

git clone https://github.com/qhymqhym/flask-blog.git
cd flask-blog

2. 安装依赖
   
bash
运行

pip install -r requirements.txt

3. 初始化数据库
bash

# 自动创建管理员账户（admin / admin123）
python app.py

4. 启动项目

bash
运行

python app.py

5. 访问地址

前台首页：http://127.0.0.1:5000
后台管理：http://127.0.0.1:5000/admin

默认管理员账号：
用户名：admin
密码：admin123

🧪 功能预览

首页展示所有博客列表

博客详情页支持 Markdown 渲染

管理员登录后可发布、编辑、删除文章

权限控制：未登录用户无法进入后台

安全加密：密码哈希存储，防 XSS 攻击

🎓 毕业设计说明

本项目为 计算机专业毕业设计包含：

完整论文（基于 Flask 的轻量级博客系统设计与实现）

可运行源码

标准项目结构

前后端完整功能

可直接用于答辩与提交

📄 许可证

本项目仅供学习、毕业设计使用，禁止商用。

✉️ 联系方式

GitHub：@qhymqhym
