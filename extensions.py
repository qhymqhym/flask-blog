from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_session import Session

# 初始化扩展
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
session = Session()

# 初始化缓存
cache = Cache(config={
    'CACHE_TYPE': 'simple',  # 简单内存缓存，生产环境建议使用 Redis
    'CACHE_DEFAULT_TIMEOUT': 300  # 默认缓存时间 5 分钟
})
