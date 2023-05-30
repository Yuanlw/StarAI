import pymysql
import datetime
from sqlalchemy.dialects.mysql import pymysql
from sqlalchemy.orm import scoped_session, sessionmaker
from concurrent.futures import ThreadPoolExecutor
from star.chat import Chat
from functools import wraps
from star.database import engine

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


# 定义 ChatDAO 操作类
class ChatDAO:
    def __init__(self, engine):
        # 创建会话工厂
        self.session = scoped_session(session_factory)
        self.session.configure(bind=engine)
        # 重用会话对象，每个请求只创建一个会话对象

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.remove()

    # 添加对话记录
    @reconnect
    def add_conversation(self, user_id, question, answer, type):
        chat = Chat(user_id=user_id, chat_q=question, chat_a=answer, type=type)
        with ThreadPoolExecutor(max_workers=5) as executor:
            future = executor.submit(self.session.add, chat)
            future.result()
            future = executor.submit(self.session.commit)
            future.result()

    # 查询对话记录(默认type=0)
    @reconnect
    def get_conversations_by_user(self, user_id, offset=0, limit=10):
        with ThreadPoolExecutor(max_workers=5) as executor:
            future = executor.submit(
                self.session.query(Chat).filter_by(user_id=user_id, type=0).order_by(Chat.create_time.desc()).offset(
                    offset).limit(limit).all)
            chats = future.result()
        return [chat.to_dict() for chat in chats]

    # 删除历史记录
    @reconnect
    def del_conversations_by_user(self, user_id):
        chats = self.session.query(Chat).filter(Chat.user_id == user_id)
        if chats:
            with ThreadPoolExecutor(max_workers=5) as executor:
                future = executor.submit(self.session.query(Chat).filter(Chat.user_id == user_id))
                chats = future.result()
                for chat in chats:
                    future = executor.submit(self.session.delete, chat)
                    future.result()
                future = executor.submit(self.session.commit)
                future.result()

        # 关闭数据库会话

    def close(self):
        self.session.close()
