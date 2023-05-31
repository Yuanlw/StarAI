from datetime import datetime

from sqlalchemy import Column, BigInteger, String, DateTime, Integer, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from star.snowflakeGenerator import SnowflakeGenerator

Base = declarative_base()

#实体
class Business(Base):
    __tablename__ = 't_business'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键')
    user_id = Column(BigInteger, nullable=False, default=0, comment='用户ID')
    count = Column(Integer, nullable=False, default=0, comment='次数')
    business_type = Column(Integer, nullable=False, default=1, comment='类型,1默认捐赠; 2月度;3年度;')
    pay_time = Column(DateTime, nullable=False, comment='支付时间')
    pay_money = Column(DECIMAL(10, 0), nullable=False, comment='支付金额')
    activity_time = Column(DateTime, nullable=False, comment='有效时间')
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def as_dict(self):
        return {'id': str(self.id), 'count': self.count, 'activity_time': self.activity_time}
