const express = require('express');
const db = require('../database');

const router = express.Router();

const JOB_NAMES = { 1: '班主任', 2: '讲师', 3: '学工主管', 4: '教研主管', 5: '咨询师' };
const DEGREE_NAMES = { 1: '初中', 2: '高中', 3: '大专', 4: '本科', 5: '硕士', 6: '博士' };

// GET /report/empJobData - 员工职位统计
router.get('/empJobData', (req, res) => {
  const rows = db.prepare('SELECT job, COUNT(*) AS count FROM emp GROUP BY job').all();
  const jobList = rows.map(r => JOB_NAMES[r.job] || '其他');
  const dataList = rows.map(r => r.count);
  res.json({ code: 1, msg: 'success', data: { jobList, dataList } });
});

// GET /report/empGenderData - 员工性别统计
router.get('/empGenderData', (req, res) => {
  const rows = db.prepare("SELECT CASE WHEN gender = 1 THEN '男' ELSE '女' END AS name, COUNT(*) AS value FROM emp GROUP BY gender").all();
  res.json({ code: 1, msg: 'success', data: rows });
});

// GET /report/studentCountData - 班级人数统计
router.get('/studentCountData', (req, res) => {
  const rows = db.prepare('SELECT c.name AS clazz_list, COUNT(s.id) AS data_list FROM clazz c LEFT JOIN student s ON c.id = s.clazz_id GROUP BY c.id, c.name').all();
  const clazzList = rows.map(r => r.clazz_list);
  const dataList = rows.map(r => r.data_list);
  res.json({ code: 1, msg: 'success', data: { clazzList, dataList } });
});

// GET /report/studentDegreeData - 学员学历统计
router.get('/studentDegreeData', (req, res) => {
  const rows = db.prepare('SELECT degree, COUNT(*) AS count FROM student GROUP BY degree').all();
  const data = rows.map(r => ({ name: DEGREE_NAMES[r.degree] || '其他', value: r.count }));
  res.json({ code: 1, msg: 'success', data: { data } });
});

module.exports = router;
