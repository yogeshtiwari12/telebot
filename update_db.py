import sqlite3

conn = sqlite3.connect('dating_bot.db')

# Add the missing columns
try:
    conn.execute('ALTER TABLE users ADD COLUMN favorite_game TEXT')
    print("Added favorite_game column")
except sqlite3.OperationalError as e:
    print(f"favorite_game column: {e}")

try:
    conn.execute('ALTER TABLE users ADD COLUMN favorite_movie TEXT')
    print("Added favorite_movie column")
except sqlite3.OperationalError as e:
    print(f"favorite_movie column: {e}")

try:
    conn.execute('ALTER TABLE users ADD COLUMN favorite_music TEXT')
    print("Added favorite_music column")
except sqlite3.OperationalError as e:
    print(f"favorite_music column: {e}")

try:
    conn.execute('ALTER TABLE users ADD COLUMN hobbies TEXT')
    print("Added hobbies column")
except sqlite3.OperationalError as e:
    print(f"hobbies column: {e}")

conn.commit()

# Check updated structure
print('\nUpdated users table structure:')
for row in conn.execute('PRAGMA table_info(users)').fetchall():
    print(row)

conn.close()
print("\nDatabase schema updated successfully!")
