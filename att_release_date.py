import sqlite3

con = sqlite3.connect('database.db')
cursor = con.cursor()


def att_date_format():
    dates = cursor.execute('SELECT release_date, id FROM movies').fetchall() 
    for release_date, id in dates:
        date = release_date[0:4]
        print(date)
        print(id)
        cursor.execute('UPDATE movies SET release_date = ? WHERE id = ?', (date, id)).fetchall()
        con.commit()

def discover_min_max():
    dates_ = cursor.execute('SELECT release_date FROM movies').fetchall() 
    time = cursor.execute('SELECT runtime FROM movies').fetchall() 
    min_year = 2024
    min_time = 60
    max_time = 60
    for i in dates_:
        if int(i[0]) < min_year:
            min_year = int(i[0])
    for t in time:
        if t[0] > max_time:
            max_time = t[0]
        if t[0] < min_time:
            min_time = t[0]
    
    return min_year, min_time, max_time #1902 0 248

def anomalias():
    zero=30
    movies = cursor.execute('SELECT * FROM movies WHERE runtime = ?', (zero,)).fetchall() 
    print(movies)

anomalias()
#print(discover_min_max())