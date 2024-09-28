import sqlite3
import numpy as np
import random

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome
    return conn

def movies_search(provider, genres):
    conn = get_db_connection()
    cursor = conn.cursor()
    count_genres = len(genres)

    if count_genres > 1:
        query = '''
        SELECT * FROM movies 
        WHERE provider = ? 
        AND (
            (genre_ids LIKE ? OR genre_ids LIKE ? OR genre_ids LIKE ? OR genre_ids = ?)
            AND
            (genre_ids LIKE ? OR genre_ids LIKE ? OR genre_ids LIKE ? OR genre_ids = ?)
        )
        '''
        results = cursor.execute(query, (
            provider, 
            f'%, {genres[0]},%', f'{genres[0]},%', f'%, {genres[0]}', genres[0], 
            f'%, {genres[1]},%', f'{genres[1]},%', f'%, {genres[1]}', genres[1]
        )).fetchall()
    
    else:
        query = '''
        SELECT * FROM movies 
        WHERE provider = ? 
        AND (genre_ids LIKE ? OR genre_ids LIKE ? OR genre_ids LIKE ? OR genre_ids = ?)
        '''
        results = cursor.execute(query, (
            provider, 
            f'%,{genres[0]},%', f'{genres[0]},%', f'%,{genres[0]}', genres[0]
        )).fetchall()

    conn.close()
    return np.array(results)

def update_movie_weights(ids_to_gain, ids_to_lose):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for i in ids_to_lose:
        new_value = float(ids_to_lose[i])
        new_value -= 0.1 if new_value >= 0.3 else new_value

        cursor.execute('''UPDATE movies SET weight = ? WHERE id = ?''', (new_value, i))
        conn.commit()

    if len(ids_to_gain) > 0:
        i, value = next(iter(ids_to_gain.items()))
        new_value = float(value)
        new_value += 0.1 if new_value <= 1.0 else new_value
        cursor.execute('''UPDATE movies SET weight = ? WHERE id = ?''', (new_value, i))
        conn.commit()

    conn.close()

def main():
    provider = str(input("Enter provider: "))
    genre_input = str(input("Write 1 or 2 genres ex: Action and Thriller: "))
    genres = genre_input.split(' and ')
    movies_list = movies_search(provider, genres)  

    movies_to_return = []

    for movie in movies_list:
        weight = movie['weight']
        probability = random.uniform(0, 1)
        probability, weight, vote_average = round(probability, 3), weight, movie['vote_average']

        if (len(movies_to_return) < 20 and 
            (len(movies_list) - len(movies_to_return) > 20) and 
            weight > probability and 
            vote_average > 6.5):
            movies_to_return.append(movie)

    id_to_gain = {}
    ids_to_lose = {}

    for movie in movies_to_return:
        movie_name = movie['title']
        print(f'Filme: {movie_name} | Disponível em {movie["provider"]}')
        ask = input(f"Que tal assistir {movie_name}? (S/N)")
        
        if ask.lower() == 's':
            id_to_gain[f'{movie["id"]}'] = movie['weight']
            break
        elif ask.lower() == 'n':
            ids_to_lose[f'{movie["id"]}'] = movie['weight']
        else:
            print('Resposta inválida...\nMostrando outro filme')     

    update_movie_weights(id_to_gain, ids_to_lose)

if __name__ == '__main__':
    main()
