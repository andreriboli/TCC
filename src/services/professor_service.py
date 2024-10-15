from flask import jsonify, request

class ProfessorService:
    def __init__(self, app, db_operations):
        self.db_operations = db_operations

        @app.route('/api/professor/top-professor', methods=['GET'])
        def top_professores():
            
            professor = self.db_operations.top_professores()
            
            if professor:
                return jsonify(professor), 200
            else:
                return jsonify({"error": "Nenhum usuário encontrado."}), 404
