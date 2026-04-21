from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_login import login_user, logout_user, login_required, current_user
from models import Article, Category, Tag, Comment, Visit, User, article_like
from extensions import db, bcrypt, cache
from utils.markdown import markdown_to_html
from forms import LoginForm, RegistrationForm, UpdateProfileForm, ArticleForm, CommentForm
from datetime import datetime
import json
import os
import time

bp = Blueprint('frontend', __name__)

@bp.route('/')
def index():
    articles = Article.query.filter_by(status='published').order_by(Article.is_top.desc(), Article.created_at.desc()).all()
    categories = Category.query.all()
    tags = Tag.query.all()
    
    # 获取点赞数前十的文章
    from sqlalchemy import func, desc
    top_liked_articles = db.session.query(Article).join(article_like).filter(Article.status=='published').group_by(Article.id).order_by(func.count(article_like.c.user_id).desc()).limit(10).all()
    
    # 获取访问量前十的文章
    top_viewed_articles = Article.query.filter_by(status='published').order_by(Article.views.desc()).limit(10).all()
    
    return render_template('frontend/index.html', articles=articles, categories=categories, tags=tags, top_liked_articles=top_liked_articles, top_viewed_articles=top_viewed_articles)

@bp.route('/article/<int:id>')
def article_detail(id):
    article = Article.query.get_or_404(id)
    article.views += 1
    db.session.commit()
    
    # 记录访问
    visit = Visit(
        article_id=id,
        ip=request.remote_addr,
        user_agent=request.user_agent.string,
        referer=request.referrer
    )
    db.session.add(visit)
    db.session.commit()
    
    comments = Comment.query.filter_by(article_id=id, status='approved', parent_id=None).order_by(Comment.created_at.desc()).all()
    categories = Category.query.all()
    tags = Tag.query.all()
    
    # 获取点赞数前十的文章
    from sqlalchemy import func, desc
    top_liked_articles = db.session.query(Article).join(article_like).filter(Article.status=='published').group_by(Article.id).order_by(func.count(article_like.c.user_id).desc()).limit(10).all()
    
    # 获取访问量前十的文章
    top_viewed_articles = Article.query.filter_by(status='published').order_by(Article.views.desc()).limit(10).all()
    
    return render_template('frontend/article_detail.html', article=article, comments=comments, categories=categories, tags=tags, top_liked_articles=top_liked_articles, top_viewed_articles=top_viewed_articles)

@bp.route('/category/<int:id>')
def category_detail(id):
    category = Category.query.get_or_404(id)
    articles = Article.query.filter_by(category_id=id, status='published').order_by(Article.is_top.desc(), Article.created_at.desc()).all()
    categories = Category.query.all()
    tags = Tag.query.all()
    
    # 获取点赞数前十的文章
    from sqlalchemy import func, desc
    top_liked_articles = db.session.query(Article).join(article_like).filter(Article.status=='published').group_by(Article.id).order_by(func.count(article_like.c.user_id).desc()).limit(10).all()
    
    # 获取访问量前十的文章
    top_viewed_articles = Article.query.filter_by(status='published').order_by(Article.views.desc()).limit(10).all()
    
    return render_template('frontend/category_detail.html', category=category, articles=articles, categories=categories, tags=tags, top_liked_articles=top_liked_articles, top_viewed_articles=top_viewed_articles)

@bp.route('/tag/<int:id>')
def tag_detail(id):
    tag = Tag.query.get_or_404(id)
    articles = tag.articles.filter_by(status='published').order_by(Article.is_top.desc(), Article.created_at.desc()).all()
    categories = Category.query.all()
    tags = Tag.query.all()
    
    # 获取点赞数前十的文章
    from sqlalchemy import func, desc
    top_liked_articles = db.session.query(Article).join(article_like).filter(Article.status=='published').group_by(Article.id).order_by(func.count(article_like.c.user_id).desc()).limit(10).all()
    
    # 获取访问量前十的文章
    top_viewed_articles = Article.query.filter_by(status='published').order_by(Article.views.desc()).limit(10).all()
    
    return render_template('frontend/tag_detail.html', tag=tag, articles=articles, categories=categories, tags=tags, top_liked_articles=top_liked_articles, top_viewed_articles=top_viewed_articles)

