const jwt = require('jsonwebtoken');

const SECRET = 'tlias-secret-key-2024-project-intelligent-agriculture';
const EXPIRATION = '24h';

function generateToken(userId, name) {
  return jwt.sign({ userId, name }, SECRET, { expiresIn: EXPIRATION });
}

function verifyToken(token) {
  return jwt.verify(token, SECRET);
}

module.exports = { generateToken, verifyToken };
