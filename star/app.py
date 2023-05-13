import re
import random
import string
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from flask import Flask, jsonify, request, session
from sqlalchemy import create_engine, inspect
from functools import wraps
from star import logger
from star.chat_dao import ChatDAO
from star.chatgpt import chatGPT
from user import User
from user_dao import UserDAO
from star.logger import logger

# 创建 Flask 实例
app = Flask(__name__)

# 创建数据库引擎和 ORM 操作类
engine = create_engine('mysql+pymysql://root:root1234@127.0.0.1:3306/starAI')
user_dao = UserDAO(engine)
chat_dao = ChatDAO(engine)


# 登录状态检查装饰器
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 检查用户是否已经登录
        # 这里假设用户登录状态保存在session中
        if 'userid' not in session:
            return jsonify({'error': 'login required'}), 401

        id = session.get('userid')
        user = user_dao.get_by_id(id)
        if user is None:
            return jsonify({'error': 'login required'}), 401

        return func(*args, **kwargs)

    return wrapper


# 定义接口路由
@app.route('/starai/users', methods=['GET'])
@login_required
def list_users():
    # 解析请求参数
    # question=request.get_json();
    # logger.info(question);
    # q=question['question']
    name = request.get_json().get('name')
    mail = request.get_json().get('mail')
    business_type = request.get_json().get('business_type', None)
    if business_type is not None:
        business_type = int(business_type)
    # business_type = request.args.get('business_type', type=int, default=None)
    offset = request.get_json().get('offset', 0)
    if offset is not None:
        offset = int(offset)
    limit = request.get_json().get('limit', 10)
    if limit is not None:
        limit = int(limit)
    # offset = request.args.get('offset', type=int, default=0)
    # limit = request.args.get('limit', type=int, default=10)

    # 查询用户列表
    users = user_dao.get_list(mail=mail, business_type=business_type)

    # 返回结果
    # return jsonify([user.__dict__ for user in users])

    def to_dict(obj):
        return {c.key: getattr(obj, c.key)
                for c in inspect(obj).mapper.column_attrs}

    json_data = jsonify([to_dict(user) for user in users])
    return json_data


# 登录
@app.route('/starai/login', methods=['POST'])
def login():
    # 解析请求体
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    # 获取邮箱
    mail = data.get('mail')
    if not mail:
        return jsonify({'error': 'Mail is required'}), 400

    # 判断邮箱格式是否正确
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', mail):
        return jsonify({'error': 'Invalid mail format'}), 400

    # 判断邮箱是否已注册
    if user_dao.get_list(mail=mail):
        return jsonify({'error': 'Mail has been registered'}), 400

    # 生成密码
    password = ''.join(random.sample(string.ascii_letters + string.digits, 6))

    # 创建新用户
    name = mail.split('@')[0]
    user = User(name=name, user_password=password, mail=mail, business_type=0, create_time=datetime.now(),
                update_time=datetime.now())

    # 保存用户信息
    try:
        user_dao.add(user)
    except IntegrityError:
        return jsonify({'error': 'Mail has been registered'}), 400

    # 发送密码到邮箱
    # ... todo
    # logger.get_logger(user_password)
    logger.info(password)

    # 返回用户信息
    # 将对象转换为字典格式
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    return jsonify(as_dict(user))


# 根据ID 获取用户信息
@app.route('/starai/users', methods=['GET'])
@login_required
def get_user():
    id = session.get('userid')
    # 查询用户信息
    user = user_dao.get_by_id(id)

    # 判断用户是否存在
    if not user:
        return jsonify({'error': f'User with id={id} not found'}), 404

    # 返回结果
    return jsonify(user.__dict__)


# 根据ID 更新用户信息
@app.route('/starai/users/<int:id>', methods=['PUT'])
def update_user(id):
    # 查询用户信息
    user = user_dao.get_list(id)

    # 判断用户是否存在
    if not user:
        return jsonify({'error': f'User with id={id} not found'}), 404

    # 解析请求体
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400

    # 更新用户信息
    user = user_dao.update(id, data)

    # 返回结果
    return jsonify(user.__dict__)


# 生成回答接口
@app.route('/starai/question', methods=['POST'])
# @login_required
def answer():
    data = request.get_json()
    # user_id = session.get('userid')
    user_id = 123456789
    question = data.get('question')
    if not user_id or not question:
        return jsonify({"error": "user_id and question are required"}), 400

    # 敏感词过滤 TODO

    # answers = chatGPT(question)
    answers = "chatGPT(question)"
    chat_dao.add_conversation(user_id, question, answers)
    return jsonify({"answer": answers})


# 查询对话记录接口
@app.route('/starai/conversations', methods=['GET'])
# @login_required
def conversations():
    # user_id = session.get('userid')
    data = request.get_json()
    user_id = data.get('userId')
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    conversations = chat_dao.get_conversations_by_user(user_id, 0, 10)
    return jsonify({"conversations": conversations})
