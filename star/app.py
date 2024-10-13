import asyncio
import re
import random
import string
import jieba
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from flask import Flask, jsonify, request, session, render_template
from sqlalchemy import create_engine, inspect, event
from functools import wraps
from star.logger import logger
from star.chat_dao import ChatDAO
from star.chatgpt import chatGPT
from star.mail_util import send_mail
from star.password_util import encrypt_password, check_password
from star.user import User
from star.user_dao import UserDAO
from star.logger import logger
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, current_user, get_jwt_identity
from datetime import timedelta
from star.database import engine

# from flask_cors import CORS

# 创建 Flask 实例
app = Flask(__name__)

user_dao = UserDAO(engine)
chat_dao = ChatDAO(engine)

# 设置JWT secret key
app.config["JWT_SECRET_KEY"] = "my_secret_key_star_ai_"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=720)


# 初始化JWTManager
jwt = JWTManager(app)

with open('sensitive_words.txt') as f:
    sensitive_words = f.read().splitlines()


@app.route("/starai/login", methods=["POST"])
def login():
    userId = request.json.get("userId", None)
    password = request.json.get("password", None)

    # 对用户名和密码进行验证，这里简单起见不做演示
    user = user_dao.get_by_id(userId)
    check = check_password(password, user.user_password)
    logger.info(check)
    # if not check:
    #     return jsonify({'error': 'login required'}), 401
    if user is None:
        return jsonify({'error': 'login required'}), 401
    # 如果验证成功，就创建一个JWT token
    access_token = create_access_token(identity=userId)

    # 返回token
    return jsonify(access_token=access_token)


# 登录
@app.route('/starai/register', methods=['POST'])
def register():
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
    reUser = user_dao.get_list(mail=mail)
    if reUser:
        user_dict = reUser.__getitem__(0).as_dict()
        return jsonify(user_dict), 200

    # 生成密码
    password = ''.join(random.sample(string.ascii_letters + string.digits, 6))

    # 创建新用户
    name = mail.split('@')[0]
    # 发送密码到邮箱
    send_status = send_mail(mail, password)
    if not send_status:
        return jsonify({'error': 'Failed to send mail'}), 500

    # 密码加密
    hashed = encrypt_password(password)
    user = User(name=name, user_password=hashed, mail=mail, business_type=0, create_time=datetime.now(),
                update_time=datetime.now())
    # 保存用户信息
    try:
        user_dao.add(user)
    except IntegrityError:
        return jsonify({'error': 'Mail has been registered'}), 400

    logger.info(password)

    # 返回用户信息
    # # 将对象转换为字典格式
    # def as_dict(self):
    #     return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    user_dict = user.as_dict()
    return jsonify(user_dict), 200


# 根据ID 获取用户信息
@app.route('/starai/user', methods=['GET'])
@jwt_required()
def get_user():
    # 获取JWT token中的身份信息
    user_id = get_jwt_identity()
    logger.info(user_id)
    # 查询用户信息
    user = user_dao.get_by_id(user_id)

    # 判断用户是否存在
    if not user:
        return jsonify({'error': f'User with id={id} not found'}), 404

    # 返回结果
    return jsonify(user.__dict__)


# 生成回答接口

@app.route('/starai/question', methods=['POST'])
@jwt_required()
async def question():
    # user_id = session.get('userid')
    # user_id = 123456789
    # 获取JWT token中的身份信息
    user_id = get_jwt_identity()
    logger.info(user_id)
    # user_id = current_user.get('userId')
    data = request.get_json()
    question = data.get('question')
    # user_id = data.get('user_id')
    if not user_id or not question:
        return jsonify({"error": "user_id and question are required"}), 400
    #
    # # 敏感词过滤
    if contains_sensitive_words(question):
        return jsonify({"answer": "含有敏感词"})
    #
    answers = chatGPT(question)
    awaitable = asyncio.ensure_future(answers)  # 包装为awaitable对象
    await awaitable  # 等待协程完成
    result = awaitable.result()  # 获取返回值
    # answers = "chatGPT(question)"
    chat_dao.add_conversation(user_id, question, result, 0)
    return jsonify({"answer": result})


# 查询对话记录接口

@app.route('/starai/clean', methods=['POST'])
@jwt_required()
def clean():
    # user_id = session.get('userid')
    user_id = get_jwt_identity()
    logger.info(user_id)
    data = request.get_json()
    logger.info(request)
    # userId = current_user.get('userId')
    # logger.info(userId)
    # user_id = data.get('userId')
    logger.info(user_id)
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    chat_dao.del_conversations_by_user(user_id)
    return jsonify({
        "success": True,
        "code": 200,
        "message": "成功"
    })


@app.route('/starai/conversations', methods=['GET'])
@jwt_required()
def conversations():
    # user_id = session.get('userid')
    # data = request.get_json()
    user_id = get_jwt_identity()
    logger.info(user_id)
    # user_id = current_user.get('userId')
    logger.info(user_id)
    # user_id = request.args.get('userId')
    logger.info(user_id)
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    conversations = chat_dao.get_conversations_by_user(user_id, 0, 10)
    return jsonify({"conversations": conversations})


@app.route('/starai/ask', methods=['POST'])
# @jwt_required()
async def ask():
    data = request.get_json()
    question = data.get('ask')
    words = jieba.cut(question)
    for word in words:
        if word in sensitive_words:
            return jsonify({'敏感词': True})
    answers = chatGPT(question)
    awaitable = asyncio.ensure_future(answers)  # 包装为awaitable对象
    await awaitable  # 等待协程完成
    result = awaitable.result()  # 获取返回值
    # answers = "chatGPT(question)"
    # chat_dao.add_conversation(user_id, question, result)
    return jsonify({"answer": result})


def contains_sensitive_words(text):
    words = jieba.cut(text)
    for word in words:
        if word in sensitive_words:
            return True
    return False


# 指定为用户查找回调函数
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data['sub']
    return user_dao.get_by_id(identity)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001, use_reloader=False)
