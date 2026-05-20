const express = require('express');
const db = require('../database');

const router = express.Router();

// GET /students - 分页条件查询
router.get('/', (req, res) => {
  const { clazzId, degree, name = '', page = 1, pageSize = 10 } = req.query;
  const pageNum = parseInt(page);
  const pageSizeNum = parseInt(pageSize);

  let where = 'WHERE 1=1';
  const params = [];

  if (clazzId) { where += ' AND s.clazz_id = ?'; params.push(parseInt(clazzId)); }
  if (degree) { where += ' AND s.degree = ?'; params.push(parseInt(degree)); }
  if (name) { where += ' AND s.name LIKE ?'; params.push(`%${name}%`); }

  const countSql = `SELECT COUNT(*) AS total FROM student s ${where}`;
  const { total } = db.prepare(countSql).get(...params);

  const sql = `
    SELECT s.*, c.name AS clazz_name
    FROM student s
    LEFT JOIN clazz c ON s.clazz_id = c.id
    ${where}
    ORDER BY s.update_time DESC
    LIMIT ? OFFSET ?
  `;
  params.push(pageSizeNum, (pageNum - 1) * pageSizeNum);
  const rows = db.prepare(sql).all(...params);

  res.json({ code: 1, msg: 'success', data: { rows, total } });
});

// GET /students/:id - 根据ID查询
router.get('/:id', (req, res) => {
  const student = db.prepare(`
    SELECT s.*, c.name AS clazz_name
    FROM student s
    LEFT JOIN clazz c ON s.clazz_id = c.id
    WHERE s.id = ?
  `).get(req.params.id);
  res.json({ code: 1, msg: 'success', data: student });
});

// POST /students - 新增
router.post('/', (req, res) => {
  const { name, no, gender, phone, idCard, isCollege, address, degree, graduationDate, clazzId } = req.body;
  const result = db.prepare(`
    INSERT INTO student (name, no, gender, phone, id_card, is_college, address, degree, graduation_date, clazz_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).run(name, no, gender || null, phone || null, idCard || null, isCollege || 0, address || null, degree || null, graduationDate || null, clazzId || null);
  res.json({ code: 1, msg: 'success', data: { id: result.lastInsertRowid } });
});

// PUT /students - 修改
router.put('/', (req, res) => {
  const { id, name, no, gender, phone, idCard, isCollege, address, degree, graduationDate, clazzId } = req.body;
  db.prepare(`
    UPDATE student SET name=?, no=?, gender=?, phone=?, id_card=?, is_college=?, address=?, degree=?, graduation_date=?, clazz_id=?, update_time=datetime('now','localtime')
    WHERE id=?
  `).run(name, no, gender || null, phone || null, idCard || null, isCollege || 0, address || null, degree || null, graduationDate || null, clazzId || null, id);
  res.json({ code: 1, msg: 'success', data: null });
});

// DELETE /students/:ids - 删除(支持逗号分隔)
router.delete('/:ids', (req, res) => {
  const ids = req.params.ids.split(',').map(id => parseInt(id.trim()));
  const stmt = db.prepare('DELETE FROM student WHERE id = ?');
  const deleteMany = db.transaction((ids) => { for (const id of ids) stmt.run(id); });
  deleteMany(ids);
  res.json({ code: 1, msg: 'success', data: null });
});

// PUT /students/violation/:id/:score - 违纪扣分
router.put('/violation/:id/:score', (req, res) => {
  const { id, score } = req.params;
  const scoreNum = parseInt(score);
  db.prepare(`
    UPDATE student SET violation_count = violation_count + 1, violation_score = violation_score + ?, update_time = datetime('now','localtime')
    WHERE id = ?
  `).run(scoreNum, id);
  res.json({ code: 1, msg: 'success', data: null });
});

module.exports = router;
