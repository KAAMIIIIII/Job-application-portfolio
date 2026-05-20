import os
import uuid
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from database import get_db
from middleware.auth import auth_required
from utils.camelize import camelize

dept_bp = Blueprint('dept', __name__)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXT = {'zip', 'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'rar', '7z'}


def _save_file(file) -> tuple:
    """保存上传文件，返回 (file_path, file_name)"""
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_EXT:
        raise ValueError(f'不支持的文件格式: .{ext}')
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f'{uuid.uuid4().hex}.{ext}'
    file.save(os.path.join(UPLOAD_DIR, filename))
    return filename, file.filename


@dept_bp.route('/depts/file/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=False)


@dept_bp.route('/depts', methods=['GET'])
@auth_required
def query_all():
    conn = get_db()
    rows = conn.execute('SELECT * FROM dept ORDER BY update_time DESC').fetchall()
    conn.close()
    return jsonify({'code': 1, 'msg': 'success', 'data': camelize([dict(r) for r in rows])})


@dept_bp.route('/depts/<int:id>', methods=['GET'])
@auth_required
def query_by_id(id):
    conn = get_db()
    row = conn.execute('SELECT * FROM dept WHERE id = ?', (id,)).fetchone()
    conn.close()
    return jsonify({'code': 1, 'msg': 'success', 'data': camelize(dict(row)) if row else None})


@dept_bp.route('/depts', methods=['POST'])
@auth_required
def add():
    name = request.form.get('name', '')
    url = request.form.get('url', '')
    file = request.files.get('file')

    if not url and not file:
        return jsonify({'code': 0, 'msg': '链接和本地文件至少填写一项', 'data': None})

    file_path = ''
    file_name = ''
    if file:
        try:
            file_path, file_name = _save_file(file)
        except ValueError as e:
            return jsonify({'code': 0, 'msg': str(e), 'data': None})

    conn = get_db()
    cur = conn.execute(
        'INSERT INTO dept (name, url, file_path, file_name) VALUES (?, ?, ?, ?)',
        (name, url, file_path, file_name)
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return jsonify({'code': 1, 'msg': 'success', 'data': {'id': new_id}})


@dept_bp.route('/depts', methods=['PUT'])
@auth_required
def update():
    id_val = request.form.get('id', '')
    name = request.form.get('name', '')
    url = request.form.get('url', '')
    file = request.files.get('file')
    keep_file = request.form.get('keepFile', '1')  # 未上传新文件时保留旧文件

    if not url and not file and keep_file == '0':
        return jsonify({'code': 0, 'msg': '链接和本地文件至少填写一项', 'data': None})

    conn = get_db()

    if file:
        try:
            file_path, file_name = _save_file(file)
        except ValueError as e:
            conn.close()
            return jsonify({'code': 0, 'msg': str(e), 'data': None})
        conn.execute(
            "UPDATE dept SET name=?, url=?, file_path=?, file_name=?, update_time=datetime('now','localtime') WHERE id=?",
            (name, url, file_path, file_name, id_val)
        )
    elif keep_file == '0':
        conn.execute(
            "UPDATE dept SET name=?, url=?, file_path=?, file_name=?, update_time=datetime('now','localtime') WHERE id=?",
            (name, url, '', '', id_val)
        )
    else:
        conn.execute(
            "UPDATE dept SET name=?, url=?, update_time=datetime('now','localtime') WHERE id=?",
            (name, url, id_val)
        )

    conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': 'success', 'data': None})


@dept_bp.route('/depts', methods=['DELETE'])
@auth_required
def delete():
    conn = get_db()
    # 删除前获取文件路径
    row = conn.execute('SELECT file_path FROM dept WHERE id = ?', (request.args.get('id'),)).fetchone()
    if row and row['file_path']:
        filepath = os.path.join(UPLOAD_DIR, row['file_path'])
        if os.path.exists(filepath):
            os.remove(filepath)
    conn.execute('DELETE FROM dept WHERE id = ?', (request.args.get('id'),))
    conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': 'success', 'data': None})
