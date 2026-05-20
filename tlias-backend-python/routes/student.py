from flask import Blueprint, request, jsonify
from database import get_db
from middleware.auth import auth_required
from utils.camelize import camelize

student_bp = Blueprint('student', __name__)


@student_bp.route('/students', methods=['GET'])
@auth_required
def query_page():
    clazz_id = request.args.get('clazzId')
    degree = request.args.get('degree')
    name = request.args.get('name', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 10))

    where = 'WHERE 1=1'
    params = []

    if clazz_id:
        where += ' AND s.clazz_id = ?'
        params.append(int(clazz_id))
    if degree:
        where += ' AND s.degree = ?'
        params.append(int(degree))
    if name:
        where += ' AND s.name LIKE ?'
        params.append(f'%{name}%')

    conn = get_db()
    total = conn.execute(f'SELECT COUNT(*) AS total FROM student s {where}', params).fetchone()[0]

    sql = f"""
        SELECT s.*, c.name AS clazz_name, e.name AS master_name
        FROM student s
        LEFT JOIN clazz c ON s.clazz_id = c.id
        LEFT JOIN emp e ON c.master_id = e.id
        {where}
        ORDER BY s.update_time DESC
        LIMIT ? OFFSET ?
    """
    params.extend([page_size, (page - 1) * page_size])
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    return jsonify({
        'code': 1, 'msg': 'success',
        'data': {'rows': camelize([dict(r) for r in rows]), 'total': total}
    })


@student_bp.route('/students/<int:id>', methods=['GET'])
@auth_required
def query_by_id(id):
    conn = get_db()
    row = conn.execute("""
        SELECT s.*, c.name AS clazz_name, e.name AS master_name
        FROM student s
        LEFT JOIN clazz c ON s.clazz_id = c.id
        LEFT JOIN emp e ON c.master_id = e.id
        WHERE s.id = ?
    """, (id,)).fetchone()
    conn.close()
    return jsonify({'code': 1, 'msg': 'success', 'data': camelize(dict(row)) if row else None})


@student_bp.route('/students', methods=['POST'])
@auth_required
def add():
    data = request.get_json()
    conn = get_db()
    cur = conn.execute("""
        INSERT INTO student (name, no, gender, phone, id_card, is_college, address, degree, graduation_date, clazz_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['name'], data['no'], data.get('gender'), data.get('phone'),
        data.get('idCard'), data.get('isCollege', 0), data.get('address'),
        data.get('degree'), data.get('graduationDate'), data.get('clazzId')
    ))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return jsonify({'code': 1, 'msg': 'success', 'data': {'id': new_id}})


@student_bp.route('/students', methods=['PUT'])
@auth_required
def update():
    data = request.get_json()
    conn = get_db()
    conn.execute("""
        UPDATE student SET name=?, no=?, gender=?, phone=?, id_card=?, is_college=?,
            address=?, degree=?, graduation_date=?, clazz_id=?, update_time=datetime('now','localtime')
        WHERE id=?
    """, (
        data['name'], data['no'], data.get('gender'), data.get('phone'),
        data.get('idCard'), data.get('isCollege', 0), data.get('address'),
        data.get('degree'), data.get('graduationDate'), data.get('clazzId'), data['id']
    ))
    conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': 'success', 'data': None})


@student_bp.route('/students/<ids>', methods=['DELETE'])
@auth_required
def delete(ids):
    id_list = [int(x.strip()) for x in ids.split(',') if x.strip()]
    conn = get_db()
    conn.execute('BEGIN')
    for sid in id_list:
        conn.execute('DELETE FROM student WHERE id = ?', (sid,))
    conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': 'success', 'data': None})


@student_bp.route('/students/violation/<int:id>/<int:score>', methods=['PUT'])
@auth_required
def violation(id, score):
    conn = get_db()
    conn.execute("""
        UPDATE student SET violation_count = violation_count + 1, violation_score = violation_score + ?,
            update_time = datetime('now','localtime')
        WHERE id = ?
    """, (score, id))
    conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': 'success', 'data': None})
