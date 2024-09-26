# from flask import Flask, request, jsonify

# app = Flask(__name__)

# @app.route('/api/consulta', methods=['POST'])
# def consulta_post():
#     data = request.json
#     parametro1 = data.get('parametro1')
#     parametro2 = data.get('parametro2')
#     resultado = f"Recebido: {parametro1} e {parametro2}"
#     return jsonify({"resultado": resultado})

# @app.route('/api/consulta', methods=['GET'])
# def consulta_get():
#     parametro1 = request.args.get('parametro1')
#     parametro2 = request.args.get('parametro2')
    
#     if parametro1 and parametro2:
#         resultado = f"GET Recebido: {parametro1} e {parametro2}"
#         return jsonify({"resultado": resultado})
#     else:
#         return jsonify({"erro": "Parâmetros faltando"}), 400

# if __name__ == "__main__":
#     app.run(debug=False)

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/consulta', methods=['GET'])
def consulta():
    parametro1 = request.args.get('parametro1')
    parametro2 = request.args.get('parametro2')

    resultado = f"Recebido: {parametro1} e {parametro2}"
    return jsonify({"resultado": resultado})

@app.route('/api/coleta', methods=['POST'])
def coleta_dados():
    try:
        return jsonify({"status": "Coleta de dados iniciada com sucesso!"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def start_api():
    app.run(debug=False, port=5000)