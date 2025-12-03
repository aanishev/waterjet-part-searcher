from config import branch
import sqlite3

# === База данных ===
# === На хостинге перед путями к файлам добавить "/" ===
if branch == "test":
    conn = sqlite3.connect("data/bot-test.db", check_same_thread=False)
else:
    conn = sqlite3.connect("data/bot.db", check_same_thread=False)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS applications (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER UNIQUE,
status TEXT DEFAULT 'Pending' -- pending / approved / rejected
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
user_id INTEGER PRIMARY KEY,
uname TEXT DEFAULT 'Not stated',
urole TEXT DEFAULT 'Guest', -- Guest / Manager / Administrator,
lang TEXT DEFAULT 'en' -- en / ka / ru
)
""")

conn.commit()