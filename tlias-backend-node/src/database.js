const Database = require('better-sqlite3');
const path = require('path');
const bcrypt = require('bcryptjs');

const db = new Database(path.join(__dirname, '..', 'data', 'tlias.db'));

db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

// 建表
db.exec(`
  CREATE TABLE IF NOT EXISTS dept (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    update_time TEXT DEFAULT (datetime('now','localtime'))
  );

  CREATE TABLE IF NOT EXISTS emp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    name TEXT NOT NULL,
    gender INTEGER,
    phone TEXT,
    job INTEGER,
    update_time TEXT DEFAULT (datetime('now','localtime'))
  );

  CREATE TABLE IF NOT EXISTS clazz (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    room TEXT,
    begin_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    subject INTEGER NOT NULL,
    master_id INTEGER,
    update_time TEXT DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (master_id) REFERENCES emp(id) ON DELETE SET NULL
  );

  CREATE TABLE IF NOT EXISTS student (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    no TEXT NOT NULL,
    gender INTEGER,
    phone TEXT,
    id_card TEXT,
    is_college INTEGER DEFAULT 0,
    address TEXT,
    degree INTEGER,
    graduation_date TEXT,
    clazz_id INTEGER,
    violation_count INTEGER DEFAULT 0,
    violation_score INTEGER DEFAULT 0,
    update_time TEXT DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (clazz_id) REFERENCES clazz(id) ON DELETE SET NULL
  );
`);

// 默认管理员账号
const adminExists = db.prepare('SELECT 1 FROM emp WHERE username = ?').get('admin');
if (!adminExists) {
  const hash = bcrypt.hashSync('admin123', 10);
  db.prepare('INSERT INTO emp (username, password, name, gender, phone, job) VALUES (?, ?, ?, ?, ?, ?)')
    .run('admin', hash, '管理员', 1, '13800000001', 1);
  console.log('===================================');
  console.log('  默认管理员账号已创建:');
  console.log('  用户名: admin  密码: admin123');
  console.log('===================================');
}

module.exports = db;
