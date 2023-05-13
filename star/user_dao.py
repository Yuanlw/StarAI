from sqlalchemy.orm import sessionmaker
from user import User

# 创建 Session 工厂
Session = sessionmaker()

# 定义 ORM 操作
class UserDAO:
    def __init__(self, engine):
        # 创建会话工厂
        Session.configure(bind=engine)
        self.session = Session()

 # 添加新用户
    def add(self, user):
        self.session.add(user)
        self.session.commit()

    # 根据 ID 查询用户
    def get_by_id(self, id):
        return self.session.query(User).filter_by(id=id).first()

    # 根据邮箱查询用户
    def get_list(self, mail=None, business_type=None):
        query = self.session.query(User)
        if mail:
            query = query.filter_by(mail=mail)
        if business_type is not None:
            query = query.filter_by(business_type=business_type)
        return query.all()

    # 更新用户信息
    def update(self, user):
        # 如果用户未与 Session 相关联，则使用 merge 方法重新关联
        if not self.session.is_active:
            user = self.session.merge(user)
        self.session.commit()

    # 删除用户
    def delete(self, user):
        self.session.delete(user)
        self.session.commit()