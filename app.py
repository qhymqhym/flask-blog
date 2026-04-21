from flask import Flask
import os
import pymysql
pymysql.install_as_MySQLdb()
from extensions import db, bcrypt, login_manager, cache, session

# 配置
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'mysql://root:root@localhost/blog_db?charset=utf8mb4&connect_timeout=30&read_timeout=30&write_timeout=30')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'images')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # 数据库连接池配置
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_POOL_RECYCLE = 600  # 10分钟，更频繁地回收连接
    SQLALCHEMY_MAX_OVERFLOW = 5
    
    # Flask-WTF配置
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY', 'your-csrf-secret-key-here')
    
    # 会话配置
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = 3600  # 1小时

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# 应用工厂模式
def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # 初始化扩展
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    session.init_app(app)
    cache.init_app(app)
    login_manager.login_view = 'frontend.login'
    
    # 注册错误处理
    register_error_handlers(app)
    
    # 添加请求前处理函数，确保数据库连接有效
    @app.before_request
    def before_request():
        try:
            # 尝试执行一个简单的查询来检查连接是否有效
            db.session.execute('SELECT 1')
        except Exception as e:
            # 如果连接无效，重新创建连接
            print(f"数据库连接无效，重新连接: {str(e)}")
            db.session.rollback()
            db.session.close()
            # 重新绑定引擎
            from sqlalchemy import create_engine
            engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
            db.session.bind = engine
    
    # 导入模型
    from models import User, Article, Category, Tag, Comment, Visit
    
    # 导入路由
    from routes import frontend, admin
    app.register_blueprint(frontend.bp)
    app.register_blueprint(admin.bp, url_prefix='/admin')
    
    return app

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def server_error(e):
        return {'error': 'Internal server error'}, 500

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    app.run()