@bp.route('/about')
def about():
    categories = Category.query.all()
    tags = Tag.query.all()
    
    # 获取点赞数前十的文章
    from sqlalchemy import func, desc
    top_liked_articles = db.session.query(Article).join(article_like).filter(Article.status=='published').group_by(Article.id).order_by(func.count(article_like.c.user_id).desc()).limit(10).all()
    
    # 获取访问量前十的文章
    top_viewed_articles = Article.query.filter_by(status='published').order_by(Article.views.desc()).limit(10).all()
    
    return render_template('frontend/about.html', categories=categories, tags=tags, top_liked_articles=top_liked_articles, top_viewed_articles=top_viewed_articles)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    用户登录
    """
    if current_user.is_authenticated:
        return redirect(url_for('frontend.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        
        # 检查是否是管理员账号
        if username == 'admin':
            flash('请使用管理员登录页面')
            return redirect(url_for('frontend.login'))
            
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=form.remember.data)
            print(f"User {user.username} logged in successfully")
            print(f"current_user.is_authenticated: {current_user.is_authenticated}")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('frontend.index'))
        flash('用户名或密码错误')
    
    categories = Category.query.all()
    tags = Tag.query.all()
    
    # 获取点赞数前十的文章
    from sqlalchemy import func, desc
    top_liked_articles = db.session.query(Article).join(article_like).filter(Article.status=='published').group_by(Article.id).order_by(func.count(article_like.c.user_id).desc()).limit(10).all()
    
    # 获取访问量前十的文章
    top_viewed_articles = Article.query.filter_by(status='published').order_by(Article.views.desc()).limit(10).all()
    
    return render_template('frontend/login.html', form=form, categories=categories, tags=tags, top_liked_articles=top_liked_articles, top_viewed_articles=top_viewed_articles)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    用户注册
    """
    if current_user.is_authenticated:
        return redirect(url_for('frontend.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # 创建新用户
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        # 自动登录
        login_user(user)
        flash('注册成功！')
        return redirect(url_for('frontend.index'))
    
    categories = Category.query.all()
    tags = Tag.query.all()
    
    # 获取点赞数前十的文章
    from sqlalchemy import func, desc
    top_liked_articles = db.session.query(Article).join(article_like).filter(Article.status=='published').group_by(Article.id).order_by(func.count(article_like.c.user_id).desc()).limit(10).all()
    
    # 获取访问量前十的文章
    top_viewed_articles = Article.query.filter_by(status='published').order_by(Article.views.desc()).limit(10).all()
    
    return render_template('frontend/register.html', form=form, categories=categories, tags=tags, top_liked_articles=top_liked_articles, top_viewed_articles=top_viewed_articles)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('frontend.index'))

@bp.route('/my_articles')
@login_required
def my_articles():
    articles = Article.query.filter_by(user_id=current_user.id).order_by(Article.created_at.desc()).all()
    categories = Category.query.all()
    tags = Tag.query.all()
    
    # 获取点赞数前十的文章
    from sqlalchemy import func, desc
    top_liked_articles = db.session.query(Article).join(article_like).filter(Article.status=='published').group_by(Article.id).order_by(func.count(article_like.c.user_id).desc()).limit(10).all()
    
    # 获取访问量前十的文章
    top_viewed_articles = Article.query.filter_by(status='published').order_by(Article.views.desc()).limit(10).all()
    
    return render_template('frontend/my_articles.html', articles=articles, categories=categories, tags=tags, top_liked_articles=top_liked_articles, top_viewed_articles=top_viewed_articles)

@bp.route('/create_article', methods=['GET', 'POST'])
@login_required
def create_article():
    categories = Category.query.all()
    tags = Tag.query.all()
    
    # 获取点赞数前十的文章
    from sqlalchemy import func, desc
    top_liked_articles = db.session.query(Article).join(article_like).filter(Article.status=='published').group_by(Article.id).order_by(func.count(article_like.c.user_id).desc()).limit(10).all()
    
    # 获取访问量前十的文章
    top_viewed_articles = Article.query.filter_by(status='published').order_by(Article.views.desc()).limit(10).all()
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category_id = int(request.form['category_id'])
        tag_ids = request.form.getlist('tags')
        status = request.form['status']
        
        # 处理封面图上传
        cover_image = None
        if 'cover' in request.files:
            file = request.files['cover']
            if file.filename:
                import os
                # 确保images目录存在
                image_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'images')
                if not os.path.exists(image_dir):
                    os.makedirs(image_dir)
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                file.save(os.path.join(image_dir, filename))
                cover_image = filename
        
        # 转换Markdown为HTML
        content_html = markdown_to_html(content)
        
        article = Article(
            title=title,
            content=content,
            content_html=content_html,
            category_id=category_id,
            user_id=current_user.id,
            status=status,
            cover_image=cover_image
        )
        
        # 添加标签
        for tag_id in tag_ids:
            tag = Tag.query.get(int(tag_id))
            article.tags.append(tag)
        
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('frontend.index'))
    return render_template('frontend/create_article.html', categories=categories, tags=tags, top_liked_articles=top_liked_articles, top_viewed_articles=top_viewed_articles)

