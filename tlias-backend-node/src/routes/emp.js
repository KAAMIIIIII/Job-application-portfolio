const express = require('express');
const bcrypt = require('bcryptjs');
const db = require('../database');

const router = express.Router();

// GET /emps - 分页条件查询
router.get('/', (req, res) => {
  const { name = '', gender, begin = '', end = '', page = 1, pageSize = 10 } = req.query;
  const pageNum = parseInt(page);
  const pageSizeNum = parseInt(pageSize);

  let sql = 'SELECT id, username, name, gender, phone, job, update_time FROM emp WHERE 1=1';
  let countSql = 'SELECT COUNT(*) AS total FROM emp WHERE 1=1';
  const params = [];

  if (name) { sql += ' AND name LIKE ?'; countSql += ' AND name LIKE ?'; params.push(`%${name}%`); }
  if (gender) { sql += ' AND gender = ?'; countSql += ' AND gender = ?'; params.push(parseInt(gender)); }
  if (begin) { sql += ' AND update_time >= ?'; countSql += ' AND update_time >= ?'; params.push(begin); }
  if (end) { sql += ' AND update_time <= ?'; countSql += ' AND update_time <= ?'; params.push(end); }

  const { total } = db.prepare(countSql).get(...params);

  sql += ' ORDER BY update_time DESC LIMIT ? OFFSET ?';
  params.push(pageSizeNum, (pageNum - 1) * pageSizeNum);

  const rows = db.prepare(sql).all(...params);

  res.json({ code: 1, msg: 'success', data: { rows, total } });
});

// GET /emps/list - 查询全部
router.get('/list', (req, res) => {
  const list = db.prepare('SELECT id, username, name, gender, phone, job, update_time FROM emp ORDER BY update_time DESC').all();
  res.json({ code: 1, msg: 'success', data: list });
});

// GET /emps/:id - 根据ID查询
router.get('/:id', (req, res) => {
  const emp = db.prepare('SELECT id, username, name, gender, phone, job, update_time FROM emp WHERE id = ?').get(req.params.id);
  res.json({ code: 1, msg: 'success', data: emp });
});

// POST /emps - 新增
router.post('/', (req, res) => {
  const { username, name, gender, phone, job } = req.body;
  const password = bcrypt.hashSync(req.body.password || '123456', 10);
  const result = db.prepare('INSERT INTO emp (username, password, name, gender, phone, job) VALUES (?, ?, ?, ?, ?, ?)')
    .run(username, password, name, gender || null, phone || null, job || null);
  res.json({ code: 1, msg: 'success', data: { id: result.lastInsertRowid } });
});

// PUT /emps - 修改
router.put('/', (req, res) => {
  const { id, username, name, gender, phone, job, password } = req.body;
  if (password) {
    const hash = bcrypt.hashSync(password, 10);
    db.prepare("UPDATE emp SET username=?, name=?, gender=?, phone=?, job=?, password=?, update_time=datetime('now','localtime') WHERE id=?")
      .run(username, name, gender || null, phone || null, job || null, hash, id);
  } else {
    db.prepare("UPDATE emp SET username=?, name=?, gender=?, phone=?, job=?, update_time=datetime('now','localtime') WHERE id=?")
      .run(username, name, gender || null, phone || null, job || null, id);
  }
  res.json({ code: 1, msg: 'success', data: null });
});

// DELETE /emps?ids=1,2,3
router.delete('/', (req, res) => {
  const ids = req.query.ids.split(',').map(id => parseInt(id.trim()));
  const stmt = db.prepare('DELETE FROM emp WHERE id = ?');
  const deleteMany = db.transaction((ids) => { for (const id of ids) stmt.run(id); });
  deleteMany(ids);
  res.json({ code: 1, msg: 'success', data: null });
});

module.exports = router;
