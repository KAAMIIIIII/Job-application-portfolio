from flask import Blueprint, request, jsonify
import bcrypt
from database import get_db
from middleware.auth import auth_required
from utils.camelize import camelize

emp_bp = Blueprint('emp', __name__)


@emp_bp.route('/emps/list', methods=['GET'])
@auth_required
def list_all():
    conn = get_db()
    rows = conn.execute(
        'SELECT id, username, name, gender, phone, job, update_time FROM emp ORDER BY update_time DESC'
    ).fetchall()
    conn.close()
    return jsonify({'code': 1, 'msg': 'success', 'data': camelize([dict(r) for r in rows])})


@emp_bp.route('/emps', methods=['GET'])
@auth_required
def query_page():
    name = request.args.get('name', '')
    gender = request.args.get('gender')
    begin = request.args.get('begin', '')
    end = request.args.get('end', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 10))

    where = 'WHERE 1=1'
    params = []

    if name:
        where += ' AND e.name LIKE ?'
        params.append(f'%{name}%')
    if gender:
        where += ' AND e.gender = ?'
        params.append(int(gender))
    if begin:
        where += ' AND e.update_time >= ?'
        params.append(begin)
    if end:
        where += ' AND e.update_time <= ?'
        params.append(end)

    conn = get_db()

    # 总数
    total = conn.execute(
        f'SELECT COUNT(*) AS total FROM emp e {where}', params
    ).fetchone()[0]

    # 列表：关联班级名称和学生总数
    sql = f'''
        SELECT e.id, e.username, e.name, e.gender, e.phone, e.job, e.update_time,
            GROUP_CONCAT(c.name, '、') AS clazz_names,
            COALESCE(SUM(stud.cnt), 0) AS total_students
        FROM emp e
        LEFT JOIN clazz c ON c.master_id = e.id
        LEFT JOIN (SELECT clazz_id, COUNT(*) AS cnt FROM student GROUP BY clazz_id) stud
            ON stud.clazz_id = c.id
        {where}
        GROUP BY e.id
        ORDER BY e.update_time DESC
        LIMIT ? OFFSET ?
    '''
    params.extend([page_size, (page - 1) * page_size])
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    data = camelize([dict(r) for r in rows])
    return jsonify({
        'code': 1, 'msg': 'success',
        'data': {'rows': data, 'total': total}
    })


@emp_bp.route('/emps/<int:id>', methods=['GET'])
@auth_required
def query_by_id(id):
    conn = get_db()
    row = conn.execute(
        'SELECT id, username, name, gender, phone, job, update_time FROM emp WHERE id = ?', (id,)
    ).fetchone()
    conn.close()
    return jsonify({'code': 1, 'msg': 'success', 'data': camelize(dict(row)) if row else None})


@emp_bp.route('/emps', methods=['POST'])
@auth_required
def add():
    data = request.get_json()
    password = data.get('password', '123456')
    hash_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt(10)).decode()
    conn = get_db()
    cur = conn.execute(
        'INSERT INTO emp (username, password, name, gender, phone, job) VALUES (?, ?, ?, ?, ?, ?)',
        (data['username'], hash_pw, data['name'], data.get('gender'), data.get('phone'), data.get('job'))
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return jsonify({'code': 1, 'msg': 'success', 'data': {'id': new_id}})


@emp_bp.route('/emps', methods=['PUT'])
@auth_required
def update():
    data = request.get_json()
    conn = get_db()
    password = data.get('password')
    if password:
        hash_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt(10)).decode()
        conn.execute(
            "UPDATE emp SET username=?, name=?, gender=?, phone=?, job=?, password=?, update_time=datetime('now','localtime') WHERE id=?",
            (data['username'], data['name'], data.get('gender'), data.get('phone'), data.get('job'), hash_pw, data['id'])
        )
    else:
        conn.execute(
            "UPDATE emp SET username=?, name=?, gender=?, phone=?, job=?, update_time=datetime('now','localtime') WHERE id=?",
            (data['username'], data['name'], data.get('gender'), data.get('phone'), data.get('job'), data['id'])
        )
    conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': 'success', 'data': None})


@emp_bp.route('/emps', methods=['DELETE'])
@auth_required
def delete():
    ids_str = request.args.get('ids', '')
    ids = [int(x.strip()) for x in ids_str.split(',') if x.strip()]
    conn = get_db()
    conn.execute('BEGIN')
    for eid in ids:
        conn.execute('DELETE FROM emp WHERE id = ?', (eid,))
    conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': 'success', 'data': None})
