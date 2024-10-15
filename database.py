import sqlite3 as sq


# Метод для подключения в бд. В него обёрнуты все остальные методы для работы с бд
def db_connect(func):
    async def connect(*args, **kwargs):
        db = sq.connect('users.db')
        cursor = db.cursor()
        result = await func(cursor, *args, **kwargs)
        db.commit()
        return result
    return connect


# Метод для создания бд. 3 столбца: id пользователя в телеграми, имя для бота и время последнего обновления имени
@db_connect
async def db_start(cursor):
    cursor.execute("CREATE TABLE IF NOT EXISTS users("
                   "user_id INTEGER PRIMARY KEY,"
                   "name TEXT,"
                   "last_update TEXT)")


# Метод для добавления пользователя в бд
@db_connect
async def add_user(cursor, user_id, user_name, time):
    cursor.execute(f"INSERT INTO users (user_id, name, last_update) VALUES ({user_id}, '{user_name}', '{time}')")


# Метод для получения пользователя из бд
@db_connect
async def get_user(cursor, user_id) -> tuple:
    user = cursor.execute(f"SELECT * FROM users WHERE user_id = {user_id}").fetchone()
    return user


# Метод для обновления имени пользователя в бд
@db_connect
async def update_user(cursor, user_id, name, time):
    cursor.execute(f"UPDATE users SET name = '{name}', last_update = '{time}' WHERE user_id = {user_id}")
