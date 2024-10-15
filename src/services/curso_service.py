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
            
        
        @app.route('/api/cursos/menos-inscricoes', methods=['GET'])
        def cursos_com_menos_inscricoes():
            try:
                resultado = db_operations.cursos_com_menos_inscricoes()
                return jsonify(resultado), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500    
            
        @app.route('/api/cursos/criados-por-semestre', methods=['GET'])
        def get_cursos_criados_por_semestre():
            result = db_operations.get_cursos_por_semestre()

            if result:
                return jsonify(result)
            else:
                return jsonify({"error": "Nenhum dado encontrado."}), 404
