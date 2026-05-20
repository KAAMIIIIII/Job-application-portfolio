const express = require('express');
const db = require('../database');

const router = express.Router();

// GET /clazzs - 分页条件查询
router.get('/', (req, res) => {
  const { begin = '', end = '', name = '', page = 1, pageSize = 10 } = req.query;
  const pageNum = parseInt(page);
  const pageSizeNum = parseInt(pageSize);

  let where = 'WHERE 1=1';
  const params = [];

  if (name) { where += ' AND c.name LIKE ?'; params.push(`%${name}%`); }
  if (begin) { where += ' AND c.begin_date = ?'; params.push(begin); }
  if (end) { where += ' AND c.end_date = ?'; params.push(end); }

  const countSql = `SELECT COUNT(*) AS total FROM clazz c ${where}`;
  const { total } = db.prepare(countSql).get(...params);

  const sql = `
    SELECT c.*, e.name AS master_name,
      CASE WHEN c.end_date >= date('now') THEN '在读' ELSE '已结课' END AS status
    FROM clazz c
    LEFT JOIN emp e ON c.master_id = e.id
    ${where}
    ORDER BY c.update_time DESC
    LIMIT ? OFFSET ?
  `;
  params.push(pageSizeNum, (pageNum - 1) * pageSizeNum);
  const rows = db.prepare(sql).all(...params);

  res.json({ code: 1, msg: 'success', data: { rows, total } });
});

// GET /clazzs/list - 查询全部班级(下拉选项用)
router.get('/list', (req, res) => {
  const list = db.prepare('SELECT id, name FROM clazz ORDER BY name').all();
  res.json({ code: 1, msg: 'success', data: list });
});

// GET /clazzs/:id - 根据ID查询
router.get('/:id', (req, res) => {
  const clazz = db.prepare(`
    SELECT c.*, e.name AS master_name,
      CASE WHEN c.end_date >= date('now') THEN '在读' ELSE '已结课' END AS status
    FROM clazz c
    LEFT JOIN emp e ON c.master_id = e.id
    WHERE c.id = ?
  `).get(req.params.id);
  res.json({ code: 1, msg: 'success', data: clazz });
});

// POST /clazzs - 新增
router.post('/', (req, res) => {
  const { name, room, beginDate, endDate, subject, masterId } = req.body;
  const result = db.prepare('INSERT INTO clazz (name, room, begin_date, end_date, subject, master_id) VALUES (?, ?, ?, ?, ?, ?)')
    .run(name, room || null, beginDate, endDate, subject, masterId || null);
  res.json({ code: 1, msg: 'success', data: { id: result.lastInsertRowid } });
});

// PUT /clazzs - 修改
router.put('/', (req, res) => {
  const { id, name, room, beginDate, endDate, subject, masterId } = req.body;
  db.prepare("UPDATE clazz SET name=?, room=?, begin_date=?, end_date=?, subject=?, master_id=?, update_time=datetime('now','localtime') WHERE id=?")
    .run(name, room || null, beginDate, endDate, subject, masterId || null, id);
  res.json({ code: 1, msg: 'success', data: null });
});

// DELETE /clazzs/:id - 删除
router.delete('/:id', (req, res) => {
  db.prepare('DELETE FROM clazz WHERE id = ?').run(req.params.id);
  res.json({ code: 1, msg: 'success', data: null });
});

module.exports = router;
