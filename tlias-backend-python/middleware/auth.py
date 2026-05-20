from functools import wraps
from flask import request, jsonify
from utils.jwt_util import verify_token


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)

        token = request.headers.get('token')
        if not token:
            return jsonify({'code': 0, 'msg': '未登录', 'data': None}), 401

        try:
            payload = verify_token(token)
            request.user_id = payload['userId']
            request.user_name = payload['name']
        except Exception:
            return jsonify({'code': 0, 'msg': '登录失效，请重新登录', 'data': None}), 401

        return f(*args, **kwargs)

    return decorated
