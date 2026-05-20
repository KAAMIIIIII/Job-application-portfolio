import sqlite3
import os
import bcrypt

DB_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_PATH = os.path.join(DB_DIR, 'tlias.db')


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS dept (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT,
            file_path TEXT,
            file_name TEXT,
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
    """)

    admin = conn.execute("SELECT 1 FROM emp WHERE username = ?", ('admin',)).fetchone()
    if not admin:
        hash_pw = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt(10)).decode()
        conn.execute(
            'INSERT INTO emp (username, password, name, gender, phone, job) VALUES (?, ?, ?, ?, ?, ?)',
            ('admin', hash_pw, '管理员', 1, '13800000001', 1)
        )
        print('===================================')
        print('  默认管理员账号已创建:')
        print('  用户名: admin  密码: admin123')
        print('===================================')

    conn.commit()

    # 兼容旧表：添加 file_path / file_name 列（如果不存在）
    for col in ('file_path', 'file_name'):
        try:
            conn.execute(f'ALTER TABLE dept ADD COLUMN {col} TEXT')
        except Exception:
            pass

    conn.commit()
    conn.close()
