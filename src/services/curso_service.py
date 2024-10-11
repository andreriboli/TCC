from flask import jsonify, request

class CursoService:
    def __init__(self, app, db_operations):
        self.db_operations = db_operations

        @app.route('/api/cursos/distribuicao-alunos', methods=['GET'])
        def distribuicao_alunos_por_curso():
            try:
                resultado = db_operations.distribuicao_cursos_ativos()
                return jsonify(resultado), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500
            

        @app.route('/api/cursos/mais-acessados-semana', methods=['GET'])
        def top_cursos_mais_acessados_semana():
            try:
                resultado = db_operations.top_cursos_mais_acessados_semana()
                return jsonify(resultado), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500    
