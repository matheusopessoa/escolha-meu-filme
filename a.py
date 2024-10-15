import sqlite3


con = sqlite3.connect('database.db')
cursor = con.cursor()
ids = cursor.execute('SELECT id FROM movies').fetchall()
print(ids)
ids_num = []
for id in ids:
    ids_num.append(id[0])

print(ids_num)