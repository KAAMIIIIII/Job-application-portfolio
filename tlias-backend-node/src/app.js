const express = require('express');
const cors = require('cors');
const authMiddleware = require('./middleware/auth');
const { camelizeMiddleware } = require('./utils/camelize');

const loginRouter = require('./routes/login');
const deptRouter = require('./routes/dept');
const empRouter = require('./routes/emp');
const clazzRouter = require('./routes/clazz');
const studentRouter = require('./routes/student');
const reportRouter = require('./routes/report');

const app = express();

// 中间件
app.use(cors());
app.use(express.json());
app.use(camelizeMiddleware);

// 登录接口不需要鉴权
app.use('/login', loginRouter);

// 其他接口需要 token 鉴权
app.use('/depts', authMiddleware, deptRouter);
app.use('/emps', authMiddleware, empRouter);
app.use('/clazzs', authMiddleware, clazzRouter);
app.use('/students', authMiddleware, studentRouter);
app.use('/report', authMiddleware, reportRouter);

// 全局错误处理
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ code: 0, msg: err.message || '服务器内部错误', data: null });
});

const PORT = 8080;
app.listen(PORT, () => {
  console.log(`后端服务已启动: http://localhost:${PORT}`);
  console.log(`默认管理员: admin / admin123`);
});

module.exports = app;
