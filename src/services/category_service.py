from flask import jsonify, request

class CategoryService:
    def __init__(self, app, db_operations):
        self.db_operations = db_operations

        @app.route('/api/categorias/distribuicao-cursos-ativos-by-category', methods=['GET'])
        def distribuicao_cursos_ativos():
            end_date = request.args.get('endDate')

            print(f"Data de fim: {end_date}")
            categorias = self.db_operations.distribuicao_cursos_ativos_by_category(end_date)
            
            if categorias:
                return jsonify(categorias), 200
            else:
                return jsonify({"error": "Nenhum usuário encontrado."}), 404
