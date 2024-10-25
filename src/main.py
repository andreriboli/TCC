import threading
import time
from datetime import datetime, timedelta

import pandas as pd
from api import start_api
from data_collection import coletar_atividades_concluidas_do_usuario, coletar_detalhes_usuario_do_curso, coletar_todos_os_cursos, coletar_usuarios_do_curso, coletar_atividades_do_curso
from database import DatabaseOperations
from db_util import DBUtil
from config import Config
from scrap_vimeo import VimeoScraper

def executar_coleta_diaria(config, db_util):

    try:
        db_util.connect()

        database_operations = DatabaseOperations(db_util, config)

        now = datetime.now()
        print(f"Iniciando coleta de dados às {now}")

        cursos = coletar_todos_os_cursos(config)
        if cursos:
            print("Cursos coletados com sucesso.")
            
            print("Iniciando inserção de categorias.")
            inserir_categorias(cursos, database_operations)
            print("Inserção de categorias concluída.")

            print("Iniciando inserção de cursos.")
            inserir_cursos(cursos, database_operations)
            print("Inserção de cursos concluída.")

            print("Iniciando inserção de usuários e inscrições.")
            inserir_usuarios_e_inscricoes(cursos, database_operations, config)
            print("Inserção de usuários e inscrições concluída.")

        print(f"Coleta e armazenamento concluídos às {datetime.now()}")

    except Exception as e:
        print(f"Erro durante a coleta de dados: {e}")
    finally:
        db_util.disconnect()

def inserir_categorias(cursos, database_operations):
    for curso in cursos:
        id_categoria = curso['categoryid']
        database_operations.inserir_categoria_por_id(id_categoria)
        print(f"Categoria {id_categoria} inserida para o curso {curso['fullname']}")

def inserir_cursos(cursos, database_operations):
    for curso in cursos:
        database_operations.inserir_curso(curso)
        print(f"Curso {curso['fullname']} inserido.")

def inserir_usuarios_e_inscricoes(cursos, database_operations, config):
    for curso in cursos:
        if curso['id'] == 1:
            continue

        usuarios = coletar_usuarios_do_curso(config, curso['id'])
        if usuarios:
            for usuario in usuarios:
                if usuario['id'] == 1 or usuario['username'] == 'guest':
                    continue

                moodle_id = usuario['id']

                is_teacher = False
                for role in usuario['roles']:
                    if role['shortname'] in ['editingteacher', 'teacher']:
                        is_teacher = True
                        break

                if is_teacher:
                    print(f"Professor encontrado: {usuario['fullname']}")
                    database_operations.inserir_professor(moodle_id, curso['id'])

                    atividades = coletar_atividades_do_curso(config, curso['id'])
                    if atividades:
                        for atividade in atividades:
                            print(f"Inserindo atividade {atividade['name']} criada pelo professor {usuario['fullname']}")
                            database_operations.inserir_atividade(moodle_id, curso['id'], atividade)

                detalhes_usuario = coletar_detalhes_usuario_do_curso(config, curso['id'], moodle_id)
                
                progresso = detalhes_usuario.get('progress') if detalhes_usuario else 0
                primeiro_acesso = usuario.get('firstaccess', 0)
                ultimo_acesso = usuario.get('lastaccess', 0)

                data_primeiro_acesso = datetime.fromtimestamp(primeiro_acesso) if primeiro_acesso > 0 else None
                data_ultimo_acesso = datetime.fromtimestamp(ultimo_acesso) if ultimo_acesso > 0 else None

                tempo_medio_conclusao = None

                if data_primeiro_acesso and data_ultimo_acesso:
                    tempo_medio_conclusao = data_ultimo_acesso - data_primeiro_acesso
                else:
                    tempo_medio_conclusao = timedelta(0)

                print(f"Inserindo usuário {usuario['fullname']} com progresso {progresso}, "
                    f"primeiro acesso {data_primeiro_acesso}, último acesso {data_ultimo_acesso}, "
                    f"tempo médio de conclusão: {tempo_medio_conclusao}")

                database_operations.inserir_usuario(usuario)

                if detalhes_usuario is None:
                    print(f"Detalhes do usuário {usuario['fullname']} não encontrados.")
                    continue

                database_operations.inserir_inscricao(
                    moodle_id=moodle_id,
                    curso_id=curso['id'],
                    progresso=progresso,
                    detalhes_usuario=detalhes_usuario,
                    usuario=usuario
                )

                atividades_concluidas = coletar_atividades_concluidas_do_usuario(config, curso['id'], moodle_id)
                if atividades_concluidas:
                    for atividade in atividades_concluidas:
                        database_operations.inserir_atividade_concluida(moodle_id, curso['id'], atividade)

