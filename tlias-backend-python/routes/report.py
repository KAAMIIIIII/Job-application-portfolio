from flask import Blueprint, jsonify
from database import get_db
from middleware.auth import auth_required

report_bp = Blueprint('report', __name__)

JOB_NAMES = {1: '班主任', 2: '讲师', 3: '学工主管', 4: '教研主管', 5: '咨询师'}
DEGREE_NAMES = {1: '初中', 2: '高中', 3: '大专', 4: '本科', 5: '硕士', 6: '博士'}


@report_bp.route('/report/empJobData', methods=['GET'])
@auth_required
def emp_job_data():
    conn = get_db()
    rows = conn.execute('SELECT job, COUNT(*) AS count FROM emp GROUP BY job').fetchall()
    conn.close()
    job_list = [JOB_NAMES.get(r['job'], '其他') for r in rows]
    data_list = [r['count'] for r in rows]
    return jsonify({'code': 1, 'msg': 'success', 'data': {'jobList': job_list, 'dataList': data_list}})


@report_bp.route('/report/empGenderData', methods=['GET'])
@auth_required
def emp_gender_data():
    conn = get_db()
    rows = conn.execute(
        "SELECT CASE WHEN gender = 1 THEN '男' ELSE '女' END AS name, COUNT(*) AS value FROM emp GROUP BY gender"
    ).fetchall()
    conn.close()
    return jsonify({'code': 1, 'msg': 'success', 'data': [dict(r) for r in rows]})


@report_bp.route('/report/studentCountData', methods=['GET'])
@auth_required
def student_count_data():
    conn = get_db()
    rows = conn.execute(
        'SELECT c.name AS clazz_list, COUNT(s.id) AS data_list FROM clazz c LEFT JOIN student s ON c.id = s.clazz_id GROUP BY c.id, c.name'
    ).fetchall()
    conn.close()
    clazz_list = [r['clazz_list'] for r in rows]
    data_list = [r['data_list'] for r in rows]
    return jsonify({'code': 1, 'msg': 'success', 'data': {'clazzList': clazz_list, 'dataList': data_list}})


@report_bp.route('/report/studentDegreeData', methods=['GET'])
@auth_required
def student_degree_data():
    conn = get_db()
    rows = conn.execute('SELECT degree, COUNT(*) AS count FROM student GROUP BY degree').fetchall()
    conn.close()
    data = [{'name': DEGREE_NAMES.get(r['degree'], '其他'), 'value': r['count']} for r in rows]
    return jsonify({'code': 1, 'msg': 'success', 'data': {'data': data}})
