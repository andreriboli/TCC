from flask import jsonify, request

class UserService:
    def __init__(self, app, db_operations):
        self.db_operations = db_operations

        @app.route('/api/usuarios/logados', methods=['GET'])
        def ultimos_usuarios_logados():
            start_date = request.args.get('startDate')
            end_date = request.args.get('endDate')
            
            usuarios_logados = self.db_operations.ultimos_usuarios_logados(start_date, end_date)
            
            if usuarios_logados:
                return jsonify(usuarios_logados), 200
            else:
                return jsonify({"error": "Nenhum usuário encontrado."}), 404
