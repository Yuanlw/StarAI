from sqlalchemy.dialects.mysql import pymysql
from sqlalchemy.orm import scoped_session, sessionmaker

from star.database import engine
from star.user import User

from star.user import User
from functools import wraps
# 创建 Session 工厂
session_factory = sessionmaker(autocommit=False, expire_on_commit=True)


def reconnect(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except pymysql.err.OperationalError as e:
            # Error code 2013 represents "Lost connection to MySQL server during query"
            if e.args[0] == 2013:
                self = args[0]
                self.session.remove()
                self.session.configure(bind=engine)
                return func(*args, **kwargs)
            else:
                raise
    return wrapper


# 定义 UserDAO 操作类
class UserDAO:
    def __init__(self, engine):
        self.session = scoped_session(session_factory)
        self.session.configure(bind=engine)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.remove()

    # 添加新用户
    @reconnect
    def add(self, user):
        with self.session.begin():
            self.session.add(user)

    # 根据 ID 查询用户
    @reconnect
    def get_by_id(self, id):
        return self.session.query(User).filter_by(id=id).first()

    # 根据邮箱查询用户
    @reconnect
    def get_list(self, mail=None, business_type=None):
        query = self.session.query(User)
        if mail:
            query = query.filter_by(mail=mail)
        if business_type is not None:
            query = query.filter_by(business_type=business_type)
        return query.all()

    # 更新用户信息
    @reconnect
    def update(self, user):
        with self.session.begin():
            self.session.merge(user)

    # 删除用户
    @reconnect
    def delete(self, user):
        with self.session.begin():
            self.session.delete(user)

    # 关闭数据库会话

    def close(self):
        self.session.close()