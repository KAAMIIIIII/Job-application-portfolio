from flask import Flask, jsonify
from flask_cors import CORS
from database import init_db

app = Flask(__name__)
CORS(app)

# 初始化数据库（建表 + 默认管理员）
init_db()

# 注册路由 Blueprint
from routes.login import login_bp
from routes.dept import dept_bp
from routes.emp import emp_bp
from routes.clazz import clazz_bp
from routes.student import student_bp
from routes.report import report_bp

app.register_blueprint(login_bp)
app.register_blueprint(dept_bp)
app.register_blueprint(emp_bp)
app.register_blueprint(clazz_bp)
app.register_blueprint(student_bp)
app.register_blueprint(report_bp)


@app.errorhandler(Exception)
def handle_error(err):
    return jsonify({'code': 0, 'msg': str(err) or '服务器内部错误', 'data': None}), 500


if __name__ == '__main__':
    print('后端服务已启动: http://localhost:8080')
    print('默认管理员: admin / admin123')
    app.run(host='0.0.0.0', port=8080, debug=False)
