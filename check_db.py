import sqlite3

try:
    conn = sqlite3.connect('dating_bot.db')
    print('Current users table columns:')
    for i, row in enumerate(conn.execute('PRAGMA table_info(users)').fetchall()):
        print(f'  {i}: {row[1]} ({row[2]})')
    conn.close()
except Exception as e:
    print(f'Database error: {e}')