def start_api_in_thread(database_operations):
    start_api(database_operations)

if __name__ == "__main__":
    config = Config()

    db_util_coleta = DBUtil(
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT
    )

    db_util_api = DBUtil(
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT
    )
    
    database_operations_api = DatabaseOperations(db_util_api, config)
    api_thread = threading.Thread(target=start_api_in_thread, args=(database_operations_api,))
    api_thread.start()  # Inicia a thread da API Flask

    # database_operations_coleta = DatabaseOperations(db_util_coleta, config)
    # coleta_thread = threading.Thread(target=executar_coleta_diaria, args=(config, db_util_coleta))
    # coleta_thread.start()  # Inicia a thread da coleta de dados
    # coleta_thread.join()

    api_thread.join()




    # database_operations = DatabaseOperations(db_util_coleta, config)
    # coleta_thread = threading.Thread(target=executar_coleta_diaria, args=(config, db_util_coleta))
    # coleta_thread.start()

    # vimeo_scraper = VimeoScraper(email=config.VIMEO_EMAIL, password=config.VIMEO_PASSWORD, download_dir=config.DOWNLOAD_DIR)

    # vimeo_scraper.login()
    # csv_url = vimeo_scraper.obter_link_csv()

    # if csv_url:
            # csv_file_path = vimeo_scraper.download_csv_directly(csv_url, config.DOWNLOAD_DIR)

    #         if csv_file_path:
    # try:
    #     file_path = r"C:\Desenvolvimento\stats_export (2).csv"
    #     df = pd.read_csv(file_path, skip_blank_lines=True)
 
    #     if df.iloc[-1].isnull().all() or df.iloc[-1].str.contains(r'["]').any():
    #         df = df[:-1]
        
    #     # Renomear as colunas para corresponder à tabela no banco de dados
    #     df.rename(columns={
    #         'views': 'views',
    #         'impressions': 'impressions',
    #         'finishes': 'finishes',
    #         'downloads': 'downloads',
    #         'unique_impressions': 'unique_impressions',
    #         'unique_viewers': 'unique_viewers',
    #         'mean_percent_watched': 'mean_percent_watched',
    #         'mean_seconds_watched': 'mean_seconds_watched',
    #         'total_seconds_watched': 'total_seconds_watched',
    #         'metadata.connections.video.uri': 'id_vimeo_video',
    #         'metadata.connections.video.title': 'title',
    #         'metadata.connections.video.created_time': 'created_time',
    #         'metadata.connections.video.likes': 'likes',
    #         'metadata.connections.video.comments': 'comments'
    #     }, inplace=True)
        
    #     # Exibir as primeiras linhas para verificar os dados
    #     # print("Dados com colunas renomeadas:")
    #     # print(df.head())

    #     # Iterar sobre cada linha do DataFrame e inserir no banco de dados
    #     for index, row in df.iterrows():
    #         database_operations.inserir_dados_vimeo(row)  # Chama a função passando cada linha (row) como parâmetro

    # except FileNotFoundError:
    #     print(f"Erro: O arquivo {file_path} não foi encontrado.")
    # except Exception as e:
    #     print(f"Ocorreu um erro ao tentar ler o arquivo: {e}")

                
    #             database_operations = DatabaseOperations(db_util, config)

    #             try:
    #                 db_util.connect()
    #                 print("Conectado ao banco de dados com sucesso.")

    #                 database_operations.salvar_dados_vimeo(df)

    #             except Exception as e:
    #                 logging.error(f"Erro durante a inserção dos dados no banco: {e}")
                
    #             finally:
    #                 db_util.disconnect()
    #                 print("Desconectado do banco de dados.")

    #         else:
    #             logging.error("O link do CSV não foi capturado com sucesso.")
            
    #         vimeo_scraper.fechar()