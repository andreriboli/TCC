import time
import logging
from datetime import datetime
from data_collection import coletar_todos_os_cursos, coletar_usuarios_do_curso
from database import DatabaseOperations
from db_util import DBUtil
from config import Config

# Configurar o logging para gravar em um arquivo
logging.basicConfig(
    filename='log_coleta_dados.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

def executar_coleta_diaria():
    config = Config()  # Certifique-se de que o config é passado

    # Inicializar a classe DBUtil
    db_util = DBUtil(
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT
    )

    try:
        # Conectar ao banco de dados
        db_util.connect()

        # Inicializar operações no banco de dados
        database_operations = DatabaseOperations(db_util, config)

        now = datetime.now()
        logging.info(f"Iniciando coleta de dados às {now}")

        # Coletar todos os cursos
        cursos = coletar_todos_os_cursos(config)
        if cursos:
            print("Cursos coletados com sucesso.")
            # Continue com o processamento de cursos aqui, se necessário

        logging.info(f"Coleta e armazenamento concluídos às {datetime.now()}")

    except Exception as e:
        logging.error(f"Erro durante a coleta de dados: {e}")
    finally:
        # Garantir que a conexão com o banco de dados seja encerrada
        db_util.disconnect()

def inserir_categorias(cursos, database_operations):
    for curso in cursos:
        id_categoria = curso['category']
        database_operations.inserir_categoria_por_id(id_categoria)

def inserir_cursos(cursos, database_operations):
    for curso in cursos:
        database_operations.inserir_curso(curso)

def inserir_usuarios_e_inscricoes(cursos, database_operations):
    for curso in cursos:
        usuarios = coletar_usuarios_do_curso(curso['id'])  # Função que coleta usuários por curso
        for usuario in usuarios:
            database_operations.inserir_usuario(usuario)
            database_operations.inserir_inscricao(usuario['id'], curso)


if __name__ == "__main__":
    executar_coleta_diaria()
