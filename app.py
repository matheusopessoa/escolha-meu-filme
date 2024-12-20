from flask import Flask, request, jsonify
from get_movies import main, update_movie_weights
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": [
    #"http://localhost:5173",
    "https://www.escolhameufilme.com",
    "https://escolhameufilme.com",
    "https://escolhameufilme.vercel.app",
    "http://escolhameufilme.com",
    "http://www.escolhameufilme.com",
]}})

# Rota para buscar filmes com base no provedor e gêneros fornecidos via parâmetros de URL
@app.route('/movies', methods=['GET'])
def get_movies():
    provider = request.args.get('provider')
    runtime = request.args.getlist('runtime')
    release_year = request.args.getlist('release_year')
    genres = request.args.getlist('genres')


    if not provider or not genres:
        return jsonify({'error': 'Parâmetros "provider" e "genres" são necessários.'}), 400

    movies = main(provider, genres, runtime, release_year)

    return jsonify(movies)

# Rota para receber feedback dos usuários sobre os filmes
@app.route('/feedback', methods=['POST'])
def feedback():
    feedbacks = request.get_json()

    if not feedbacks:
        return jsonify({'error': 'Nenhum feedback encontrado.'}), 400

    update_movie_weights(feedbacks)
    return jsonify({'message': 'Feedback recebido com sucesso.'})

if __name__ == '__main__':
    app.run()
