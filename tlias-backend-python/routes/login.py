from flask import Blueprint, request, jsonify
import bcrypt
from database import get_db
from utils.jwt_util import generate_token

login_bp = Blueprint('login', __name__)


@login_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'code': 0, 'msg': '用户名和密码不能为空', 'data': None})

    conn = get_db()
    emp = conn.execute('SELECT * FROM emp WHERE username = ?', (username,)).fetchone()
    conn.close()

    if not emp or not bcrypt.checkpw(password.encode(), emp['password'].encode()):
        return jsonify({'code': 0, 'msg': '用户名或密码错误', 'data': None})

    token = generate_token(emp['id'], emp['name'])
    return jsonify({'code': 1, 'msg': 'success', 'data': {'token': token, 'name': emp['name']}})
