import requests
import sqlite3 

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

def get_movie_by_id(movie_id: int) -> dict:
    movie_id = int(movie_id)

    base_url = "https://api.themoviedb.org/3"
    url = f"{base_url}/movie/{movie_id}"
    params = {
        "api_key": "9f49b76745c71b8a1aa4407888bbb40a",
        "language": "pt-BR"  
    }

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()  
    else:
        print("Erro ao buscar filme:", response.status_code)
        return None     

def update_title_and_overview(id, overview, title):
    id = str(id)

    cursor.execute("""
        UPDATE movies
        SET title = ?, overview = ?
        WHERE id = ?
    """, (title, overview, id))
    conn.commit()
    print(f'{id} Ok')
    print()

def main():
    
    movies: list = cursor.execute('SELECT id FROM movies').fetchall() #lista de tuplas

    for tuple in movies:
            id = tuple[0]
            if id > 11003:         
                movie_data = get_movie_by_id(id)
                
                overview_pt = movie_data['overview']
                title_pt = movie_data['title']

                update_title_and_overview(id, overview_pt, title_pt)
                
if __name__ == '__main__':
     main()