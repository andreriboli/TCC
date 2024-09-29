from flask import Flask
from flask_cors import CORS  # Importa o CORS
from services.user_service import UserService

app = Flask(__name__)
CORS(app)  # Habilita o CORS para todas as rotas

# Função para registrar os serviços, passando o database_operations
def register_services(app, database_operations):
    UserService(app, database_operations)

# Função para iniciar a API, recebendo a instância de database_operations
def start_api(database_operations):
    register_services(app, database_operations)
    app.run(debug=False, port=5000)
