from star.business import Business
from sqlalchemy.dialects.mysql import pymysql
from sqlalchemy.orm import scoped_session, sessionmaker

from star.database import engine
from star.user import User

from star.user import User
from functools import wraps

# 创建 Session 工厂
session_factory = sessionmaker(autocommit=False, expire_on_commit=True)
session = scoped_session(session_factory)
session.configure(bind=engine)

class BusinessDAO:
    def __init__(self):
        self.session = session

    def add(self, business):
        try:
            self.session.add(business)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_by_user_id(self, user_id):
        return self.session.query(Business).filter_by(user_id=user_id).first()

    def update(self, business):
        with self.session.begin():
            self.session.merge(business)

    def update_count(self, user_id):
        business = self.session.query(Business).filter_by(user_id=user_id).first()
        business.count -= 1
        with self.session.begin():
            self.session.merge(business)
    def delete(self, business):
        try:
            self.session.delete(business)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e