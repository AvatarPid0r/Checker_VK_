import sqlite3

with sqlite3.connect('database.db') as con:
    cursor = con.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS vk_id
                      (ids INTEGER,
                      off TEXT,
                      user_id)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS user_id
                      (user_id INTEGER PRIMARY KEY,
                      status INTEGER DEFAULT 0)''')

