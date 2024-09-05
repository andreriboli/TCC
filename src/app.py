from flask import Flask, jsonify
from flask_cors import CORS
from db_util import DBUtil
from config import Config

app = Flask(__name__)
CORS(app)  # Permitir CORS para comunicação com o frontend

# Inicializar a configuração
config = Config()

# Inicializar a conexão com o banco de dados usando as configurações
db_config = config.get_db_config()
db = DBUtil(
    dbname=db_config['dbname'],
    user=db_config['user'],
    password=db_config['password'],
    host=db_config['host'],
    port=db_config['port']
)
db.connect()

# Endpoint para retornar dados da tabela example_table
@app.route('/api/example-endpoint', methods=['GET'])
def get_example_data():
    query = "SELECT id, nome, descricao FROM example_table;"
    try:
        with db.connection.cursor() as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
            results = [{"id": row[0], "nome": row[1], "descricao": row[2]} for row in data]
            a = jsonify(results)
            print(a)
            return a 
    except Exception as e:
        print(f"Erro ao executar consulta: {e}")
        return jsonify({"error": "Erro ao buscar dados"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3000)
