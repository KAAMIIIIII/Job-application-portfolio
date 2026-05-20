// 递归将对象所有 key 从 snake_case 转为 camelCase
function toCamel(str) {
  return str.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
}

function camelize(val) {
  if (Array.isArray(val)) {
    return val.map(camelize);
  }
  if (val !== null && typeof val === 'object' && !(val instanceof Date)) {
    const out = {};
    for (const [k, v] of Object.entries(val)) {
      out[toCamel(k)] = camelize(v);
    }
    return out;
  }
  return val;
}

// Express 中间件，拦截 res.json 自动转换
function camelizeMiddleware(req, res, next) {
  const original = res.json.bind(res);
  res.json = (body) => original(camelize(body));
  next();
}

module.exports = { camelize, camelizeMiddleware };
