import sqlite3

# Connect to both databases
source_conn = sqlite3.connect('files/quiz_database_cleaned.sqlite3')
target_conn = sqlite3.connect('backend/quiz_database_cleaned.sqlite3')

# Copy data
source_cursor = source_conn.cursor()
target_cursor = target_conn.cursor()

# Get the table creation SQL
source_cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='options'")
create_table_sql = source_cursor.fetchone()[0]

# Create the table in target database
target_cursor.execute(create_table_sql)

# Copy the data
source_cursor.execute("SELECT * FROM options")
target_cursor.executemany("INSERT INTO options VALUES ({})".format(','.join(['?' for _ in range(len(source_cursor.description))])), source_cursor.fetchall())

# Commit changes and close connections
target_conn.commit()
source_conn.close()
target_conn.close()
print("Data copied successfully")