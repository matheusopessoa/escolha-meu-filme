import sqlite3
import numpy as np
import random
from googletrans import Translator

def get_db_connection():
    conn = sqlite3.connect('database.db')
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
    #ID[0], Genres[1], Provider[2], Weight[3], Tittle[4], Description[5], Orignal_Lang[6], 
    #Popularity[7], Release_date[8], Vote_Average[9], Vote_count[10] 
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
    movies_list: np.array = movies_search(provider, genres)
    movies_to_return = []

    for movie in movies_list:
        weight = movie[3].astype(np.float16)
        probability = random.uniform(0, 1)
        probability = round(probability, 3)
        vote_average = movie[9].astype(np.float16)

        if len(movies_list) > 100:
            if (len(movies_to_return) != len(movies_list) and 
                weight > probability and 
                vote_average > 7.5):
                movies_to_return.append(movie)
        elif len(movies_list) > 50:
            if (len(movies_to_return) != len(movies_list) and 
                weight > probability and 
                vote_average > 7):
                movies_to_return.append(movie)     
        elif len(movies_list) > 10:
            if (len(movies_to_return) != len(movies_list) and 
                weight > probability and 
                vote_average > 6.5):
                movies_to_return.append(movie)        
        else:
            if vote_average > 6.0:
                movies_to_return.append(movie)
            
    id_to_gain = {}
    ids_to_lose = {}
    return_size = len(movies_to_return)
    print(f'Selecionamos uma lista com {return_size} filmes, escolhidos a dedo para você')
    
    for movie in movies_to_return:
        print(f'Restam {return_size - len(ids_to_lose)} filmes em sua lista')
        movie_id, movie_weight, movie_name, movie_provider = movie[0], movie[3], movie[4], movie[2]
        print(f'Filme: {movie_name} | Disponível em {movie_provider}')
        ask = input(f"Que tal assistir {movie_name}? (S/N)")
        if ask.lower() == 's':
            id_to_gain[f'{movie_id}'] = movie_weight
            break
        elif ask.lower() == 'n':
            ids_to_lose[f'{movie_id}'] = movie_weight
        else:
            print('Resposta inválida...\nMostrando outro filme')     

    update_movie_weights(id_to_gain, ids_to_lose)

if __name__ == '__main__':
    main()
