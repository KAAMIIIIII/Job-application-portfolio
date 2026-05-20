from flask import Blueprint, request, jsonify
from database import get_db
from middleware.auth import auth_required
from utils.camelize import camelize

clazz_bp = Blueprint('clazz', __name__)


@clazz_bp.route('/clazzs/list', methods=['GET'])
@auth_required
def list_all():
    conn = get_db()
    rows = conn.execute('SELECT id, name FROM clazz ORDER BY name').fetchall()
    conn.close()
    return jsonify({'code': 1, 'msg': 'success', 'data': camelize([dict(r) for r in rows])})


@clazz_bp.route('/clazzs', methods=['GET'])
@auth_required
def query_page():
    begin = request.args.get('begin', '')
    end = request.args.get('end', '')
    name = request.args.get('name', '')
    master_id = request.args.get('masterId')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 10))

    where = 'WHERE 1=1'
    params = []

    if name:
        where += ' AND c.name LIKE ?'
        params.append(f'%{name}%')
    if begin:
        where += ' AND c.begin_date = ?'
        params.append(begin)
    if end:
        where += ' AND c.end_date = ?'
        params.append(end)
    if master_id:
        where += ' AND c.master_id = ?'
        params.append(int(master_id))

    conn = get_db()
    total = conn.execute(f'SELECT COUNT(*) AS total FROM clazz c {where}', params).fetchone()[0]

    sql = f"""
        SELECT c.*, e.name AS master_name,
            CASE WHEN c.end_date >= date('now') THEN '在读' ELSE '已结课' END AS status
        FROM clazz c
        LEFT JOIN emp e ON c.master_id = e.id
        {where}
        ORDER BY c.update_time DESC
        LIMIT ? OFFSET ?
    """
    params.extend([page_size, (page - 1) * page_size])
    rows = conn.execute(sql, params).fetchall()
    conn.close()

    return jsonify({
        'code': 1, 'msg': 'success',
        'data': {'rows': camelize([dict(r) for r in rows]), 'total': total}
    })


@clazz_bp.route('/clazzs/<int:id>', methods=['GET'])
@auth_required
def query_by_id(id):
    conn = get_db()
    row = conn.execute("""
        SELECT c.*, e.name AS master_name,
            CASE WHEN c.end_date >= date('now') THEN '在读' ELSE '已结课' END AS status
        FROM clazz c
        LEFT JOIN emp e ON c.master_id = e.id
        WHERE c.id = ?
    """, (id,)).fetchone()
    conn.close()
    return jsonify({'code': 1, 'msg': 'success', 'data': camelize(dict(row)) if row else None})


@clazz_bp.route('/clazzs', methods=['POST'])
@auth_required
def add():
    data = request.get_json()
    conn = get_db()
    cur = conn.execute(
        'INSERT INTO clazz (name, room, begin_date, end_date, subject, master_id) VALUES (?, ?, ?, ?, ?, ?)',
        (data['name'], data.get('room'), data['beginDate'], data['endDate'], data['subject'], data.get('masterId'))
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return jsonify({'code': 1, 'msg': 'success', 'data': {'id': new_id}})


@clazz_bp.route('/clazzs', methods=['PUT'])
@auth_required
def update():
    data = request.get_json()
    conn = get_db()
    conn.execute(
        "UPDATE clazz SET name=?, room=?, begin_date=?, end_date=?, subject=?, master_id=?, update_time=datetime('now','localtime') WHERE id=?",
        (data['name'], data.get('room'), data['beginDate'], data['endDate'], data['subject'], data.get('masterId'), data['id'])
    )
    conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': 'success', 'data': None})


@clazz_bp.route('/clazzs/<int:id>', methods=['DELETE'])
@auth_required
def delete(id):
    conn = get_db()
    conn.execute('DELETE FROM clazz WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': 'success', 'data': None})
