from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import User, Article, Category, Tag, Comment, Visit, article_like
from extensions import db, bcrypt, cache
from utils.markdown import markdown_to_html
from forms import LoginForm
from datetime import datetime
import os

bp = Blueprint('admin', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    管理员登录
    """
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password) and username == 'admin':
            login_user(user, remember=form.remember.data)
            return redirect(url_for('admin.dashboard'))
        flash('用户名或密码错误')
    return render_template('admin/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('frontend.login'))

@bp.route('/dashboard')
@login_required
@cache.cached(timeout=300, key_prefix='admin_dashboard')
def dashboard():
    if current_user.username != 'admin':
        logout_user()
        flash('Access denied. Only admin can access the admin panel.')
        return redirect(url_for('admin.login'))
    articles = Article.query.count()
    categories = Category.query.count()
    tags = Tag.query.count()
    comments = Comment.query.count()
    users = User.query.count()
    total_visits = Visit.query.count()
    return render_template('admin/dashboard.html', articles=articles, categories=categories, tags=tags, comments=comments, users=users, total_visits=total_visits)

# 文章管理
@bp.route('/articles')
@login_required
def articles():
    if current_user.username != 'admin':
        logout_user()
        flash('Access denied. Only admin can access the admin panel.')
        return redirect(url_for('admin.login'))
    
    query = request.args.get('q', '')
    if query:
        articles = Article.query.join(User).filter(
            (Article.title.like(f'%{query}%')) | 
            (User.username.like(f'%{query}%'))
        ).order_by(Article.is_top.desc(), Article.created_at.desc()).all()
    else:
        articles = Article.query.order_by(Article.is_top.desc(), Article.created_at.desc()).all()
    
    return render_template('admin/articles.html', articles=articles, query=query)

@bp.route('/article/create', methods=['GET', 'POST'])
@login_required
def create_article():
    if current_user.username != 'admin':
        logout_user()
        flash('Access denied. Only admin can access the admin panel.')
        return redirect(url_for('admin.login'))
    categories = Category.query.all()
    tags = Tag.query.all()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category_id = int(request.form['category_id'])
        tag_ids = request.form.getlist('tags')
        status = request.form['status']
        is_top = request.form.get('is_top') == 'on'
        
        # 处理封面图上传
        cover_image = None
        if 'cover' in request.files:
            file = request.files['cover']
            if file.filename:
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
            is_top=is_top,
            cover_image=cover_image
        )
        
        # 添加标签
        for tag_id in tag_ids:
            tag = Tag.query.get(int(tag_id))
            article.tags.append(tag)
        
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('admin.articles'))
    return render_template('admin/create_article.html', categories=categories, tags=tags)

@bp.route('/article/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_article(id):
    if current_user.username != 'admin':
        logout_user()
        flash('Access denied. Only admin can access the admin panel.')
        return redirect(url_for('admin.login'))
    article = Article.query.get_or_404(id)
    categories = Category.query.all()
    tags = Tag.query.all()
    if request.method == 'POST':
        article.title = request.form['title']
        article.content = request.form['content']
        # 转换Markdown为HTML
        article.content_html = markdown_to_html(article.content)
        article.category_id = int(request.form['category_id'])
        article.status = request.form['status']
        article.is_top = request.form.get('is_top') == 'on'
        
        # 处理封面图上传
        if 'cover' in request.files:
            file = request.files['cover']
            if file.filename:
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
        return redirect(url_for('admin.articles'))
    return render_template('admin/edit_article.html', article=article, categories=categories, tags=tags)

@bp.route('/article/delete/<int:id>')
@login_required
def delete_article(id):
    if current_user.username != 'admin':
        logout_user()
        flash('Access denied. Only admin can access the admin panel.')
        return redirect(url_for('admin.login'))
    article = Article.query.get_or_404(id)
    # 删除相关的访问记录
    Visit.query.filter_by(article_id=id).delete()
    # 删除封面图
    if article.cover_image:
        image_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'images')
        image_path = os.path.join(image_dir, article.cover_image)
        if os.path.exists(image_path):
            os.remove(image_path)
    db.session.delete(article)
    db.session.commit()
    return redirect(url_for('admin.articles'))

@bp.route('/article/top/<int:id>')
@login_required
def toggle_top(id):
    if current_user.username != 'admin':
        logout_user()
        flash('Access denied. Only admin can access the admin panel.')
        return redirect(url_for('admin.login'))
    article = Article.query.get_or_404(id)
    article.is_top = not article.is_top
    db.session.commit()
    return redirect(url_for('admin.articles'))

# 分类管理
@bp.route('/categories')
@login_required
def categories():
    if current_user.username != 'admin':
        logout_user()
        flash('Access denied. Only admin can access the admin panel.')
        return redirect(url_for('admin.login'))
    
    query = request.args.get('q', '')
    if query:
        categories = Category.query.filter(
            Category.name.like(f'%{query}%')
        ).all()
    else:
        categories = Category.query.all()
    
    return render_template('admin/categories.html', categories=categories, query=query)

@bp.route('/category/create', methods=['GET', 'POST'])
@login_required
def create_category():
    if current_user.username != 'admin':
        logout_user()
        flash('Access denied. Only admin can access the admin panel.')
        return redirect(url_for('admin.login'))
    if request.method == 'POST':
        name = request.form['name']
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        return redirect(url_for('admin.categories'))
    return render_template('admin/create_category.html')

@bp.route('/category/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    if current_user.username != 'admin':
        logout_user()
        flash('Access denied. Only admin can access the admin panel.')
        return redirect(url_for('admin.login'))
    category = Category.query.get_or_404(id)
    if request.method == 'POST':
        category.name = request.form['name']
        db.session.commit()
        return redirect(url_for('admin.categories'))
    return render_template('admin/edit_category.html', category=category)

@bp.route('/category/delete/<int:id>')
@login_required
def delete_category(id):
    if current_user.username != 'admin':
        logout_user()
        flash('Access denied. Only admin can access the admin panel.')
        return redirect(url_for('admin.login'))
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('admin.categories'))

# 标签管理
@bp.route('/tags')
@login_required
def tags():
    if current_user.username != 'admin':
        logout_user()
        flash('Access denied. Only admin can access the admin panel.')
        return redirect(url_for('admin.login'))
    
    query = request.args.get('q', '')
    if query:
        tags = Tag.query.filter(
            Tag.name.like(f'%{query}%')
        ).all()
    else:
        tags = Tag.query.all()
    
    return render_template('admin/tags.html', tags=tags, query=query)

@bp.route('/tag/create', methods=['GET', 'POST'])
@login_required
def create_tag():
    if current_user.username != 'admin':
        logout_user()
        flash('Access denied. Only admin can access the admin panel.')
        return redirect(url_for('admin.login'))
    if request.method == 'POST':
        name = request.form['name']
        tag = Tag(name=name)
        db.session.add(tag)
        db.session.commit()
        return redirect(url_for('admin.tags'))
    return render_template('admin/create_tag.html')

@bp.route('/tag/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_tag(id):
    if current_user.username != 'admin':
        logout_user()
        flash('Access denied. Only admin can access the admin panel.')
        return redirect(url_for('admin.login'))
    tag = Tag.query.get_or_404(id)
    if request.method == 'POST':
        tag.name = request.form['name']
        db.session.commit()
        return redirect(url_for('admin.tags'))
    return render_template('admin/edit_tag.html', tag=tag)

@bp.route('/tag/delete/<int:id>')
@login_required
def delete_tag(id):
    if current_user.username != 'admin':
        logout_user()
        flash('Access denied. Only admin can access the admin panel.')
        return redirect(url_for('admin.login'))
    tag = Tag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    return redirect(url_for('admin.tags'))

# 用户管理
@bp.route('/users')
@login_required
def users():
    if current_user.username != 'admin':
        logout_user()
        flash('Access denied. Only admin can access the admin panel.')
        return redirect(url_for('admin.login'))
    
    query = request.args.get('q', '')
    if query:
        users = User.query.filter(
            User.username.like(f'%{query}%')
        ).all()
    else:
        users = User.query.all()
    
    return render_template('admin/users.html', users=users, query=query)

@bp.route('/user/create', methods=['GET', 'POST'])
@login_required
def create_user():
    if current_user.username != 'admin':
        logout_user()
        flash('Access denied. Only admin can access the admin panel.')
        return redirect(url_for('admin.login'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('admin.create_user'))
        
        # 创建新用户
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('admin.users'))
    return render_template('admin/create_user.html')

@bp.route('/user/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if current_user.username != 'admin':
        logout_user()
        flash('Access denied. Only admin can access the admin panel.')
        return redirect(url_for('admin.login'))
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 检查用户名是否已存在（排除当前用户）
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != id:
            flash('Username already exists')
            return redirect(url_for('admin.edit_user', id=id))
        
        # 更新用户信息
        user.username = username
        if password:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user.password = hashed_password
        db.session.commit()
        return redirect(url_for('admin.users'))
    return render_template('admin/edit_user.html', user=user)

@bp.route('/user/delete/<int:id>')
@login_required
def delete_user(id):
    if current_user.username != 'admin':
        logout_user()
        flash('Access denied. Only admin can access the admin panel.')
        return redirect(url_for('admin.login'))
    user = User.query.get_or_404(id)
    # 不允许删除admin用户
    if user.username == 'admin':
        flash('Cannot delete admin user')
        return redirect(url_for('admin.users'))
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin.users'))

# 评论管理
@bp.route('/comments')
@login_required
def comments():
    if current_user.username != 'admin':
        logout_user()
        flash('Access denied. Only admin can access the admin panel.')
        return redirect(url_for('admin.login'))
    
    query = request.args.get('q', '')
    if query:
        comments = Comment.query.filter(
            Comment.content.like(f'%{query}%')
        ).order_by(Comment.created_at.desc()).all()
    else:
        comments = Comment.query.order_by(Comment.created_at.desc()).all()
    
    return render_template('admin/comments.html', comments=comments, query=query)

@bp.route('/comment/approve/<int:id>')
@login_required
def approve_comment(id):
    if current_user.username != 'admin':
        logout_user()
        flash('Access denied. Only admin can access the admin panel.')
        return redirect(url_for('admin.login'))
    comment = Comment.query.get_or_404(id)
    comment.status = 'approved'
    db.session.commit()
    return redirect(url_for('admin.comments'))

@bp.route('/comment/delete/<int:id>')
@login_required
def delete_comment(id):
    if current_user.username != 'admin':
        logout_user()
        flash('Access denied. Only admin can access the admin panel.')
        return redirect(url_for('admin.login'))
    comment = Comment.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('admin.comments'))

# 访问统计
@bp.route('/stats')
@login_required
def stats():
    if current_user.username != 'admin':
        logout_user()
        flash('Access denied. Only admin can access the admin panel.')
        return redirect(url_for('admin.login'))
    from sqlalchemy import func, desc
    
    # 总访问量
    total_visits = Visit.query.count()
    
    # 按日期统计访问量
    daily_visits = []
    try:
        result = db.session.query(
            func.date(Visit.created_at).label('date'),
            func.count(Visit.id).label('count')
        ).group_by(func.date(Visit.created_at)).order_by(func.date(Visit.created_at)).all()
        if result:
            daily_visits = result
    except:
        pass
    
    # 按文章统计访问量
    article_visits = []
    try:
        result = db.session.query(
            Article.id,
            Article.title,
            func.count(Visit.id).label('visit_count')
        ).join(Visit).group_by(Article.id).order_by(desc('visit_count')).limit(10).all()
        if result:
            article_visits = result
    except:
        pass
    
    # 按分类统计文章数
    category_article_count = []
    try:
        result = db.session.query(
            Category.name,
            func.count(Article.id).label('count')
        ).join(Article).group_by(Category.name).all()
        if result:
            category_article_count = result
    except:
        pass
    
    # 按标签统计文章数
    tag_article_count = []
    try:
        result = db.session.query(
            Tag.name,
            func.count(Article.id).label('count')
        ).join(Article.tags).group_by(Tag.name).order_by(desc('count')).limit(10).all()
        if result:
            tag_article_count = result
    except:
        pass
    
    # 按文章统计点赞数
    article_likes = []
    try:
        result = db.session.query(
            Article.id,
            Article.title,
            func.count(article_like.c.user_id).label('like_count')
        ).join(article_like).group_by(Article.id).order_by(desc('like_count')).limit(10).all()
        if result:
            article_likes = result
    except:
        pass
    
    return render_template('admin/stats.html', 
                         total_visits=total_visits,
                         daily_visits=daily_visits,
                         article_visits=article_visits,
                         category_article_count=category_article_count,
                         tag_article_count=tag_article_count,
                         article_likes=article_likes)

# 搜索功能
@bp.route('/search')
@login_required
def search():
    if current_user.username != 'admin':
        logout_user()
        flash('Access denied. Only admin can access the admin panel.')
        return redirect(url_for('admin.login'))
    
    query = request.args.get('q', '')
    
    # 搜索文章
    articles = Article.query.filter(
        Article.title.like(f'%{query}%') | 
        Article.content.like(f'%{query}%')
    ).all()
    
    # 搜索用户
    users = User.query.filter(
        User.username.like(f'%{query}%')
    ).all()
    
    # 搜索分类
    categories = Category.query.filter(
        Category.name.like(f'%{query}%')
    ).all()
    
    # 搜索标签
    tags = Tag.query.filter(
        Tag.name.like(f'%{query}%')
    ).all()
    
    # 搜索评论
    comments = Comment.query.filter(
        Comment.content.like(f'%{query}%')
    ).all()
    
    return render_template('admin/search_result.html', 
                         query=query,
                         articles=articles,
                         users=users,
                         categories=categories,
                         tags=tags,
                         comments=comments)
