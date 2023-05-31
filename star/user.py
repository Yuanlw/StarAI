from datetime import datetime

from sqlalchemy import Column, BigInteger, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from star.snowflakeGenerator import SnowflakeGenerator
import hashlib
import os

# 创建基础实体类
Base = declarative_base()

# 创建 Snowflake ID 生成器
generator = SnowflakeGenerator(datacenter_id=0, worker_id=0)




# 定义用户实体类
class User(Base):
    __tablename__ = 't_user'

    id = Column(BigInteger, primary_key=True, default=generator.generate_id, comment='主键ID')
    name = Column(String(50), nullable=False, default='', comment='用户名')
    user_password = Column(String(100), default='', comment='密码')
    mail = Column(String(100), nullable=False, default='', comment='邮箱')
    business_type = Column(Integer, nullable=False, default=0, comment='商业类型（0:免费 1:付费）')
    count = Column(Integer, nullable=False, default=100, comment='次数')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate='CURRENT_TIMESTAMP',
                         comment='更新时间')

    def as_dict(self):
        return {'id': str(self.id), 'name': self.name}

    def __repr__(self):
        return f'<User {self.id}: {self.name}>'
    #
