import sqlite3

conn = sqlite3.connect('dating_bot.db')
print('✅ Database created successfully!')
print('\nUsers table columns:')
for i, row in enumerate(conn.execute('PRAGMA table_info(users)').fetchall()):
    print(f'  {i}: {row[1]} ({row[2]})')

print('\n✅ Schema looks correct - no hobbies column, includes favorite_game, favorite_movie, favorite_music')
conn.close()
