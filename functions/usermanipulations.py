from functions.dbconn import conn, cursor

# === Получение или создание пользователя ===
def get_or_create_user(user):
    cursor.execute("SELECT uname FROM users WHERE user_id=?", (user.id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO users (user_id, uname) VALUES (?, ?)",
                       (str(user.id), str(user.first_name)))
        conn.commit()
        cursor.execute("SELECT uname FROM users WHERE user_id=?", (user.id,))
        row = cursor.fetchone()
        return row[0]
    return row[0]