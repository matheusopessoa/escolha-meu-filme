import sqlite3
import random

# Função para estabelecer uma conexão com o banco de dados SQLite
def get_db_connection():
    # Conecta ao banco de dados 'database.db' (SQLite)
    conn = sqlite3.connect('database.db')
    # Retorna o objeto de conexão para ser usado nas operações de banco de dados
    return conn

# Função que busca filmes de acordo com o provedor e os gêneros fornecidos
def movies_search(provider: str, genres: list, runtime_list: list, release_year_list: list) -> list:
    conn = get_db_connection()  # Estabelece a conexão com o banco de dados
    cursor = conn.cursor()  # Cria um cursor para executar consultas SQL
    count_genres = len(genres)  # Conta quantos gêneros foram passados como argumento

    # Se houver mais de um gênero, monta uma query mais complexa
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
        # Executa a query, buscando filmes que correspondam ao provedor e aos dois gêneros
        results = cursor.execute(query, (
            provider, 
            f'%, {genres[0]},%', f'{genres[0]},%', f'%, {genres[0]}', genres[0], 
            f'%, {genres[1]},%', f'{genres[1]},%', f'%, {genres[1]}', genres[1]
        )).fetchall()

        if len(results) < 5:
            movies_in_results = []
            for movie in results:
                movies_in_results.append(movie[0])
            query = '''
                    SELECT * FROM movies 
                    WHERE provider = ? 
                    AND (genre_ids LIKE ? OR genre_ids LIKE ? OR genre_ids LIKE ? OR genre_ids = ?)
        '''
        # Executa a query buscando filmes que correspondam ao provedor e ao único gênero
            results2 = cursor.execute(query, (
                provider, 
                f'%,{genres[0]},%', f'{genres[0]},%', f'%,{genres[0]}', genres[0]
            )).fetchall()

            for movie in results2:
                if movie[0] not in movies_in_results:
                    results.append(movie)

            results3 = cursor.execute(query, (
                provider, 
                f'%,{genres[1]},%', f'{genres[1]},%', f'%,{genres[1]}', genres[1]
            )).fetchall()      
            for movie in results3:
                if movie[0] not in movies_in_results:
                    results.append(movie) 


    else:
        # Caso haja apenas um gênero, monta uma query mais simples
        query = '''
        SELECT * FROM movies 
        WHERE provider = ? 
        AND (genre_ids LIKE ? OR genre_ids LIKE ? OR genre_ids LIKE ? OR genre_ids = ?)
        '''
        # Executa a query buscando filmes que correspondam ao provedor e ao único gênero
        results = cursor.execute(query, (
            provider, 
            f'%,{genres[0]},%', f'{genres[0]},%', f'%,{genres[0]}', genres[0]
        )).fetchall()
    
    conn.close()  # Fecha a conexão com o banco de dados
    
    filter_runtime = []
  
    for movie in results:
        runtime = movie[12]

        if runtime_list[0] == 'T':
            filter_runtime.append(movie)

        else:
            if runtime_list[1] == 'T' and runtime < 60:
                filter_runtime.append(movie)
            elif runtime_list[2] == 'T' and runtime < 120:
                filter_runtime.append(movie)
            elif runtime_list[3] == 'T' and runtime < 250: 
                filter_runtime.append(movie)

    filter_release = []
    
    for movie in filter_runtime:
        date = movie[8]
        date = int(date)

        if release_year_list[0] == 'T':
            filter_release.append(movie)
        else:
            if release_year_list[1] == 'T'  and date >= 2014: 
                filter_release.append(movie)
            elif release_year_list[2] == 'T' and date >= 2004: 
                filter_release.append(movie)
            elif release_year_list[3] == 'T' and date >= 1990:
                filter_release.append(movie)
            elif release_year_list[4] == 'T' and date >= 1980:
                filter_release.append(movie)

    # A query retorna várias colunas: ID, Gêneros, Provedor, Peso, Título, Descrição, etc.
    #ID[0], Genres[1], Provider[2], Weight[3], Title[4], Description[5], Original_Lang[6], 
    #Popularity[7], Release_date[8], Vote_Average[9], Vote_count[10] #POSTER[11] #RUNTIME[12]
    return filter_release  # Retorna a lista de resultados da busca

# Função que atualiza os pesos dos filmes com base no feedback do usuário
def update_movie_weights(feedbacks_dict: dict) -> None:
    conn = get_db_connection()  # Estabelece a conexão com o banco de dados
    cursor = conn.cursor()  # Cria um cursor para executar comandos SQL
    feedbacks_list = feedbacks_dict['feedbacks']  # Extrai a lista de feedbacks do dicionário

    # Itera sobre a lista de feedbacks para processar cada filme
    for feedb in feedbacks_list:
        id, feedback = feedb['movie_id'], feedb['feedback']  # Extrai o ID do filme e o feedback
        # Obtém o peso atual do filme no banco de dados
        weight = cursor.execute('SELECT weight FROM movies WHERE id = ?', (id,)).fetchone()
        weight = float(weight[0])  # Converte o peso para um número decimal

        if feedback == 'like':
            if weight < 1.0:
                new_weight = weight + 0.25
            else:
                new_weight = 1.0
        elif feedback == 'dislike':
            if weight > 0.3:
                new_weight = weight - 0.01  
            else:
                new_weight = 0.3
        # Arredonda o novo peso para 2 casas decimais
        weight = (round(new_weight, 2))
        # Atualiza o peso do filme no banco de dados
        cursor.execute('UPDATE movies SET weight = ? WHERE id = ?', (weight, id))
    
    conn.commit()  # Confirma as alterações no banco de dados
    conn.close()  # Fecha a conexão

# Função principal que filtra e retorna filmes com base no provedor e gêneros fornecidos
def main(provider: str, genres: list, runtime: list, release_year: list) -> dict: #main(provider, genres, runtime, release_year)
    movies_list = movies_search(provider, genres, runtime, release_year)  # Busca a lista de filmes com base nos parâmetros
    movies_to_return = {}  # Dicionário para armazenar os filmes selecionados

    # Itera sobre a lista de filmes retornada pela busca
    for movie in movies_list:
        weight, vote_average, title = float(movie[3]), float(movie[9]), str(movie[4])  # Extrai peso, média de votos e título
        probability = round(random.uniform(0, 1), 3)  # Gera um número aleatório para comparar com o peso

        # Se houver mais de 100 filmes, filtra os que têm peso e média de votos maiores
        if len(movies_list) > 100:
            if (len(movies_to_return) != len(movies_list) and 
                weight > probability and 
                vote_average > 7.5):
                # Adiciona o filme ao dicionário de retorno se atender aos critérios
                movies_to_return[f'{title}'] = movie

        # Se houver mais de 50 filmes, usa um critério menos restritivo
        elif len(movies_list) > 50:
            if (len(movies_to_return) != len(movies_list) and 
                weight > probability and 
                vote_average > 7):
                movies_to_return[f'{title}'] = movie

        # Se houver mais de 10 filmes, relaxa ainda mais o critério
        elif len(movies_list) > 10:
            if (len(movies_to_return) != len(movies_list) and 
                weight > (probability - 0.1) and 
                vote_average > 6.5):
                movies_to_return[f'{title}'] = movie

        # Se houver poucos filmes, usa critérios mais flexíveis
        else:
            if vote_average > 6.0:
                movies_to_return[f'{title}'] = movie
    
    return movies_to_return  # Retorna o dicionário com os filmes filtrados