@bp.route('/article/<int:id>/comment', methods=['POST'])
@login_required
def add_comment(id):
    article = Article.query.get_or_404(id)
    content = request.form['content']
    
    comment = Comment(
        content=content,
        author=current_user.username,
        email='user@example.com',  # 可以从用户信息中获取
        status='pending',
        article_id=id
    )
    
    db.session.add(comment)
    db.session.commit()
    flash('评论已提交，等待审核')
    return redirect(url_for('frontend.article_detail', id=id))

@bp.route('/article/<int:id>/reply', methods=['POST'])
@login_required
def add_reply(id):
    parent_id = request.form['parent_id']
    content = request.form['content']
    
    reply = Comment(
        content=content,
        author=current_user.username,
        email='user@example.com',  # 可以从用户信息中获取
        status='pending',
        article_id=id,
        parent_id=parent_id
    )
    
    db.session.add(reply)
    db.session.commit()
    flash('回复已提交，等待审核')
    return redirect(url_for('frontend.article_detail', id=id))

@bp.route('/article/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_article(id):
    article = Article.query.get_or_404(id)
    
    # 检查是否是文章作者
    if article.user_id != current_user.id:
        flash('You can only edit your own articles')
        return redirect(url_for('frontend.my_articles'))
    
    categories = Category.query.all()
    tags = Tag.query.all()
    
    # 获取点赞数前十的文章
    from sqlalchemy import func, desc
    top_liked_articles = db.session.query(Article).join(article_like).filter(Article.status=='published').group_by(Article.id).order_by(func.count(article_like.c.user_id).desc()).limit(10).all()
    
    # 获取访问量前十的文章
    top_viewed_articles = Article.query.filter_by(status='published').order_by(Article.views.desc()).limit(10).all()
    
    if request.method == 'POST':
        article.title = request.form['title']
        article.content = request.form['content']
        # 转换Markdown为HTML
        article.content_html = markdown_to_html(article.content)
        article.category_id = int(request.form['category_id'])
        article.status = request.form['status']
        
        # 处理封面图上传
        if 'cover' in request.files:
            file = request.files['cover']
            if file.filename:
                import os
                # 确保images目录存在
                image_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'images')
                if not os.path.exists(image_dir):
                    os.makedirs(image_dir)
                # 删除旧图片
                if article.cover_image:
                    old_path = os.path.join(image_dir, article.cover_image)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                # 保存新图片
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                file.save(os.path.join(image_dir, filename))
                article.cover_image = filename
        
        # 更新标签
        # 先获取当前标签列表，然后逐个删除
        for tag in list(article.tags):
            article.tags.remove(tag)
        # 添加新标签
        tag_ids = request.form.getlist('tags')
        for tag_id in tag_ids:
            tag = Tag.query.get(int(tag_id))
            article.tags.append(tag)
        
        db.session.commit()
        return redirect(url_for('frontend.my_articles'))
    
    return render_template('frontend/edit_article.html', article=article, categories=categories, tags=tags, top_liked_articles=top_liked_articles, top_viewed_articles=top_viewed_articles)

@bp.route('/article/<int:id>/delete', methods=['POST'])
@login_required
def delete_article(id):
    article = Article.query.get_or_404(id)
    
    # 检查是否是文章作者
    if article.user_id != current_user.id:
        flash('You can only delete your own articles')
        return redirect(url_for('frontend.my_articles'))
    
    # 删除相关的访问记录
    Visit.query.filter_by(article_id=id).delete()
    
    # 删除封面图
    if article.cover_image:
        import os
        # 使用绝对路径
        image_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'images', article.cover_image)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(article)
    db.session.commit()
    flash('文章已删除')
    return redirect(url_for('frontend.my_articles'))

