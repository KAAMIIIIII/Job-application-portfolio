const { verifyToken } = require('../utils/jwt');

function authMiddleware(req, res, next) {
  if (req.method === 'OPTIONS') {
    return next();
  }

  const token = req.headers.token;
  if (!token) {
    return res.status(401).json({ code: 0, msg: '未登录', data: null });
  }

  try {
    const payload = verifyToken(token);
    req.userId = payload.userId;
    req.userName = payload.name;
    next();
  } catch (err) {
    return res.status(401).json({ code: 0, msg: '登录失效，请重新登录', data: null });
  }
}

module.exports = authMiddleware;
