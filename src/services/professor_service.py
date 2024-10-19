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
        
        
        @app.route('/api/professor/mais-engajados', methods=['GET'])
        def get_professor_mais_engajado():
            result = self.db_operations.get_professor_mais_engajado()

            if result:
                return jsonify(result), 200
            else:
                return jsonify({"error": "Nenhum dado encontrado."}), 404
        
