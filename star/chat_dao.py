import pymysql
import datetime
from sqlalchemy.orm import sessionmaker
from concurrent.futures import ThreadPoolExecutor
from star.chat import Chat


# 创建 Session 工厂
Session = sessionmaker()


# 定义 ChatDAO 操作类
class ChatDAO:
    def __init__(self, engine):
        # 创建会话工厂
        Session.configure(bind=engine)
        self.session = Session()

    # 添加对话记录
    def add_conversation(self, user_id, question, answer):
        chat = Chat(user_id=user_id, chat_q=question, chat_a=answer)
        with ThreadPoolExecutor(max_workers=5) as executor:
            future = executor.submit(self.session.add, chat)
            future.result()
            future = executor.submit(self.session.commit)
            future.result()

    # 查询对话记录
    def get_conversations_by_user(self, user_id, offset=0, limit=10):
        with ThreadPoolExecutor(max_workers=5) as executor:
            future = executor.submit(self.session.query(Chat).filter_by(user_id=user_id).order_by(Chat.create_time.desc()).offset(offset).limit(limit).all)
            chats = future.result()
        return [chat.to_dict() for chat in chats]


