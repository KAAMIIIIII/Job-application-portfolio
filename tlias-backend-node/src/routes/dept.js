const express = require('express');
const db = require('../database');

const router = express.Router();

// GET /depts - 查询全部
router.get('/', (req, res) => {
  const list = db.prepare('SELECT * FROM dept ORDER BY update_time DESC').all();
  res.json({ code: 1, msg: 'success', data: list });
});

// GET /depts/:id - 根据ID查询
router.get('/:id', (req, res) => {
  const dept = db.prepare('SELECT * FROM dept WHERE id = ?').get(req.params.id);
  res.json({ code: 1, msg: 'success', data: dept });
});

// POST /depts - 新增
router.post('/', (req, res) => {
  const { name, url } = req.body;
  const result = db.prepare('INSERT INTO dept (name, url) VALUES (?, ?)').run(name, url);
  res.json({ code: 1, msg: 'success', data: { id: result.lastInsertRowid } });
});

// PUT /depts - 修改
router.put('/', (req, res) => {
  const { id, name, url } = req.body;
  db.prepare("UPDATE dept SET name = ?, url = ?, update_time = datetime('now','localtime') WHERE id = ?")
    .run(name, url, id);
  res.json({ code: 1, msg: 'success', data: null });
});

// DELETE /depts?id=xxx
router.delete('/', (req, res) => {
  db.prepare('DELETE FROM dept WHERE id = ?').run(req.query.id);
  res.json({ code: 1, msg: 'success', data: null });
});

module.exports = router;
