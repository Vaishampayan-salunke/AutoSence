import sqlite3

conn = sqlite3.connect('V:/BDT/bigdata/mysql/autosense_local.db')
c = conn.cursor()

c.execute("SELECT sql FROM sqlite_master WHERE type='table'")
for row in c.fetchall():
    print(row[0])
    print('-'*50)

conn.close()
