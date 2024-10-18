import sqlite3
import requests

con = sqlite3.connect('database.db')
cursor = con.cursor()

movies = cursor.execute('SELECT * FROM movies').fetchall()

def get_runtime_and_att_provider():
    API_KEY = '9f49b76745c71b8a1aa4407888bbb40a'

    for movie in movies:
        id = movie[0]
        url = f"https://api.themoviedb.org/3/movie/{id}?api_key={API_KEY}&language=pt-BR"
        movie_att = requests.get(url).json()
        runtime = movie_att['runtime'] 
        
        cursor.execute('UPDATE movies SET runtime = ? WHERE id = ?', (runtime, id))
        con.commit()
        print(f'{id} OK')

get_runtime_and_att_provider()