from flask import Flask
from flask_cors import CORS
from services.category_service import CategoryService
from services.curso_service import CursoService
from services.professor_service import ProfessorService
from services.user_service import UserService

app = Flask(__name__)
CORS(app)

def register_services(app, database_operations):
    CategoryService(app, database_operations)
    UserService(app, database_operations)
    CursoService(app, database_operations)
    ProfessorService(app, database_operations)

def start_api(database_operations):
    register_services(app, database_operations)
    app.run(debug=False, port=5000)
