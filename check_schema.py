import sqlite3

conn = sqlite3.connect('dating_bot.db')
print('Users table columns:')
for row in conn.execute('PRAGMA table_info(users)').fetchall():
    print(f'  {row[1]} ({row[2]})')
conn.close()
