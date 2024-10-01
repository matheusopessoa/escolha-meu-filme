import sqlite3
import random

def get_db_connection():
    conn = sqlite3.connect('database.db')
    return conn

def movies_search(provider: str, genres: list) -> list:
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
    return results

def update_movie_weights(feedbacks_dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    feedbacks_list = feedbacks_dict['feedbacks']

    for feedb in feedbacks_list:
        id, feedback = feedb['movie_id'], feedb['feedback']
        weight = cursor.execute('SELECT weight FROM movies WHERE id = ?', (id,)).fetchone()
        new_weight = float(weight[0])

        if new_weight > 0.35 and new_weight < 0.85:
            if feedback == 'like':
                new_weight += 0.10
            elif feedback == 'dislike':
                new_weight -= 0.10
        
        weight = (round(new_weight, 2))
        cursor.execute('UPDATE movies SET weight = ? WHERE id = ?', (weight, id))
    conn.commit()

    conn.close()

def main(provider: str, genres: list):
    movies_list = movies_search(provider, genres)
    movies_to_return = {}

    for movie in movies_list:
        weight, vote_average, title = float(movie[3]), float(movie[9]), str(movie[4])
        probability = round(random.uniform(0, 1), 3)

        if len(movies_list) > 100:
            if (len(movies_to_return) != len(movies_list) and 
                weight > probability and 
                vote_average > 7.5):
                movies_to_return[f'{title}'] = movie
        elif len(movies_list) > 50:
            if (len(movies_to_return) != len(movies_list) and 
                weight > probability and 
                vote_average > 7):
                movies_to_return[f'{title}'] = movie
        elif len(movies_list) > 10:
            if (len(movies_to_return) != len(movies_list) and 
                weight > probability and 
                vote_average > 6.5):
                movies_to_return[f'{title}'] = movie
        else:
            if vote_average > 6.0:
                movies_to_return[f'{title}'] = movie
    
    return movies_to_return

if __name__ == '__main__':
    a = {
  "feedbacks": [
    {
      "movie_id": "10515",
      "feedback": "like"
    },
    {
      "movie_id": "497582",
      "feedback": "dislike"
    }
  ]
}
    update_movie_weights(a)

