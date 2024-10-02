from flask import Flask, request, jsonify
from get_movies import main, update_movie_weights

app = Flask(__name__)

# Rota para buscar filmes com base no provedor e gêneros fornecidos via parâmetros de URL
@app.route('/movies', methods=['GET'])
def get_movies():
    # Obtém o parâmetro 'provider' da URL (ex: ?provider=Netflix)
    provider = request.args.get('provider')
    
    # Obtém a lista de gêneros do parâmetro 'genres' (ex: ?genres=action&genres=comedy)
    genres = request.args.getlist('genres')

    # Valida se os parâmetros obrigatórios foram passados
    if not provider or not genres:
        # Retorna um erro 400 se 'provider' ou 'genres' não forem fornecidos
        return jsonify({'error': 'Parâmetros "provider" e "genres" são necessários.'}), 400

    # Chama a função principal que filtra os filmes com base no provedor e gêneros
    movies = main(provider, genres)

    # Retorna a lista de filmes filtrados em formato JSON
    return jsonify(movies)

# Rota para receber feedback dos usuários sobre os filmes
@app.route('/feedback', methods=['POST'])
def feedback():
    # Obtém os feedbacks enviados no corpo da requisição em formato JSON
    feedbacks = request.get_json()

    # Verifica se os feedbacks foram fornecidos
    if not feedbacks:
        # Retorna um erro 400 se não houver feedbacks na requisição
        return jsonify({'error': 'Nenhum feedback encontrado.'}), 400

    # Atualiza os pesos dos filmes com base nos feedbacks recebidos
    update_movie_weights(feedbacks)

    # Retorna uma mensagem de sucesso após processar os feedbacks
    return jsonify({'message': 'Feedback recebido com sucesso.'})

# Inicia o servidor Flask em modo de depuração
if __name__ == '__main__':
    app.run(debug=True)

