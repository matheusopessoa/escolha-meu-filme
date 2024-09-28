from flask import Flask, request, jsonify
from get_movies import movies_search, update_movie_weights

app = Flask(__name__)

@app.route('/movies', methods=['GET'])
def get_movies():
    provider = request.args.get('provider')
    genres = request.args.getlist('genres')

    if not provider or not genres:
        return jsonify({'error': 'Parâmetros "provider" e "genres" são necessários.'}), 400

    movies = movies_search(provider, genres)
    movies_list = [dict(movie) for movie in movies]

    return jsonify(movies_list)

@app.route('/feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    movie_id = data.get('movie_id')
    feedback = data.get('feedback')  # 'like' ou 'dislike'

    if not movie_id or feedback not in ['like', 'dislike']:
        return jsonify({'error': 'Campos "movie_id" e "feedback" são necessários.'}), 400

    if feedback == 'like':
        id_to_gain = {movie_id: 0}  # O valor real não importa aqui
        ids_to_lose = {}
    else:
        id_to_gain = {}
        ids_to_lose = {movie_id: 0}

    update_movie_weights(id_to_gain, ids_to_lose)

    return jsonify({'message': 'Feedback recebido com sucesso.'})

if __name__ == '__main__':
    app.run(debug=True)
