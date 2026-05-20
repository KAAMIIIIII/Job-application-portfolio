const express = require('express');
const bcrypt = require('bcryptjs');
const db = require('../database');
const { generateToken } = require('../utils/jwt');

const router = express.Router();

// POST /  - 完整路径为 /login (app.use 已挂载到 /login)
router.post('/', (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.json({ code: 0, msg: '用户名和密码不能为空', data: null });
  }

  const emp = db.prepare('SELECT * FROM emp WHERE username = ?').get(username);
  if (!emp || !bcrypt.compareSync(password, emp.password)) {
    return res.json({ code: 0, msg: '用户名或密码错误', data: null });
  }

  const token = generateToken(emp.id, emp.name);
  res.json({ code: 1, msg: 'success', data: { token, name: emp.name } });
});

module.exports = router;
