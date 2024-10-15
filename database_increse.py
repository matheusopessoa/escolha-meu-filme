#Incrementar mais filmes nos streamings menores

import sqlite3
import requests

con = sqlite3.connect('database.db')
cursor = con.cursor()

cursor = con.cursor()
ids = cursor.execute('SELECT id FROM movies').fetchall()
print(ids)
ids_num = []

for id in ids:
    ids_num.append(id[0])

providers = {
    'Disney Plus': 337,
    'Amazon Prime Video': 119,
    'Netflix': 8,
    'Paramount Plus': 531,
    'Max': 1899,
    'Apple TV Plus': 350,
    'Globoplay': 307,
    'Crunchyroll': 283,
    'Pluto TV': 300
}

genres_dict = {'Action': 28, 'Adventure': 12, 'Comedy': 35, 'Animation': 16, 'Crime': 80,
               'Documentary': 99, 'Drama': 18, 'Family': 10751, 'Fantasy': 14, 'History': 36,
               'Horror': 27, 'Music': 10402, 'Mystery': 9648, 'Romance': 10749, 'Science Fiction': 878,
               'TV Movie': 10770, 'Thriller': 53, 'War': 10752, 'Western': 37}

def get_movies(provedor_id, total_paginas=400):
    API_KEY = '9f49b76745c71b8a1aa4407888bbb40a'
    BASE_URL = 'https://api.themoviedb.org/3'
    movies = {}
    ids_movies = set() 
    
    min_rates = 50
    min_av_votes = 6.0
    ids = cursor.execute('SELECT id FROM movies')
    for pagina in range(1, total_paginas + 1):

        url = f"{BASE_URL}/discover/movie?api_key={API_KEY}&with_watch_providers={provedor_id}&sort_by=vote_average.desc&vote_count.gte={min_rates}&watch_region=BR&page={pagina}&vote_average.gte={min_av_votes}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            for movie in data.get('results', []):
                if movie.get('id') not in ids_movies and movie.get('id') not in ids_num:
                    movie_data = {
                        'id': movie.get('id'),
                        'vote_count': movie.get('vote_count'),
                        'vote_average': movie.get('vote_average'),
                        'genre_ids': movie.get('genre_ids'),
                        'original_language': movie.get('original_language'),
                        'title': movie.get('title'),
                        'overview': movie.get('overview'),
                        'popularity': movie.get('popularity'),
                        'release_date': movie.get('release_date'),
                        'poster_path': movie.get('poster_path')
                    }
                    movies[movie.get('title')] = movie_data
                    ids_movies.add(movie.get('id'))  
        else:
            print(f"Erro ao buscar dados: {response.status_code}")
            break 

    return movies



cursor.execute('''
CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY,
    genre_ids TEXT,
    provider TEXT,
    weight REAL,
    title TEXT,
    overview TEXT,
    original_language TEXT,
    popularity REAL,
    release_date TEXT,
    vote_average REAL,
    vote_count INTEGER,
    poster_path TEXT
)
''')

paramount_movies, appletv_movies, globoplay_movies, crunchyroll_movies, plutotv_movies = get_movies(531), get_movies(350), get_movies(307), get_movies(283), get_movies(300)
def insert_movie(provider, movie_dict):
    genre_ids_string = ', '.join(map(str, movie_dict.get('genre_ids', [])))  # Converte IDs para string
    try:
        cursor.execute('''
        INSERT INTO movies (id, provider, genre_ids, weight, title, overview, original_language, popularity, release_date, vote_average, vote_count, poster_path)
        VALUES (:id, :provider, :genre_ids, 0.7, :title, :overview, :original_language, :popularity, :release_date, :vote_average, :vote_count, :poster_path)
        ''', {**movie_dict, 'provider': provider, 'genre_ids': genre_ids_string})
    except:
        return f'Error {provider}'

for title, movie in crunchyroll_movies.items():
    insert_movie('crunchyroll', movie)
for title, movie in paramount_movies.items():
    insert_movie('paramount', movie)
for title, movie in appletv_movies.items():
    insert_movie('appletv', movie)
for title, movie in globoplay_movies.items():
    insert_movie('globoplay', movie)
for title, movie in plutotv_movies.items():
    insert_movie('plutotv', movie)

print('ok')

con.commit()
con.close()
