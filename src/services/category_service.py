from flask import jsonify, request

class CategoryService:
    def __init__(self, app, db_operations):
        self.db_operations = db_operations

        @app.route('/api/categorias/distribuicao-cursos-ativos', methods=['GET'])
        def distribuicao_cursos_ativos():

            categorias = self.db_operations.distribuicao_cursos_ativos()
            
            if categorias:
                return jsonify(categorias), 200
            else:
                return jsonify({"error": "Nenhum usuário encontrado."}), 404