@bp.route('/article/<int:id>/like', methods=['POST'])
@login_required
def like_article(id):
    article = Article.query.get_or_404(id)
    
    if current_user in article.likes:
        # 取消点赞
        article.likes.remove(current_user)
        db.session.commit()
        return {'status': 'unliked', 'like_count': article.like_count}
    else:
        # 添加点赞
        article.likes.append(current_user)
        db.session.commit()
        return {'status': 'liked', 'like_count': article.like_count}

# AI伴侣相关功能

# 确保会话目录存在
def ensure_session_dir():
    session_dir = os.path.join(os.path.dirname(__file__), '..', 'sessions')
    if not os.path.exists(session_dir):
        os.makedirs(session_dir)
    return session_dir

# 生成会话ID
def generate_session_id():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 获取用户会话文件路径
def get_user_session_path(user_id, session_name=None):
    session_dir = ensure_session_dir()
    user_dir = os.path.join(session_dir, str(user_id))
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    if session_name:
        return os.path.join(user_dir, f"{session_name.replace(':', '-')}.json")
    return user_dir

# 保存会话
def save_session(user_id, session_data):
    session_path = get_user_session_path(user_id, session_data['current_session'])
    with open(session_path, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)

# 加载会话
def load_session(user_id, session_name):
    session_path = get_user_session_path(user_id, session_name)
    if os.path.exists(session_path):
        with open(session_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

# 删除会话
def delete_session(user_id, session_name):
    session_path = get_user_session_path(user_id, session_name)
    if os.path.exists(session_path):
        os.remove(session_path)

# 获取用户会话列表
def get_user_sessions(user_id):
    user_dir = get_user_session_path(user_id)
    if not os.path.exists(user_dir):
        return []
    sessions = []
    for filename in os.listdir(user_dir):
        if filename.endswith('.json'):
            sessions.append(filename[:-5])
    sessions.sort(reverse=True)
    return sessions

@bp.route('/ai_companion')
@login_required
def ai_companion():
    # 初始化用户会话
    user_id = current_user.id
    sessions = get_user_sessions(user_id)
    
    # 如果没有会话，创建一个新会话
    if not sessions:
        session_id = generate_session_id()
        session_data = {
            'nick_name': '小甜甜',
            'character': '活泼开朗的东北姑娘',
            'current_session': session_id,
            'messages': []
        }
        save_session(user_id, session_data)
        sessions = [session_id]
    
    # 检查是否有current_session参数
    current_session = request.args.get('current_session')
    
    # 加载指定会话或默认会话
    if current_session and current_session in sessions:
        session_data = load_session(user_id, current_session)
    else:
        # 加载第一个会话
        default_session = sessions[0]
        session_data = load_session(user_id, default_session)
    
    return render_template('frontend/ai_companion.html', 
                          sessions=sessions,
                          current_session_name=session_data['current_session'],
                          nick_name=session_data['nick_name'],
                          character=session_data['character'],
                          messages=session_data['messages'])

@bp.route('/ai_companion/new_session', methods=['POST'])
@login_required
def new_session():
    user_id = current_user.id
    session_id = generate_session_id()
    session_data = {
        'nick_name': '小甜甜',
        'character': '活泼开朗的东北姑娘',
        'current_session': session_id,
        'messages': []
    }
    save_session(user_id, session_data)
    return jsonify({'success': True})

@bp.route('/ai_companion/load_session')
@login_required
def load_session_route():
    user_id = current_user.id
    session_name = request.args.get('session')
    if session_name:
        session_data = load_session(user_id, session_name)
        if session_data:
            # 更新当前会话为加载的会话
            session_data['current_session'] = session_name
            save_session(user_id, session_data)
            return jsonify({'success': True})
    return jsonify({'success': False})

@bp.route('/ai_companion/delete_session')
@login_required
def delete_session_route():
    user_id = current_user.id
    session_name = request.args.get('session')
    if session_name:
        delete_session(user_id, session_name)
        return jsonify({'success': True})
    return jsonify({'success': False})

@bp.route('/ai_companion/save_settings', methods=['POST'])
@login_required
def save_settings():
    user_id = current_user.id
    data = request.get_json()
    nick_name = data.get('nick_name', '小甜甜')
    character = data.get('character', '活泼开朗的东北姑娘')
    
    # 获取当前会话
    sessions = get_user_sessions(user_id)
    if sessions:
        current_session = sessions[0]
        session_data = load_session(user_id, current_session)
        if session_data:
            session_data['nick_name'] = nick_name
            session_data['character'] = character
            save_session(user_id, session_data)
    
    return jsonify({'success': True})

@bp.route('/ai_companion/chat', methods=['POST'])
@login_required
def ai_chat():
    user_id = current_user.id
    data = request.get_json()
    message = data.get('message', '')
    nick_name = data.get('nick_name', '小甜甜')
    character = data.get('character', '活泼开朗的东北姑娘')
    model = data.get('model', 'deepseek-chat')
    
    # 获取当前会话
    sessions = get_user_sessions(user_id)
    if not sessions:
        session_id = generate_session_id()
        session_data = {
            'nick_name': nick_name,
            'character': character,
            'current_session': session_id,
            'messages': []
        }
        save_session(user_id, session_data)
        current_session = session_id
    else:
        current_session = sessions[0]
        session_data = load_session(user_id, current_session)
        if not session_data:
            session_data = {
                'nick_name': nick_name,
                'character': character,
                'current_session': current_session,
                'messages': []
            }
    
    # 添加用户消息
    session_data['messages'].append({'role': 'user', 'content': message})
    
    # 构建系统提示词
    system_prompt = f"""
    你叫{nick_name}，现在是用户的真实伴侣，请完全代入伴侣角色。：
    规则：
    1. 每次只回1条消息
    2.禁止任何场景或状态描述性文字
    3. 匹配用户的语言
    4.回复简短，像微信聊天一样
    5.有需要的话可以用emoji表情
    6.用符合伴侣性格的方式对话
    7.回复的内容，要充分体现伴侣的性格特征
    伴侣性格：
    -{character}
    你必须严格遵守上述规则来回复用户。
    """
    
    def generate_response():
        # 导入必要的模块
        from openai import OpenAI
        import traceback
        
        try:
            
            if model == 'glm-4.5-air' or model == 'glm-4.7':
                # 使用GLM模型
                api_key = '665fda0ed0b94353a4d13b6faa5bf5bd.FNyk5wTE87gxIbwl'
                if model == 'glm-4.5-air':
                    model_name = 'glm-4.5-air'
                else:
                    model_name = 'glm-4.7'
                
                # 打印调试信息
                print(f"GLM模型配置: api_key={'存在' if api_key else '不存在'}, model_name={model_name}")
                
                # 使用ZhipuAiClient
                from zai import ZhipuAiClient
                client = ZhipuAiClient(api_key=api_key)
                
                # 打印客户端初始化成功信息
                print(f"ZhipuAiClient初始化成功，准备调用模型: {model_name}")
            elif model == 'aliyun':
                # 使用阿里云模型
                # 直接使用用户提供的API密钥
                api_key = 'sk-584189c0eeb54ee582624365a797ad44'
                model_name = 'qwen-plus'
                base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
                
                # 打印调试信息
                print(f"阿里云模型配置: api_key={'存在' if api_key else '不存在'}, base_url={base_url}, model_name={model_name}")
                
                client = OpenAI(
                    api_key=api_key,
                    base_url=base_url
                )
            else:
                # 默认使用DeepSeek模型
                api_key = os.environ.get('DEEPSEEK_API_KEY')
                model_name = 'deepseek-chat'
                base_url = "https://api.deepseek.com"
                
                client = OpenAI(
                    api_key=api_key,
                    base_url=base_url
                )
            
            if api_key:
                # 调用API，使用流式输出
                try:
                    # 检查是否是GLM模型
                    if model == 'glm-4.5-air' or model == 'glm-4.7':
                        # 使用ZhipuAiClient调用GLM模型
                        response = client.chat.completions.create(
                            model=model_name,
                            messages=[
                                {"role": "system", "content": system_prompt},
                                *session_data['messages']
                            ],
                            stream=True
                        )
                        
                        full_response = ""
                        for chunk in response:
                            if chunk.choices[0].delta.content is not None:
                                content = chunk.choices[0].delta.content
                                full_response += content
                                yield content
                                # 减少延迟，使输出更流畅
                                time.sleep(0.01)  # 控制输出速度
                        
                        # 保存AI回复
                        session_data['messages'].append({'role': 'assistant', 'content': full_response})
                        save_session(user_id, session_data)
                    else:
                        # 使用OpenAI客户端调用其他模型
                        response = client.chat.completions.create(
                            model=model_name,
                            messages=[
                                {"role": "system", "content": system_prompt},
                                *session_data['messages']
                            ],
                            stream=True
                        )
                        
                        full_response = ""
                        for chunk in response:
                            if chunk.choices[0].delta.content is not None:
                                content = chunk.choices[0].delta.content
                                full_response += content
                                yield content
                                # 减少延迟，使输出更流畅
                                time.sleep(0.01)  # 控制输出速度
                        
                        # 保存AI回复
                        session_data['messages'].append({'role': 'assistant', 'content': full_response})
                        save_session(user_id, session_data)
                except Exception as e:
                    print(f"流式输出错误: {str(e)}")
                    # 如果流式输出失败，尝试使用非流式输出
                    if model == 'glm-4.5-air' or model == 'glm-4.7':
                        # 使用ZhipuAiClient调用GLM模型
                        response = client.chat.completions.create(
                            model=model_name,
                            messages=[
                                {"role": "system", "content": system_prompt},
                                *session_data['messages']
                            ],
                            stream=False
                        )
                        
                        full_response = response.choices[0].message.content
                    else:
                        # 使用OpenAI客户端调用其他模型
                        response = client.chat.completions.create(
                            model=model_name,
                            messages=[
                                {"role": "system", "content": system_prompt},
                                *session_data['messages']
                            ],
                            stream=False
                        )
                        
                        full_response = response.choices[0].message.content
                    
                    # 模拟流式输出
                    for char in full_response:
                        yield char
                        time.sleep(0.01)
                    
                    # 保存AI回复
                    session_data['messages'].append({'role': 'assistant', 'content': full_response})
                    save_session(user_id, session_data)
            else:
                # 如果没有API密钥，使用增强的预设回复
                import re
                
                # 模式匹配
                if re.search(r'你好|嗨|Hello|hi', message, re.IGNORECASE):
                    reply = f'你好！我是{nick_name}，很高兴见到你！今天有什么可以帮助你的吗？'
                elif re.search(r'你是谁|你是什么', message, re.IGNORECASE):
                    reply = f'我是{nick_name}，你的AI智能伴侣，{character}。我可以陪你聊天、回答问题，或者只是倾听你的想法。'
                elif re.search(r'天气|温度', message, re.IGNORECASE):
                    reply = '抱歉，我目前还没有实时天气查询功能，但我可以陪你聊天！你最近过得怎么样？'
                elif re.search(r'时间|几点', message, re.IGNORECASE):
                    reply = f'当前时间是 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}，希望你今天过得愉快！'
                elif re.search(r'帮助|支持', message, re.IGNORECASE):
                    reply = '我可以陪你聊天，回答简单的问题，或者只是倾听你的想法。你有什么具体需要帮助的吗？'
                elif re.search(r'名字|称呼', message, re.IGNORECASE):
                    reply = f'你可以叫我{nick_name}，我随时准备为你服务！'
                elif re.search(r'再见|拜拜', message, re.IGNORECASE):
                    reply = '再见！期待下次和你聊天！'
                else:
                    # 通用回复
                    reply = f'我理解你说的"{message}"，这是一个很有趣的话题。你能告诉我更多关于这个的信息吗？'
                
                # 模拟流式输出
                for char in reply:
                    yield char
                    time.sleep(0.05)
                
                # 保存AI回复
                session_data['messages'].append({'role': 'assistant', 'content': reply})
                save_session(user_id, session_data)
        except Exception as e:
            # 打印详细错误信息
            print(f"模型调用错误 ({model}): {str(e)}")
            print(traceback.format_exc())
            
            # 如果API调用失败，使用备用回复
            error_reply = f'抱歉，我暂时无法连接到{model}服务，但我仍然可以陪你聊天！错误信息：{str(e)[:50]}...'
            for char in error_reply:
                yield char
                time.sleep(0.05)
            
            # 保存错误回复
            session_data['messages'].append({'role': 'assistant', 'content': error_reply})
            save_session(user_id, session_data)
    
    return Response(generate_response(), mimetype='text/plain')

@bp.route('/search')
def search():
    query = request.args.get('q', '')
    
    # 搜索文章标题和作者
    articles = Article.query.join(User).filter(
        (Article.title.like(f'%{query}%')) | 
        (User.username.like(f'%{query}%')),
        Article.status == 'published'
    ).order_by(Article.is_top.desc(), Article.created_at.desc()).all()
    
    categories = Category.query.all()
    tags = Tag.query.all()
    
    # 获取点赞数前十的文章
    from sqlalchemy import func, desc
    top_liked_articles = db.session.query(Article).join(article_like).filter(Article.status=='published').group_by(Article.id).order_by(func.count(article_like.c.user_id).desc()).limit(10).all()
    
    # 获取访问量前十的文章
    top_viewed_articles = Article.query.filter_by(status='published').order_by(Article.views.desc()).limit(10).all()
    
    return render_template('frontend/search_result.html', articles=articles, query=query, categories=categories, tags=tags, top_liked_articles=top_liked_articles, top_viewed_articles=top_viewed_articles)

@bp.route('/import_markdown', methods=['GET', 'POST'])
@login_required
def import_markdown():
    """
    批量导入Markdown文件
    """
    categories = Category.query.all()
    
    if request.method == 'POST':
        # 检查是否有文件上传
        if 'files' not in request.files:
            flash('请选择要导入的Markdown文件')
            return redirect(url_for('frontend.import_markdown'))
        
        files = request.files.getlist('files')
        category_id = int(request.form['category_id'])
        status = request.form['status']
        
        imported_count = 0
        
        for file in files:
            if file.filename.endswith('.md'):
                # 读取文件内容
                content = file.read().decode('utf-8')
                
                # 尝试从文件内容中提取标题
                # 查找第一个以#开头的行作为标题
                lines = content.split('\n')
                title = "无标题"
                for line in lines:
                    if line.startswith('# '):
                        title = line[2:].strip()
                        break
                
                # 转换Markdown为HTML
                content_html = markdown_to_html(content)
                
                # 创建文章
                article = Article(
                    title=title,
                    content=content,
                    content_html=content_html,
                    category_id=category_id,
                    user_id=current_user.id,
                    status=status
                )
                
                db.session.add(article)
                imported_count += 1
        
        db.session.commit()
        flash(f'成功导入 {imported_count} 篇文章')
        return redirect(url_for('frontend.my_articles'))
    
    return render_template('frontend/import_markdown.html', categories=categories)

@bp.route('/user/<int:user_id>')
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    
    # 检查个人主页是否公开
    if not user.profile_public and (not current_user.is_authenticated or current_user.id != user_id):
        flash('该用户的个人主页未公开', 'warning')
        return redirect(url_for('frontend.index'))
    
    # 获取用户发布的文章
    articles = Article.query.filter_by(user_id=user_id, status='published').order_by(Article.created_at.desc()).all()
    
    # 获取用户的统计数据
    total_articles = len(articles)
    total_comments = Comment.query.filter_by(author=user.username).count()
    total_likes = sum(article.like_count for article in articles)
    
    categories = Category.query.all()
    tags = Tag.query.all()
    
    # 获取点赞数前十的文章
    from sqlalchemy import func, desc
    top_liked_articles = db.session.query(Article).join(article_like).filter(Article.status=='published').group_by(Article.id).order_by(func.count(article_like.c.user_id).desc()).limit(10).all()
    
    # 获取访问量前十的文章
    top_viewed_articles = Article.query.filter_by(status='published').order_by(Article.views.desc()).limit(10).all()
    
    return render_template('frontend/user_profile.html', user=user, articles=articles, 
                         total_articles=total_articles, total_comments=total_comments, total_likes=total_likes,
                         categories=categories, tags=tags, top_liked_articles=top_liked_articles, top_viewed_articles=top_viewed_articles)

@bp.route('/personal_center')
@login_required
def personal_center():
    # 个人数据概览
    total_articles = Article.query.filter_by(user_id=current_user.id).count()
    total_published = Article.query.filter_by(user_id=current_user.id, status='published').count()
    total_drafts = Article.query.filter_by(user_id=current_user.id, status='draft').count()
    total_comments = Comment.query.filter_by(author=current_user.username).count()
    total_likes = sum(article.like_count for article in Article.query.filter_by(user_id=current_user.id).all())
    
    return render_template('frontend/personal_center.html', 
                         total_articles=total_articles,
                         total_published=total_published,
                         total_drafts=total_drafts,
                         total_comments=total_comments,
                         total_likes=total_likes)

@bp.route('/personal_articles')
@login_required
def personal_articles():
    # 文章管理
    status = request.args.get('status', 'all')
    
    if status == 'published':
        articles = Article.query.filter_by(user_id=current_user.id, status='published').order_by(Article.created_at.desc()).all()
    elif status == 'draft':
        articles = Article.query.filter_by(user_id=current_user.id, status='draft').order_by(Article.created_at.desc()).all()
    else:
        articles = Article.query.filter_by(user_id=current_user.id).order_by(Article.created_at.desc()).all()
    
    return render_template('frontend/personal_articles.html', articles=articles, status=status)

@bp.route('/personal_comments')
@login_required
def personal_comments():
    # 评论管理
    comments = Comment.query.filter_by(author=current_user.username).order_by(Comment.created_at.desc()).all()
    return render_template('frontend/personal_comments.html', comments=comments)

@bp.route('/personal_likes')
@login_required
def personal_likes():
    # 点赞管理
    liked_articles = current_user.liked_articles.filter_by(status='published').order_by(Article.created_at.desc()).all()
    return render_template('frontend/personal_likes.html', articles=liked_articles)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # 编辑资料
    if request.method == 'POST':
        current_user.nickname = request.form.get('nickname')
        current_user.email = request.form.get('email')
        current_user.bio = request.form.get('bio')
        current_user.profile_public = request.form.get('profile_public') == '1'
        db.session.commit()
        flash('个人资料已更新', 'success')
        return redirect(url_for('frontend.personal_center'))
    
    return render_template('frontend/edit_profile.html', user=current_user)

@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    # 修改密码
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not bcrypt.check_password_hash(current_user.password, old_password):
            flash('原密码错误', 'danger')
            return redirect(url_for('frontend.change_password'))
        
        if new_password != confirm_password:
            flash('两次输入的密码不一致', 'danger')
            return redirect(url_for('frontend.change_password'))
        
        current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()
        flash('密码已更新', 'success')
        return redirect(url_for('frontend.personal_center'))
    
    return render_template('frontend/change_password.html')

@bp.route('/delete_comment/<int:comment_id>')
@login_required
def delete_comment(comment_id):
    # 删除评论
    comment = Comment.query.get_or_404(comment_id)
    
    # 检查是否是评论作者
    if comment.author != current_user.username:
        flash('您没有权限删除这条评论', 'danger')
        return redirect(url_for('frontend.personal_comments'))
    
    db.session.delete(comment)
    db.session.commit()
    flash('评论已删除', 'success')
    return redirect(url_for('frontend.personal_comments'))

@bp.route('/account_deactivate', methods=['GET', 'POST'])
@login_required
def account_deactivate():
    # 账号注销
    if request.method == 'POST':
        password = request.form.get('password')
        
        if not bcrypt.check_password_hash(current_user.password, password):
            flash('密码错误', 'danger')
            return redirect(url_for('frontend.account_deactivate'))
        
        # 删除用户的所有数据
        # 删除用户的文章
        articles = Article.query.filter_by(user_id=current_user.id).all()
        for article in articles:
            # 删除文章的评论
            Comment.query.filter_by(article_id=article.id).delete()
            # 删除文章的访问记录
            Visit.query.filter_by(article_id=article.id).delete()
            # 删除文章的封面图
            if article.cover_image:
                import os
                image_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'images', article.cover_image)
                if os.path.exists(image_path):
                    os.remove(image_path)
            # 删除文章
            db.session.delete(article)
        
        # 删除用户的评论
        Comment.query.filter_by(author=current_user.username).delete()
        
        # 删除用户的点赞记录
        current_user.liked_articles.clear()
        
        # 删除用户
        user_id = current_user.id
        logout_user()
        user = User.query.get(user_id)
        db.session.delete(user)
        db.session.commit()
        
        flash('账号已注销', 'success')
        return redirect(url_for('frontend.index'))
    
    return render_template('frontend/account_deactivate.html')
