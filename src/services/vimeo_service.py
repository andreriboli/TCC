from flask import jsonify, request

class VimeoService:
    def __init__(self, app, db_operations):
        self.db_operations = db_operations
        
        @app.route('/api/vimeo/mais-engajados', methods=['GET'])
        def getVideosMaisEngajados():
            result = self.db_operations.get_videos_mais_engajado()

            if result:
                return jsonify(result), 200
            else:
                return jsonify({"error": "Nenhum dado encontrado."}), 404

        @app.route('/api/vimeo/melhor-conclusao', methods=['GET'])
        def getVideosMelhorConclusao():
            result = self.db_operations.get_videos_melhor_conclusao()

            if result:
                return jsonify(result), 200
            else:
                return jsonify({"error": "Nenhum dado encontrado."}), 404
        
