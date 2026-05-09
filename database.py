import sqlite3
import os
import json
import time

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gamebot.db')


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT DEFAULT '',
        name TEXT DEFAULT '',
        balance INTEGER DEFAULT 0,
        xp INTEGER DEFAULT 0,
        kills INTEGER DEFAULT 0,
        is_dead INTEGER DEFAULT 0,
        is_premium INTEGER DEFAULT 0,
        premium_emoji TEXT DEFAULT '',
        protection_until INTEGER DEFAULT 0,
        daily_last INTEGER DEFAULT 0,
        rob_count INTEGER DEFAULT 0,
        rob_reset INTEGER DEFAULT 0,
        kill_count INTEGER DEFAULT 0,
        kill_reset INTEGER DEFAULT 0,
        items TEXT DEFAULT '{}',
        created_at INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS codes (
        code TEXT PRIMARY KEY,
        amount INTEGER,
        type TEXT DEFAULT 'balance',
        used INTEGER DEFAULT 0,
        used_by INTEGER DEFAULT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS groups (
        chat_id INTEGER PRIMARY KEY,
        claimed_by INTEGER DEFAULT NULL,
        claimed_at INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS warnings (
        chat_id INTEGER,
        user_id INTEGER,
        count INTEGER DEFAULT 0,
        PRIMARY KEY (chat_id, user_id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS bomb_scores (
        user_id INTEGER PRIMARY KEY,
        wins INTEGER DEFAULT 0,
        games INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS chats (
        chat_id INTEGER PRIMARY KEY,
        title TEXT DEFAULT '',
        type TEXT DEFAULT ''
    )''')
    conn.commit()
    conn.close()


def get_user(user_id, name=None, username=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = c.fetchone()
    if not user:
        c.execute(
            'INSERT INTO users (user_id, username, name, balance, xp, created_at) VALUES (?, ?, ?, 1000, 0, ?)',
            (user_id, username or '', name or str(user_id), int(time.time()))
        )
        conn.commit()
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = c.fetchone()
    else:
        updates = {}
        if name:
            updates['name'] = name
        if username is not None:
            updates['username'] = username
        if updates:
            sets = ', '.join(f'{k} = ?' for k in updates)
            vals = list(updates.values()) + [user_id]
            c.execute(f'UPDATE users SET {sets} WHERE user_id = ?', vals)
            conn.commit()
            c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            user = c.fetchone()
    conn.close()
    return dict(user)


def update_user(user_id, **kwargs):
    if not kwargs:
        return
    conn = get_conn()
    c = conn.cursor()
    sets = ', '.join(f'{k} = ?' for k in kwargs)
    vals = list(kwargs.values()) + [user_id]
    c.execute(f'UPDATE users SET {sets} WHERE user_id = ?', vals)
    conn.commit()
    conn.close()


def get_all_users():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    users = [dict(u) for u in c.fetchall()]
    conn.close()
    return users


def get_top_rich(limit=10):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM users ORDER BY balance DESC LIMIT ?', (limit,))
    users = [dict(u) for u in c.fetchall()]
    conn.close()
    return users


def get_top_kills(limit=10):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM users ORDER BY kills DESC LIMIT ?', (limit,))
    users = [dict(u) for u in c.fetchall()]
    conn.close()
    return users


def get_global_rank(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        'SELECT COUNT(*) FROM users WHERE balance > (SELECT balance FROM users WHERE user_id = ?)',
        (user_id,)
    )
    rank = c.fetchone()[0] + 1
    conn.close()
    return rank


def save_code(code, amount, code_type='balance'):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        'INSERT OR REPLACE INTO codes (code, amount, type, used) VALUES (?, ?, ?, 0)',
        (code, amount, code_type)
    )
    conn.commit()
    conn.close()


def use_code(code, user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM codes WHERE code = ?', (code,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None, '❌ Code not found!'
    row = dict(row)
    if row['used']:
        conn.close()
        return None, '❌ This code has already been used!'
    c.execute('UPDATE codes SET used = 1, used_by = ? WHERE code = ?', (user_id, code))
    conn.commit()
    conn.close()
    return row, None


def get_group(chat_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM groups WHERE chat_id = ?', (chat_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def save_group(chat_id, claimed_by):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        'INSERT OR REPLACE INTO groups (chat_id, claimed_by, claimed_at) VALUES (?, ?, ?)',
        (chat_id, claimed_by, int(time.time()))
    )
    conn.commit()
    conn.close()


def get_warnings(chat_id, user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT count FROM warnings WHERE chat_id = ? AND user_id = ?', (chat_id, user_id))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0


def add_warning(chat_id, user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        'INSERT INTO warnings (chat_id, user_id, count) VALUES (?, ?, 1) '
        'ON CONFLICT(chat_id, user_id) DO UPDATE SET count = count + 1',
        (chat_id, user_id)
    )
    conn.commit()
    c.execute('SELECT count FROM warnings WHERE chat_id = ? AND user_id = ?', (chat_id, user_id))
    count = c.fetchone()[0]
    conn.close()
    return count


def remove_warning(chat_id, user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        'UPDATE warnings SET count = MAX(0, count - 1) WHERE chat_id = ? AND user_id = ?',
        (chat_id, user_id)
    )
    conn.commit()
    conn.close()


def update_bomb_score(user_id, won=False):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        'INSERT INTO bomb_scores (user_id, wins, games) VALUES (?, ?, 1) '
        'ON CONFLICT(user_id) DO UPDATE SET wins = wins + ?, games = games + 1',
        (user_id, 1 if won else 0, 1 if won else 0)
    )
    conn.commit()
    conn.close()


def get_bomb_leaders():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        SELECT bs.user_id, bs.wins, bs.games, u.name, u.is_premium, u.premium_emoji
        FROM bomb_scores bs
        JOIN users u ON bs.user_id = u.user_id
        ORDER BY bs.wins DESC LIMIT 10
    ''')
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_bomb_rank(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT wins, games FROM bomb_scores WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return 0, 0, 0
    wins, games = row[0], row[1]
    c.execute('SELECT COUNT(*) FROM bomb_scores WHERE wins > ?', (wins,))
    rank = c.fetchone()[0] + 1
    conn.close()
    return wins, games, rank


def save_chat(chat_id, title='', chat_type=''):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        'INSERT OR REPLACE INTO chats (chat_id, title, type) VALUES (?, ?, ?)',
        (chat_id, title, chat_type)
    )
    conn.commit()
    conn.close()
