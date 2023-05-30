from datetime import datetime
from sqlalchemy import Column, BigInteger, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

# 创建基础实体类
Base = declarative_base()


# 定义 Chat 模型
class Chat(Base):
    __tablename__ = 't_chat'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    user_id = Column(BigInteger, nullable=False, comment='用户id')
    type = Column(BigInteger, nullable=False, comment='对话类型')
    chat_q = Column(String(255), nullable=False, comment='问题')
    chat_a = Column(String(32), nullable=False, comment='回答')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'chat_q': self.chat_q,
            'chat_a': self.chat_a,
            'create_time': str(self.create_time),
            'update_time': str(self.update_time)
        }
